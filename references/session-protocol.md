# Session protocol

## Names

- Agent: one upper-case word from the registry (`ATLAS`).
- Session: `<AGENT>-<phase>` (`ATLAS-2`). A continuation inside the same phase, because the
  context ran out or the owner switched tools, appends a lowercase letter in order: `ATLAS-2`,
  `ATLAS-2b`, `ATLAS-2c`. A letter means *same lane, same phase, continued*; never a new scope.
- Codex and Claude Code sessions use the same names and the same files.
- The owner starts a session with one message: "You are `ATLAS-2`. Execute lane `L5-platform`
  per `Docs/Execution/Lanes/L5-platform.md`." Everything else the session reads for itself.

## Handoff path

```
Docs/Execution/Handoffs/<lane-key>/<SESSION-NAME>.md
```

Derivable from the name alone. The validator checks that every file in a lane's handoff directory
is named for that lane's agent.

## Inheritance: what a session reads before its first edit

1. Its continuation parent, if it carries a letter (`ATLAS-2c` reads `ATLAS-2b`).
2. Its phase parent: the same agent's last session of the previous phase (`ATLAS-2` reads
   `ATLAS-1` or `ATLAS-1c`). Phase-1 sessions read the lane brief and the roadmap instead.
3. The checkpoint record: the integrator's handoff for the previous phase, which says what merged,
   what failed and what to rebase onto. Phase-1 sessions read the CP0 board rows.
4. Its named upstream agents' newest handoffs, from the registry's `upstreamAgents`.
5. The board, for rows addressed to its lane.

A session whose parent handoff is missing stops and says so on the board. It does not
reconstruct the parent's state by reading code and guessing.

## First five actions

1. Read `Docs/Execution/Lanes/_COMMON.md` and the lane brief.
2. Read the inherited handoffs, nearest parent first.
3. Read the board for rows addressed to the lane.
4. `git fetch`; create or update the lane worktree and branch where `_COMMON.md` says.
5. Append a board row: date, lane key, checkpoint, `CLAIMED`, session name in the ref column,
   sub-team file split in the note.

## Last three actions

1. Push `lane/<key>`.
2. Write the full handoff. Budget the last part of the session for it; write it before running
   out of room, not after. Mandatory even when the session achieved nothing.
3. Append a board row with the final state and the handoff path.

## Handoff contract

Header, then the sections. Nothing is optional.

```
Agent: <SESSION-NAME>          Lane: <lane-key>          Phase: <n>
Predecessor: <SESSION-NAME or "none, first phase">
Branch and head: lane/<key> at <sha>, pushed: yes/no
Board rows appended: <dates and states>
```

- **Outcome**: the user-visible or operational behaviour now proven, and which kind of evidence it
  is: source, local test, integrator stage, staging, device, release.
- **Changes**: every path with its reason.
- **Verification**: every test named; result `PASS`, `FAIL` or `NOT RUN`; log path when run by the
  integrator. Distinguish "ran in my worktree" from "ran at a checkpoint".
- **Limitations and external gates**: every unrun gate, exactly. Never inferred from another.
- **Open shared claims**: each claim posted, its owner, whether it landed.
- **Owner facts requested**: each, with the register entry.
- **Next action**: the exact next task, file and first step, for a reader with none of this
  context. If blocked, the missing fact instead.

Shared-claim hunks are attached as fenced diffs inside the handoff. No secrets, credentials,
personal data or raw third-party payloads in a handoff or on the board.

## Coordinator session shape

1. Read the predecessor's handoff, the board's open rows, and the newest handoff of every lane that
   posted since. Skim; the record is the memory.
2. Answer every open question, conflict and stalled shared claim, in that order, by the ladder.
   One board row per answer; a `D-nnn` entry for anything binding.
3. Review each new handoff against its brief: name what is thin, what was promoted by inference,
   what claims an artifact it does not have. Name, do not fix.
4. Reconcile roadmap, registry and briefs when they disagree; re-run the validator.
5. Route owner-only facts into the owner-decisions table with the exact missing fact.
6. Say whether the phase is ready for the integrator to close, and if not, which lane and which row.
7. Write the handoff and push.

## Integrator session shape

1. Read the coordinator's readiness call and the `SOURCE_READY` rows.
2. Follow `CHECKPOINTS.md`: call, merge serially, apply claims and manifests, run stages once each,
   record, write the changelog entry, push, tell lanes to rebase, hand to the coordinator, promote
   state on evidence only.
3. Between checkpoints, wake only for build slots and the device or environment queue.
