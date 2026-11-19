# Placement Application Copilot | Business evidence and pilot plan

This is a classroom prototype with fictional campuses, roles and student records. Public examples establish that the workflow exists. Pricing, adoption, servicing costs and staff savings are hypotheses for a pilot.

## The buyer and the problem

- **User:** a final-year MBA or PGDM student trying to decide which campus roles to pursue this week and what to do before each deadline.
- **Reviewer:** the placement office officer responsible for exceptions, corrections and conflicting evidence.
- **Buyer:** head of career services or placement at an Indian MBA/PGDM institute with recurring campus hiring rounds, sanctioned digital notice distribution and a designated exception reviewer.
- **Observed workflow:** The International Institute of Management Studies’ public policy manual says recruiters inform the institute of role descriptions and eligibility norms. These sources establish the rules and institutional responsibility. They do not measure how often notices change, student confusion, staff workload, or willingness to pay. The prototype uses original synthetic policies only.
- **Value hypothesis:** when a role notice changes or an equivalency is unclear, give the student a dated, cited next action and give the office a case with verified evidence. The original notice remains available for audit, and the published portal remains the authoritative place to apply.

Sources: [International Institute of Management Studies policy manual, §18](https://iimspune.edu.in/wp-content/uploads/2024/09/Institutes-policy-Manual.pdf).

## Positioning and the competitive landscape

**Positioning:** a student-facing eligibility explanation and human exception workflow beside the campus's existing job portal. The proposition to validate is its combination of notice version comparison, evidence for each decision, and a student-visible outcome after a placement officer reviews an exception.

| Alternative | Documented strength | Pilot comparison |
|---|---|---|
| Superset TnpSuite and Launchpad+ | Campus eligibility rules, job distribution, applications, interviews, offers, preparation, and existing system integrations. | Closest incumbent. Ask whether the campus already has version-visible explanations, dispute resolution, and student-visible review. Explore integration or a cheaper rules-only configuration before proposing an additional purchase. |
| Unstop | Campus recruiting, early talent outreach, branded engagements, assessments, interviews and offers. | Strong employer recruitment option. Compare who operates the service and how a specific student resolves an institution-specific exception. |
| Handshake | Career discovery and configurable candidate qualifications, including major and minimum GPA. Its employer documentation describes qualifications as optional and says adding them does not prevent applying. | Compare advertised qualifications and applicant filtering with rule provenance and officer correction for one campus's controlled drives. |
| Campus team, notices and email | Already trusted, immediately available and flexible for unusual cases. | Reference baseline for time, missed updates, repeated questions and consistency of next steps. |
| Placement Application Copilot | Proposed focus: tracks governing notice versions, checks structured facts, and creates an evidence-backed review. | Early prototype with synthetic records. Campus integration, cost at scale and paid demand are unverified. Incumbents could reproduce the workflow. |

Public documentation supports the stated features. An unlisted feature should be treated as unknown. Vendor-reported performance is excluded from the prototype's metrics.

Sources: [Superset for universities](https://joinsuperset.com/university), [Unstop campus hiring](https://unstop.com/employers/campus-hiring?openmodal=true), [Handshake candidate qualifications](https://support.joinhandshake.com/hc/en-us/articles/218693208-Understanding-Job-and-Candidate-Qualifications).

**Industry precedents:** Google Cloud profiles Beyond 12's personalized student coaching and Tabiya's Compass, which elicits skills and experience to match people to opportunities. NTU Singapore's Lyon Housing chatbot is a useful adjacent precedent for campus staff handoff. These inspire the student and office workflow. Their performance does not predict this product's results.

Sources: [Google Cloud's industry use-case catalog](https://cloud.google.com/transform/101-real-world-generative-ai-use-cases-from-industry-leaders), [Google Cloud student coaching and opportunity matching](https://cloud.google.com/transform/gen-ai-economic-opportunity-google-org-nonprofit-ai-incubator?e=48754805v), [NTU Singapore customer case](https://cloud.google.com/customers/nanyang-technological-university?hl=ja).

## Market and commercial assumptions

The Ministry of Education's **AISHE 2023–24** report counted **363 registered stand-alone PGDM institutes**, of which **235 responded**. This is a focused sector reference point with a clearly defined institution category. It excludes university MBA programmes. The count does not establish buyer fit, access, price or adoption.

| Layer | Basis | Annual equivalent |
|---|---|---:|
| Sector reference | 363 registered stand-alone PGDM institutes, AISHE 2023–24, Box 5, printed p. 20 | No validated revenue estimate |
| Initial prospecting target | 30 campuses × illustrative ₹1,20,000 annual campus license | ₹36,00,000 at full conversion |
| First paid cohort scenario | 10 campuses × the same illustrative license | ₹12,00,000 ARR |
| First stage | Two placement offices, one placement round each | Adoption and budget discovery |

Identify 30 named prospects from official institute lists, then qualify them on recurring recruiter notices, a named reviewer, export/API rights, willingness to share synthetic or redacted process artifacts, and a decision maker with budget. The 30 and 10 above are planning assumptions. A signed pilot, contact list or pipeline should only be shown once obtained.

**Business model:** annual institution license with a usage allowance, offered free to the campus's students. After paid adoption, test an optional integration fee for unusually complex onboarding. Test the assumed price in buyer interviews before making revenue projections. Revenue should arise from the institution receiving measurable process value rather than selling student records or charging for access to a role.

| Annual delivery economics, assumed | Per campus |
|---|---:|
| License for up to 10,000 application checks per year | ₹1,20,000 |
| 10,000 checks × ₹3 delivery cost per check | ₹30,000 |
| Campus support and allocated hosting | ₹24,000 |
| Delivery cost total | ₹54,000 |
| Contribution before acquisition, fixed development, tax and other overhead | ₹66,000 / 55% |

At the same check volume, ₹1 / ₹3 / ₹6 per check gives about **72% / 55% / 30%** modeled contribution. The ₹3 assumption bundles variable model and workflow delivery costs. It must be replaced with measured calls, provider prices, and usage by case type. Human reviewer labor belongs in the campus value model unless the vendor provides it.

An illustrative office-only break-even at ₹500 per hour is **240 hours saved per campus per year**. For example, 2,400 questions would need a net six-minute saving each. Include any additional verification and exception-review time in the measured net saving. Fewer repeat questions and deadline misses can add value, but report them separately from proven labor savings.

Source: [AISHE 2023–24 official report, PDF p. 39, Box 5](https://cdnbbsr.s3waas.gov.in/s392049debbe566ca5782a3045cf300a3c/uploads/2026/07/202607131602421770.pdf#page=39). [Ministry release and survey limitations](https://www.pib.gov.in/PressReleasePage.aspx?PRID=2282525&lang=1&reg=48).

## Evidence to collect in the first pilot

1. Interview two placement heads, two coordinators and six students. Ask each to walk through an actual, redacted case. Ask what the last amended role notice changed, how many enquiries it created, how long the office took to resolve them and which authority made the final determination.
2. Measure a rules-only workflow and the adaptive workflow on the same labeled cases. Include contradictory notices, missing facts, expired deadlines, fixed thresholds and ambiguous equivalencies. Score correct disposition, correct source/version, missed escalation and unnecessary escalation. Log latency and variable cost where available. Report the exact denominator.
3. Test a manual office baseline with timing for active handling time and wait time separately. Measure experiment groups of similar difficulty. Synthetic correctness scores do not demonstrate office time savings.
4. Interview the actual purchasing authority about integrations, willingness to pay, the procurement calendar and required permissions. Ask what measurable outcome would trigger a renewal.
5. Take a deliberate go/no-go decision: validate that the adaptive workflow adds something beyond a version-aware rules engine, and that the incremental value exceeds the operating and integration costs.

## Production scalability and trust

- Keep the campus portal as source of record. Ingest approved notices with issuer, publication date, effective time, scope and supersession metadata. Bind each decision to a notice version and profile snapshot. Deduplicate by campus and source identifier, and refresh affected cases when a notice changes.
- Start with one cohort and one portal export. Roll out a common schema with campus-specific rules and queue/notification settings. Partition data by campus and student, reuse embeddings or cached retrieval within a campus where safe, and process peak-day runs with queues, budgets and monitoring. This is a production plan.
- Present the current notice, source date, deadline with timezone, and a route to correct factual errors. Human officers handle ambiguous equivalence and disputed evidence. Official recruitment decisions stay with the authorized campus or employer. Do not infer suitability from names, caste, gender, disability, nationality or other unapproved attributes.
- The classroom demo uses synthetic records only. For an authorized real pilot, identify the campus and vendor data roles and approved processing grounds, display a clear purpose notice, restrict reviewer access to assigned cases, minimize fields in the prompt, avoid sending CVs and transcripts when a verified field suffices, and maintain a retention schedule, access logs, correction route and incident procedure. Verify provider data handling, retention, contract and applicable transfer conditions.
- **India DPDP status, checked 19 November 2026:** the Digital Personal Data Protection Act, 2023 and the Digital Personal Data Protection Rules, 2025 have phased commencement. MeitY's November 2025 Act commencement notice places the principal processing duties, including sections 3–5, most of 6, and 7–17, at 18 months from publication. Compare the actual deployment date with the Gazette and current guidance, along with applicable campus policies and other obligations. Prototype controls are not a certification or a determination of compliance.

Sources: [DPDP Act, 2023](https://www.meity.gov.in/static/uploads/2024/02/Digital-Personal-Data-Protection-Act-2023.pdf), [Act commencement Gazette G.S.R. 843(E)](https://www.meity.gov.in/static/uploads/2025/11/c56ceae6c383460ca69577428d36828b.pdf), [DPDP Rules, 2025 and corrigendum](https://www.meity.gov.in/documents/act-and-policies/digital-personal-data-protection-rules-2025-gDOxUjMtQWa?pageTitle=Digital-Personal-Data-Protection-Rules-2025&trk=article-ssr-frontend-pulse_little-text-block).
