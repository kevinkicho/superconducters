#!/usr/bin/env python3
"""
Generate paginated, GitHub-viewport-friendly CHANGELOG pages from git history.

Layout
------
  CHANGELOG.md              Hub: TOC, agent guide, summary, page 1 (compact table)
  changelog/README.md       Page index
  changelog/page-NN.md      Older pages (same compact schema)

UX principles (GitHub README viewport)
-------------------------------------
  * Tables stay narrow: short time, short who, single Delta column, hard-truncated summary.
  * No <details> inside table cells (they explode row height when expanded / wrap badly).
  * Full text lives under "Commit details" as one-line <details> blocks with anchors.
  * TOC links jump to sections and other pages.

Usage
-----
  python scripts/generate_changelog.py
  python scripts/generate_changelog.py --page-size 50

Agents: after commits, re-run this script and commit CHANGELOG.md + changelog/.
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
DEFAULT_PAGE_SIZE = 50  # fewer rows = less vertical scroll per page on GitHub
DEFAULT_REPO = "https://github.com/kevinkicho/superconducters"
SUMMARY_LEN = 42  # hard cap so table cells rarely wrap on desktop GitHub


def parse_iso(s: str) -> datetime:
    return datetime.fromisoformat(s)


def fmt_duration(seconds: float | None) -> str:
    if seconds is None or seconds < 0:
        return "--"
    if seconds < 60:
        return f"{int(seconds)}s"
    if seconds < 3600:
        m, s = int(seconds // 60), int(seconds % 60)
        return f"{m}m{s:02d}s" if s else f"{m}m"
    h, m = int(seconds // 3600), int((seconds % 3600) // 60)
    if seconds > 6 * 3600:
        return f">{h}h+"
    return f"{h}h{m:02d}m" if m else f"{h}h"


def compact_when(ad: str) -> str:
    """2026-07-10T00:50:35-07:00 -> 07-10 00:50"""
    try:
        dt = parse_iso(ad)
        return dt.strftime("%m-%d %H:%M")
    except ValueError:
        return ad[5:16].replace("T", " ")


def short_who(an: str) -> str:
    m = re.match(r"agent-(\d+)", an, re.I)
    if m:
        return f"a{m.group(1)}"
    if an.lower() in {"ollama-swarm", "swarm"}:
        return "swarm"
    if "evin" in an.lower() or an == "Kevinkicho":
        return "human"
    # keep short
    return an[:12]


def truncate(text: str, limit: int = SUMMARY_LEN) -> str:
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[: max(1, limit - 1)].rstrip() + "..."


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
                "h": h[:7],
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
        base = "logs only"
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
                "docs: " + ", ".join(sorted({Path(f).name for f in docs})[:4])
            )
        if pys:
            parts.append(
                "code: " + ", ".join(sorted({Path(f).name for f in pys})[:4])
            )
        if tests:
            parts.append(
                "tests: " + ", ".join(sorted({Path(f).name for f in tests})[:3])
            )
        if data:
            parts.append(
                "data: " + ", ".join(sorted({Path(f).name for f in data})[:3])
            )
        if not parts:
            parts.append(f"{len(files)} paths")
        joined = "; ".join(parts)
        if re.match(r"^(agent-\d+:\s*)?t\d+\s*$", e["subj"]):
            base = f"{task}: {joined}"
        else:
            base = f"{e['subj']}: {joined}"

    n = len(e["files"])
    nlog = sum(1 for f in e["files"] if f.startswith("logs/"))
    if n:
        base += f" [{n}f"
        if nlog:
            base += f"/{nlog}log"
        base += "]"
    return base


def page_href(p: int, *, hub: bool) -> str:
    if p <= 1:
        return "CHANGELOG.md#activity-log" if hub else "../CHANGELOG.md#activity-log"
    return f"changelog/page-{p:02d}.md" if hub else f"page-{p:02d}.md"


def nav_bar(page: int, total_pages: int, page_size: int, total: int, *, hub: bool) -> str:
    bits: list[str] = []
    if page > 1:
        bits.append(f"[Prev]({page_href(page - 1, hub=hub)})")
    else:
        bits.append("Prev")

    window: list[int] = []
    for p in range(1, total_pages + 1):
        if p == 1 or p == total_pages or abs(p - page) <= 2:
            window.append(p)
        elif window and window[-1] != -1:
            window.append(-1)

    for p in window:
        if p == -1:
            bits.append("...")
        elif p == page:
            bits.append(f"**{p}**")
        else:
            bits.append(f"[{p}]({page_href(p, hub=hub)})")

    if page < total_pages:
        bits.append(f"[Next]({page_href(page + 1, hub=hub)})")
    else:
        bits.append("Next")

    start = (page - 1) * page_size + 1
    end = min(page * page_size, total)
    return (
        " | ".join(bits)
        + f"\n\n**Page {page}/{total_pages}** | rows **{start}-{end}** of **{total}** | newest first"
    )


def esc_cell(s: str) -> str:
    return s.replace("|", "\\|").replace("\n", " ")


def table_block(
    slice_entries: list[dict],
    start_index: int,
    repo_url: str,
    *,
    detail_prefix: str,
) -> list[str]:
    """
    Compact markdown table + separate detail anchors.
    detail_prefix: relative path prefix for #c-SHA links from this file.
      hub page 1: "" or "#"
      subpages: ""
    """
    lines: list[str] = []
    lines.append(
        "| # | When | Who | Summary | +/- | Dur | more |"
    )
    lines.append("|--:|:----:|:--:|:--------|----:|:--:|:---:|")

    for i, e in enumerate(slice_entries):
        rank = start_index + i
        when = compact_when(e["ad"])
        who = short_who(e["an"])
        # Prefer short subject for summary column
        if re.match(r"^agent-\d+:\s*t\d+\s*$", e["subj"]):
            summary_src = describe(e)
        else:
            summary_src = e["subj"]
        summary = esc_cell(truncate(summary_src, SUMMARY_LEN))
        delta = f"+{e['ins']}/-{e['del']}"
        # tighten huge numbers
        if e["ins"] >= 10000 or e["del"] >= 10000:
            delta = f"+{e['ins']/1000:.0f}k/-{e['del']/1000:.0f}k"
        dur = fmt_duration(e.get("duration_s"))
        anchor = f"c-{e['h']}"
        more = f"[...]({detail_prefix}#{anchor})"
        lines.append(
            f"| {rank} | `{when}` | `{who}` | {summary} | `{delta}` | `{dur}` | {more} |"
        )

    lines.append("")
    lines.append("### Commit details")
    lines.append("")
    lines.append(
        "Expand an item for full task text, paths, author, and commit link. "
        "The table above stays short so you can scan many rows without scrolling past wrapped cells."
    )
    lines.append("")

    for i, e in enumerate(slice_entries):
        rank = start_index + i
        when_full = e["ad"].replace("T", " ")
        who_full = e["an"]
        what = describe(e)
        files = e["files"][:40]
        more_files = len(e["files"]) - len(files)
        file_list = ", ".join(f"`{html.escape(f)}`" for f in files)
        if more_files > 0:
            file_list += f", ... +{more_files} more"
        if not file_list:
            file_list = "_(none)_"
        dur = fmt_duration(e.get("duration_s"))
        title = html.escape(truncate(f"#{rank} | {e['subj']}", 72))
        body_subj = html.escape(e["subj"])
        body_what = html.escape(what)
        lines.append(
            f'<a id="c-{e["h"]}"></a>\n'
            f"<details>\n"
            f"<summary>{title}</summary>\n\n"
            f"- **When:** `{when_full}`\n"
            f"- **Who:** `{html.escape(who_full)}` (`{short_who(who_full)}`)\n"
            f"- **Task:** {body_subj}\n"
            f"- **What:** {body_what}\n"
            f"- **LOC:** +{e['ins']:,} / -{e['del']:,}\n"
            f"- **Duration (est.):** {dur}\n"
            f"- **SHA:** [`{e['h']}`]({repo_url}/commit/{e['full']})\n"
            f"- **Files:** {file_list}\n\n"
            f"</details>\n"
        )

    return lines


def agent_guide(page_size: int) -> str:
    return f"""## Agent instructions

