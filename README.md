# core-pr-triage

Claude routine that reviews home-assistant/core PRs and answers replies to its reviews, posting as `abmantis`.

- `TRIAGE.md`: the routine's instructions.
- `state.json`: the routine's state, created and updated by the routine on `main`.

## Routine setup
Create a scheduled routine at claude.ai/code:
- Repositories: `abmantis/core-pr-triage`, `home-assistant/core`.
- Schedule: hourly.
- Model: Opus 5.5.
- Environment: default.
- Instructions:
  ```
  Read TRIAGE.md in the core-pr-triage clone and follow it. Push state.json changes directly to main of abmantis/core-pr-triage.
  ```

## Notes
- The GitHub proxy serves only repositories attached to the routine, so core is attached and cloned on every run.
- The proxy doesn't restrict pushes. Core is protected by `TRIAGE.md` and its own branch protection.
- Mute a PR: add its number to `muted` in `state.json` on `main`.
- Posts may carry a Claude Code footer added by the proxy.
