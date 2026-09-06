# Roadmap: {{PROGRAM}}

Defined: {{DATE}}. Classification: **executable plan**. It assigns the goal below to lanes that
agents can run concurrently and fixes the checkpoints at which the lanes come together to verify
and merge. It promotes no task state.

**Goal.** {{GOAL}}

Machine-readable authority for ownership: [`lanes.json`](lanes.json), validated by
`python3 Docs/Execution/validate_program.py`. Shared progress: [`PROGRESS.md`](PROGRESS.md).
Checkpoint protocol: [`CHECKPOINTS.md`](CHECKPOINTS.md). One brief per lane: [`Lanes/`](Lanes/).
Who runs each lane and what each session inherits: [`ROSTER.md`](ROSTER.md). Who answers
questions and resolves conflicts: [`COORDINATION.md`](COORDINATION.md), with its log at
[`DECISIONS.md`](DECISIONS.md). What each checkpoint merged: [`CHANGELOG.md`](CHANGELOG.md).

## 1. Scope

In scope: (fill in from the goal and the task ledger).

Deferred by owner decision: (lanes with status `DEFERRED`, their validators keep running, no lane
may depend on them).

Owner-only facts stay owner-only: (list them). A lane may prepare a packet; it never fills in a
blank.

## 2. The operating model in one page

**A lane is the unit of ownership.** One lead agent, an exclusive set of owner paths, a
`lane/<key>` branch and a list of tasks it carries end to end. The lead may spawn subagents; the
lane, not the subagent, owns the paths.

**No two lanes write the same tracked file.** The validator expands every owner glob against
`git ls-files` and fails on any file two lanes claim. A file another lane needs is a *shared claim*:
hunk in the handoff, row on the board, the owning lane applies it.

**Lanes write; checkpoints verify.** Build policy `{{BUILD_POLICY}}`; see `CHECKPOINTS.md`. Only
{{INTEGRATOR}}'s stage run turns `SOURCE_READY` into `VERIFIED`.

**Three powers, held separately.** {{COORDINATOR}} coordinates, {{INTEGRATOR}} integrates, the
owner approves. See `COORDINATION.md`.

**Progress lives in one file.** `PROGRESS.md` is append-only and parsed by the validator.

## 3. Lanes

{{LANE_TABLE}}

Start order inside a phase, and why: (the lane others depend on first, short repairs early, then
the rest; the integrator warms caches before any fan-out).

## 4. Checkpoints

{{CHECKPOINT_TABLE}}

Checkpoints are events, not dates. One opens when every ACTIVE lane has posted `SOURCE_READY` for
its deliverable, or when {{INTEGRATOR}} calls it because the remaining lanes are blocked on
something a merge would unblock.

## 5. Dependencies that cross lanes

Each is a board row when requested and another when it lands. Front-loaded into the providing
lane's first phase.

{{DEPENDENCY_TABLE}}

## 6. Machine policy

Worktree root: `{{WORKTREE_ROOT}}`. Build root: `{{BUILD_ROOT}}`. {{MACHINE_NOTES}}

Fan-out: at most four lane leads per owner session, three subagents per lead, briefs in the
prompt. Push after every coherent step.

## 7. Communication protocol

See the row-to-post table in `COORDINATION.md`. A message that is not on the board did not happen.

## 8. What "done" means, per layer

- A **lane deliverable**: source, failure-path tests, fixtures, manifests and handoff pushed on
  `lane/<key>`; board row `SOURCE_READY`.
- A **checkpoint**: every listed stage passed at one SHA on `main`; a `VERIFIED` row per lane with
  log paths. A skipped test, a zero-test run or a stage that could not start is a finding.
- A **task**: its own registry's terminal rule, applied by {{INTEGRATOR}} on checkpoint evidence.
- The **programme**: the final checkpoint closes for the stated scope.
