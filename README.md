# Parallel Program

[![Skill](https://img.shields.io/badge/Claude%20Code-skill-6C4FF7)](https://code.claude.com/docs/en/skills)
[![Codex](https://img.shields.io/badge/Codex-skill-000000)](https://developers.openai.com/codex)
[![Validator](https://github.com/RNT56/parallel-program/actions/workflows/validate.yml/badge.svg)](https://github.com/RNT56/parallel-program/actions/workflows/validate.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-3776AB)](https://www.python.org/)
[![Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)](#requirements)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

**Run several coding agents on one repository at the same time without them colliding, losing state
between sessions, or guessing an answer that belongs to someone else.**

A skill for Claude Code and Codex. Give it a repository and a goal; it designs a programme of
concurrent **lanes**, installs the documents the agents run on, and hands you the exact first
message for each session.

It is a distillation of a real nine-lane, five-checkpoint programme that ran on a Swift 6
iOS/macOS monorepo with Codex and Claude Code sessions mixed. Every rule in it exists because
something went wrong without it, and [the lessons file](references/lessons.md) says what.

---

## The problem

Spawning ten agents on one repository fails in four predictable ways.

| Failure | What it looks like |
| --- | --- |
| **Collision** | Two agents edit one file. The second overwrites the first, silently. |
| **Amnesia** | Session 3 has no idea what sessions 1 and 2 decided. Their context is gone. |
| **Invention** | An agent needs a fact only you have, so it makes one up and builds on it. |
| **False green** | A validator scans zero files and reports success. Nobody notices for weeks. |

Conventions do not fix these. Structure and a validator do.

## The model in six sentences

1. A **lane** is the unit of ownership: one lead agent, one branch, one exclusive set of owner
   paths, one list of carried tasks. No tracked file is owned by two lanes, and a validator proves
   it against `git ls-files`.
2. **Three powers are held by three different agents.** The coordinator decides who and what next.
   The integrator decides whether it built and merged. You decide whether it ships and supply every
   fact an agent may not invent. The coordinator owns no source, runs no build, promotes no state.
3. **The board is the record.** One append-only file. A claim, a question, a blocker or a decision
   exists exactly to the extent that it is a row there.
4. **Lanes write; checkpoints verify.** Only the integrator's stage run turns `SOURCE_READY` into
   `VERIFIED`. Lanes mark their tests `NOT RUN`, and that is honest.
5. **One session is one named agent**, `ATLAS-2`. Its first act is reading its predecessor's
   handoff; its last act is writing its own, at a path derivable from its name.
6. **Blocked means keep going.** A lane posts the row, does the rest of its work, and hands off
   with the request open. It never idles and never guesses.

## Why the coordinator writes no code

This is the part people skip, and it is the part that matters.

An arbiter with a lane of its own has a stake in every dispute it settles. An arbiter that builds
spends its context on logs instead of on the picture no single lane has. So the coordinator owns
exactly the plan and the record, and the validator fails the build if it ever owns anything else.

That constraint also keeps it cheap. A coordination session reads the board, the open claims and
the newest handoffs, answers everything open, records what binds, and ends. Cheap enough to run
mid-phase, which is what removes most of the stall risk in a parallel programme.

## Install

```bash
git clone https://github.com/RNT56/parallel-program.git ~/.claude/skills/parallel-program
ln -s ~/.claude/skills/parallel-program ~/.codex/skills/parallel-program
```

The repository root *is* the skill directory, so the clone installs it. The symlink gives Codex the
same copy. Restart your session and the skill appears in both.

Verify:

```bash
python3 ~/.claude/skills/parallel-program/scripts/validate_program.py --self-test
```

## Use

Ask for it in either harness:

> Use `parallel-program` to turn this repository and my goals into a multi-agent execution
> programme. Install it and give me the first message for each session.

Or drive the scripts directly:

```bash
python3 scripts/scaffold.py --root /path/to/repo --init
```

That writes a starter `Docs/Execution/lanes.json`. Edit it — lanes, owner paths, agent names,
checkpoints, stage commands, machine constraints — then:

```bash
python3 scripts/scaffold.py --root /path/to/repo --apply-instructions
python3 /path/to/repo/Docs/Execution/validate_program.py
```

The scaffold never overwrites an existing file, so re-running it after adding a lane renders only
the new brief and leaves your live board and edited briefs alone.

## What lands in your repository

```
Docs/Execution/
├── lanes.json              the machine authority: who may write where
├── validate_program.py     fail-closed validator, with a mutation self-test
├── ROADMAP.md              scope, operating model, lanes, checkpoints, dependencies
├── PROGRESS.md             the board: append-only, parsed, three tables
├── ROSTER.md               agents, session names, inheritance, start messages
├── COORDINATION.md         three powers, the precedence ladder, which row to post
├── DECISIONS.md            numbered arbitration log, superseded but never edited
├── CHECKPOINTS.md          stages, protocol, what counts as green, build slots
├── CHANGELOG.md            written by the integrator from merges, never from memory
├── Lanes/                  _COMMON.md plus one brief per lane, paste-ready
├── Handoffs/               one directory per lane, one file per session
└── Manifests/              single-writer resources the integrator applies once
```

Plus a short block appended to `AGENTS.md` and `CLAUDE.md` pointing every agent at `_COMMON.md`.

## The validator

Ownership is enforced by a program, not a convention. It expands every owner glob against
`git ls-files` and fails on any file two lanes claim. It also checks that every carried task exists
and is carried once, that the coordinator owns no source and carries no task, that agent names are
unique, that every handoff file is named for its lane's agent, and that every board row parses and
names a known lane, checkpoint and state.

It fails closed. An unreadable registry, an unknown task ID or a row it cannot parse is an error,
never a skipped check. And because a check that cannot tell *held* from *never looked* is not a
check, it mutation-tests itself:

```console
$ python3 Docs/Execution/validate_program.py --self-test
Self-test OK: 17 mutations caught, clean fixture passes.
```

Each of those seventeen mutations breaks the programme in a specific way — two lanes owning one
file, the coordinator grabbing a source path, a task carried twice, a board row that does not
parse — and the self-test fails loudly if any of them stops being caught.

## Sizing

The number of lanes falls out of the code, not out of preference.

| Tier | Delivery lanes | Concurrent sessions | Phases | When |
| --- | --- | --- | --- | --- |
| S | 1–2 | 3–4 | 2–3 | One feature area, a refactor, a small product |
| M | 3–5 | 5–7 | 3–5 | A product with several surfaces or packages |
| L | 6–9 | 6–7 active | 5–6 | A whole-product release with hardware or external gates |

Never more than seven at once. The last phases of any release programme collapse to width one
anyway, because a single device, a single signing identity and your own attention serialise
everything.

**Build policy** is an explicit choice. `integrator-only` when builds share a machine, a disk, a
simulator or a build database. `lanes-focused` when each worktree builds cheaply and independently,
which is the normal case for web, Python, Go and Rust repositories.

**When not to use this.** One agent, one branch, no concurrency. A single session gains nothing
from a board and pays for it in ceremony. Use a plain plan and a handoff file.

## Works with `aft-gauntlet`

When a lane's deliverable is a product surface with subjective quality — a website, a game screen,
an app flow — generate that lane's execution prompt with the `aft-gauntlet` skill, if you have it,
and store the emitted prompt beside the brief. The Gauntlet's builders and critics become the lane's subagents and inherit the
file-ownership, board and handoff rules. Its terminal condition is the lane's `SOURCE_READY`;
verification is still the integrator's.

## Contents

| Path | What it is |
| --- | --- |
| [`SKILL.md`](SKILL.md) | The skill itself: workflow, rules, when to reach for what |
| [`references/lessons.md`](references/lessons.md) | Thirty lessons from the source programme, each with the failure it prevents |
| [`references/operating-model.md`](references/operating-model.md) | Roles, lane anatomy, board schema, precedence ladder, what counts as green |
| [`references/sizing.md`](references/sizing.md) | Tiers, phases, build policy, start order, fan-out limits |
| [`references/session-protocol.md`](references/session-protocol.md) | Naming, inheritance, first five and last three actions, handoff contract |
| [`references/harness-adapters.md`](references/harness-adapters.md) | Claude Code and Codex mechanics; mixed programmes |
| [`references/failure-catalog.md`](references/failure-catalog.md) | Twenty ways a programme lies to itself, and the question that catches each |
| [`assets/templates/`](assets/templates/) | Every rendered document |
| [`scripts/scaffold.py`](scripts/scaffold.py) | Renders the templates from the registry |
| [`scripts/validate_program.py`](scripts/validate_program.py) | The validator, copied into the target repository |

## Requirements

Python 3.10 or newer and `git`. No third-party packages, no network access, nothing to install.

## License

MIT. See [LICENSE](LICENSE).
