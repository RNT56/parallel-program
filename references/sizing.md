# Sizing a programme

The number of lanes is not a preference; it falls out of the code and the goal.

## Step 1: find the ownership sets

List the top-level areas the goal touches (packages, modules, apps, services, docs, CI). Merge two
areas into one set when they are compiled together and a second writer in one breaks the other
(shared packages, a schema and its consumers, a router and its routes). Split a set when its work
is large enough to occupy an agent for a phase and its files are disjoint from the rest. Each
resulting set that carries real work is a candidate delivery lane.

Then name the **shared files** every set will want a hunk in, and give each a fixed owner.

## Step 2: cap by sessions

| Tier | Delivery lanes | Concurrent sessions | Phases | When |
| --- | --- | --- | --- | --- |
| S | 1–2 | 3–4 (coordinator, integrator, lanes) | 2–3 | One feature area, a refactor, a small product |
| M | 3–5 | 5–7 | 3–5 | A product with several surfaces or packages |
| L | 6–9 | 6–7 active, rest STANDBY or DEFERRED | 5–6 | A whole-product release with hardware or external gates |

Never run more than seven sessions at once; a human cannot supervise more, and the last phases of
any release programme collapse to width one anyway. Extra candidate lanes become `STANDBY` (joins
in a later phase) or `DEFERRED` (owner paused it; validators keep running; nothing depends on it).

The coordinator and integrator are always separate sessions, even at tier S. At tier S they are
short: a coordinator session is minutes; an integrator session is one checkpoint.

**When not to use this skill:** one agent, one branch, no concurrency. A single session gains
nothing from a board and pays for it in ceremony. Use a plain plan and a handoff file.

## Step 3: fix the phases

A phase is a checkpoint window. Place a checkpoint at each natural verification plateau:

- CP0 always: the plan is installed and ownership is overlap-free.
- One checkpoint after the first vertical slice from every lane (catches integration drift early).
- One per additional verification tier the goal needs (integration/UI suites, release build,
  hardware or staging acceptance, external approval).

Three to five is typical. Fewer than three means lanes go too long without a merge; more than six
means the checkpoints themselves become the schedule.

## Step 4: choose the build policy

| Policy | Lanes may | Integrator does | Choose when |
| --- | --- | --- | --- |
| `integrator-only` | Run static validators and `git diff --check` only; write tests marked `NOT RUN`; request build slots | Every build and test, serially, behind a lock, at checkpoints and in granted slots | Builds share a machine, a disk near full, a simulator, a device, a build database, or a licence |
| `lanes-focused` | Run focused unit tests inside their own worktree; still mark integration suites `NOT RUN` | The full stage run at checkpoints; only that promotes to `VERIFIED` | Each worktree builds cheaply and independently (typical web, Python, Go, Rust repos) |

Under both policies the handoff distinguishes "I ran it in my worktree" from "the integrator ran it
at a checkpoint", and only the second is `VERIFIED`.

## Step 5: order inside a phase

1. Coordinator, to brief on what the last checkpoint changed (skip in phase 1).
2. The lane most others depend on (schema, platform, shared models, design system).
3. Short dependency-free repairs (a red validator, a broken gate), because nothing waits on them
   and they unblock the checkpoint.
4. The remaining delivery lanes.
5. The integrator, only for build slots until the checkpoint opens.

Write the order and the reason into the roadmap; the next phase's coordinator re-derives it from
the dependency table.

## Fan-out limits inside a session

- At most four lane leads started from one owner session.
- At most three subagents per lead, each confined to a named file set, brief in the prompt.
- Critics do not edit what they judge. Builders never grade themselves.
- Warm shared caches serially before any fan-out; never run a heavy build beside one.
