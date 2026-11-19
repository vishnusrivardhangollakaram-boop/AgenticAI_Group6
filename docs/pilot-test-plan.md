# One-campus shadow pilot

**Pilot question:** Does the evidence-first workflow help a placement office resolve queries about changed or ambiguous eligibility rules with the same or better decision quality and lower handling effort?

**Pilot proposal only.** The classroom prototype is synthetic. No pilot, stakeholder interview, paid demand or production performance is claimed.

## Sponsor and weeks

- **Sponsor:** a placement head authorized to approve the test, nominate two reviewers and confirm which office can resolve a recruiter interpretation.
- **Week 1:** review the campus notice process, collect permissioned redacted examples, agree the labels and thresholds, and verify the approved data path. Keep official applications on the campus portal.
- **Weeks 2–3:** run 50 cases in shadow mode. Use 20 straightforward published-rule cases, 15 amended/deadline cases and 15 ambiguous or missing-evidence cases. Log source version and the final disposition for each. These counts define a proposed mix and do not represent campus demand.
- **Week 4:** adjudicate disagreements, calculate time and cost, and review the result with the buyer. Decide whether to end, continue rules-only, revise the workflow or run a larger pilot.

One documented example confirms that the International Institute of Management Studies publishes a placement policy with recruiter eligibility norms. Use it to explain the workflow premise. It gives no estimate of amendment frequency, response times or buyer need. Superset’s public description makes its campus platform a relevant incumbent. Test whether an office already solves the proposed problem in its existing setup. [IIMS policy manual, §18](https://iimspune.edu.in/wp-content/uploads/2024/09/Institutes-policy-Manual.pdf) and [Superset for universities](https://joinsuperset.com/university).

## Comparison and measurement

Prepare versioned sources and a minimum profile record per case. Assign an expected disposition, governing source and appropriate escalation before running any tool. An officer with the relevant policy context resolves label disagreements. Give the same records to the existing staff process, a version-aware rules workflow, and the adaptive workflow. Use a balanced assignment across reviewers and matched case difficulty to reduce familiarity and ordering effects. Separate system execution time, active staff handling time and time awaiting a reply.

| Measure | Definition | Proposed gate |
|---|---|---|
| Unsupported ready recommendation | System indicates ready without the required governing source and verified facts | Zero observed in the shadow set. Review each candidate failure. |
| Missed required escalation | A labelled review-required case reaches a conclusive automated disposition | Zero observed in the shadow set. Review each candidate failure. |
| Governing citation accuracy | Decision references the correct applicable notice version when a governing source exists | At least 95%, with the numerator, denominator and each material error reported. |
| Median active office handling time | Hands-on time to verify, draft and approve the answer, including exception work | At least 20% lower than the office comparison process. Review results separately for routine and exception cases. |
| Incremental value | Adaptive workflow’s handling effort and evidence quality compared with the strong rules workflow | Adaptive achieves a measurable benefit on the exception cases after accounting for provider and review costs. |
| Buyer case | Measured usage and effort converted to annual value, with buyer feedback on advance, revise or stop | Named owner confirms the threshold for a paid trial. Record scope limits and the reason for the decision. |

A small test set can miss failure modes. Treat the quality thresholds as minimum pilot gates and use a larger representative set before a production rollout. A missed escalation or unsupported ready result blocks advancement until corrected and retested. If a rule-based solution meets the need at lower cost, use it for straightforward cases.

## Approval and limits

Start with synthetic records. A real pilot needs permission to use specific redacted records, a clear purpose, data access and retention limits, and a path for corrections. The placement policy, the recruiter’s governing documents and the institution’s official channels decide eligibility. A shadow output goes to pilot reviewers for assessment.

For a real India deployment, review applicable DPDP obligations and commencement dates, authorised campus and vendor roles, provider retention/sharing terms, incident response and who can correct records. The central commencement notice defines phases. Check the deployment date and any subsequent notifications with the institution before using real records. [MeitY Gazette, Act commencement G.S.R. 843(E)](https://www.meity.gov.in/static/uploads/2025/11/c56ceae6c383460ca69577428d36828b.pdf) and [DPDP Rules, 2025](https://www.meity.gov.in/static/uploads/2025/11/53450e6e5dc0bfa85ebd78686cadad39.pdf).

See [business evidence](business-evidence.md) for the published market denominator, source links and licence sensitivity. Replace projected cost and time inputs with measured pilot data.
