# Lessons from the source programme

Extracted from a nine-lane, five-checkpoint programme that ran on a Swift 6 iOS/macOS monorepo in
September 2026, with Codex and Claude Code sessions mixed, on a machine whose internal disk was 94 %
full. Each lesson names the failure it prevents. The rule without its reason gets bent by the next
agent who does not see the reason.

## Ownership

1. **Ownership is by file, and a machine proves it.** The failures that cost the most time were
   two concurrent agents editing one file. Conventions did not stop it; a validator that expands
   every owner glob against `git ls-files` and fails on any file two lanes match did. A lane owns
   paths, not topics.
2. **Pre-declare the files everyone will want.** The app entry point, the project file, the string
   catalog, the schema file, the matcher: every lane eventually needs a hunk in one of them. Give
   each a fixed owner up front and a shared-claim mechanism (hunk in the handoff, row on the board,
   owner applies and posts the SHA). Discovering the owner mid-phase costs a phase.
3. **Global single-writer resources get manifests.** A string catalog hand-maintained in eighteen
   shapes cannot take nine writers. Lanes write REMOVED/ADDED/CHANGED manifests; the integrator
   applies all of them once per checkpoint in one literal-surgery pass.
4. **The registry wins over the brief.** When a brief and the registry disagree, the registry is
   right and the brief is fixed in the same change. One machine-readable authority, several human
   renderings of it.
5. **A sub-team split is by file too.** A lead with three subagents records which subagent owns
   which files when it claims, or the collision moves one level down.

## Power

6. **Three powers, three agents.** Coordination (who and what next), integration (did it build and
   merge), ownership (does it ship, and every fact an agent may not invent). An arbiter with a lane
   of its own has a stake in every dispute it settles; an arbiter that builds spends its context on
   logs instead of on the picture no single lane has. The validator enforces that the coordinating
   lane owns no source and carries no task.
7. **The coordinator is cheap on purpose.** It reads the board, the open claims and the newest
   handoffs, answers, records, ends. It does not hold the programme in its context; the record does.
   That is what makes running it mid-phase affordable.
8. **A coordinator that lanes must wait for is the bottleneck it was meant to remove.** The
   programme must work without it, more slowly. Lanes post and move on.
9. **The coordinator names findings; it never fixes them.** The one-line unblock is still the
   lane's file. A coordinator that edits source becomes an unvalidated tenth writer.
10. **The precedence ladder makes arbitration reviewable.** Stricter privacy/security rule, then
    canonical contract, then registry ownership, then evidence over assertion, then the earlier
    claim, then the lane that unblocks more, then it is the owner's. Stop at the first rung that
    decides. Record both positions and the rung.

## Record

11. **The board is the only thing that survives between sessions.** Two live sessions may agree on
    anything in a chat window and the agreement dies with their context. A message not on the board
    did not happen. Peer messaging stays allowed for plain facts because routing a lookup through a
    third party is slower without being safer.
12. **Append-only, validated.** Rows are never edited; they are superseded. The validator parses
    every row so a malformed one fails a gate rather than being ignored.
13. **Decisions are numbered and superseded, never edited.** D-003 held a wave back; D-004 lifted
    it and says why. Both stay.
14. **Every session writes a handoff, without exception.** The session that ran out of context
    mid-edit is exactly the one whose successor needs the record most. "Nothing to hand off" is
    itself the finding.
15. **The handoff path is derivable from the session name.** `ATLAS-1b` writes
    `Handoffs/<lane>/ATLAS-1b.md`; `ATLAS-2` reads `ATLAS-1*` without searching. A missing parent
    handoff stops the session; it is not reconstructed by reading code and guessing.
16. **A changelog is written from merges, not memory.** The integrator appends one entry per
    checkpoint naming the SHAs, the lanes merged, the stages run and the state moved.

## Verification

17. **Lanes write, checkpoints verify.** On a shared machine two concurrent builds corrupt each
    other's build database and a second derived-data tree fills the disk. So lanes do not build;
    the integrator runs stages serially behind a lock at checkpoints. Where builds are cheap and
    isolated the policy can relax to focused tests in the lane's worktree, but only the integrator's
    stage run promotes to `VERIFIED`.
18. **`NOT RUN` is honest and expected.** A lane that could not run its tests says so. The
    integrator fills in the result and log path after the stage runs.
19. **What counts as green is written down.** Zero tests executed is a failure of the stage.
    A skipped test is a finding. A test that passes only in isolation is a finding. Read executed
    counts from the summary, never from exit codes.
20. **Never infer a gate from an earlier gate.** Source is not simulator; simulator is not device; a
    fixture is not an external gate; a free-development signing result is not distribution signing.
21. **Checks must fail closed.** A gate that skips paths containing "worktrees" scanned zero files
    and reported success for weeks. A check that cannot tell "held" from "never looked" is not a
    check; mutation-test the validator (`--self-test`) so a broken copy is caught.
22. **Build slots between checkpoints.** A lane that needs compile feedback posts a row; the
    integrator runs the smallest stage against a throwaway merge, records the log, discards the
    worktree. One at a time, never during a checkpoint's own run.

## Scheduling

23. **Nobody is listening while lanes run.** A lane that discovers a cross-lane need mid-phase after
    the providing lane's session ended waits until the next phase. Three mitigations: front-load
    every known edge into the provider's first phase; start the provider lane first and let it get
    well ahead; run a short coordinator session mid-phase whenever question or blocked rows
    accumulate.
24. **Checkpoints are events, not dates.** One opens when every active lane posted `SOURCE_READY`,
    or when the integrator calls it because a merge would unblock the rest.
25. **Fan-out has a ceiling.** Four lane leads per session and three subagents per lead; more
    exhausts the session limit and kills agents mid-edit. Subagent briefs go in the prompt, not a
    scratch file, so a killed subagent can be resumed by message. Critics do not edit what they
    judge.
26. **Deferred lanes keep their validators running.** A lane the owner paused stays in the registry
    as `DEFERRED` so it cannot rot silently and no lane can reactivate it as an accidental
    prerequisite.
27. **Width collapses at hardware gates.** A single device, a single signing identity and the
    owner's presence serialise everything. Plan the last phases at width one.

## Owner

28. **An agent that hits an owner fact stops.** Entity, contract, approval, device time, signing,
    product decisions the owner has not made. The board carries an owner-decisions table with the
    exact missing fact and where it belongs; the agent does the rest of its work and hands off with
    the row open.
29. **Reconcile the plan when reality moves.** A stale plan silently misleading nine agents is worse
    than no plan. The coordinator amends roadmap, registry and briefs in one change and re-runs the
    validator.
30. **Machine constraints are programme rules.** Where worktrees live, what disk builds may use,
    push after every coherent step because the scratchpad is purgeable and the internal disk is
    nearly full. These go in `_COMMON.md`, not in someone's memory.
