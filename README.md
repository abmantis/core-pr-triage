# core-pr-triage

Claude routine that reviews home-assistant/core PRs and answers replies to its reviews, posting as the bot user `hacoreview`.

- `TRIAGE.md`: the routine's instructions.
- `state.json`: the routine's state, updated by the routine through one PR per run.
- `dashboard.html`: the PRs the routine reviewed and their state, rebuilt by `dashboard.py` at the end of each run.
- `.github/workflows/post.yml`: posts the routine's reviews and replies on core as `hacoreview`. The routine dispatches it instead of posting itself, so the proxy's Claude Code footer isn't added.

## Routine setup
Create a scheduled routine at claude.ai/code:
- Repositories: `abmantis/core-pr-triage`, `home-assistant/core`.
- Model: Opus 5.5.
- Environment: `GH_TOKEN` set to a classic token with scope `public_repo` (GitHub's docs say dispatching a workflow needs `repo`; switch to it if dispatching `post.yml` is refused) for the routine's user: `hacoreview` or any other user. Reviews and replies are posted as `hacoreview` either way.
- Instructions:
  ```
  Read TRIAGE.md in the core-pr-triage clone and follow it. Push state.json changes to the run's branch in abmantis/core-pr-triage, as TRIAGE.md says.
  ```

In abmantis/core-pr-triage:
- Give the routine's user write access. It opens, closes and merges the state PRs, and dispatches `post.yml`.
- Add the Actions secret `HACOREVIEW_TOKEN`: a classic `hacoreview` token with scope `public_repo` (the routine's token, if it runs as `hacoreview`). `post.yml` posts with it.
- Enable "Automatically delete head branches", so merged `run/` branches don't pile up.

## Notes
- The GitHub proxy serves only repositories attached to the routine, so core is attached and cloned on every run.
- The proxy doesn't restrict pushes. Core is protected by `TRIAGE.md` and its own branch protection.
- Mute a PR: add its number to `muted` in `state.json` on `main`.