This changelog is **machine-generated** and **paginated**. Do not hand-edit table rows.

### Layout

| Path | Role |
|------|------|
| [`CHANGELOG.md`](CHANGELOG.md) | Hub: TOC, this guide, summary, **page 1** (latest {page_size} commits) |
| [`changelog/README.md`](changelog/README.md) | Page index |
| [`changelog/page-NN.md`](changelog/) | Older pages (`page-02`, ...), same compact schema |
| [`scripts/generate_changelog.py`](scripts/generate_changelog.py) | Only supported way to refresh |

**Order:** newest -> oldest. Global `#` is stable (1 = tip of `main`).

### Why the table looks like this

GitHub's README viewport is **narrow and scrolls vertically**. Wide cells and in-table expanders force huge row heights. So:

1. **Compact table only** -- short time (`MM-DD HH:MM`), short who (`a2`/`human`), hard-truncated summary (~{SUMMARY_LEN} chars), combined `+/-` LOC, short duration.
2. **No `<details>` inside table cells.**
3. **Full text** under [Commit details](#commit-details) on each page; jump via the `...` column (`#c-<sha>`).
4. **Pagination** ({page_size} commits/page) so one page does not dominate the scroll.

### Table columns

| Col | Meaning |
|-----|---------|
| `#` | Newest-first rank |
| When | Author time, compact |
| Who | `a2`/`a3`/`a4`/`human`/`swarm` |
| Summary | Truncated task/paths |
| `+/-` | Insertions/deletions (`git numstat`) |
| Dur | Est. gap since same author's previous commit (`6h+` => idle) |
| `...` | Link to full detail block on this page |

### After you upgrade the app

```bash
# 1) commit your feature/fix first
git add -A && git commit -m "describe your change"

# 2) regenerate changelog (from repo root)
python scripts/generate_changelog.py
# optional: python scripts/generate_changelog.py --page-size {page_size}

# 3) commit generated docs only
git add CHANGELOG.md changelog/
git commit -m "docs: refresh changelog after <change> [skip ci]"
```

**Do not:** insert rows by hand, delete this generator, or dump full history into one unpaginated table.

### Generator flags

```text
--page-size N     Rows per page (default {page_size}, min 10)
--repo-url URL    Commit link base
--dry-run         Print plan only
```
"""


def build(page_size: int, repo_url: str, dry_run: bool = False) -> None:
    entries = git_entries()
    attach_duration(entries)
    total = len(entries)
    total_pages = max(1, (total + page_size - 1) // page_size)

    agent_n = sum(1 for e in entries if e["an"].startswith("agent-"))
    other_n = total - agent_n
    total_ins = sum(e["ins"] for e in entries)
    total_del = sum(e["del"] for e in entries)

    pages = [
        entries[p * page_size : (p + 1) * page_size] for p in range(total_pages)
    ]
    gen_at = datetime.now().astimezone().isoformat(timespec="seconds")

    if dry_run:
        print(f"commits={total} pages={total_pages} page_size={page_size}")
        return

    out_dir = ROOT / "changelog"
    if out_dir.exists():
        for old in out_dir.glob("page-*.md"):
            old.unlink()
    out_dir.mkdir(parents=True, exist_ok=True)

    # ----- Hub -----
    hub: list[str] = []
    hub.append("# Changelog")
    hub.append("")
    hub.append(
        "Paginated agent/human activity for **superconducters** "
        "(newest first). Optimized for the GitHub README viewport: "
        "**compact table** + **details below** + **TOC links**."
    )
    hub.append("")
    hub.append("## Table of contents")
    hub.append("")
    hub.append("- [Agent instructions](#agent-instructions)")
    hub.append("  - [Layout](#layout)")
    hub.append("  - [Why the table looks like this](#why-the-table-looks-like-this)")
    hub.append("  - [Table columns](#table-columns)")
    hub.append("  - [After you upgrade the app](#after-you-upgrade-the-app)")
    hub.append("  - [Generator flags](#generator-flags)")
    hub.append("- [Summary](#summary)")
    hub.append("- [Jump to page](#jump-to-page)")
    hub.append("- [Activity log (page 1)](#activity-log)")
    hub.append("- [Commit details (page 1)](#commit-details)")
    hub.append("- [All pages index](changelog/README.md)")
    for p in range(2, total_pages + 1):
        label = f"Page {p}"
        if p == total_pages:
            label += " (oldest)"
        hub.append(f"- [{label}](changelog/page-{p:02d}.md)")
    hub.append("")
    hub.append("---")
    hub.append("")
    hub.append(agent_guide(page_size))
    hub.append("")
    hub.append("---")
    hub.append("")
    hub.append("## Summary")
    hub.append("")
    hub.append("| Metric | Value |")
    hub.append("|--------|-------|")
    hub.append(f"| Commits | {total} |")
    hub.append(f"| Pages | {total_pages} x {page_size}/page |")
    hub.append(f"| Agents | {agent_n} |")
    hub.append(f"| Human/other | {other_n} |")
    hub.append(f"| +LOC / -LOC | +{total_ins:,} / -{total_del:,} |")
    hub.append(f"| Net | {total_ins - total_del:+,} |")
    hub.append(f"| Generated | `{gen_at}` |")
    hub.append("")
    hub.append("## Jump to page")
    hub.append("")
    jump = [f"[**1 (latest)**](#activity-log)"]
    for p in range(2, total_pages + 1):
        jump.append(f"[{p}](changelog/page-{p:02d}.md)")
    hub.append(" | ".join(jump))
    hub.append("")
    hub.append(f"Index: [`changelog/README.md`](changelog/README.md)")
    hub.append("")
    hub.append("---")
    hub.append("")
    hub.append("## Activity log")
    hub.append("")
    hub.append(nav_bar(1, total_pages, page_size, total, hub=True))
    hub.append("")
    hub.append(
        "Tip: keep the table collapsed in mind -- use the `...` column for full text "
        "instead of hoping cells wrap. Prefer Next page over endless scroll."
    )
    hub.append("")
    hub.extend(
        table_block(pages[0], start_index=1, repo_url=repo_url, detail_prefix="")
    )
    hub.append("")
    hub.append(nav_bar(1, total_pages, page_size, total, hub=True))
    hub.append("")
    hub.append("---")
    hub.append("")
    hub.append(
        f"*Regen: `python scripts/generate_changelog.py` | "
        f"{total} commits | {total_pages} pages | size {page_size}*"
    )
    hub.append("")

    (ROOT / "CHANGELOG.md").write_text("\n".join(hub), encoding="utf-8", newline="\n")

    # ----- Other pages -----
    for p in range(2, total_pages + 1):
        start_index = (p - 1) * page_size + 1
        end_index = min(p * page_size, total)
        body: list[str] = []
        body.append(f"# Changelog -- page {p}/{total_pages}")
        body.append("")
        body.append(
            f"Rows **{start_index}-{end_index}** (newest-first global order). "
            f"[Hub + TOC](../CHANGELOG.md#table-of-contents) | "
            f"[Agent instructions](../CHANGELOG.md#agent-instructions)"
        )
        body.append("")
        body.append("## On this page")
        body.append("")
        body.append("- [Activity table](#activity-log)")
        body.append("- [Commit details](#commit-details)")
        body.append(
            f"- [Prev page]({page_href(p - 1, hub=False)})" if p > 1 else "- Prev"
        )
        if p < total_pages:
            body.append(f"- [Next page]({page_href(p + 1, hub=False)})")
        body.append("")
        body.append(nav_bar(p, total_pages, page_size, total, hub=False))
        body.append("")
        body.append("## Activity log")
        body.append("")
        body.extend(
            table_block(
                pages[p - 1],
                start_index=start_index,
                repo_url=repo_url,
                detail_prefix="",
            )
        )
        body.append("")
        body.append(nav_bar(p, total_pages, page_size, total, hub=False))
        body.append("")
        body.append(f"*Generated `{gen_at}`*")
        body.append("")
        (out_dir / f"page-{p:02d}.md").write_text(
            "\n".join(body), encoding="utf-8", newline="\n"
        )

    # ----- Index -----
    idx: list[str] = []
    idx.append("# Changelog pages")
    idx.append("")
    idx.append(
        "**Start here:** [`../CHANGELOG.md`](../CHANGELOG.md#table-of-contents) "
        "(TOC, agent guide, latest page)."
    )
    idx.append("")
    idx.append("## Pages")
    idx.append("")
    idx.append("| Page | Rows | Link |")
    idx.append("|-----:|------|------|")
    for p in range(1, total_pages + 1):
        a, b = (p - 1) * page_size + 1, min(p * page_size, total)
        if p == 1:
            link = "[latest](../CHANGELOG.md#activity-log)"
            label = "1 (latest)"
        else:
            link = f"[page-{p:02d}.md](page-{p:02d}.md)"
            label = str(p)
        idx.append(f"| {label} | {a}-{b} | {link} |")
    idx.append("")
    idx.append("## Regenerate")
    idx.append("")
    idx.append("```bash")
    idx.append("python scripts/generate_changelog.py")
    idx.append("git add CHANGELOG.md changelog/")
    idx.append('git commit -m "docs: refresh changelog [skip ci]"')
    idx.append("```")
    idx.append("")
    idx.append(f"*{total} commits | {total_pages} pages | `{gen_at}`*")
    idx.append("")
    (out_dir / "README.md").write_text("\n".join(idx), encoding="utf-8", newline="\n")

    print(
        f"Wrote CHANGELOG.md + changelog/ "
        f"({total_pages} pages, {page_size}/page, {total} commits)"
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--page-size", type=int, default=DEFAULT_PAGE_SIZE)
    ap.add_argument("--repo-url", default=DEFAULT_REPO)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)
    if args.page_size < 10:
        print("page-size must be >= 10", file=sys.stderr)
        return 2
    build(
        page_size=args.page_size,
        repo_url=args.repo_url.rstrip("/"),
        dry_run=args.dry_run,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
