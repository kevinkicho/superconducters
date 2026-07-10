#!/usr/bin/env python3
"""
Generate paginated CHANGELOG pages from git history.

Output layout
-------------
  CHANGELOG.md              # Hub: agent guide, summary, page 1 (newest commits)
  changelog/README.md       # Index of all pages + regen instructions
  changelog/page-NN.md      # Additional pages (older commits), newest-first overall

Usage
-----
  python scripts/generate_changelog.py
  python scripts/generate_changelog.py --page-size 75
  python scripts/generate_changelog.py --repo-url https://github.com/owner/repo

Agents: after finishing work and committing, re-run this script and commit the
updated CHANGELOG.md + changelog/** files so the log stays current.
"""
from __future__ import annotations

import argparse
import html
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PAGE_SIZE = 80
DEFAULT_REPO = "https://github.com/kevinkicho/superconducters"


def parse_iso(s: str) -> datetime:
    return datetime.fromisoformat(s)


def fmt_duration(seconds: float | None) -> str:
    if seconds is None or seconds < 0:
        return "--"
    if seconds < 60:
        return f"{int(seconds)}s"
    if seconds < 3600:
        m, s = int(seconds // 60), int(seconds % 60)
        return f"{m}m {s}s" if s else f"{m}m"
    h, m = int(seconds // 3600), int((seconds % 3600) // 60)
    return f"{h}h {m}m" if m else f"{h}h"


def truncate(text: str, limit: int = 72) -> tuple[str, str | None]:
    text = " ".join(text.split())
    if len(text) <= limit:
        return text, None
    return text[: limit - 1].rstrip() + "...", text


def one_line_details(short: str, full: str | None) -> str:
    if not full:
        return html.escape(short).replace("|", "\\|")
    return (
        f"<details><summary>{html.escape(short)}</summary>"
        f"<code>{html.escape(full)}</code></details>"
    ).replace("|", "\\|")


def git_entries() -> list[dict]:
    raw = subprocess.check_output(
        [
            "git",
            "log",
            "--pretty=format:>>>|%H|%ad|%an|%s",
            "--date=iso-strict",
            "--numstat",
        ],
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    entries: list[dict] = []
    cur = None
    for line in raw.splitlines():
        if line.startswith(">>>|"):
            if cur:
                entries.append(cur)
            _, h, ad, an, subj = line.split("|", 4)
            cur = {
                "h": h[:8],
                "full": h,
                "ad": ad,
                "an": an,
                "subj": subj,
                "ins": 0,
                "del": 0,
                "files": [],
            }
            continue
        if not line.strip() or cur is None:
            continue
        parts = line.split("\t")
        if len(parts) < 3:
            parts = re.split(r"\s+", line, maxsplit=2)
        if len(parts) < 3:
            continue
        a, d, path = parts[0], parts[1], parts[2]
        cur["files"].append(path)
        if a != "-":
            try:
                cur["ins"] += int(a)
            except ValueError:
                pass
        if d != "-":
            try:
                cur["del"] += int(d)
            except ValueError:
                pass
    if cur:
        entries.append(cur)
    return entries


def attach_duration(entries: list[dict]) -> None:
    """entries newest-first; duration = gap since same author's previous commit."""
    last_by_author: dict[str, datetime] = {}
    for e in reversed(entries):
        t = parse_iso(e["ad"])
        prev = last_by_author.get(e["an"])
        e["duration_s"] = None if prev is None else (t - prev).total_seconds()
        last_by_author[e["an"]] = t


def describe(e: dict) -> str:
    files = [f for f in e["files"] if not f.startswith("logs/")]
    log_only = not files and bool(e["files"])
    m = re.match(r"agent-(\d+):\s*(t\d+|.*)$", e["subj"])
    task = m.group(2) if m else e["subj"]

    if log_only:
        base = "Session/logging artifacts only"
    elif not e["files"]:
        base = e["subj"]
    else:
        docs = [f for f in files if f.startswith("docs/") or f.endswith(".md")]
        pys = [f for f in files if f.endswith(".py") and not f.startswith("tests/")]
        tests = [f for f in files if f.startswith("tests/")]
        data = [
            f
            for f in files
            if f.startswith("data/")
            or (f.endswith(".json") and not f.startswith("logs/"))
        ]
        parts: list[str] = []
        if docs:
            parts.append(
                "docs/md: " + ", ".join(sorted({Path(f).name for f in docs})[:5])
            )
        if pys:
            parts.append(
                "code: " + ", ".join(sorted({Path(f).name for f in pys})[:5])
            )
        if tests:
            parts.append(
                "tests: " + ", ".join(sorted({Path(f).name for f in tests})[:4])
            )
        if data:
            parts.append(
                "data: " + ", ".join(sorted({Path(f).name for f in data})[:4])
            )
        if not parts:
            parts.append(f"{len(files)} path(s)")
        joined = "; ".join(parts)
        if re.match(r"^(agent-\d+:\s*)?t\d+\s*$", e["subj"]):
            base = f"Task {task}: {joined}"
        elif not e["subj"].startswith("agent-"):
            base = f"{e['subj']} -- {joined}"
        else:
            base = f"{e['subj']}: {joined}"

    if e["files"]:
        nlog = sum(1 for f in e["files"] if f.startswith("logs/"))
        n = len(e["files"])
        extra = f" ({n} files"
        if nlog:
            extra += f", {nlog} logs"
        extra += ")"
        base += extra
    return base


def duration_cell(e: dict, cap: float = 6 * 3600) -> str:
    dur_s = e.get("duration_s")
    if dur_s is None:
        return "--"
    if dur_s > cap:
        return f">6h ({fmt_duration(dur_s)})"
    return fmt_duration(dur_s)


def table_header() -> list[str]:
    return [
        "| # | When | Who | Task | What | +LOC | -LOC | Duration | SHA |",
        "|--:|------|-----|------|------|-----:|-----:|----------|-----|",
    ]


def table_rows(
    slice_entries: list[dict],
    start_index: int,
    repo_url: str,
) -> list[str]:
    """start_index is 1-based global rank among newest-first list."""
    rows: list[str] = []
    for i, e in enumerate(slice_entries):
        rank = start_index + i
        when = e["ad"].replace("T", " ")
        who = e["an"]
        task_short, task_full = truncate(e["subj"], 48)
        what_short, what_full = truncate(describe(e), 64)
        task_cell = one_line_details(task_short, task_full)
        what_cell = one_line_details(what_short, what_full)
        dur = duration_cell(e)
        sha_url = f"{repo_url}/commit/{e['full']}"
        rows.append(
            f"| {rank} | `{when}` | `{who}` | {task_cell} | {what_cell} | "
            f"+{e['ins']:,} | -{e['del']:,} | {dur} | "
            f"[`{e['h']}`]({sha_url}) |"
        )
    return rows


def page_href(p: int, *, hub: bool) -> str:
    """Href to page p. hub=True: paths as seen from repo-root CHANGELOG.md."""
    if p <= 1:
        return "CHANGELOG.md#activity-log-page-1-latest" if hub else "../CHANGELOG.md"
    return f"changelog/page-{p:02d}.md" if hub else f"page-{p:02d}.md"


def nav_bar(
    page: int,
    total_pages: int,
    page_size: int,
    total: int,
    *,
    hub: bool,
) -> str:
    """Markdown navigation between paginated changelog pages."""
    parts: list[str] = []

    if page > 1:
        parts.append(f"[<- Previous]({page_href(page - 1, hub=hub)})")
    else:
        parts.append("<- Previous")

    # Compact page list with ellipses
    window: list[int] = []
    for p in range(1, total_pages + 1):
        if p == 1 or p == total_pages or abs(p - page) <= 2:
            window.append(p)
        elif window and window[-1] != -1:
            window.append(-1)

    num_bits: list[str] = []
    for p in window:
        if p == -1:
            num_bits.append("...")
            continue
        if p == page:
            num_bits.append(f"**{p}**")
        else:
            num_bits.append(f"[{p}]({page_href(p, hub=hub)})")
    parts.append(" ".join(num_bits))

    if page < total_pages:
        parts.append(f"[Next ->]({page_href(page + 1, hub=hub)})")
    else:
        parts.append("Next ->")

    start = (page - 1) * page_size + 1
    end = min(page * page_size, total)
    meta = (
        f"Page **{page}** of **{total_pages}** | "
        f"commits **{start}-{end}** of **{total}** (newest first)"
    )
    return f"{' | '.join(parts)}\n\n{meta}"


def agent_guide_md(page_size: int) -> str:
    return f"""## Agent instructions (read before editing this changelog)

This changelog is **machine-generated** and **paginated** for GitHub viewing. Do not hand-edit hundreds of table rows.

### Layout

| Path | Role |
|------|------|
| [`CHANGELOG.md`](CHANGELOG.md) | Hub: this guide, summary stats, **page 1** (latest {page_size} commits) |
| [`changelog/README.md`](changelog/README.md) | Page index + regen cheat-sheet |
| [`changelog/page-NN.md`](changelog/) | Older pages (`page-02`, `page-03`, ...), same table schema |

Commit order in tables is always **newest -> oldest**. Global row `#` is stable across pages (1 = newest commit).

### Table columns

| Column | Source |
|--------|--------|
| `#` | Rank in newest-first history (1 = tip of `main`) |
| When | `git` author date (`--date=iso-strict`) |
| Who | `git` author (`agent-2` / `agent-3` / `agent-4` / human) |
| Task | Commit subject; long text uses `<details>` expanders |
| What | Inferred from paths (`--numstat`); expanders for long text |
| +LOC / -LOC | `git log --numstat` line counts |
| Duration | Wall-clock gap since **same author's** previous commit (not model runtime). `>`6h marks idle gaps. `--` if first commit by that author |
| SHA | Link to commit on GitHub |

### When you upgrade the app / finish a task

1. Commit your work with a **descriptive subject** (avoid empty `agent-N: tK` if you can name the change).
2. From the repo root, regenerate:

```bash
python scripts/generate_changelog.py
# optional:
python scripts/generate_changelog.py --page-size {page_size}
```

3. Stage and commit generated files only:

```bash
git add CHANGELOG.md changelog/
git commit -m "docs: refresh changelog after <your change> [skip ci]"
```

4. **Do not**:
   - Manually insert rows into the middle of a page (regen will overwrite)
   - Delete `scripts/generate_changelog.py`
   - Put full history only in `CHANGELOG.md` without pagination (GitHub UI becomes unusable)
   - Change column meanings without updating this guide and the generator together

### Optional flags

```text
--page-size N     Rows per page (default {page_size})
--repo-url URL    Base URL for commit links
--dry-run         Print plan only, write nothing
```

### Duration caveat

Duration is **estimated** from commit timestamps, not token/inference time. Parallel agents and overnight gaps produce large durations; treat `>6h` as session boundaries, not continuous work.
"""


def build(
    page_size: int,
    repo_url: str,
    dry_run: bool = False,
) -> None:
    entries = git_entries()
    attach_duration(entries)
    total = len(entries)
    total_pages = max(1, (total + page_size - 1) // page_size)

    agent_n = sum(1 for e in entries if e["an"].startswith("agent-"))
    other_n = total - agent_n
    total_ins = sum(e["ins"] for e in entries)
    total_del = sum(e["del"] for e in entries)

    pages: list[list[dict]] = []
    for p in range(total_pages):
        start = p * page_size
        pages.append(entries[start : start + page_size])

    gen_at = datetime.now().astimezone().isoformat(timespec="seconds")

    if dry_run:
        print(f"commits={total} pages={total_pages} page_size={page_size}")
        print(f"+LOC={total_ins} -LOC={total_del}")
        return

    out_dir = ROOT / "changelog"
    # remove old page-*.md to avoid stale pages when history shrinks
    if out_dir.exists():
        for old in out_dir.glob("page-*.md"):
            old.unlink()
    out_dir.mkdir(parents=True, exist_ok=True)

    # --- CHANGELOG.md hub + page 1 ---
    hub: list[str] = []
    hub.append("# Changelog")
    hub.append("")
    hub.append(
        "Paginated activity log for **superconducters** (newest first). "
        "Built mainly by **Ollama Swarm** (DeepSeek V4 Flash agents) with human maintainer commits."
    )
    hub.append("")
    hub.append(agent_guide_md(page_size))
    hub.append("")
    hub.append("---")
    hub.append("")
    hub.append("## Summary")
    hub.append("")
    hub.append("| Metric | Value |")
    hub.append("|--------|-------|")
    hub.append(f"| Commits listed | {total} |")
    hub.append(f"| Pages (`{page_size}` per page) | {total_pages} |")
    hub.append(f"| Agent commits | {agent_n} |")
    hub.append(f"| Human / other | {other_n} |")
    hub.append(f"| Total +LOC | +{total_ins:,} |")
    hub.append(f"| Total -LOC | -{total_del:,} |")
    hub.append(f"| Net LOC | {total_ins - total_del:+,} |")
    hub.append("| Order | Newest -> oldest |")
    hub.append(f"| Generated | `{gen_at}` |")
    hub.append("")
    hub.append("### Jump to page")
    hub.append("")
    jump = ["[1 (latest)](CHANGELOG.md#activity-log-page-1-latest)"]
    for p in range(2, total_pages + 1):
        jump.append(f"[{p}](changelog/page-{p:02d}.md)")
    hub.append(" | ".join(jump))
    hub.append("")
    hub.append(f"Full index: [`changelog/README.md`](changelog/README.md)")
    hub.append("")
    hub.append("---")
    hub.append("")
    hub.append("## Activity log (page 1, latest)")
    hub.append("")
    hub.append(nav_bar(1, total_pages, page_size, total, hub=True))
    hub.append("")
    hub.append(
        "> Click a truncated **Task** / **What** cell (summary ends with `...`) to expand."
    )
    hub.append("")
    hub.extend(table_header())
    hub.extend(table_rows(pages[0], start_index=1, repo_url=repo_url))
    hub.append("")
    hub.append(nav_bar(1, total_pages, page_size, total, hub=True))
    hub.append("")
    hub.append("---")
    hub.append("")
    hub.append(
        f"*Regenerate: `python scripts/generate_changelog.py` | "
        f"page size {page_size} | {total} commits | {total_pages} pages*"
    )
    hub.append("")

    (ROOT / "CHANGELOG.md").write_text("\n".join(hub), encoding="utf-8", newline="\n")

    # --- additional pages ---
    for p in range(2, total_pages + 1):
        start_index = (p - 1) * page_size + 1
        end_index = min(p * page_size, total)
        body: list[str] = []
        body.append(f"# Changelog -- page {p} of {total_pages}")
        body.append("")
        body.append(
            f"Older commits (global rows **{start_index}-{end_index}**, newest-first overall). "
            f"Hub + agent guide: [`../CHANGELOG.md`](../CHANGELOG.md)."
        )
        body.append("")
        body.append(nav_bar(p, total_pages, page_size, total, hub=False))
        body.append("")
        body.append(
            "> Click truncated **Task** / **What** cells to expand full text."
        )
        body.append("")
        body.extend(table_header())
        body.extend(
            table_rows(pages[p - 1], start_index=start_index, repo_url=repo_url)
        )
        body.append("")
        body.append(nav_bar(p, total_pages, page_size, total, hub=False))
        body.append("")
        body.append(
            f"*Generated `{gen_at}` | `python scripts/generate_changelog.py`*"
        )
        body.append("")
        path = out_dir / f"page-{p:02d}.md"
        path.write_text("\n".join(body), encoding="utf-8", newline="\n")

    # --- changelog/README.md index ---
    idx: list[str] = []
    idx.append("# Changelog pages")
    idx.append("")
    idx.append(
        "Paginated views of repository activity. "
        "**Start at the hub:** [`../CHANGELOG.md`](../CHANGELOG.md) (includes agent instructions)."
    )
    idx.append("")
    idx.append("## Pages")
    idx.append("")
    idx.append("| Page | Commits (global #) | File |")
    idx.append("|-----:|--------------------|------|")
    for p in range(1, total_pages + 1):
        start_index = (p - 1) * page_size + 1
        end_index = min(p * page_size, total)
        if p == 1:
            link = f"[CHANGELOG.md](../CHANGELOG.md#activity-log-page-1-latest)"
            label = "1 (latest)"
        else:
            link = f"[page-{p:02d}.md](page-{p:02d}.md)"
            label = str(p)
        idx.append(f"| {label} | {start_index}-{end_index} | {link} |")
    idx.append("")
    idx.append("## Regenerate (for agents)")
    idx.append("")
    idx.append("```bash")
    idx.append("python scripts/generate_changelog.py")
    idx.append(f"python scripts/generate_changelog.py --page-size {page_size}")
    idx.append("git add CHANGELOG.md changelog/")
    idx.append('git commit -m "docs: refresh changelog [skip ci]"')
    idx.append("```")
    idx.append("")
    idx.append(
        "Do not hand-merge pages. Always re-run the generator after new commits."
    )
    idx.append("")
    idx.append(f"*Generated `{gen_at}` | {total} commits | {total_pages} pages*")
    idx.append("")
    (out_dir / "README.md").write_text("\n".join(idx), encoding="utf-8", newline="\n")

    print(
        f"Wrote CHANGELOG.md + changelog/ ({total_pages} pages, "
        f"{page_size}/page, {total} commits)"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--page-size", type=int, default=DEFAULT_PAGE_SIZE)
    parser.add_argument("--repo-url", default=DEFAULT_REPO)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    if args.page_size < 10:
        print("page-size must be >= 10", file=sys.stderr)
        return 2
    build(page_size=args.page_size, repo_url=args.repo_url.rstrip("/"), dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
