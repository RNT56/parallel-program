# Failure catalog

The recurring ways a programme lies to itself, for the coordinator's handoff reviews and the
integrator's checkpoint reading. Each names what it looks like in a handoff and the question to ask.

| Failure | What it looks like | Ask |
| --- | --- | --- |
| Blind check | A gate passed after scanning zero files, or skipped a path pattern | How many files did it scan? Was it mutation-tested? |
| Promoted by inference | "Verified" from a local run; device state from a simulator; external gate from a fixture | Which stage, which SHA, which log? |
| Zero-test pass | A stage exited zero with nothing executed | What is the executed count in the summary? |
| Skip as pass | A skipped or isolation-only test reported green | Which tests skipped, and why? |
| Phantom test | A registry names a test path that does not exist, so its validator proves nothing | Does the file exist and does it contain the case? |
| Assumed owner fact | A legal, product, signing, budget or approval fact filled in by the agent | Which custodian recorded it, where? |
| Silent scope change | A brief's task quietly narrowed, widened or swapped | Does the deliverable match the brief's sentence? |
| Chat-only agreement | Two sessions agreed something and no row exists | Which board row? |
| Edited history | A board row or decision changed in place | Which superseding row? |
| Tenth writer | The coordinator or integrator edited a lane's source to unblock it | Whose file is it? |
| Wrong holder | A lane asked the integrator for an ownership ruling, or the coordinator whether it built | Who decides this? |
| Unpushed work | A handoff names a head that is not on origin | `git branch -r --contains`? |
| Missing handoff | A session ended without one | Stop; the successor cannot start |
| Guess instead of row | A lane proceeded on an assumed answer to its own question | Where is the question row? |
| Stale plan | Brief, registry and roadmap disagree | Reconcile in one change; re-run validator |
| Fan-out overrun | More subagents than the ceiling; agents killed mid-edit | Which files were half-written? |
| Heavy build beside fan-out | A build ran while agents were spawning | Was the cache warmed serially first? |
| Flaky rerun | A test rerun until green | Record it; the owning lane fixes or justifies |
| Conflict outside owner paths | The integrator resolved a merge conflict in a file the lane does not own | Send it back |
| Secrets in the record | A token, credential or personal datum in a handoff, board or evidence file | Remove, rotate, record |
