# Changelog

Paginated activity log for **superconducters** (newest first). Built mainly by **Ollama Swarm** (DeepSeek V4 Flash agents) with human maintainer commits.

## Agent instructions (read before editing this changelog)

This changelog is **machine-generated** and **paginated** for GitHub viewing. Do not hand-edit hundreds of table rows.

### Layout

| Path | Role |
|------|------|
| [`CHANGELOG.md`](CHANGELOG.md) | Hub: this guide, summary stats, **page 1** (latest 80 commits) |
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
python scripts/generate_changelog.py --page-size 80
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
--page-size N     Rows per page (default 80)
--repo-url URL    Base URL for commit links
--dry-run         Print plan only, write nothing
```

### Duration caveat

Duration is **estimated** from commit timestamps, not token/inference time. Parallel agents and overnight gaps produce large durations; treat `>6h` as session boundaries, not continuous work.


---

## Summary

| Metric | Value |
|--------|-------|
| Commits listed | 689 |
| Pages (`80` per page) | 9 |
| Agent commits | 680 |
| Human / other | 9 |
| Total +LOC | +146,343 |
| Total -LOC | -99,343 |
| Net LOC | +47,000 |
| Order | Newest -> oldest |
| Generated | `2026-07-10T01:02:03-07:00` |

### Jump to page

[1 (latest)](CHANGELOG.md#activity-log-page-1-latest) | [2](changelog/page-02.md) | [3](changelog/page-03.md) | [4](changelog/page-04.md) | [5](changelog/page-05.md) | [6](changelog/page-06.md) | [7](changelog/page-07.md) | [8](changelog/page-08.md) | [9](changelog/page-09.md)

Full index: [`changelog/README.md`](changelog/README.md)

---

## Activity log (page 1, latest)

<- Previous | **1** [2](changelog/page-02.md) [3](changelog/page-03.md) ... [9](changelog/page-09.md) | [Next ->](changelog/page-02.md)

Page **1** of **9** | commits **1-80** of **689** (newest first)

> Click a truncated **Task** / **What** cell (summary ends with `...`) to expand.

| # | When | Who | Task | What | +LOC | -LOC | Duration | SHA |
|--:|------|-----|------|------|-----:|-----:|----------|-----|
| 1 | `2026-07-10 00:50:35-07:00` | `Kevinkicho` | <details><summary>Fix GitHub homepage showing .github/README over...</summary><code>Fix GitHub homepage showing .github/README over root README</code></details> | <details><summary>Fix GitHub homepage showing .github/README over root README --...</summary><code>Fix GitHub homepage showing .github/README over root README -- docs/md: README.md (1 files)</code></details> | +0 | -8 | 1m 23s | [`7edaa780`](https://github.com/kevinkicho/superconducters/commit/7edaa780468ec0f0e594aab759479c16e75dde29) |
| 2 | `2026-07-10 00:49:12-07:00` | `Kevinkicho` | <details><summary>Restore fuller README with accurate document ca...</summary><code>Restore fuller README with accurate document catalog</code></details> | <details><summary>Restore fuller README with accurate document catalog -- docs/md...</summary><code>Restore fuller README with accurate document catalog -- docs/md: README.md (1 files)</code></details> | +610 | -147 | >6h (8h 11m) | [`8b5a37de`](https://github.com/kevinkicho/superconducters/commit/8b5a37dedb83841ab6b7e4431c6880e382b90f12) |
| 3 | `2026-07-09 16:37:22-07:00` | `Kevinkicho` | <details><summary>Clean up docs, logs, and README; dedupe materia...</summary><code>Clean up docs, logs, and README; dedupe materials DB</code></details> | <details><summary>Clean up docs, logs, and README; dedupe materials DB -- docs/md...</summary><code>Clean up docs, logs, and README; dedupe materials DB -- docs/md: README.md, candidate_materials.md, characterization_techniques.md, discovery_strategy.md, experimental_feedback_loop.md; tests: tests_predict_tc.py; data: superconductor_database.json (135 files, 109 logs)</code></details> | +3,780 | -34,133 | >6h (27h 15m) | [`d1457a7a`](https://github.com/kevinkicho/superconducters/commit/d1457a7aee087a388a5918aca4dedcb32e1479c7) |
| 4 | `2026-07-09 15:39:39-07:00` | `agent-2` | agent-2: t11 | Task t11: tests: test_run_pipeline.py (2 files, 1 logs) | +539 | -2 | 4m 7s | [`38e702c5`](https://github.com/kevinkicho/superconducters/commit/38e702c5c9aefc594d9594f0cfc1ade546db6ba5) |
| 5 | `2026-07-09 15:36:33-07:00` | `agent-3` | agent-3: t10 | Task t10: docs/md: theoretical_framework.md (1 files) | +41 | -0 | 10m 59s | [`81824f11`](https://github.com/kevinkicho/superconducters/commit/81824f11d78e7146cbef0b15a0eb4fcb05336e5b) |
| 6 | `2026-07-09 15:35:32-07:00` | `agent-2` | agent-2: t9 | Task t9: docs/md: experimental_feedback_loop.md (1 files) | +91 | -0 | 2h 44m | [`285f0c69`](https://github.com/kevinkicho/superconducters/commit/285f0c69c2cc7768966714df601976c2ef6f4d66) |
| 7 | `2026-07-09 15:25:34-07:00` | `agent-3` | agent-3: t5 | Task t5: code: predict_tc.py (2 files, 1 logs) | +232 | -6 | 4m 53s | [`676c3f38`](https://github.com/kevinkicho/superconducters/commit/676c3f38de0c55b278ceb5b9204ff4b1b6f31243) |
| 8 | `2026-07-09 15:20:41-07:00` | `agent-3` | agent-3: t3 | Task t3: docs/md: proposed_chemistry_physics.md (1 files) | +8 | -8 | 3m 15s | [`8d8b2c06`](https://github.com/kevinkicho/superconducters/commit/8d8b2c064df6c9e45a3699e3a254532605a66302) |
| 9 | `2026-07-09 15:17:26-07:00` | `agent-3` | agent-3: t2 | <details><summary>Task t2: docs/md: proposed_chemistry_physics.md (7 files, 5 log...</summary><code>Task t2: docs/md: proposed_chemistry_physics.md (7 files, 5 logs)</code></details> | +2,690 | -2,361 | 2h 26m | [`e4b39c4d`](https://github.com/kevinkicho/superconducters/commit/e4b39c4df4c10bc1b9edf14584a1f03027ecd0f4) |
| 10 | `2026-07-09 12:51:20-07:00` | `agent-2` | agent-2: t11 | Task t11: docs/md: theoretical_framework.md (1 files) | +50 | -0 | 12m 24s | [`634124e7`](https://github.com/kevinkicho/superconducters/commit/634124e743ec55b04701224832988c470054a8ad) |
| 11 | `2026-07-09 12:51:19-07:00` | `agent-3` | agent-3: t12 | Task t12: docs/md: manufacturing_scalability.md (1 files) | +82 | -0 | 1m 19s | [`f1e939d3`](https://github.com/kevinkicho/superconducters/commit/f1e939d31478bd02a8ca3e0abf904ec2777f6047) |
| 12 | `2026-07-09 12:50:00-07:00` | `agent-3` | agent-3: t10 | Task t10: docs/md: synthesis_methods.md (1 files) | +83 | -0 | 1m 10s | [`061a8c9f`](https://github.com/kevinkicho/superconducters/commit/061a8c9fbb2a0237ebb0943915e7d022f33ef04f) |
| 13 | `2026-07-09 12:48:50-07:00` | `agent-3` | agent-3: t9 | Task t9: docs/md: discovery_strategy.md (1 files) | +117 | -0 | 1m 38s | [`dd5a7d31`](https://github.com/kevinkicho/superconducters/commit/dd5a7d31064a3399053d69c03a63eb6de6176f69) |
| 14 | `2026-07-09 12:47:12-07:00` | `agent-3` | agent-3: t8 | Task t8: docs/md: online_research_summary.md (1 files) | +19 | -0 | 3m 7s | [`85d74084`](https://github.com/kevinkicho/superconducters/commit/85d740848ca954b81fe70700f662706f22146849) |
| 15 | `2026-07-09 12:44:05-07:00` | `agent-3` | agent-3: t7 | <details><summary>Task t7: docs/md: proposed_chemistry_physics.md (2 files, 1 log...</summary><code>Task t7: docs/md: proposed_chemistry_physics.md (2 files, 1 logs)</code></details> | +63 | -186 | 6m 31s | [`e0e653ce`](https://github.com/kevinkicho/superconducters/commit/e0e653cebe7900f412572873d5c7384e908534a4) |
| 16 | `2026-07-09 12:38:56-07:00` | `agent-2` | agent-2: t4 | Task t4: code: streamlit_dashboard.py (1 files) | +4 | -7 | 1m 23s | [`56f2372f`](https://github.com/kevinkicho/superconducters/commit/56f2372f7399e8cea65e3cef164573a13f525f5a) |
| 17 | `2026-07-09 12:37:34-07:00` | `agent-3` | agent-3: t3 | Task t3: code: run_pipeline.py (1 files) | +3 | -3 | 56s | [`fb5e4fde`](https://github.com/kevinkicho/superconducters/commit/fb5e4fde8110d470c2ea3d052065fff77304b781) |
| 18 | `2026-07-09 12:37:33-07:00` | `agent-2` | agent-2: t1 | Task t1: code: dft_calculator.py (1 files) | +19 | -26 | 2h 8m | [`84fde38b`](https://github.com/kevinkicho/superconducters/commit/84fde38b7c0825b0de0f04e25be4f242f9e23471) |
| 19 | `2026-07-09 12:36:38-07:00` | `agent-3` | agent-3: t2 | Task t2: code: generate_candidates.py (6 files, 4 logs) | +2,821 | -1,491 | >6h (11h 1m) | [`2a96a04d`](https://github.com/kevinkicho/superconducters/commit/2a96a04dbff6371230af0c076743d907763c1253) |
| 20 | `2026-07-09 10:29:25-07:00` | `agent-2` | agent-2: t5 | Task t5: docs/md: online_research_summary.md (1 files) | +101 | -13 | 10m 53s | [`525e8149`](https://github.com/kevinkicho/superconducters/commit/525e8149a42891e4e78a9bc66c7c116095604562) |
| 21 | `2026-07-09 10:20:54-07:00` | `agent-4` | agent-4: t4 | Task t4: docs/md: candidate_materials.md (1 files) | +166 | -0 | 4m 42s | [`f69c30a8`](https://github.com/kevinkicho/superconducters/commit/f69c30a8f04cbb2b94809e8106a6b981a6215178) |
| 22 | `2026-07-09 10:18:32-07:00` | `agent-2` | agent-2: t1 | Task t1: code: predict_tc.py (1 files) | +4 | -5 | >6h (8h 41m) | [`f3abb7ee`](https://github.com/kevinkicho/superconducters/commit/f3abb7ee39ccbfe1aeee3d9a94c346694826c6f9) |
| 23 | `2026-07-09 10:16:12-07:00` | `agent-4` | agent-4: t3 | Task t3: code: streamlit_dashboard.py (6 files, 5 logs) | +1,917 | -1,732 | >6h (8h 38m) | [`cdc06de3`](https://github.com/kevinkicho/superconducters/commit/cdc06de37bafde74fe551265c008dfd476c9cdb3) |
| 24 | `2026-07-09 01:37:57-07:00` | `agent-4` | agent-4: t7 | Task t7: code: generate_candidates.py (1 files) | +79 | -77 | 1m 19s | [`1d8d5d2a`](https://github.com/kevinkicho/superconducters/commit/1d8d5d2a9af5614279073ade305139d4583b97ca) |
| 25 | `2026-07-09 01:36:45-07:00` | `agent-2` | agent-2: t1 | Task t1: code: predict_tc.py (1 files) | +3 | -209 | 35m 58s | [`daf7ae3f`](https://github.com/kevinkicho/superconducters/commit/daf7ae3f402d93c30dbb3ebb160dc9ee81c9cf72) |
| 26 | `2026-07-09 01:36:38-07:00` | `agent-4` | agent-4: t6 | Task t6: code: run_pipeline.py (1 files) | +22 | -10 | 1m 32s | [`1373ccbe`](https://github.com/kevinkicho/superconducters/commit/1373ccbe6399460c9229066a37e88a1ec294106c) |
| 27 | `2026-07-09 01:35:06-07:00` | `agent-4` | agent-4: t4 | Task t4: 1 path(s) (1 files) | +43 | -6 | 2m 12s | [`dfeaddda`](https://github.com/kevinkicho/superconducters/commit/dfeaddda6e296c551826febc94cccdec138f9865) |
| 28 | `2026-07-09 01:34:51-07:00` | `agent-3` | agent-3: t2 | Task t2: code: streamlit_dashboard.py (1 files) | +9 | -27 | >6h (7h 46m) | [`168a8294`](https://github.com/kevinkicho/superconducters/commit/168a8294c928f21f1b1378a55cdee0405c24b6cb) |
| 29 | `2026-07-09 01:32:54-07:00` | `agent-4` | agent-4: t3 | Task t3: code: dft_calculator.py (4 files, 3 logs) | +360 | -10 | 27m 57s | [`d3d469af`](https://github.com/kevinkicho/superconducters/commit/d3d469af1a9b11be46bf960042537c5f3614a6dc) |
| 30 | `2026-07-09 01:04:57-07:00` | `agent-4` | agent-4: t5 | <details><summary>Task t5: docs/md: proposed_chemistry_physics.md (2 files, 1 log...</summary><code>Task t5: docs/md: proposed_chemistry_physics.md (2 files, 1 logs)</code></details> | +2,998 | -241 | 9m 21s | [`5657faff`](https://github.com/kevinkicho/superconducters/commit/5657fafff274b6bcfe28f871b1db6a6cc7b40587) |
| 31 | `2026-07-09 01:00:47-07:00` | `agent-2` | agent-2: t1 | Task t1: data: superconductor_database.json (1 files) | +8 | -222 | >6h (6h 2m) | [`b1e02261`](https://github.com/kevinkicho/superconducters/commit/b1e02261ccfb4a5bc77f9965989ba07d513fe8d0) |
| 32 | `2026-07-09 00:55:36-07:00` | `agent-4` | agent-4: t4 | Task t4: tests: test_api_client.py (1 files) | +5 | -6 | 3m 19s | [`dc616535`](https://github.com/kevinkicho/superconducters/commit/dc616535e6a537564dc9a09f06fa4d8c595332a4) |
| 33 | `2026-07-09 00:52:17-07:00` | `agent-4` | agent-4: t3 | Task t3: code: run_pipeline.py (19 files, 17 logs) | +1,758 | -1,528 | >6h (8h 42m) | [`50c99261`](https://github.com/kevinkicho/superconducters/commit/50c99261b59f7783ec4d0a10cdeee3cb2b7aaa5e) |
| 34 | `2026-07-08 18:58:23-07:00` | `agent-2` | agent-2: t5 | Task t5: tests: test_api_client.py (1 files) | +8 | -8 | 42s | [`1bab57ae`](https://github.com/kevinkicho/superconducters/commit/1bab57ae40df6e6cf0d5c3cb8a6c4cf2f861586d) |
| 35 | `2026-07-08 18:57:41-07:00` | `agent-2` | agent-2: t1 | Task t1: code: predict_tc.py (7 files, 5 logs) | +1,789 | -533 | 2h 47m | [`a25d0957`](https://github.com/kevinkicho/superconducters/commit/a25d095788328cb3561c72035b0a7be0fa4c9f29) |
| 36 | `2026-07-08 17:48:15-07:00` | `agent-3` | agent-3: t4 | Task t4: code: streamlit_dashboard.py (1 files) | +43 | -1 | 23s | [`36ab4c30`](https://github.com/kevinkicho/superconducters/commit/36ab4c30b99dee70d9211282d74af8f36bb544f7) |
| 37 | `2026-07-08 17:47:52-07:00` | `agent-3` | agent-3: t2 | Task t2: code: dft_calculator.py (7 files, 5 logs) | +953 | -263 | 1h 37m | [`f8d9383f`](https://github.com/kevinkicho/superconducters/commit/f8d9383f215220ae0aa98fb9ed82f3eb043bf42a) |
| 38 | `2026-07-08 16:10:41-07:00` | `agent-3` | agent-3: t8 | Task t8: docs/md: proposed_chemistry_physics.md (1 files) | +22 | -0 | 1m 8s | [`9fb6c7e7`](https://github.com/kevinkicho/superconducters/commit/9fb6c7e795b6239c7d06be141afc21d673d3b037) |
| 39 | `2026-07-08 16:10:21-07:00` | `agent-2` | agent-2: t7 | Task t7: docs/md: discovery_strategy.md (1 files) | +1 | -33 | 31s | [`599ff418`](https://github.com/kevinkicho/superconducters/commit/599ff41826f465bf813f790ca461e60bcb8c3e37) |
| 40 | `2026-07-08 16:09:50-07:00` | `agent-2` | agent-2: t1 | Task t1: code: dft_calculator.py (1 files) | +130 | -3 | 18m 8s | [`c358f6aa`](https://github.com/kevinkicho/superconducters/commit/c358f6aafb78f2649415482f5d138fee6be4f882) |
| 41 | `2026-07-08 16:09:33-07:00` | `agent-3` | agent-3: t4 | Task t4: code: run_pipeline.py (1 files) | +38 | -2 | 18m 31s | [`7b6276ef`](https://github.com/kevinkicho/superconducters/commit/7b6276ef3b2526c1c5bada470a3d909d7c262b6f) |
| 42 | `2026-07-08 16:09:28-07:00` | `agent-4` | agent-4: t3 | Task t3: code: predict_tc.py (6 files, 4 logs) | +429 | -0 | 22m 52s | [`175ea67a`](https://github.com/kevinkicho/superconducters/commit/175ea67abbb20e63508dd80484db8f7db6dee26c) |
| 43 | `2026-07-08 15:51:42-07:00` | `agent-2` | agent-2: t4 | <details><summary>Task t4: code: app.py; tests: test_api_client.py (4 files, 2 lo...</summary><code>Task t4: code: app.py; tests: test_api_client.py (4 files, 2 logs)</code></details> | +404 | -420 | 5m 11s | [`92abaad1`](https://github.com/kevinkicho/superconducters/commit/92abaad10369dbc3a1ec7ce9532ef45ed5a76982) |
| 44 | `2026-07-08 15:51:02-07:00` | `agent-3` | agent-3: t2 | <details><summary>Task t2: code: arxiv_scraper.py, run_pipeline.py (6 files, 4 lo...</summary><code>Task t2: code: arxiv_scraper.py, run_pipeline.py (6 files, 4 logs)</code></details> | +911 | -66 | 4m 7s | [`ecd37fae`](https://github.com/kevinkicho/superconducters/commit/ecd37fae63df7137f2aa707bc7e8db8cfcb5d357) |
| 45 | `2026-07-08 15:46:55-07:00` | `agent-3` | agent-3: t6 | Task t6: docs/md: README.md (1 files) | +1 | -3 | 28s | [`0f4bd688`](https://github.com/kevinkicho/superconducters/commit/0f4bd688263e911e87549421ca6456b1790ed8d3) |
| 46 | `2026-07-08 15:46:36-07:00` | `agent-4` | agent-4: t5 | Task t5: docs/md: proposed_chemistry_physics.md (1 files) | +4 | -3 | 32s | [`821f8452`](https://github.com/kevinkicho/superconducters/commit/821f84522a3863bb6088f614de576f10a8405e34) |
| 47 | `2026-07-08 15:46:31-07:00` | `agent-2` | agent-2: t1 | Task t1: code: api_client.py (1 files) | +107 | -0 | 38m 51s | [`5e2b936b`](https://github.com/kevinkicho/superconducters/commit/5e2b936bea986eea483932d5472d92e0ea600bfb) |
| 48 | `2026-07-08 15:46:27-07:00` | `agent-3` | agent-3: t2 | Task t2: code: run_pipeline.py (1 files) | +54 | -1 | >6h (7h 35m) | [`acdcdce7`](https://github.com/kevinkicho/superconducters/commit/acdcdce7c9043d9f62f8c5cb53a093830bec45ea) |
| 49 | `2026-07-08 15:46:04-07:00` | `agent-4` | agent-4: t4 | Task t4: docs/md: discovery_strategy.md (6 files, 4 logs) | +510 | -203 | >6h (7h 20m) | [`0a5554e1`](https://github.com/kevinkicho/superconducters/commit/0a5554e16a8e7b8f8bdc29dc4750c9301dbe7163) |
| 50 | `2026-07-08 15:07:40-07:00` | `agent-2` | agent-2: t4 | <details><summary>Task t4: docs/md: proposed_chemistry_physics.md (7 files, 5 log...</summary><code>Task t4: docs/md: proposed_chemistry_physics.md (7 files, 5 logs)</code></details> | +1,144 | -10,526 | >6h (6h 54m) | [`ade641db`](https://github.com/kevinkicho/superconducters/commit/ade641db6b7a3a4168810ea2742946cf76b4edd3) |
| 51 | `2026-07-08 13:21:33-07:00` | `Kevinkicho` | <details><summary>Remove GitHub Actions workflows to disable all...</summary><code>Remove GitHub Actions workflows to disable all CI</code></details> | <details><summary>Remove GitHub Actions workflows to disable all CI -- 2 path(s)...</summary><code>Remove GitHub Actions workflows to disable all CI -- 2 path(s) (2 files)</code></details> | +0 | -280 | 2h 13m | [`e98d4fce`](https://github.com/kevinkicho/superconducters/commit/e98d4fce6517f9e07a9d227a1a67641a577b8970) |
| 52 | `2026-07-08 11:07:43-07:00` | `Kevinkicho` | <details><summary>Add LaH10 protocol doc to README, remove remain...</summary><code>Add LaH10 protocol doc to README, remove remaining broken links</code></details> | <details><summary>Add LaH10 protocol doc to README, remove remaining broken links...</summary><code>Add LaH10 protocol doc to README, remove remaining broken links -- docs/md: README.md (1 files)</code></details> | +8 | -11 | >6h (12h 57m) | [`52abe6f5`](https://github.com/kevinkicho/superconducters/commit/52abe6f527f9fce51bfefd77f92f2042e5e5f10b) |
| 53 | `2026-07-08 08:25:43-07:00` | `agent-4` | agent-4: t340 | Task t340: docs/md: technology_transfer_plan.md (1 files) | +24 | -0 | 22s | [`08992332`](https://github.com/kevinkicho/superconducters/commit/08992332b505e4889a9fd1157ea4805c7efd0521) |
| 54 | `2026-07-08 08:25:21-07:00` | `agent-4` | agent-4: t339 | Task t339: docs/md: manufacturing_scalability.md (1 files) | +38 | -0 | 15s | [`f8c6c0a9`](https://github.com/kevinkicho/superconducters/commit/f8c6c0a9ed823bdac58478075f2ff7073b3a5902) |
| 55 | `2026-07-08 08:25:06-07:00` | `agent-4` | agent-4: t338 | Task t338: docs/md: challenges_and_mitigations.md (1 files) | +38 | -0 | 17s | [`6e3f12b0`](https://github.com/kevinkicho/superconducters/commit/6e3f12b01ef868ebc64b06c40ad2758df52242b9) |
| 56 | `2026-07-08 08:24:49-07:00` | `agent-4` | agent-4: t337 | Task t337: docs/md: candidate_materials.md (1 files) | +21 | -0 | 20s | [`7191a59e`](https://github.com/kevinkicho/superconducters/commit/7191a59e76e96e5bff8274175d073c09cc52c302) |
| 57 | `2026-07-08 08:24:29-07:00` | `agent-4` | agent-4: t336 | Task t336: docs/md: theoretical_framework.md (2 files, 1 logs) | +256 | -224 | 11m 35s | [`ce94318c`](https://github.com/kevinkicho/superconducters/commit/ce94318c51c94aa1d3bbd9f7a82c4fa62dacde3b) |
| 58 | `2026-07-08 08:13:06-07:00` | `agent-2` | agent-2: t332 | <details><summary>Task t332: docs/md: final_report.md, public_outreach_summary.md...</summary><code>Task t332: docs/md: final_report.md, public_outreach_summary.md (2 files)</code></details> | +47 | -3 | 31s | [`8d135619`](https://github.com/kevinkicho/superconducters/commit/8d135619380c1d294b8848b23bf6cf79f32d9771) |
| 59 | `2026-07-08 08:12:54-07:00` | `agent-4` | agent-4: t331 | Task t331: docs/md: manufacturing_scalability.md (1 files) | +101 | -0 | 30s | [`bdf629fb`](https://github.com/kevinkicho/superconducters/commit/bdf629fb0ac7ac801ea3806546b082e31040c269) |
| 60 | `2026-07-08 08:12:35-07:00` | `agent-2` | agent-2: t330 | <details><summary>Task t330: docs/md: experimental_protocol_new_compound.md (1 fi...</summary><code>Task t330: docs/md: experimental_protocol_new_compound.md (1 files)</code></details> | +117 | -0 | 16s | [`e05c94ff`](https://github.com/kevinkicho/superconducters/commit/e05c94ff2f152b21601b36357d0d4c65fc13565e) |
| 61 | `2026-07-08 08:12:24-07:00` | `agent-4` | agent-4: t329 | <details><summary>Task t329: docs/md: candidate_materials.md; data: experimental_...</summary><code>Task t329: docs/md: candidate_materials.md; data: experimental_results.json (2 files)</code></details> | +39 | -3 | 1m 52s | [`6323e0f7`](https://github.com/kevinkicho/superconducters/commit/6323e0f755d4f5d0a2cffe3cea00d58bda26eaa5) |
| 62 | `2026-07-08 08:12:19-07:00` | `agent-2` | agent-2: t327 | Task t327: code: run_pipeline.py (2 files, 1 logs) | +370 | -277 | 2m 9s | [`becf6fa3`](https://github.com/kevinkicho/superconducters/commit/becf6fa364fe3fc4d17efac5c4407f48fe0e0f9c) |
| 63 | `2026-07-08 08:10:39-07:00` | `agent-3` | agent-3: t318 | Task t318: tests: test_run_pipeline.py (1 files) | +52 | -0 | 8m 21s | [`2eda0d1b`](https://github.com/kevinkicho/superconducters/commit/2eda0d1b1a15dcc691f7c7e42f70cbca606c2568) |
| 64 | `2026-07-08 08:10:32-07:00` | `agent-4` | agent-4: t322 | Task t322: tests: test_generate_candidates.py (1 files) | +28 | -0 | 12s | [`a1d19012`](https://github.com/kevinkicho/superconducters/commit/a1d190128b329e9c068b7765d9b48a0ed8914eef) |
| 65 | `2026-07-08 08:10:20-07:00` | `agent-4` | agent-4: t317 | Task t317: code: run_pipeline.py (1 files) | +74 | -0 | 1m 53s | [`f9326f91`](https://github.com/kevinkicho/superconducters/commit/f9326f91b931dbc8f7a24f419211acf6e88c7561) |
| 66 | `2026-07-08 08:10:10-07:00` | `agent-2` | agent-2: t315 | Task t315: code: generate_report.py (2 files, 1 logs) | +231 | -227 | 1m 27s | [`97f20917`](https://github.com/kevinkicho/superconducters/commit/97f2091796a27eb853d7e3e7876d019ce26e24cf) |
| 67 | `2026-07-08 08:08:43-07:00` | `agent-2` | agent-2: t310 | Task t310: tests: test_run_pipeline.py (1 files) | +311 | -0 | 6m 45s | [`0c777642`](https://github.com/kevinkicho/superconducters/commit/0c777642bbb42f1f84254519368d4926b1049d88) |
| 68 | `2026-07-08 08:08:27-07:00` | `agent-4` | agent-4: t312 | <details><summary>Task t312: docs/md: experimental_feedback_loop.md (2 files, 1 l...</summary><code>Task t312: docs/md: experimental_feedback_loop.md (2 files, 1 logs)</code></details> | +326 | -273 | 6m 37s | [`dae65601`](https://github.com/kevinkicho/superconducters/commit/dae65601687ef44d66e90cd0b59b3fe09a42f8f1) |
| 69 | `2026-07-08 08:02:18-07:00` | `agent-3` | agent-3: t309 | Task t309: docs/md: manufacturing_scalability.md (1 files) | +24 | -0 | 16s | [`f06d3be8`](https://github.com/kevinkicho/superconducters/commit/f06d3be8350aa131776fb9c81adabfcec4c97dbb) |
| 70 | `2026-07-08 08:02:02-07:00` | `agent-3` | agent-3: t300 | Task t300: code: generate_report.py (1 files) | +36 | -2 | 1m 47s | [`39f85a85`](https://github.com/kevinkicho/superconducters/commit/39f85a85c16ea305f214563dfdb02346fd0d2abe) |
| 71 | `2026-07-08 08:01:58-07:00` | `agent-2` | agent-2: t304 | Task t304: tests: test_api_client.py (1 files) | +25 | -0 | 12s | [`0f0e19d0`](https://github.com/kevinkicho/superconducters/commit/0f0e19d0db12b5d3c3d41bc5c1da26ded1176c0e) |
| 72 | `2026-07-08 08:01:50-07:00` | `agent-4` | agent-4: t302 | Task t302: tests: test_run_pipeline.py (1 files) | +100 | -0 | 5m | [`ceb24076`](https://github.com/kevinkicho/superconducters/commit/ceb240764b428e22a0fdfb3cbdcfbdeb0a12a495) |
| 73 | `2026-07-08 08:01:46-07:00` | `agent-2` | agent-2: t303 | Task t303: tests: test_generate_report.py (1 files) | +25 | -0 | 13s | [`aa4715d3`](https://github.com/kevinkicho/superconducters/commit/aa4715d378a5db49b80618b3b074c9ba7c5108e4) |
| 74 | `2026-07-08 08:01:33-07:00` | `agent-2` | agent-2: t299 | Task t299: code: run_pipeline.py (2 files, 1 logs) | +343 | -238 | 2m 37s | [`ee8e48b8`](https://github.com/kevinkicho/superconducters/commit/ee8e48b851b953166c24ca6bde41a334352d1104) |
| 75 | `2026-07-08 08:00:15-07:00` | `agent-3` | agent-3: t293 | Task t293: code: run_pipeline.py (1 files) | +38 | -52 | 3m 7s | [`f012219d`](https://github.com/kevinkicho/superconducters/commit/f012219d7506f398068588739668d8d64a3b30aa) |
| 76 | `2026-07-08 07:58:56-07:00` | `agent-2` | agent-2: t296 | Task t296: docs/md: discovery_strategy.md (2 files, 1 logs) | +239 | -205 | 3m 11s | [`c896f081`](https://github.com/kevinkicho/superconducters/commit/c896f08174b110a8eb194e7d1b2c11542b0c351f) |
| 77 | `2026-07-08 07:57:08-07:00` | `agent-3` | agent-3: t289 | Task t289: code: run_pipeline.py (1 files) | +104 | -0 | 19m 34s | [`1f1cf9fc`](https://github.com/kevinkicho/superconducters/commit/1f1cf9fc645148a8aad40cb616c33d0a7f979e4c) |
| 78 | `2026-07-08 07:56:50-07:00` | `agent-4` | agent-4: t290 | <details><summary>Task t290: docs/md: challenges_and_mitigations.md (2 files, 1 l...</summary><code>Task t290: docs/md: challenges_and_mitigations.md (2 files, 1 logs)</code></details> | +14 | -13 | 25m 39s | [`c02c0c20`](https://github.com/kevinkicho/superconducters/commit/c02c0c2034121defdaef7536e5d4fc8e98736844) |
| 79 | `2026-07-08 07:55:45-07:00` | `agent-2` | agent-2: t287 | Task t287: code: streamlit_dashboard.py (2 files, 1 logs) | +277 | -270 | 7m 39s | [`9eefde0f`](https://github.com/kevinkicho/superconducters/commit/9eefde0ff60e75d647d5b939353424be0337550e) |
| 80 | `2026-07-08 07:48:06-07:00` | `agent-2` | agent-2: t277 | Task t277: code: run_pipeline.py (2 files, 1 logs) | +273 | -233 | 17m 45s | [`0dc1efa5`](https://github.com/kevinkicho/superconducters/commit/0dc1efa5a1fde504a8eafda98ae4cfa4a8f06cb0) |

<- Previous | **1** [2](changelog/page-02.md) [3](changelog/page-03.md) ... [9](changelog/page-09.md) | [Next ->](changelog/page-02.md)

Page **1** of **9** | commits **1-80** of **689** (newest first)

---

*Regenerate: `python scripts/generate_changelog.py` | page size 80 | 689 commits | 9 pages*
