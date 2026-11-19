# Placement Application Copilot presentation runbook

The project brief allows **10 minutes for the pitch and 2 minutes for Q&A**. The core pitch runs **9:00** across slides 1–14. Slides 15 and 16 support Q&A. The planned slots leave **1:00** for handoffs or navigation.

> Opening line: “I have 18 months of experience. The original job notice says 12 months, the update says 24, and the deadline is close. Which one do I trust?”

The three demo roles use illustrative data. The prototype shows how an advisory system can give a student the current evidence and route an exception to the placement office. Applications and official decisions remain with the institution and employer.

| Slide | Rubric attribute or role | Time | What to show | Owner |
|---|---|---:|---|---|
| 1 | Cover and speaker handoff | 0:20 | Establish the decision students face when a recruiter changes a published requirement. | [Speaker name] |
| 2 | Problem Solving | 0:35 | One student has 18 months of experience. Show the original 12-month notice and the 24-month amendment, plus why the office may need to help. | [Name] |
| 3 | Innovation and Uniqueness | 0:35 | Contrast separate notice searches and follow-ups with a single cited next step and an evidence-ready handoff. The campus portal remains the source of record. | [Name] |
| 4 | Student workspace demo | 0:55 | Show all three outcomes for the same synthetic profile. Open the governing amendment and the unresolved equivalence case. | [Demo presenter] |
| 5 | Technical Feasibility | 0:45 | Step through a bounded read-only tool loop, code-owned decisions, case replay and fallback. Name the runtime actually used. | [Name] |
| 6 | Placement office handoff demo | 0:40 | Resolve only the capstone equivalence, record the evidence, and show the rest of the criteria being rechecked. | [Demo presenter] |
| 7 | Value Proposition | 0:50 | Show 14/14 correct for each offline approach, lookup counts of 46/43/43 and zero unsupported ready outcomes. The adaptive simulation tied strong rules. A campus pilot would measure quality and active handling time. | [Name] |
| 8 | Market Potential | 0:40 | Distinguish the published standalone PGDM institute count from the initial prospecting target and paid cohort scenario. Name the campus placement head as the buyer. | [Name] |
| 9 | Business Model | 0:45 | Present ₹1.20 lakh licence, ₹54,000 annual delivery cost and ₹66,000 contribution as modelling assumptions. The time-saving threshold is a hypothesis. | [Name] |
| 10 | Competitive Landscape | 0:40 | Show Superset, Handshake, Unstop and the manual campus workflow. Explain the proposed role beside the placement portal and the risk of incumbent parity. | [Name] |
| 11 | Scalability | 0:35 | Show staged deployment from a synthetic cycle to a one-campus shadow pilot and multi-cycle rollout. Describe proposed scoping, peak queues and monitoring. | [Name] |
| 12 | Data Privacy and Security | 0:40 | Distinguish synthetic, allowlisted workflow controls from real-pilot controls for identity, data minimization, access logging and retention. | [Name] |
| 13 | Regulatory Compliance | 0:35 | Identify institutional and recruiter decision ownership, the correction route, and the data and authority checks for a real pilot. | [Name] |
| 14 | Close and proposal | 0:25 | Ask for one authorized shadow pilot with 50 cases over four weeks. Explain how the team would decide whether to continue. | [Speaker name] |
| 15 | Appendix: Course concepts | Q&A | Map Agentic AI concepts to verified project behavior and explain deliberate omissions. | [Optional owner] |
| 16 | Appendix: Evaluation and pilot evidence | Q&A | Defend the test design, runtime evidence and thresholds for expansion. | [Optional owner] |

## 95-second demo across slides 4 and 6

**Slide 4 (0:55).** Open the preflighted student workspace in the selected mode. Spend the first 15 seconds on the three-role shortlist and the cited Product Analyst result. Spend 20 seconds comparing Business Analyst's original 12-month notice and governing 24-month amendment against the student's 18 months. Use the remaining 20 seconds to show that AI Strategy Associate needs an analytics capstone or verified equivalent and that no decision is on file for this student's capstone.

**Slide 5 (0:45, architecture explanation).** Trace that unresolved requirement through the permitted evidence lookups and authoritative rule check before moving to the office workspace.

**Slide 6 (0:40).** Spend about 25 seconds selecting the pending AI Strategy Associate case and recording “Verify as equivalent” with an evidence note. Return to the student view in the final 15 seconds and show the updated decision. Say: “The officer resolved the ambiguous requirement. The workflow checked the rest of the criteria again.”

Use a clean browser session for rehearsal. Confirm the example state before screen sharing. If the network or model stalls, switch to the checked offline demo or the deck visuals and name the mode. An imported or published workflow shows setup. A successful run with a captured trace shows model execution for that case.

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
