# Deployment runbook

The demo contains fictional notices, user profiles, and office decisions. Session state models the reviewer workflow for a presentation. It does not authenticate a placement officer or share rulings across sessions.

## 1. Serve the simulation on Streamlit

1. In [Streamlit Community Cloud](https://share.streamlit.io), use **Create app** and select an existing GitHub app.
2. Select repository `vishnusrivardhangollakaram-boop/AgenticAI_Group6`, the branch containing the release (normally `main`), and `app.py` as the entrypoint. Use Python 3.12 for parity with the release checks.
3. For a public classroom demo, leave Secrets empty. The placement office, shortlist, evidence trail and evaluation all run with synthetic records in **Case simulation**.
4. Open the deployed app. Verify the synthetic Business Analyst amendment and record an AI Strategy Associate office ruling. Confirm the updated result survives a fresh check within that browser session.

The deploying Streamlit account needs access to the connected GitHub repository. For exact cloud setup steps see [Connect your GitHub account](https://docs.streamlit.io/deploy/streamlit-community-cloud/get-started/connect-your-github-account) and [Deploy your app](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy).

## 2. Publish the Dify workflow

1. Import the included [DSL file](../workflow/Placement_Application_Copilot.yml) as a Workflow in Dify Studio.
2. Select a model already enabled in the workspace. If the model in the import is unavailable, select the replacement on each **Choose lookup** node.
3. Test `PC-101`, `PC-102` and `PC-103` in the Studio, checking for outcomes `ready`, `not_ready` and `needs_review`. Inspect accepted evidence reads and confirm an amendment check precedes a supported readiness decision.
4. Publish the workflow and obtain a Service API app key from Dify. The model provider credential stays in Dify. The Service API app key is a separate Streamlit server secret. [Workflow setup](../workflow/README.md) documents the request and verification contract.

## 3. Enable and verify live Dify in Streamlit

Use a restricted Streamlit app for the Dify-backed demo so only your team and invited viewers can trigger provider calls. Leave the public app in Simulation mode if unrestricted access is required. See [Streamlit sharing](https://docs.streamlit.io/deploy/streamlit-community-cloud/share-your-app).

Add these entries through the app's [Secrets settings](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management). The values below are placeholders.

```toml
DIFY_API_BASE_URL = "https://api.dify.ai/v1"
DIFY_API_KEY = "<published-workflow-app-key>"
```

After restarting, select **Dify agent** and check all three roles. The actual run must return the three expected statuses and a case trace that the app verifies against its own fixtures. Capture the deployed URL and Dify run identifiers. A successful simulation, a working Streamlit page, and a verified live Dify execution are three separate checks.

## Presentation fallback

Open [the offline browser demo](../demo/Placement_Copilot_Offline_Demo.html) from the downloaded project folder if the network or hosted app is unavailable. It replays the compiled synthetic evidence and allows the same office ruling without cloud access.
