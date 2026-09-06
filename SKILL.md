---
name: parallel-program
description: Design, install and operate a multi-agent, multi-session, multi-phase execution programme for any coding project. Use when a user wants several agents (Codex or Claude Code sessions) to work a codebase in parallel with named lanes, exclusive file ownership, a calm central coordinator, an integrator that owns every build and merge, an append-only progress board, checkpoints, per-session handoffs, a decisions log and a changelog. Also use to size a programme to a goal, to write lane briefs and agent names, to audit a running programme, or to close a phase.
---

# Parallel Program

Turn a project plus a goal into a programme that several agent sessions can execute concurrently
without colliding, without losing state between sessions, and without anyone guessing an answer
that belongs to someone else. The design is extracted from a nine-lane programme that ran on a real
iOS codebase; [lessons.md](references/lessons.md) records what was learned and why each rule exists.
Read it once before your first programme; after that the rules below are enough.

The output is a set of files in the target repository under `Docs/Execution/`, an owner-facing
summary, and the exact first message to paste into each agent session. Do not start executing the
lanes yourself unless the user asks you to take a lane.

## The model in six sentences

1. A **lane** is the unit of ownership: one lead agent, one branch, one exclusive set of owner
   paths, one list of carried tasks. No tracked file is owned by two lanes, and a validator proves it.
2. **Three powers are held by three different agents**: the coordinator decides who and what next,
   the integrator decides whether it built and merged, the owner decides whether it ships and
   supplies every fact an agent may not invent. The coordinator owns no source, runs no build,
   promotes no state.
3. **The board is the record.** `Docs/Execution/PROGRESS.md` is append-only and parsed by the
   validator. A claim, a question, a blocker or a decision exists exactly to the extent it is a row.
4. **Lanes write; checkpoints verify.** Only the integrator's checkpoint run turns `SOURCE_READY`
   into `VERIFIED`. Lanes mark their tests `NOT RUN` and that is honest.
5. **One session is one named agent**, `<AGENT>-<phase>[letter]`. Its first act is reading its
   predecessor's handoff; its last act is writing its own, at a path derivable from its name.
6. **Blocked means keep going.** A lane posts the row, does the rest of its work, and hands off with
   the request open. It never idles and never guesses.

## Workflow

### 1. Establish the harness and the scope

- Ask which harness each session will run in only if it matters for the mechanics you emit (worktree
  commands, subagent limits, session naming are shared; see
  [harness-adapters.md](references/harness-adapters.md)). Programmes may mix Codex and Claude Code
  sessions; they share the same names, board and handoff files.
- Read the repository: `git status --short`, `git log --oneline -20`, existing `AGENTS.md`,
  `CLAUDE.md`, plans, task ledgers, CI scripts, build commands, test layout, disk and machine
  constraints. Existing uncommitted changes belong to the user; never fold them into the programme.
- Take the user's goals verbatim. Separate facts, assumptions and unknowns. Anything only the user
  can decide (release approval, credentials, legal facts, product choices they have not made) goes
  into the owner-decisions table, never into a lane's assumptions.

### 2. Size the programme

Follow [sizing.md](references/sizing.md). The number of delivery lanes is the number of disjoint
ownership sets that carry real work, capped by how many sessions the user can run at once. Every
programme, however small, has a coordinator and an integrator as separate sessions; a solo
programme is the one case where this skill is the wrong tool. Phases are checkpoint windows; there
are as many as the goal has natural verification plateaus, usually three to five.

Decide the **build policy** explicitly: `integrator-only` when builds share a machine, a disk, a
simulator or a build database (the safe default); `lanes-focused` when each worktree can run its
own focused tests cheaply and in isolation. Under either policy only the integrator's stage run
counts as `VERIFIED`.

### 3. Design the lanes

For each lane fix: key (`L1-<slug>`), a one-word upper-case agent name, owner paths as globs,
excluded paths, carried task IDs, sub-team split by file, first deliverable per checkpoint, upstream
agents it reads. Then write the **cross-lane dependency table**: every edge where one lane needs a
file, a read model, a schema change, a shared resource or an owner fact from another. Front-load
every known edge into the providing lane's first phase, and order the providing lane first.

Pre-declare **shared files** with a fixed owner (the app entry point, the project file, string
catalogs, lockfiles, the router, the schema). Everyone else files a shared claim with the hunk in
their handoff. Global single-writer resources get a **manifest** mechanism the integrator applies
once per checkpoint.

Name agents with single, distinctive, upper-case words that are not project nouns and not easily
confused with each other. Reuse the roles: coordinator, integrator, then one name per delivery lane.

