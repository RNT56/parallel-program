# Checkpoint protocol: {{PROGRAM}}

{{INTEGRATOR}} owns this file and runs everything in it. Lanes read it to know what will be run
against their work and what counts as green. Build policy: `{{BUILD_POLICY}}`.

## Stages

{{STAGES_TABLE}}

Build root: `{{BUILD_ROOT}}`. Machine notes: {{MACHINE_NOTES}}

## Before a checkpoint

{{COORDINATOR}} says whether the phase is ready, naming any lane that is not and the row that
proves it. {{INTEGRATOR}} may still call a checkpoint over that reading, and records why.

## Running a checkpoint

1. **Call it.** Append a board row `{{INTEGRATOR_LANE}} | CPn | IN_PROGRESS` naming the lanes that
   posted `SOURCE_READY` and the ones that did not. Lanes that did not post are not merged.
2. **Merge serially,** in the order that minimises shared-claim churn (the lane others depend on
   first): fetch `origin/lane/<key>`, merge into `main` locally, resolve conflicts only inside the
   lane's own owner paths, run `gates` after each merge. A conflict outside the lane's owner paths
   is a process failure: stop, record, send back.
3. **Apply shared claims and manifests** in the order posted, each as its own commit, then `gates`.
4. **Run the stages** listed for the checkpoint, in order, each once. A failing stage stops the
   checkpoint; record the failure with its log path and return it to the lane whose owner paths the
   failing test names. Do not rerun a flaky test until it passes; record it and let the owning lane
   fix or justify it.
5. **Record.** One `VERIFIED` or `BLOCKED` row per lane with the SHA and log paths; one row for the
   checkpoint. Copy summaries a task needs into the evidence location; the build root is not
   evidence.
6. **Write the changelog entry** in [`CHANGELOG.md`](CHANGELOG.md) from the merges and summaries.
7. **Push `main`,** then tell every lane to rebase `lane/<key>` before continuing.
8. **Hand the phase to {{COORDINATOR}},** which rebriefs the lanes and folds what was learned into
   the roadmap and briefs.
9. **Promote state** only where checkpoint evidence satisfies the task's own terminal rule. Re-run
   `gates` after every registry edit.

## What counts as green

- A stage passes only if it ran to completion with exit zero and its summary shows a non-zero
  executed count. "0 tests executed" is a failure of the stage.
- A skipped test is a finding. A test that passes only in isolation is a finding. A warning under
  warnings-as-errors is a failure.
- Known-red items are attributed to a lane and recorded; once that lane's fix lands they are a stop.
- A local or simulated result never closes an environment, device or external gate.

## Build slots between checkpoints

A lane posts `Ln | CPn | CLAIMED | build slot: <target>`. {{INTEGRATOR}} runs the smallest matching
stage against a throwaway merge of that lane's branch onto `main` in a disposable worktree, records
the row with the log path, discards the worktree. One at a time, never during a checkpoint's own run.

## Verification matrix

{{MATRIX_TABLE}}
