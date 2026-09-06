# Lane handoffs

One directory per lane key, one file per session, named for the session:

```
Docs/Execution/Handoffs/<lane-key>/<SESSION-NAME>.md
```

`{{FIRST_AGENT}}-1` writes `<its lane>/{{FIRST_AGENT}}-1.md`; its continuation `{{FIRST_AGENT}}-1b`
writes beside it; the next phase's `{{FIRST_AGENT}}-2` reads them both. The path is derivable from
the name, which is what lets the next session find its parent without searching. Agent names,
phase digits and inheritance order are in [`../ROSTER.md`](../ROSTER.md).

**Every session writes one, without exception.** A session that ran out of context mid-edit is
exactly the one whose successor needs the record most; "nothing to hand off" is itself the finding.

Use [`TEMPLATE.md`](TEMPLATE.md). Tests a lane wrote but could not run are listed `NOT RUN`; the
integrator fills in the result and log path after the stage runs. Shared-claim hunks are attached
as fenced diffs inside the handoff. No secrets, credentials, personal data or raw third-party
payloads.
