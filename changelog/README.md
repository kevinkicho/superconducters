# Changelog pages

Paginated views of repository activity. **Start at the hub:** [`../CHANGELOG.md`](../CHANGELOG.md) (includes agent instructions).

## Pages

| Page | Commits (global #) | File |
|-----:|--------------------|------|
| 1 (latest) | 1-80 | [CHANGELOG.md](../CHANGELOG.md#activity-log-page-1-latest) |
| 2 | 81-160 | [page-02.md](page-02.md) |
| 3 | 161-240 | [page-03.md](page-03.md) |
| 4 | 241-320 | [page-04.md](page-04.md) |
| 5 | 321-400 | [page-05.md](page-05.md) |
| 6 | 401-480 | [page-06.md](page-06.md) |
| 7 | 481-560 | [page-07.md](page-07.md) |
| 8 | 561-640 | [page-08.md](page-08.md) |
| 9 | 641-689 | [page-09.md](page-09.md) |

## Regenerate (for agents)

```bash
python scripts/generate_changelog.py
python scripts/generate_changelog.py --page-size 80
git add CHANGELOG.md changelog/
git commit -m "docs: refresh changelog [skip ci]"
```

Do not hand-merge pages. Always re-run the generator after new commits.

*Generated `2026-07-10T01:02:03-07:00` | 689 commits | 9 pages*
