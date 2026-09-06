# Agent roster: {{PROGRAM}}

One session is one agent. The owner starts a session by naming the agent and telling it to
execute its lane; the agent's first act is to read its predecessor's handoff, and its last act is
to write its own. [`lanes.json`](lanes.json) carries the same names in each lane's `agentName`,
and the validator fails if this file and the registry disagree.

## The agents

Three powers, held separately: **{{COORDINATOR}}** coordinates, **{{INTEGRATOR}}** integrates and
builds, the owner approves. The others deliver. See [`COORDINATION.md`](COORDINATION.md).

{{ROSTER_TABLE}}

Phases are the checkpoint windows: phase 1 runs from CP0 to CP1, phase 2 from CP1 to CP2, and so
on. {{COORDINATOR}} runs as many short sessions per phase as the board needs.

## Session names

`<AGENT>-<phase>`: `{{FIRST_AGENT}}-1`, `{{FIRST_AGENT}}-2`. A continuation inside one phase appends
a lowercase letter in order: `{{FIRST_AGENT}}-1`, `{{FIRST_AGENT}}-1b`, `{{FIRST_AGENT}}-1c`. A letter
means *same lane, same phase, continued*; never a different scope. Codex and Claude Code sessions
use the same names and the same handoff files.

## Handoff files

```
Docs/Execution/Handoffs/<lane-key>/<SESSION-NAME>.md
```

The path is derivable from the name alone, which is what lets the next session find its parent
without searching.

## Which agent inherits from which

Every session reads, in this order, before touching a file:

1. **Its continuation parent**, if its name carries a letter suffix.
2. **Its phase parent**: the same agent's last session in the previous phase. Phase-1 agents read
   their lane brief and the roadmap instead.
3. **The checkpoint record**: `{{INTEGRATOR}}-<previous phase>`. Phase-1 agents read the CP0 board
   rows instead.
4. **Its named upstream agents**:

{{UPSTREAM_TABLE}}

{{COORDINATOR}} is the one agent every other may address directly. Post a `question` or
`conflict` row and carry on; the answer arrives as a board row and, when it binds anyone else, as
a numbered entry in [`DECISIONS.md`](DECISIONS.md).

An agent that finds its parent handoff missing stops and says so on the board. It does not
reconstruct the parent's state by reading code and guessing.

## How a session starts and ends

**First five actions**, before any edit:

1. Read `Lanes/_COMMON.md` and your lane brief.
2. Read the handoffs listed above, nearest parent first.
3. Read the board, `PROGRESS.md`, for rows addressed to your lane.
4. `git fetch`, then create or update your worktree and branch where `_COMMON.md` says.
5. Append a board row: date, lane key, checkpoint, `CLAIMED`, your session name in the ref column.

**Last three actions**, before the session ends:

1. Push `lane/<key>`.
2. Write the full handoff. Mandatory even when the session achieved nothing.
3. Append a board row with your final state and the handoff path.

## What a full handoff must contain

Use [`Handoffs/TEMPLATE.md`](Handoffs/TEMPLATE.md). Nothing in it is optional. Tests a lane wrote
but could not run are listed `NOT RUN`; {{INTEGRATOR}} fills in the result and log path after the
stage runs. Nothing durable may live only in a session transcript.

## Start messages

{{START_MESSAGES}}
