# Coordination decisions: {{PROGRAM}}

Append-only. {{COORDINATOR}} records every arbitration that binds an agent other than the one who
asked, and every amendment it makes to the roadmap, the registry or a lane brief. Numbered
`D-nnn`, newest at the bottom. A decision is superseded by a later entry that names it, never by
editing it.

Each entry names the two positions, the rung of the precedence ladder in
[`COORDINATION.md`](COORDINATION.md) that settled it, the agent that must act, and the board row it
answers. A decision that needs the owner is recorded as escalated, with the exact missing fact,
and stays open until the owner supplies it.

---

## D-001 — Lanes coordinate through {{COORDINATOR}}, not with each other

Date: {{DATE}}. Rung: owner directive, above the ladder. Acts: every agent.

Lanes may exchange facts directly. Anything that binds another lane goes through {{COORDINATOR}}
and onto the board: a decision, a commitment, an ownership change, a schedule change, an
interpretation of a contract. The reason is durability rather than authority: two live sessions
can agree on anything, and the agreement disappears with their context windows, while the next
session inherits only the board and the handoff chain.

## D-002 — Three powers are held separately

Date: {{DATE}}. Rung: owner directive, above the ladder. Acts: every agent.

{{COORDINATOR}} decides who and what next and owns no source, no task, no build.
{{INTEGRATOR}} decides whether it built and merged, and alone promotes state on evidence. The
owner decides whether it ships and supplies every fact an agent may not invent. An agent that asks
the wrong holder is told which one to ask.
