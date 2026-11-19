# Deployment verification

Verified on 19 November 2026 with synthetic classroom cases only.

| Surface | Where | What was observed |
|---|---|---|
| GitHub | [AgenticAI_Group6](https://github.com/vishnusrivardhangollakaram-boop/AgenticAI_Group6) | Project source and importable Dify workflow on main. |
| Streamlit Community Cloud | [Placement Application Copilot](https://placement-copilot-group6.streamlit.app/) | Hosted Case simulation returned the three expected outcomes. A synthetic equivalence ruling updated AI Strategy Associate to Ready to apply in that browser session. |
| Dify Cloud | [Published Dify workflow](https://udify.app/workflow/bmkjQivJGTtu816q) | PC-101 returned ready and PC-102 returned not_ready in Studio. After publishing, the web app returned needs_review for PC-103. |

The Dify smoke tests use a model. They are separate from the 14-case deterministic benchmark. The public Streamlit smoke test used Case simulation. Running a live model from Streamlit also requires the app-specific Dify Service API key in Streamlit server Secrets, as explained in the [deployment runbook](deployment.md).

Dify Cloud requires unique output names across terminators. The deployed workflow and the bundled export use `result_json` for the first exit and `result_json_2` through `result_json_7` at the remaining exits. The Streamlit client verifies the selected result against the synthetic evidence trace.
