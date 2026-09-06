# Standing rules for every lane (read once, then your lane brief)

You are the lead agent of one lane of the [roadmap](../ROADMAP.md). The registry
[`lanes.json`](../lanes.json) is the authority for what you own; your brief repeats it.

**Your name is your address.** The owner starts you as `<AGENT>-<phase>`, for example
`{{FIRST_AGENT}}-1`; a letter suffix such as `{{FIRST_AGENT}}-1b` means the same lane and phase
continued in a new session. [`../ROSTER.md`](../ROSTER.md) maps every agent to its lane, says which
handoffs you inherit and in what order, and defines the handoff you must write before your session
ends. Your first act is reading your predecessor's handoff; your last act is writing your own, and
that is mandatory even if the session achieved nothing.

1. **Read order before the first edit:** the repository's root agent instructions, this file, your
   brief, any nested instructions for the paths you will touch, the task entries you carry, and the
   tests next to the code. Then `git status --short` and `git log --oneline -5`.
2. **Work in your own worktree on your own branch:**
   `git worktree add {{WORKTREE_ROOT}}/<lane> -b lane/<key> origin/main`. Never create a worktree in
   a purgeable scratchpad.
3. **Build policy `{{BUILD_POLICY}}`.** {{BUILD_POLICY_TEXT}} Write the tests anyway; mark them
   `NOT RUN` in your handoff unless {{INTEGRATOR}} ran them in a stage. If you are stuck without
   compile feedback, post a `build slot` row and continue with something else.
4. **{{COORDINATOR}} coordinates; ask it rather than guessing.** You may ask a peer lane directly
   for a plain fact. Anything that binds another lane goes through {{COORDINATOR}} and onto the
   board: a decision, a commitment, an ownership change, an interpretation of a contract. Post a
   `question` or `conflict` row, keep working on something else, and read the answer as a board
   row and a numbered entry in `../DECISIONS.md`. {{COORDINATOR}} settles ownership and order;
   {{INTEGRATOR}} settles whether something built; only the owner settles an owner fact. Never idle
   waiting, and never assume an answer.
5. **Stay inside your owner paths.** Anything else is a shared claim: write the hunk into your
   handoff, add a row under "Shared claims" in `../PROGRESS.md`, do not edit the file. Changes to
   manifest-governed resources go into `../Manifests/<lane>.md`.
6. **Push after every coherent step:** `git push -u origin lane/<key>`. Unpushed work is at risk.
7. **The board is the record.** Append rows; never edit old ones. `CLAIMED` when you start (say
   which sub-team owns which files), `SOURCE_READY` when source, tests, fixtures, manifests and
   handoff are pushed, `BLOCKED` with the exact missing fact when you cannot proceed.
8. **Handoff per session** at `../Handoffs/<lane-key>/<SESSION-NAME>.md` using
   `../Handoffs/TEMPLATE.md`. Write it before you run out of room, not after.
9. **Subagents:** at most three at once, each confined to a file set you name in the prompt (the
   prompt, not a scratch file, carries the brief; a subagent killed by a session limit is resumed by
   message). Critics do not edit what they judge.
10. **Repository hazards that bite every lane:** {{HAZARDS}}
11. **Never** invent an owner fact, promote a canonical state, use real personal or production data
    as a fixture, commit secrets, run destructive git, or reactivate a deferred lane.

Machine notes: {{MACHINE_NOTES}}
