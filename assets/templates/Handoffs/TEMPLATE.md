# Handoff

```
Agent: <SESSION-NAME>          Lane: <lane-key>          Phase: <n>
Predecessor: <SESSION-NAME or "none, first phase">
Branch and head: lane/<key> at <sha>, pushed: yes/no
Board rows appended: <dates and states>
```

## Outcome

Lead with the user-visible or operational behaviour now proven. Say which kind of evidence it is:
source, local test in this worktree, integrator stage, staging, device, release.

## Contracts and decisions

- Requirements:
- Architecture / decisions relied on (D-nnn):
- Invariants preserved:
- Explicit non-goals:

## Changes

| Path | Reason |
| --- | --- |
|  |  |

## Verification

| Test or check | Where it ran | Result | Log or artifact |
| --- | --- | --- | --- |
|  | my worktree / integrator stage / not run | PASS / FAIL / NOT RUN |  |

Cover failure paths: cancellation, timeout, retry, replay, restart, stale input, malformed or
oversized input, deletion, where relevant.

## Limitations and external gates

List every unrun gate exactly. Never infer one from another.

## Open shared claims

| Path | Owner | Posted | Landed |
| --- | --- | --- | --- |

Hunks as fenced diffs below.

## Owner facts requested

| Needed | Register or plan entry | Status |
| --- | --- | --- |

## Next action

The exact next task, file and first step, written for a reader with none of this context. If
blocked, the missing fact and its register entry instead.
