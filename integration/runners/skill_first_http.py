from __future__ import annotations

import json
import os
import time
import urllib.parse
import urllib.request

BASE = os.environ.get("SMC_SKILL_RUN_BASE_URL", "").rstrip("/")
TOKEN = os.environ.get("SMC_SKILL_RUN_TOKEN", "")
SKILL = os.environ.get("SMC_SKILL_NAME", "")
ALLOW = os.environ.get("SMC_ALLOW_INTEGRATION_RUN") == "1"

def request_json(method: str, url: str, body=None, timeout=30):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Accept", "application/json")
    if body is not None:
        req.add_header("Content-Type", "application/json")
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))

def absolute(url: str) -> str:
    return url if url.startswith("http://") or url.startswith("https://") else BASE + (url if url.startswith("/") else "/" + url)

def main():
    if not ALLOW:
        raise SystemExit("SMC_ALLOW_INTEGRATION_RUN=1 required")
    if not BASE or not TOKEN or not SKILL:
        raise SystemExit("SMC_SKILL_RUN_BASE_URL / SMC_SKILL_RUN_TOKEN / SMC_SKILL_NAME required")

    rpc = BASE + "/api/v1/mcp"
    listed = request_json("POST", rpc, {
        "jsonrpc":"2.0","id":"smc-int-list","method":"tools/list","params":{}
    })
    tools = ((listed.get("result") or {}).get("tools") or [])
    tool = next((t for t in tools if t.get("name") == SKILL), None)
    if not tool:
        raise SystemExit(f"configured safe integration skill not published: {SKILL}")
    if tool.get("capabilityKind") not in {None, "skill"}:
        raise SystemExit("integration target is not a Skill capability")

    called = request_json("POST", rpc, {
        "jsonrpc":"2.0","id":"smc-int-call","method":"tools/call",
        "params":{"name":SKILL,"arguments":{"prompt":"SMC governance closed-loop integration smoke test"}}
    })
    result = called.get("result") or {}
    structured = result.get("structuredContent") or result
    run_id = structured.get("run_id")
    result_url = structured.get("result_url")
    event_stream = structured.get("event_stream")
    if not run_id or not result_url or not event_stream:
        raise SystemExit("tools/call accepted response missing run_id/result_url/event_stream")

    # Confirm the SSE endpoint is reachable. Do not require a specific semantic event
    # because terminal completion may be faster than the stream reader attaches.
    req = urllib.request.Request(absolute(event_stream), method="GET")
    req.add_header("Accept", "text/event-stream")
    req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=15) as resp:
        if "text/event-stream" not in (resp.headers.get("Content-Type") or ""):
            raise SystemExit("event_stream is not SSE")
        # Read a bounded amount so the smoke test cannot hang indefinitely.
        resp.readline()

    deadline = time.monotonic() + 120
    terminal = None
    while time.monotonic() < deadline:
        payload = request_json("GET", absolute(result_url), timeout=15)
        status = payload.get("status") or (payload.get("result") or {}).get("status")
        if status in {"completed","failed","cancelled","timed_out"}:
            terminal = payload
            break
        if payload.get("ready") is True:
            terminal = payload
            break
        time.sleep(2)
    if terminal is None:
        raise SystemExit(f"run {run_id} did not reach terminal result")

    status = terminal.get("status") or (terminal.get("result") or {}).get("status")
    if status in {"failed","cancelled","timed_out"}:
        raise SystemExit(f"run terminal status={status}")

    artifacts_url = BASE + f"/api/v1/runs/{urllib.parse.quote(run_id)}/artifacts"
    artifacts = request_json("GET", artifacts_url, timeout=15)
    if not isinstance(artifacts, (dict, list)):
        raise SystemExit("artifact endpoint returned unsupported representation")

    print(json.dumps({
        "run_id":run_id,
        "skill":SKILL,
        "result_status":status or "ready",
        "artifact_endpoint":"reachable",
    }, ensure_ascii=False))

if __name__ == "__main__":
    main()
