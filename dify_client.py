"""Server-side client for the Placement Application Copilot Dify workflow."""

import json
import os
from time import perf_counter
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from engine import verify_remote
from fixtures import CASES


DEFAULT_BASE_URL = "https://api.dify.ai/v1"
MAX_RESPONSE_BYTES = 1_000_000
MAX_STREAM_BYTES = 8_000_000
READ_TIMEOUT_SECONDS = 35
RUN_TIMEOUT_SECONDS = 120


class RejectRedirects(HTTPRedirectHandler):
    """Never forward an app credential to a redirect target."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def settings(read_secret):
    """Read environment overrides before Streamlit secrets."""
    def setting(name):
        if os.environ.get(name):
            return os.environ[name].strip()
        try:
            return str(read_secret(name) or "").strip()
        except (FileNotFoundError, KeyError):
            return ""

    return setting("DIFY_API_BASE_URL") or DEFAULT_BASE_URL, setting("DIFY_API_KEY")


def _workflow_url(base_url):
    base = base_url.rstrip("/")
    address = urlsplit(base)
    is_local_http = address.scheme == "http" and address.hostname in {"localhost", "127.0.0.1", "::1"}
    if not address.hostname or (address.scheme != "https" and not is_local_http):
        raise ValueError("Set an HTTPS Dify Service API URL, or a local HTTP address.")
    if address.username or address.password or address.query or address.fragment:
        raise ValueError("Use the Dify Service API base URL without credentials, queries, or fragments.")
    if not address.path.endswith("/v1"):
        raise ValueError("The Dify Service API base URL should end with /v1.")
    return base + "/workflows/run"


def _read_json(body):
    try:
        response = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ValueError("Dify did not return a valid workflow response.") from None
    if not isinstance(response, dict):
        raise ValueError("Dify returned an unexpected response.")
    return response


def _read_workflow_stream(response, deadline):
    """Read the terminal result, skipping keepalives and intermediate traces."""
    total_bytes = 0
    run_id = None
    data_lines = []
    while perf_counter() <= deadline:
        line = response.readline(MAX_RESPONSE_BYTES + 1)
        total_bytes += len(line)
        if len(line) > MAX_RESPONSE_BYTES or total_bytes > MAX_STREAM_BYTES:
            raise ValueError("Dify returned an oversized stream.")
        if not line:
            break
        line = line.rstrip(b"\r\n")
        if line.startswith(b"data:"):
            data_lines.append(line[5:].removeprefix(b" "))
            continue
        if line or not data_lines:
            continue
        event = _read_json(b"\n".join(data_lines))
        data_lines.clear()
        event_run_id = event.get("workflow_run_id")
        if isinstance(event_run_id, str):
            if run_id and run_id != event_run_id:
                raise ValueError("Dify returned inconsistent run identifiers.")
            run_id = event_run_id
        if event.get("event") == "workflow_finished":
            return {"workflow_run_id": run_id, "data": event.get("data")}
        if event.get("event") == "error":
            raise ValueError("Dify stopped the workflow with an error. Check its run logs.")
    raise ValueError("Dify's stream ended before the workflow finished. Check its run logs.")


def _call_workflow(url, key, payload):
    req = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                 "Accept": "text/event-stream, application/json"},
        method="POST",
    )
    try:
        deadline = perf_counter() + RUN_TIMEOUT_SECONDS
        with build_opener(RejectRedirects).open(req, timeout=READ_TIMEOUT_SECONDS) as response:
            if response.headers.get_content_type() == "text/event-stream":
                return _read_workflow_stream(response, deadline)
            body = response.read(MAX_RESPONSE_BYTES + 1)
    except HTTPError as exc:
        if exc.code in {401, 403}:
            message = "Dify rejected the app key. Check the published workflow's Service API key."
        elif exc.code == 429:
            message = "Dify is rate limiting the workflow. Try again in a moment."
        else:
            message = f"Dify Service API returned HTTP {exc.code}. Check the workflow's run logs."
        raise ValueError(message) from None
    except (URLError, TimeoutError, OSError):
        raise ValueError("Dify could not be reached within the request window. Check the workspace and try again.") from None
    if len(body) > MAX_RESPONSE_BYTES:
        raise ValueError("Dify returned an oversized response.")
    return _read_json(body)


def run_dify(case_id, base_url, api_key, user):
    """Run the published LLM workflow and verify decisions against local evidence."""
    if case_id not in CASES:
        raise ValueError("Select a supported synthetic case.")
    if not api_key or not api_key.strip():
        raise ValueError("Configure DIFY_API_KEY before choosing the live workflow.")
    if not isinstance(user, str) or not user or len(user) > 100:
        raise ValueError("The workflow requires a short, pseudonymous user identifier.")

    started = perf_counter()
    response = _call_workflow(
        _workflow_url(base_url),
        api_key.strip(),
        {"inputs": {"case_id": case_id}, "response_mode": "streaming", "user": user},
    )
    data = response.get("data")
    if not isinstance(data, dict) or data.get("status") != "succeeded":
        raise ValueError("The Dify workflow did not complete. Check its run logs.")
    outputs = data.get("outputs")
    if not isinstance(outputs, dict) or not isinstance(outputs.get("result_json"), str):
        raise ValueError("The published workflow must return a result_json string.")
    try:
        result = json.loads(outputs["result_json"])
        if not isinstance(result, dict):
            raise ValueError
        checked = verify_remote(case_id, result)
    except (ValueError, TypeError, KeyError):
        raise ValueError("The workflow output did not match the trusted case evidence.") from None

    run_id = response.get("workflow_run_id")
    tokens = data.get("total_tokens")
    return {
        **checked,
        "workflow_run_id": run_id if isinstance(run_id, str) else None,
        "elapsed_ms": round((perf_counter() - started) * 1000),
        "tokens": tokens if type(tokens) is int and tokens >= 0 else None,
    }
