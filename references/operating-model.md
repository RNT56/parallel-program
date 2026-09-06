# Operating model

Everything the rendered documents say, in one place, so a programme designer can check a design
against it. The rendered `COORDINATION.md`, `CHECKPOINTS.md` and `_COMMON.md` carry the same
content for the agents.

## Roles

| Role | Registry `role` | Decides | May not |
| --- | --- | --- | --- |
| Coordinator | `coordination` | Who does what next; who owns a disputed file; whether a phase is ready to close; what a handoff is missing | Own source; carry a task; build, test or merge; promote state; supply or approximate an owner fact; weaken a privacy or security rule |
| Integrator | `integration` | Whether it merged; whether a stage passed; whether evidence lets a canonical state move; build-slot and device queue order | Resolve a merge conflict outside the lane's owner paths (that is a process failure sent back); rerun a flaky test until it passes |
| Delivery lane | `delivery` | Its own code, tests, fixtures, manifests and handoff | Edit a file it does not own; build under `integrator-only`; promote state; guess an answer |
| Owner | (not a lane) | Whether it ships; every fact an agent may not invent | — |

Exactly one lane has each of the first two roles. The coordinator's owner paths are the plan and
the record only: the roadmap, board, roster, coordination contract, decisions log, changelog, lane
briefs, handoff READMEs, its own handoff directory, the registry and the validator.

## Lane anatomy

```
key            L3-intelligence          stable, prefix Ln- (LC- for coordination, L0- for integration)
agentName      IRIS                     one upper-case word, unique, not a project noun
role           delivery
status         ACTIVE | STANDBY | DEFERRED
branch         lane/intelligence        integrator merges into main; coordinator writes main directly
ownerPaths     globs, expanded against git ls-files
excludedPaths  globs carved out of ownerPaths for another lane
tasks          IDs that exist in a task source; carried by exactly one lane
subTeams       name, files, tasks         up to three, disjoint files
phases         [1,2,3]                  which checkpoint windows the agent runs
upstreamAgents names it reads handoffs from
checkpointDeliverables  CPn -> one sentence each
mutexes        rules specific to this lane
```

## Board

`Docs/Execution/PROGRESS.md`, three tables, append-only, parsed by the validator.

**Board**: `| Date | Lane | Checkpoint | State | Ref | Note |`. States: `CLAIMED`, `IN_PROGRESS`,
`SOURCE_READY`, `VERIFIED`, `BLOCKED`, `DEFERRED`, `SUPERSEDED`. Row kinds inside the note:
`question`, `conflict` (for the coordinator), `build slot`, `device` (for the integrator).

**Shared claims**: `| Date | Lane | Path | Reason | Owner ack |`. Path must exist. The hunk lives in
the claimant's handoff.

**Owner decisions and facts requested**: `| Date | Lane | Needed | Register or plan entry | Status |`.

Sign rows with the session name in the ref column. Supersede, never edit.

## Which row to post

| Situation | Row | Who answers |
| --- | --- | --- |
| I need a file another lane owns | Shared claims, hunk in handoff | Owning lane; coordinator if it stalls |
| I need a schema or shared-model change | Board row addressed to the owning lane | That lane; coordinator orders it if contested |
| I need a change in a manifest-governed resource | Manifest file plus board row | Integrator, at the checkpoint |
| I need compile or test feedback | Board row `build slot` | Integrator |
| I need the shared device or environment | Board row addressed to the integrator | Integrator, in queue order |
| Two lanes want the same file | Board row `conflict` | Coordinator, by the ladder |
| My brief and the registry disagree | Board row `question` | Coordinator, and it fixes the brief |
| I am blocked on a fact nobody has | `BLOCKED` row plus owner-decisions row | Owner; coordinator routes and tracks |
| Another lane's handoff looks wrong | Board row `question` quoting both | Coordinator, rung four |

Post the row, keep working on something else.

## The precedence ladder

1. The stricter privacy, security or safety rule beats any schedule, convenience or preference.
2. A canonical product, privacy or architecture contract beats any plan, brief or roadmap.
3. The registry's declared ownership beats a lane brief; the brief is corrected.
4. Evidence beats assertion. An unrun gate stays unrun; an earlier gate never settles a later one.
5. The earlier board claim beats the later one; the later lane files a shared claim.
6. The lane that unblocks more other lanes goes first.
7. Otherwise it is the owner's; the coordinator names the missing fact rather than choosing.

Every decision that binds an agent other than the asker is a numbered `D-nnn` entry in
`DECISIONS.md` naming both positions, the rung, the acting agent and the board row it answers.

## Checkpoints

A checkpoint is a verification event with named stages and an exit condition. Typical ladder:

| Checkpoint | Purpose | Stages |
| --- | --- | --- |
| CP0 Clean page | Plan, registry, board, briefs installed; ownership overlap-free; build root fixed | gates |
| CP1 First slices | Every active lane has one vertical slice merged; validators green | gates, unit |
| CP2 Journeys | End-to-end behaviour verified by integration/UI suites; manifests applied | gates, unit, integration |
| CP3 Candidate freeze | Every in-scope task `SOURCE_READY` at one SHA; release build produced | all plus release build |
| CP4 Acceptance | Hardware, staging, performance, accessibility, external gates on the frozen SHA | gates, acceptance |
| CP5 Approval | Owner and custodian sign-off bound to the exact artifact | gates |

Protocol: call it (board row naming ready and not-ready lanes); merge serially in the order that
minimises shared-claim churn, running `gates` after each merge; apply shared claims and manifests
each as its own commit; run the stages once each, a failure stops and goes back to the owning lane;
record one `VERIFIED` or `BLOCKED` row per lane with log paths and one for the checkpoint; write the
changelog entry; push; tell lanes to rebase; hand the phase to the coordinator; promote canonical
state only where the registry's own terminal rule is met.

**What counts as green.** A stage passes only if it ran to completion with exit zero and executed a
non-zero number of tests read from its summary. Skipped tests, isolation-only passes and warnings
under warnings-as-errors are findings. Known-red items are attributed to a lane and recorded, and
become a stop once that lane's fix lands.

## Done, per layer

- **Lane deliverable**: source, failure-path tests, fixtures, manifests and handoff pushed on
  `lane/<key>`; board says `SOURCE_READY`.
- **Checkpoint**: every listed stage passed at one SHA on `main`; a `VERIFIED` row per lane with logs.
- **Canonical task**: its own registry's terminal rule, applied by the integrator on checkpoint
  evidence. Source, integration, device, review and release are separate gates.
- **Programme**: the final checkpoint closes for the stated scope.
