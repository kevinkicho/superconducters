"""Generate a compact Markdown changelog from Git history."""

from __future__ import annotations

import subprocess
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Commit:
    sha: str
    short_sha: str
    authored_at: str
    author: str
    subject: str


def read_commits(
    *,
    limit: int = 100,
    runner: Callable[[Sequence[str]], str] | None = None,
) -> list[Commit]:
    if limit <= 0:
        return []
    command = [
        "git",
        "log",
        f"-n{limit}",
        "--date=iso-strict",
        "--pretty=format:%H%x1f%h%x1f%aI%x1f%an%x1f%s%x1e",
    ]
    execute = runner or _run
    return parse_git_log(execute(command))


def parse_git_log(raw: str) -> list[Commit]:
    commits = []
    for record in raw.split("\x1e"):
        fields = record.strip().split("\x1f")
        if len(fields) != 5:
            continue
        commits.append(Commit(*fields))
    return commits


def render_changelog(commits: Sequence[Commit]) -> str:
    lines = ["# Changelog", ""]
    if not commits:
        return "\n".join([*lines, "No commits found.", ""])
    current_date = None
    for commit in commits:
        date = commit.authored_at[:10]
        if date != current_date:
            lines.extend([f"## {date}", ""])
            current_date = date
        lines.append(f"- `{commit.short_sha}` {commit.subject} - {commit.author}")
    return "\n".join([*lines, ""])


def write_changelog(
    output_path: str | Path,
    *,
    limit: int = 100,
    runner: Callable[[Sequence[str]], str] | None = None,
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_changelog(read_commits(limit=limit, runner=runner)), encoding="utf-8")
    return path


def _run(command: Sequence[str]) -> str:
    completed = subprocess.run(
        list(command),
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return completed.stdout
