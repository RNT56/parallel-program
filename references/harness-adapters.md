# Harness adapters

The programme's files, names, board and handoffs are harness-neutral. Only the session mechanics
differ. Put the relevant mechanics in the rendered `_COMMON.md` so a session does not have to know
which harness a peer is in.

## Shared mechanics

- **Worktrees.** One per lane, on the disk the machine policy names, never in a purgeable
  scratchpad: `git worktree add <worktree-root>/<lane> -b lane/<key> origin/main`. Record the root
  in the registry's `machine.worktreeRoot`.
- **Push after every coherent step.** `git push -u origin lane/<key>`.
- **Subagents.** At most three per lead, each confined to a named file set, the brief in the prompt
  rather than a scratch file. A subagent killed by a session limit is resumed by message after
  re-reading its edited files. Critics receive the artifact, the requirements and the bar, not the
  builder's rationale, and they do not edit what they judge.
- **Peer messaging.** Allowed for a plain fact. Anything binding goes to the coordinator and the
  board.
- **Build policy** from the registry decides whether a lane may run tests locally.

## Claude Code

- Sessions run as `claude` in a terminal or the desktop app; the owner opens one per agent and
  pastes the start message. `EnterWorktree` defaults to `.claude/worktrees/` on the internal disk;
  when that disk is constrained, create the worktree by hand at the machine root instead.
- A worktree-isolated session's Bash may refuse heredocs, `cd` and long chains: write scripts to
  the scratchpad and run them by path. Absolute paths for every mutating command.
- `ListAgents` and `SendMessage` reach live peer sessions and subagents; use them for facts only.
- Subagents via the `Agent` tool; four lane leads per owner session at most.
- Long-running lane work can be driven by `/loop` without an interval; the loop reads the board
  and the handoff each iteration and stops at `SOURCE_READY` or a real blocker.
- Skills that scan paths may skip anything containing `worktrees`; run repository gates from a
  detached main checkout or verify the scanned file count is non-zero.
- Memory files are not programme state. Only the board and the handoffs are.

## Codex

- Sessions run as `codex` with the same start message. `/goal` with a verifiable end state is the
  continuation engine for a lane session; the goal names `SOURCE_READY` on the board plus a pushed
  handoff as its condition.
- Native subagents are spawned by the lead with the same three-per-lead ceiling and file-set
  confinement.
- Codex reads `AGENTS.md`; make sure the programme block is appended there and that it points at
  `_COMMON.md`.

## Plugging in `aft-gauntlet`

When a lane's deliverable is a product surface with subjective quality (a website, a game screen,
an app flow, a design system), generate that lane's execution prompt with `aft-gauntlet`:

1. Name the harness explicitly for that lane.
2. Give it the lane brief, the owner paths and the evidence gates from the checkpoint table.
3. Store the emitted prompt at `Docs/Execution/Lanes/<key>.gauntlet.md` and reference it from the
   brief.
4. The Gauntlet's builders and critics are the lane's subagents; they inherit the file-ownership,
   board and handoff rules from `_COMMON.md`. The Gauntlet's terminal condition is the lane's
   `SOURCE_READY`, not `VERIFIED`; verification is still the integrator's.

## Mixed programmes

A programme may run some agents in Codex and others in Claude Code. Names, board and handoffs are
identical. The only cross-harness gap is live peer messaging, which is not the record anyway.
