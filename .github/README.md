# GitHub configuration

This repository is an **AI-generated research scaffold**. It is intentionally **not** set up for CI builds or deploy runs.

- There are **no** workflow files under `.github/workflows/`.
- Push commits use `[skip ci]` / `[skip actions]` so GitHub Actions will not run if workflows are added later by mistake.
- Prefer keeping Actions disabled at the repository level:
  Settings → Actions → General → **Disable actions**.