### 4. Install

1. Write `Docs/Execution/lanes.json` from
   [assets/templates/lanes.json](assets/templates/lanes.json).
2. Run `python3 scripts/scaffold.py --root <repo>`; it renders the roadmap, board, roster,
   coordination contract, decisions log, checkpoint protocol, changelog, common rules, one brief
   per lane, the handoff directories and the validator into the repository. It never overwrites an
   existing file.
3. Edit every rendered brief so it is specific: mission, first deliverable, what is known and must
   not be redone, hazards of this repository. A brief an agent can paste as its first message is the
   bar.
4. Append the agent-instruction block to `AGENTS.md` and `CLAUDE.md` (the scaffold prints it, and
   applies it with `--apply-instructions`). The block is short and points at `_COMMON.md`.
5. Run `python3 Docs/Execution/validate_program.py` until it is green, then
   `python3 Docs/Execution/validate_program.py --self-test` once to prove the copy fails closed.
6. Post the CP0 rows on the board: one `CLAIMED` per lane, `DEFERRED` for deferred lanes, the
   owner-decision rows, and the known-red findings.
7. Commit only when the user asks. Report the exact first message for each session, in start order.

### 5. Operate

- **Start order** inside a phase: the coordinator briefs, then the lane other lanes queue behind
  (usually schema or platform), then the rest, with the integrator warming caches serially before
  any fan-out. Short, dependency-free repair work goes early.
- **Mid-phase coordinator sessions** are cheap and remove most stall risk: read the board, answer
  every open question and conflict by the precedence ladder, review new handoffs, reconcile the
  plan, say whether the phase is ready to close, hand off.
- **Checkpoints are events, not dates.** The integrator calls one when every active lane posted
  `SOURCE_READY`, or when the remaining lanes are blocked on something a merge would unblock. The
  protocol in the rendered `CHECKPOINTS.md` is followed one stage at a time and the changelog entry
  is written from the merges, not from memory.
- When a lane is a product build with subjective surfaces, generate its execution prompt with
  `aft-gauntlet` (harness chosen explicitly, critics separated from builders) and reference that
  prompt from the lane brief; the lane still obeys `_COMMON.md`, the board and the handoff rule.
- Use [session-protocol.md](references/session-protocol.md) for the first five and last three
  actions of any session, and [failure-catalog.md](references/failure-catalog.md) when reviewing a
  handoff.

### 6. Audit an existing programme

When asked to check on a running programme: run the validator, read the board's open rows and the
newest handoff per lane, and report drift from the briefs, stalled shared claims, states promoted by
inference, and owner decisions still open. Do not fix lane files; name the finding and the lane.

## Rules that do not bend

- Never let the coordinator own source, carry a task, build, merge or promote state.
- Never let two lanes own one tracked file; a validator, not a convention, enforces it.
- Never edit or delete a board row or a decision; supersede it with a new one.
- Never infer a later gate from an earlier one: source is not simulator, simulator is not device,
  a fixture is not an external gate, a zero-test run is not a pass, a skipped test is a finding.
- Never invent an owner fact. Route it, track it, leave it open.
- Never leave a session without a handoff, including a session that achieved nothing.
- Never put durable state only in a chat, a scratchpad or a transcript. If it is not on the board,
  in a handoff or pushed, the next session does not have it.
- Persistence does not broaden authorization: a programme continues previously authorized work
  only. Commits, pushes, deployments and external messages happen when the owner asks.

## Files in this skill

- [references/lessons.md](references/lessons.md): what the source programme taught, with the why.
- [references/operating-model.md](references/operating-model.md): the full model, precedence ladder,
  row-to-post table, what counts as green.
- [references/sizing.md](references/sizing.md): tiers, session limits, phase count, build policy.
- [references/session-protocol.md](references/session-protocol.md): naming, inheritance, first and
  last actions, the handoff contract.
- [references/harness-adapters.md](references/harness-adapters.md): Claude Code and Codex mechanics,
  worktrees, subagent limits, peer messaging, how `aft-gauntlet` plugs in.
- [references/failure-catalog.md](references/failure-catalog.md): the recurring ways a programme
  lies to itself, for coordinator reviews.
- [assets/templates/](assets/templates/): every rendered document, with `{{PLACEHOLDERS}}`.
- [scripts/scaffold.py](scripts/scaffold.py): renders the templates from the registry.
- [scripts/validate_program.py](scripts/validate_program.py): the fail-closed validator the scaffold
  copies into the repository; `--self-test` mutation-tests it.
