# Execution board: {{PROGRAM}}

Append-only. One row per state change. The validator parses every table; a row it cannot parse
fails the `gates` stage. States: `CLAIMED`, `IN_PROGRESS`, `SOURCE_READY`, `VERIFIED`, `BLOCKED`,
`DEFERRED`, `SUPERSEDED`. Lane keys and checkpoint IDs are those in
[`lanes.json`](lanes.json). The `ref` column holds a SHA, a branch, a session name such as
`{{FIRST_AGENT}}-1`, a handoff path or a log path; the note is one line. Sign rows with your session
name. Never edit or delete an earlier row; supersede it with a new one.

Row kinds beyond a state change: `question` and `conflict` rows are addressed to {{COORDINATOR}},
which answers on the board and records anything binding in [`DECISIONS.md`](DECISIONS.md);
`build slot` and environment rows are addressed to {{INTEGRATOR}}.

## Board

| Date | Lane | Checkpoint | State | Ref | Note |
| --- | --- | --- | --- | --- | --- |
{{BOARD_ROWS}}

## Shared claims

| Date | Lane | Path | Reason | Owner ack |
| --- | --- | --- | --- | --- |

## Owner decisions and facts requested

| Date | Lane | Needed | Register or plan entry | Status |
| --- | --- | --- | --- | --- |
