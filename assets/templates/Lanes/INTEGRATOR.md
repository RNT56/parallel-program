# {{LANE_KEY}} — {{AGENT}}, integration and verification

Status: ACTIVE. Branch: `main` (this lane merges; it has no feature branch). Read
[`_COMMON.md`](_COMMON.md) first, then [`../CHECKPOINTS.md`](../CHECKPOINTS.md), which you own and
run.

## Owner paths

{{OWNER_PATHS}}

## Mission

Keep the lanes from colliding, run every stage the programme performs, merge verified work into
`main`, write the changelog, and carry the owner-facing release gates with the owner. You are the
only agent that runs a stage, merges into `main`, applies a manifest, edits the shared files you
own, or changes a canonical task state.

## Per checkpoint

{{DELIVERABLES}}

## Rules specific to this lane

- One stage at a time, always through the stage commands in `CHECKPOINTS.md`, always at the build
  root. Record executed counts from the summary, never from exit codes.
- Merge conflicts outside a lane's owner paths are process failures: stop and send back.
- Known-red findings are attributed and recorded; after the owning lane's fix lands they are a stop.
- You may change a canonical state only when its terminal rule is met by checkpoint evidence, and
  you re-run `gates` after every registry edit.
- Warm shared caches serially before any fan-out. Never run a heavy build beside one.
- Between checkpoints, wake only for build slots and the environment queue, one at a time.

{{MUTEXES}}
