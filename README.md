# core-pr-triage

Claude routine that reviews home-assistant/core PRs and answers replies to its reviews, posting as `abmantis`.

- `TRIAGE.md`: the routine's instructions.
- `state.json`: the routine's state, updated by the routine through one PR per run.
- `dashboard.html`: the PRs the routine reviewed and their state, rebuilt by `dashboard.py` at the end of each run.
- `.github/workflows/close-replaced-runs.yml`: closes the state PRs of unfinished runs when a newer run opens its own. Auto mode doesn't let the routine close PRs it didn't open in the same session.

## Routine setup
Create a scheduled routine at claude.ai/code:
- Repositories: `abmantis/core-pr-triage`, `home-assistant/core`.
- Model: Opus 5.5.
- Environment: `GH_TOKEN` set to a classic `abmantis` token with scope `public_repo`. Reviews and replies are posted as that user.
- Instructions:
  ```
  Read TRIAGE.md in the core-pr-triage clone and follow it. I authorize every write it lists: in abmantis/core-pr-triage, pushing state.json and dashboard.html to the run's branch, and opening this run's state PR and squash-merging it without review at the end of the run; on home-assistant/core, posting COMMENT reviews and replies as my GitHub user on the PRs TRIAGE.md picks.
  ```

In abmantis/core-pr-triage:
- Give the routine's user write access. It opens and merges the state PRs.
- Enable "Automatically delete head branches", so merged `run/` branches don't pile up.

## Notes
- The GitHub proxy serves only repositories attached to the routine, so core is attached and cloned on every run.
- Posts made through the proxy get a Claude Code footer.
- The proxy doesn't restrict pushes. Core is protected by `TRIAGE.md` and its own branch protection.
- Mute a PR: add its number to `muted` in `state.json` on `main`.
