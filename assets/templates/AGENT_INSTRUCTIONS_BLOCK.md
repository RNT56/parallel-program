<!-- parallel-program:begin -->
## Parallel execution programme

This repository runs `{{PROGRAM}}` as concurrent agent lanes. Authority: `Docs/Execution/lanes.json`
(who may write where), validated by `python3 Docs/Execution/validate_program.py`. Start from
`Docs/Execution/Lanes/_COMMON.md`, then your lane brief. The only shared record is
`Docs/Execution/PROGRESS.md`; a message that is not a row there did not happen.

- One lane, one branch `lane/<key>`, one exclusive owner-path set. A file you need but do not own
  is a shared claim on the board, applied by its owner; never edit it yourself.
- Three powers are held separately. {{COORDINATOR}} coordinates and owns no source, runs no build,
  promotes no state. {{INTEGRATOR}} integrates, runs every stage and merges. The owner approves.
  Anything that binds another lane goes through {{COORDINATOR}} and onto the board; binding
  decisions are numbered in `Docs/Execution/DECISIONS.md`.
- Build policy `{{BUILD_POLICY}}`: see `Docs/Execution/CHECKPOINTS.md`. Only the integrator's stage
  run turns `SOURCE_READY` into `VERIFIED`.
- One session is one named agent, `<AGENT>-<phase>`. Every session ends with a handoff at
  `Docs/Execution/Handoffs/<lane-key>/<SESSION-NAME>.md`, without exception.
- An agent that hits a fact only the owner can supply posts it and keeps going. It never assumes.
<!-- parallel-program:end -->
