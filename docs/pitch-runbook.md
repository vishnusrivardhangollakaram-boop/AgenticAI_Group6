# Placement Application Copilot presentation runbook

The project brief allows **10 minutes for the pitch and 2 minutes for Q&A**. The core pitch runs **8:45**. Slides 12 and 13 support Q&A. The planned slots below leave **1:15** for handoffs, a slow run or navigation.

> Opening line: “I have 18 months of experience. The original job notice says 12 months, the update says 24, and the deadline is close. Which one do I trust?”

The three demo roles use illustrative data. The prototype shows how an advisory system can give a student the current evidence and route an exception to the placement office. Applications and official decisions remain with the institution and employer.

| Slide | Rubric attribute | Time | What to show | Owner |
|---|---|---:|---|---|
| 1 | Cover and speaker handoff | 0:20 | Establish the decision students face when a role changes while applications are open. | [Speaker name] |
| 2 | Problem Solving | 0:35 | Follow one student from checking a notice to asking the office. Separate a documented industry workflow from unmeasured workload and adoption assumptions. | [Name] |
| 3 | Innovation and Uniqueness | 1:30 | Show the current notice, the review-needed case, and the revised answer after an officer ruling. Cite the source at each decision. | [Name] |
| 4 | Technical Feasibility | 0:55 | Show the live-mode design: the model selects permitted lookups, code checks authority and rules, and the officer resolves only the assigned exception. Explain the demo mode actually used. | [Name] |
| 5 | Value Proposition | 0:55 | Report the actual synthetic results. Explain where the agent is useful and where a deterministic workflow already performs well. State what a campus pilot would measure. | [Name] |
| 6 | Market Potential | 0:45 | Start with MBA/PGDM placement offices. Distinguish the published sector count, the initial prospecting target and the planned paid cohort. | [Name] |
| 7 | Business Model | 0:45 | Present the campus licence as a testable price. Show the ₹54,000 delivery cost and ₹66,000 contribution under the model assumptions. | [Name] |
| 8 | Competitive Landscape | 0:45 | Show the closest incumbent and the manual alternative. Position the product as an evidence and exception workflow beside the campus portal. | [Name] |
| 9 | Scalability | 0:40 | Start with one round and one reviewer group. Explain campus boundaries, versioned imports, peak processing and release gates as proposed production work. | [Name] |
| 10 | Data Privacy and Security | 0:40 | Show what the prototype actually protects and what changes in a real deployment: role access, limited fields, logs, retention and a manual fallback. | [Name] |
| 11 | Regulatory Compliance | 0:55 | Identify final decision ownership, explain the approval path for real student data, and close with the proposed shadow pilot and decision criteria. | [Name] |
| 12 | Appendix: Course concepts | Q&A | Map evidenced Agentic AI concepts to implementation choices. | [Optional owner] |
| 13 | Appendix: Pilot design | Q&A | Defend the test design and the thresholds for expansion. | [Optional owner] |

## 90-second live demo

1. **0:00–0:20 — Student shortlist.** Open the preflighted app and check the three roles. Point out Product Analyst’s result and the source and deadline format.
2. **0:20–0:40 — Changed decision.** Open Business Analyst. Show the original 12-month notice and the 24-month governing amendment. The fictional student has 18 months. Say: “The result cites the amendment that changed it.”
3. **0:40–1:10 — Ask the office.** Open AI Strategy Associate. The notice allows an analytics course *or equivalent*. The case lacks a binding equivalency ruling for the student’s capstone. Move to the office view and record the positive, case-specific ruling.
4. **1:10–1:30 — Close the loop.** Return to the student view and show the updated decision and its evidence. Say: “The reviewer resolved the ambiguous clause. The rest of the criteria were checked again.”

Use a clean browser session for each rehearsal. Confirm the example-run state before screen sharing. If a network or model dependency stalls, switch promptly to the offline mode or the prepared deck visuals. Name the mode out loud. A configured, imported or published workflow proves setup. A successful run with a captured trace proves the model executed that example.

## Short answers for Q&A

**Where does agent behaviour add value?** The live planner can choose a permitted next lookup after observing the case evidence. The threshold and deadline checks are deterministic. If a strong fixed workflow delivers the same outcomes and time at lower cost on office data, use it for those cases.

**How do you handle a stale notice?** Keep publication date, version and scope with the rule. Fetch and compare the relevant amendment. When a governing version is established, cite it. Where authority conflicts, hold the recommendation and route the conflict to the office.

**Can the officer change a recruiter’s requirement?** The office records a scoped interpretation or verified fact within its authority. The prototype rechecks all remaining criteria. The existing institution and recruiter processes govern applications and final decisions.

**What did your evaluation actually show?** Use the current benchmark in [evaluation method](evaluation_method.md). State the exact case count, expected outcome labels and measured comparison. The test cases are synthetic. A published Dify run, office time savings and willingness to pay each need their own evidence.

**Why would a campus pay?** A proposed campus licence is viable if office handling time, follow-up burden and exception quality change enough to justify the price. The current business model is an assumption. A short shadow pilot and a purchase-owner interview are the next evidence.

**What about personal data and fairness?** The class demo uses synthetic records. Before any real pilot, the institution authorizes a narrow data scope, verifies the model provider’s handling, assigns reviewer access and sets retention and escalation ownership. Use only legitimately required criteria and offer a correction route.

**What would you do next week?** Recruit a campus office sponsor, secure authorization to review redacted or synthetic examples, and compare the current process, a strong rules workflow and the proposed adaptive workflow in shadow mode. Use the [pilot gates](pilot-test-plan.md).

## Ownership handover

The rubric evaluates the team and each student’s contribution. **Each student needs at least one attribute and their name must appear on that attribute’s slide.** A roster on the cover does not satisfy that requirement by itself. Fill the editable roster on slide 1 when names and roll numbers are available. Then match each assessed slide’s owner label to the roster and this runbook.
