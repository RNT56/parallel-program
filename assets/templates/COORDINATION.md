# Coordination: {{PROGRAM}}

Part of the [roadmap](ROADMAP.md). This file says who coordinates the lanes, what that agent may
and may not do, and how a lane raises a question, a conflict or a blocker.

The programme separates three powers deliberately, and no agent holds two of them:

| Power | Held by | Decides |
| --- | --- | --- |
| Coordination | **{{COORDINATOR}}**, lane `{{COORDINATOR_LANE}}` | Who does what next, who owns a disputed file, whether a phase is ready to close, what a handoff is missing |
| Integration | **{{INTEGRATOR}}**, lane `{{INTEGRATOR_LANE}}` | Whether it merged, whether it built, whether the evidence lets a canonical state move |
| Ownership | the owner | Whether it ships, and every fact an agent may not invent |

{{COORDINATOR}} decides *who and what next*. {{INTEGRATOR}} decides *whether it holds*. The owner
decides *whether it ships*. An agent that wants a decision from the wrong holder is told which one
to ask.

## Why the coordinator writes no code

{{COORDINATOR}} owns no source path, carries no task and runs no build. An arbiter with a lane of
its own has a stake in every dispute it settles, and an arbiter that builds spends its context on
logs instead of on the picture no single lane has. {{COORDINATOR}} owns exactly the plan and the
record. That also keeps it cheap: a coordination session reads the board, the open claims and the
newest handoffs, answers, records, and ends.

## What {{COORDINATOR}} does

- **Overwatch.** Reads the board, the open shared claims and every lane's latest handoff, and
  keeps the cross-lane picture: what is blocked, what is merely waiting, which dependency edge is
  about to bite, which lane is drifting from its brief.
- **Answers questions.** A lane posts a `question` row and continues with other work.
  {{COORDINATOR}} answers on the board with the decision and its reason, and with a
  [`DECISIONS.md`](DECISIONS.md) entry whenever the answer binds anyone but the asker.
- **Gives feedback.** Reads a lane's handoff against its brief and returns findings: a state
  promoted by inference, a claim marked done without its artifact, a missing negative control, a
  test named but never listed as `NOT RUN`, an owner fact quietly assumed. It names the finding;
  the lane fixes it.
- **Resolves conflicts.** Two lanes wanting one file, a dependency deadlock, a brief that disagrees
  with the registry, two handoffs asserting different facts about the same code.
- **Keeps the plan true.** When reality diverges from the roadmap, it amends the roadmap, the
  registry and the affected briefs in one change and re-runs the validator.
- **Escalates.** Separates what an agent may decide from what only the owner may, and says so.

## What {{COORDINATOR}} may not do

- Write or edit production source, tests or fixtures.
- Build, test or touch a shared environment or device. That is {{INTEGRATOR}}'s.
- Merge a branch, apply a manifest or edit a shared file. That is {{INTEGRATOR}}'s.
- Promote a canonical task state.
- Supply, approve or approximate an owner fact or an external gate.
- Weaken a privacy, security or safety rule to unblock a lane.
- Overrule {{INTEGRATOR}} on whether something built, or a lane on what its own code does.

## The precedence ladder

Walk from the top; stop at the first rung that decides.

1. The stricter privacy, security or safety rule beats any schedule, convenience or preference.
2. A canonical product, privacy or architecture contract beats any plan, brief or roadmap.
3. The registry's declared ownership beats a lane brief, and a brief that disagrees is corrected.
4. Evidence beats assertion. An unrun gate stays unrun; an earlier gate never settles a later one.
5. The earlier board claim beats the later one when two lanes reach for the same file; the later
   lane files a shared claim instead.
6. The lane that unblocks more other lanes goes first when the ladder is otherwise even.
7. If none of these decides it, it is the owner's, and {{COORDINATOR}} names the missing fact.

Every decision that binds anyone but the asker is recorded in `DECISIONS.md` with both positions,
the rung and the acting agent.

## How a lane raises something

Lanes may talk to each other directly for a fact. Anything that binds goes through
{{COORDINATOR}} and onto the board.

| Situation | Row to post | Who answers |
| --- | --- | --- |
| I need a file another lane owns | Shared claims table, hunk in your handoff | The owning lane; {{COORDINATOR}} if it stalls |
| I need a shared-model or schema change | Board row addressed to the owning lane | That lane; {{COORDINATOR}} orders it if contested |
| I need a change in a manifest-governed resource | Manifest under `Manifests/`, board row | {{INTEGRATOR}} applies it at the checkpoint |
| I need compile or test feedback | Board row, `build slot` | {{INTEGRATOR}} |
| I need the shared environment or device | Board row addressed to {{INTEGRATOR}} | {{INTEGRATOR}}, in queue order |
| Two lanes want the same file | Board row, `conflict` | {{COORDINATOR}}, by the ladder |
| My brief and the registry disagree | Board row, `question` | {{COORDINATOR}}, and it fixes the brief |
| I am blocked on a fact nobody has | `BLOCKED` row plus an owner-decisions row | The owner; {{COORDINATOR}} routes and tracks |
| Another lane's handoff looks wrong | Board row, `question`, quoting both | {{COORDINATOR}}, on rung four |

Post the row, then keep working on something else. A lane never idles waiting for an answer and
never guesses one.

## When to run {{COORDINATOR}}

A short session, as often as the board needs it, not only at checkpoints: at the start of a phase;
whenever open question, conflict or blocked rows accumulate; before {{INTEGRATOR}} closes a
checkpoint; after a checkpoint, to fold what was learned into the plan; whenever the owner wants
the state read back. Sessions are `{{COORDINATOR}}-1`, `{{COORDINATOR}}-1b`, `{{COORDINATOR}}-2`,
each with a handoff at `Handoffs/{{COORDINATOR_LANE}}/`.

## If {{COORDINATOR}} is not running

The programme still works, more slowly. The board keeps its meaning, {{INTEGRATOR}} still merges
and builds, and a blocked lane still posts and moves on. Nothing requires a coordination session to
be live for a lane to make progress; a coordinator that lanes must wait for is the bottleneck it
was meant to remove.
