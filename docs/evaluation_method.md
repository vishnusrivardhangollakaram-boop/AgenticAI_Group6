# Evaluation of the Placement Application Copilot

The evaluation uses **14 synthetic scenarios** separate from the three cases in the demo. Expected dispositions are recorded in the fixture data. A separately specified scoring oracle in `evaluate.py` lists the exact notice IDs, revisions, statuses and deadline required for each case. Controllers never read the scoring oracle. These are regression scenarios developed with the prototype.

## Measured offline results

| Controller | Correct outcome | Correct notice versions | Correct deadlines | Correct review routing | Accepted lookups | Unsupported ready verdicts |
|---|---:|---:|---:|---:|---:|---:|
| Fixed checklist | 14/14 | 14/14 | 14/14 | 14/14 | 46 | 0 |
| Optimized rules | 14/14 | 14/14 | 14/14 | 14/14 | 43 | 0 |
| Adaptive simulation | 14/14 | 14/14 | 14/14 | 14/14 | 43 | 0 |

- **Fixed checklist** uses the same evidence tools and adjudication rules, but reads the profile first and completes the available checklist.
- **Optimized rules** checks the notices first and stops when the verified evidence is sufficient. It represents a stronger, deterministic alternative with no model.
- **Adaptive simulation** chooses among the same tools based on evidence in the case. This controller is also deterministic. It saves three calls against the fixed checklist and **ties the optimized rules controller**.

For a closed deadline or conflicting current notices, a notice-first lookup avoids collecting unnecessary profile evidence. When numeric experience is insufficient, stopping early avoids an irrelevant equivalence check. The two stronger offline workflows already deliver these benefits. The results establish expected behavior on the scenario set. They do not establish a performance advantage for an LLM, staff time savings, or adoption.

For notice accuracy, the scorer checks the full set of cited notice IDs, revisions, and governing, superseded, or conflicting statuses. It scores the deadline separately. Exactly two cases require escalation by the engine, and all modes identified both without escalating any of the other 12. An unsupported ready verdict is any “ready” result where the scenario expects a different outcome. Accepted lookups are counted from the execution trace. Rejected tool attempts are outside that count.

[Case-level offline data](evaluation_offline.csv) retains expected and observed values for each case, including run errors. [Officer decision checks](evaluation_review.csv) cover confirmed equivalence, rejected equivalence, and additional evidence requested. All three produced the expected next state while preserving the governing notice and investigation trace and attaching the officer decision citation.

## Reproduce and extend

```bash
python evaluate.py --csv docs/evaluation_offline.csv --review-csv docs/evaluation_review.csv
python -m unittest discover -s tests -v
```

Run the same cases against the published Dify workflow with the opt-in `--live` flag. Configure `DIFY_API_BASE_URL` and `DIFY_API_KEY` first. Live output is a separate **Dify model** group with per-case latency and token count where the API reports them. Do not substitute simulation runs for live results. The exported workflow can be verified locally with its stub planner, which checks the graph and guard logic rather than model accuracy.

For a pilot, introduce cases designed by another team or a placement coordinator after freezing the prompt. Replay representative real exceptions only after redacting or obtaining permission for the necessary records. Use the same evidence tools for the optimized rules controller and live Dify. Have an officer validate the expected dispositions and source versions before opening either result. Compare unsafe readiness, missed escalations, active handling time, and cost per resolvable case. Record failures and inconclusive cases separately.
