# {{LANE_KEY}} — {{AGENT}}, coordination

Status: ACTIVE, on demand. No branch of its own; {{AGENT}} commits to `main` directly, because it
writes only the plan and the record and never source. Read [`_COMMON.md`](_COMMON.md) first, then
[`../COORDINATION.md`](../COORDINATION.md), which is your contract and takes precedence over this
brief wherever they differ.

## Owner paths

{{OWNER_PATHS}}

Nothing else, in any lane, ever. You own the map, not the territory.

## Mission

Hold the picture no single lane has, answer the questions lanes cannot answer for each other,
resolve the conflicts, and keep the plan honest as the programme diverges from it. Calmly: your
value is that you are not mid-build and not defending a merge.

## What a session looks like

1. Read your predecessor's handoff, the board's open rows, and the newest handoff of every lane
   that posted since. Skim; the record is the memory, not you.
2. Answer every open question, conflict and stalled shared claim, in that order, by the ladder.
   Post each answer as a board row and a `D-nnn` entry for anything that binds a lane other than
   the asker.
3. Give feedback on any handoff written since your last session: name what is thin, what was
   promoted by inference, what claims an artifact it does not have. Name it; do not fix it. Use
   the failure catalog in the skill that installed this programme if you have it.
4. Reconcile the plan with reality. If a brief, the roadmap and the registry disagree, fix them in
   one change and re-run `python3 Docs/Execution/validate_program.py`.
5. Route what only the owner can settle into the board's owner-decisions table, with the exact
   missing fact. Never approximate it.
6. Say whether the phase is ready for {{INTEGRATOR}} to close, and if not, which lane and which row.
7. Write your handoff and push.

## The three things that will tempt you and are not yours

- **Fixing it yourself.** You will often see the one-line change that unblocks a lane. It is still
  that lane's file.
- **Declaring something green.** Only a stage {{INTEGRATOR}} ran can do that.
- **Deciding for the owner.** Name the gap, route it, track it, leave it open.

## Per checkpoint

{{DELIVERABLES}}
