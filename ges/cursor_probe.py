from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

from ges.errors import (
    CURSOR_CLI_NOT_FOUND,
    CURSOR_DISCOVERY_FAILED,
    CURSOR_DISCOVERY_OUTPUT_INVALID,
    CURSOR_RUNTIME_UNAVAILABLE,
    GesError,
)
from ges.stagelog import CURSOR_RUNTIME_DISCOVERY, CURSOR_STRUCTURAL_DISCOVERY, emit

PROBE_ID = "GES_CURSOR_DISCOVERY_PROBE_V1"
REQUIRED_SKILLS = {
    "grill-with-docs": Path(".agents/skills/grill-with-docs/SKILL.md"),
    "speckit-specify": Path(".cursor/skills/speckit-specify/SKILL.md"),
    "writing-plans": Path(".agents/skills/writing-plans/SKILL.md"),
}
PROBE_PROMPT = (
    "Do not edit files. Read these project skill files if they exist: "
    ".agents/skills/grill-with-docs/SKILL.md, "
    ".cursor/skills/speckit-specify/SKILL.md, "
    ".agents/skills/writing-plans/SKILL.md. "
    "Return only a machine-readable JSON object. "
    f'The object MUST be {{"probe":"{PROBE_ID}","skills":{{'
    '"grill-with-docs":true,"speckit-specify":true,"writing-plans":true}}. '
    "Set a skill true only if that SKILL.md exists and you can follow it now."
)


def resolve_cursor_cli() -> str:
    explicit = os.environ.get("GES_CURSOR_CLI")
    if explicit:
        path = Path(explicit)
        if path.is_file():
            return str(path)
        raise GesError(CURSOR_CLI_NOT_FOUND, f"GES_CURSOR_CLI is not an executable: {explicit}")
    for name in ("agent", "cursor-agent"):
        found = shutil.which(name)
        if found:
            return found
    localapp = os.environ.get("LOCALAPPDATA", "")
    for rel in ("cursor-agent/agent.cmd", "cursor-agent/cursor-agent.cmd"):
        candidate = Path(localapp) / rel
        if candidate.is_file():
            return str(candidate)
    raise GesError(CURSOR_CLI_NOT_FOUND, "neither agent nor cursor-agent is available")


def structural_discovery(repo: Path) -> dict[str, Any]:
    emit(CURSOR_STRUCTURAL_DISCOVERY, "start", repo=str(repo))
    results = {}
    for name, rel in REQUIRED_SKILLS.items():
        path = repo / rel
        frontmatter = _parse_frontmatter(path.read_text(encoding="utf-8")) if path.is_file() else {}
        results[name] = {
            "path": rel.as_posix(),
            "exists": path.is_file(),
            "name": frontmatter.get("name"),
            "description": frontmatter.get("description"),
            "valid": bool(
                path.is_file()
                and frontmatter.get("name") == name
                and _valid_skill_name(frontmatter.get("name") or "")
                and (frontmatter.get("description") or "").strip()
            ),
        }
    ok = all(item["valid"] for item in results.values())
    emit(CURSOR_STRUCTURAL_DISCOVERY, "complete", status="PASS" if ok else "FAIL")
    return {"status": "PASS" if ok else "FAIL", "skills": results}


def runtime_discovery(repo: Path) -> dict[str, Any]:
    emit(CURSOR_RUNTIME_DISCOVERY, "start", repo=str(repo))
    last_error: GesError | None = None
    for attempt in range(3):
        try:
            payload = _runtime_discovery_once(repo)
            emit(CURSOR_RUNTIME_DISCOVERY, "complete", status="PASS", attempt=attempt + 1)
            return payload
        except GesError as exc:
            last_error = exc
            if exc.code != CURSOR_DISCOVERY_FAILED or attempt == 2:
                emit(CURSOR_RUNTIME_DISCOVERY, "complete", status="FAIL", attempt=attempt + 1)
                raise
    assert last_error is not None
    raise last_error


