# Run the Dify workflow

The Streamlit demo works without Dify or a model key in **Simulation** mode. The simulation selects evidence reads deterministically. Use **Dify live** after publishing this workflow if you want the model to choose the reads.

1. In Dify Studio, import `Placement_Application_Copilot.yml` as a Workflow.
2. Install and configure a chat model provider in your workspace. The export targets the Gemini provider and Gemini 3.5 Flash-Lite. If that model is absent from the workspace's provider plugin or entitlement, choose an available chat model on all seven **Choose lookup** nodes. The workflow input and output stay the same.
3. Test `PC-101`, `PC-102`, and `PC-103` in the Dify editor. The expected outcomes are `ready`, `not_ready`, and `needs_review`. Inspect the **Validate and run lookup** nodes. The engine checks for amendments before it uses a notice to determine eligibility. The equivalence lookup applies only when the profile and current notice require one.
4. Publish the workflow and create an **app Service API key** for this workflow. This key authorizes Streamlit to run the published app. The model provider credential belongs in Dify's provider settings. Configure Streamlit server secrets as shown below and restart Streamlit.

```toml
DIFY_API_BASE_URL = "https://api.dify.ai/v1"
DIFY_API_KEY = "paste-your-app-key-in-server-secrets"
```

For local use, put those values in `.streamlit/secrets.toml` or environment variables. For Streamlit Community Cloud, enter them in the app’s Secrets settings. Do not commit a key to Git. A private Dify token still incurs model charges when a user runs the connected Streamlit app, so use an access-restricted Streamlit app for paid demos.

The exported workflow contains synthetic records. The LLM receives a compact case view and returns one JSON action. This implements ReAct-style evidence selection through a custom dispatcher. Code validates the proposed action against the case and invokes an allowed read. A gate exits after adequate evidence or the seventh round. The planner has no ability to supply evidence or choose the final decision. Streamlit replays the returned trace against the same fixture version and uses verified outputs only. Retrieval in this project is structured and version-aware.

The placement officer’s review and resumed evaluation run within Streamlit. This keeps the human step available in both modes. It is a session-based classroom demonstration, without institutional sign-in or a shared production queue.

## Service API contract

- Request: `POST /v1/workflows/run` with `inputs.case_id`, `response_mode: streaming`, and a short pseudonymous `user`.
- Response: the final `workflow_finished` event's `data.outputs.result_json` contains a JSON-encoded case result. The client also records the run ID and token count when Dify reports them. Streaming keeps the connection open during the bounded planner loop. The app displays the result after verification.
- A model request, runtime, or configuration error stays visible as an error. It does not trigger a hidden simulation run.

See [Dify Run Workflow](https://docs.dify.ai/en/api-reference/workflow-runs/run-workflow), [Dify streaming](https://docs.dify.ai/en/api-reference/guides/streaming), and the [Gemini API model list](https://ai.google.dev/gemini-api/docs/models).

## Regenerate and verify

From the repository root:

```bash
python workflow/build_workflow.py
python workflow/verify_workflow.py
```

Run these whenever the case fixtures or evidence gates change. To generate for a different configured model, use `--provider PROVIDER_ID --model MODEL_ID`. The verification walks the YAML graph and executes its exact Python nodes with a planner stub. It also checks the Service API contract, streamed completion, and failure handling with mocks. Dify Studio import, publishing, and a real model run still need a configured Dify workspace.
