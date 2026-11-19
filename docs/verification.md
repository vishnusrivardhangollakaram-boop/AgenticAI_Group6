# Verification and evidence status

## Verified locally

- **12 application, engine and evaluation tests:** includes notice precedence, evidence access, current notice citations, shortlist review and reset, a review that survives safe rechecks, and tests that catch false readiness or missed review.
- **6 Dify workflow and API tests:** exercise the exact exported node functions on all 17 synthetic cases, alternate lookup orders, invalid planner output, mocked API output and truncated or failed streams.
- **Offline evaluation:** each controller returned the expected outcome, notice versions, deadline and review routing on 14/14 scored cases. Fixed checklist used 46 accepted lookups. Optimized rules and adaptive simulation used 43 each. No unsupported ready result, missed escalation or execution error occurred.
- **Human review tests:** accepted, rejected and request-more-evidence cases passed 3/3.
- **Offline storyboard:** the embedded synthetic snapshots come from the same engine. Browser-script interactions were exercised with a local document simulator.
- **Presentation:** 13 slides, 16:9, each inspected after render, with editable content, presenter notes and placeholders.

## Separate checks for live use

1. Connect a supported model in Dify. Import and publish the workflow, then run the three hero case IDs in Dify. Verify the returned trace and capture the model name and run IDs.
2. Configure the workflow app key on the Streamlit server. Run the shortlist in Dify mode and repeat the human handoff.
3. Run the matched assessment in live mode to measure actual outcomes, tool counts, latency and tokens. Report failures and do not add live runs to the offline score.
4. Before a real campus trial, validate case handling and notice authority with a coordinator, confirm data permissions, and test usability and access controls in the intended environment.

Headless Chromium could not start in the build sandbox. The Streamlit test exercised the UI through Streamlit's developer test interface. No real placement records, user accounts or external workflow actions were used.
