# core-pr-triage

Claude routine that reviews home-assistant/core PRs and answers replies to its reviews, posting as the bot user `hacoreview`.

- `TRIAGE.md`: the routine's instructions.
- `state.json`: the routine's state, updated by the routine through one PR per run.

## Routine setup
Create a scheduled routine at claude.ai/code:
- Repositories: `abmantis/core-pr-triage`, `home-assistant/core`.
- Model: Opus 5.5.
- Environment: `GH_TOKEN` set to a classic `hacoreview` token with scope `public_repo`.
- Instructions:
  ```
  Read TRIAGE.md in the core-pr-triage clone and follow it. Push state.json changes to the run's branch in abmantis/core-pr-triage, as TRIAGE.md says.
  ```

In abmantis/core-pr-triage:
- Give `hacoreview` write access. It opens, closes and merges the state PRs.
- Enable "Automatically delete head branches", so merged `run/` branches don't pile up.

## Notes
- The GitHub proxy serves only repositories attached to the routine, so core is attached and cloned on every run.
- The proxy doesn't restrict pushes. Core is protected by `TRIAGE.md` and its own branch protection.
- Mute a PR: add its number to `muted` in `state.json` on `main`.
- Posts may carry a Claude Code footer added by the proxy.
