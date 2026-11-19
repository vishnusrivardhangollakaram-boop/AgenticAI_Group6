# Course concepts and design choices

Page numbers refer to the 195-page Agentic AI – Copilot to Autopilot course PDF.

| Concept | Where it appears in the project | Course PDF |
|---|---|---|
| Generative AI and agentic AI | The live Dify model selects read-only evidence lookups. A model-generated explanation alone would not demonstrate that behavior. The local controller simulates it and is labelled separately. | pp. 1–5, 38–62 |
| Tool invocation, planning and ReAct-style control | The live Dify model outputs a proposed lookup as JSON. A code dispatcher validates and invokes the tool, then returns the result to the planner. The workflow bounds the number of attempts. The demo trace shows tool choices and results. | pp. 40–62, 189–195 |
| Working memory | Each case retains completed lookups, scoped facts, citation identifiers and unresolved questions across the investigation. | pp. 30–37, 151–152 |
| Semantic memory, RAG and chunking | Role notices, individual policy clauses and recruiter amendments are individually retrievable. Role and cycle identifiers and explicit supersession apply before the answer cites evidence. This is structured retrieval in the prototype. A persistent embedding knowledge base is a possible extension. | pp. 75–89, 102–123, 153 |
| Context engineering | The prompt uses the question, current evidence, relevant document excerpts and the permitted next actions. Profile details unrelated to a requirement stay outside the case context. | pp. 90–101, 149–155, 186 |
| Harness engineering | Code checks identifiers, allowed actions, evidence sufficiency, explicit criteria and stopping conditions. Verified evidence controls status and source links. | pp. 178–195 |
| Human oversight and bounded autonomy | The placement officer resolves a specific policy ambiguity. The case is then rechecked against the remaining criteria. This is an advisory student workflow. | pp. 49–62, 129–130, 144–148 |
| Observability and evaluation | The interface exposes the evidence trail. A fixed checklist, optimized rules and an adaptive simulation are evaluated on the same synthetic scenarios. Live model metrics need a separately configured run. | pp. 139–148, 178–184 |
| Business context and ROI | Initial buyer, pilot hypotheses, pricing sensitivity and rollout criteria sit alongside the prototype. | pp. 90–101, 144–148 |

| Deliberately omitted or deferred | Reason |
|---|---|
| Multi-agent supervisor, network and A2A | One investigation owner and one officer handoff fit the workflow. Multiple agents add coordination, latency and evaluation work. |
| MCP | The current tools belong to one workflow. A second agent client or shared system integration would make MCP worth revisiting. |
| GraphRAG and vector infrastructure | A small set of keyed, versioned notices and clauses is sufficient. A vector index would be useful for a larger unstructured corpus. |
| Fine-tuning | Updated notices and rulings change the answer at retrieval time. The project tests evidence selection and verification. |
| Persistent episodic memory or model learning across students | The prototype stores case state where needed. It does not infer preferences from previous candidates or use one student's history to decide another case. |
| Skills, custom plugins and hooks | Tool contracts and workflow rules provide the procedural guidance in this scope. |
| Repeated self-reflection and long-horizon execution | A bounded investigation and a single reviewer intervention are enough for the demo. |
| Transformers, tokenization and sampling sweeps | The project configures an existing model. The model internals and generation settings are background concepts. |
| Image or video processing, native recruiter integrations and automatic applications | The project evaluates published notices against verified facts and demonstrates one complete review path. |

## Architecture choice

Dify owns the optional live tool-selection workflow. Streamlit shows the student shortlist, the evidence, and the officer's case decision. The offline controller provides a reproducible classroom demonstration. Standing production authority, identity provisioning and integration with the campus placement system would belong to a later deployment.