def _runtime_discovery_once(repo: Path) -> dict[str, Any]:
    executable = resolve_cursor_cli()
    argv = [executable, "-p", "--output-format", "json", "--trust", "--workspace", str(repo)]
    if _supports_ask(executable):
        argv.extend(["--mode", "ask"])
    argv.append(PROBE_PROMPT)
    try:
        version = _cli_version(executable)
        result = _run_cli(argv, cwd=repo, timeout=300)
    except OSError as exc:
        raise GesError(CURSOR_RUNTIME_UNAVAILABLE, f"Cursor runtime unavailable: {exc}") from exc
    parsed = _parse_probe_json(result.stdout)
    skills = parsed.get("skills") if isinstance(parsed.get("skills"), dict) else {}
    if parsed.get("probe") != PROBE_ID:
        raise GesError(CURSOR_DISCOVERY_OUTPUT_INVALID, "probe id missing or invalid", details={"stdout": result.stdout})
    missing = [name for name in REQUIRED_SKILLS if name not in skills]
    if missing:
        raise GesError(CURSOR_DISCOVERY_OUTPUT_INVALID, f"probe omitted skills: {missing[0]}", details={"parsed": parsed})
    if any(skills.get(name) is not True for name in REQUIRED_SKILLS):
        raise GesError(CURSOR_DISCOVERY_FAILED, "Cursor runtime did not report all required skills", details={"skills": skills, "stdout": result.stdout[-2000:]})
    return {
        "status": "PASS",
        "executable": executable,
        "version": version,
        "argv": argv,
        "exit_code": result.returncode,
        "parsed": parsed,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def _valid_skill_name(name: str) -> bool:
    return bool(re.fullmatch(r"[a-z0-9-]+", name))


def _parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    block = text[3:end]
    data: dict[str, str] = {}
    for line in block.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"').strip("'")
    return data


def _supports_ask(executable: str) -> bool:
    result = _run_cli([executable, "--help"], cwd=Path.cwd(), timeout=60)
    text = f"{result.stdout}\n{result.stderr}".lower()
    return "--mode" in text and "ask" in text


def _cli_version(executable: str) -> str:
    result = _run_cli([executable, "--version"], cwd=Path.cwd(), timeout=60)
    return (result.stdout or result.stderr).strip()


def _run_cli(argv: list[str], *, cwd: Path, timeout: int | None = None) -> subprocess.CompletedProcess[str]:
    run_argv = list(argv)
    if os.name == "nt" and Path(run_argv[0]).suffix.lower() in {".cmd", ".bat"}:
        run_argv = [os.environ.get("COMSPEC", "cmd.exe"), "/c", *run_argv]
    try:
        return subprocess.run(
            run_argv,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise GesError(CURSOR_RUNTIME_UNAVAILABLE, "Cursor CLI timed out") from exc


def _parse_probe_json(stdout: str) -> dict[str, Any]:
    text = _unwrap_cli_result(stdout)
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict) and "probe" in parsed:
            return parsed
    except json.JSONDecodeError:
        parsed = None
    start = text.find("{")
    while start >= 0:
        end = text.rfind("}")
        if end <= start:
            break
        try:
            parsed = json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            start = text.find("{", start + 1)
            continue
        if isinstance(parsed, dict) and parsed.get("probe") == PROBE_ID:
            return parsed
        if isinstance(parsed, dict) and "probe" in parsed:
            return parsed
        start = text.find("{", start + 1)
    raise GesError(CURSOR_DISCOVERY_OUTPUT_INVALID, "Cursor probe stdout is not valid JSON")


def _unwrap_cli_result(stdout: str) -> str:
    text = stdout.strip()
    try:
        outer = json.loads(text)
    except json.JSONDecodeError:
        return text
    if isinstance(outer, dict) and outer.get("type") == "result" and "result" in outer:
        result = outer["result"]
        return result if isinstance(result, str) else json.dumps(result)
    return text
