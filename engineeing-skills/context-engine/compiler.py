"""Compile a deterministic, budgeted Context Package."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from budget import available_tokens, plan_budget
from capability import handshake
from coe_common import PACKAGE_SCHEMA, PARSER_VERSION, posix, sha256_json, sha256_text
from freshness import binding_digest, content_digest_for
from path_identity import is_excluded_secret
from registry import Registry, can_enforce, load_registry
from security import filter_items, policy_as_data


def estimate_tokens(text: str) -> int:
    return max(1, (len(text) + 3) // 4)


def _item(ident: str, path: str, kind: str, text: str, *, mandatory: bool, reason: str) -> dict[str, Any]:
    return {
        "id": ident,
        "path": posix(path),
        "kind": kind,
        "mandatory": mandatory,
        "reason": reason,
        "digest": sha256_text(text),
        "estimated_tokens": estimate_tokens(text),
        "excerpt": text if mandatory else text[:400],
    }


def _read(repo: Path, rel: str) -> str:
    path = repo / rel
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def compile_package(
    repo: Path,
    request: dict[str, Any],
    registry: Registry | None = None,
    *,
    graph: dict[str, Any] | None = None,
    impact: dict[str, Any] | None = None,
    plan_text: str = "",
    write_set: list[str] | None = None,
    constraints: list[str] | None = None,
    tests: list[str] | None = None,
    extra_files: list[str] | None = None,
    host: dict[str, Any] | None = None,
    policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    registry = registry or load_registry(repo)
    phase = str(request.get("phase") or "PLANNING").upper()
    write_set = [posix(x) for x in (write_set or [])]
    budget_cfg = request.get("budget") or {}
    budget = available_tokens(
        model_window=int(budget_cfg.get("model_window") or 128000),
        system_tokens=int(budget_cfg.get("system_tokens") or 2000),
        tool_reserve=int(budget_cfg.get("tool_reserve") or 2000),
        output_reserve=int(budget_cfg.get("output_reserve") or 2000),
        safety_margin=int(budget_cfg.get("safety_margin") or 1000),
        policy_cap=budget_cfg.get("initial_context_tokens") or budget_cfg.get("max_task_tokens"),
        scope_level=str(request.get("scope_level") or "MODULE"),
    )
    items: list[dict[str, Any]] = []
    for idx, constraint in enumerate(constraints or []):
        items.append(_item(f"constraint-{idx}", "constraints", "constraint", constraint, mandatory=True, reason="governing_constraint"))
    if plan_text:
        items.append(_item("plan-ac", "plan", "acceptance", plan_text, mandatory=True, reason="task_ac"))
    modules = list(request.get("modules") or [])
    for rec in registry.modules():
        if modules and rec.rec_id not in modules:
            continue
        items.append(
            _item(
                f"module-{rec.rec_id}",
                rec.source or rec.rec_id,
                "module_boundary",
                json.dumps({"id": rec.rec_id, "include": rec.include, "exclude": rec.exclude}, sort_keys=True),
                mandatory=True,
                reason="module_boundary",
            )
        )
        for contract in rec.contracts:
            body = _read(repo, contract)
            items.append(_item(f"contract-{contract}", contract, "contract", body or contract, mandatory=True, reason="exact_contract"))
    for test in tests or []:
        body = _read(repo, test)
        items.append(_item(f"test-{test}", test, "test", body or test, mandatory=True, reason="related_test"))
    for path in extra_files or []:
        if is_excluded_secret(path):
            continue
        body = _read(repo, path)
        items.append(_item(f"src-{path}", path, "source", body, mandatory=False, reason="implementation"))

    items = filter_items(items)
    policy_as_data(policy or {}, items)

    allocation = plan_budget(items, budget)
    status = "READY"
    reasons: list[str] = []
    if registry.errors:
        status = "BLOCKED"
        reasons.extend(e["code"] for e in registry.errors)
    if not can_enforce(registry) and str((host or {}).get("mode") or "ADVISORY").upper() == "ENFORCED":
        status = "BLOCKED"
        reasons.append("CONTEXT_REGISTRY_INVALID")
    if allocation["status"] == "BLOCKED":
        status = "BLOCKED"
        reasons.append("CONTEXT_MANDATORY_OVER_BUDGET")
    cap = handshake(host or {})
    if cap["mode"] == "ENFORCED" and not cap["verified"]:
        status = "BLOCKED"
        reasons.append("CONTEXT_ACCESS_UNSUPPORTED")

    graph_digest = (graph or {}).get("digest") or sha256_json(graph or {})
    if (graph or {}).get("coverage") == "INCOMPLETE":
        if status == "READY":
            status = "INCOMPLETE"
        reasons.append("CONTEXT_GRAPH_INCOMPLETE")

    binding = {
        "plan_semantic_sha256": (request.get("binding") or {}).get("plan_semantic_sha256") or "",
        "work_facts_digest": (request.get("binding") or {}).get("work_facts_digest") or "",
        "content_digest": content_digest_for(repo, [i["path"] for i in allocation["selected"] if i.get("path")]),
        "registry_digest": registry.digest,
        "graph_digest": graph_digest,
        "policy_digest": sha256_json(policy or {}),
        "compiler_version": PARSER_VERSION,
        "tokenizer": "char/4",
    }
    selected = allocation["selected"]
    excluded = [
        {"id": i.get("id"), "path": i.get("path"), "reason": i.get("exclude_reason") or "unrelated"}
        for i in allocation["excluded"]
    ]
    selection = {
        "mandatory": [i["id"] for i in selected if i.get("mandatory")],
        "selected": selected,
        "excluded": excluded,
        "unresolved_obligations": reasons,
    }
    package = {
        "schema": PACKAGE_SCHEMA,
        "package_id": sha256_json({"request": request.get("request_id"), "binding": binding, "selected": [i["id"] for i in selected]})[7:23],
        "request_id": request.get("request_id"),
        "phase": phase,
        "plan_id": (request.get("binding") or {}).get("plan_id"),
        "todo_id": (request.get("binding") or {}).get("todo_id"),
        "epoch": int(request.get("epoch") or 1),
        "status": status,
        "reason_codes": sorted(set(reasons)),
        "enforcement_mode": cap["mode"],
        "binding": binding,
        "selection": selection,
        "budget": {
            "available": budget,
            "used_estimated": allocation["used"],
            "usage_kind": "estimated",
            "segments": allocation.get("segments") or [],
        },
        "read_set": sorted({posix(i["path"]) for i in selected if i.get("path")}),
        "write_set_ref": write_set,
        "impact": impact or {},
        "scope_level": request.get("scope_level"),
        "modules": modules,
        "manifest_digest": "",
    }
    if phase == "EXECUTION" and not package["plan_id"]:
        package["status"] = "BLOCKED"
        package["reason_codes"] = sorted(set(package["reason_codes"] + ["CONTEXT_SCOPE_UNRESOLVED"]))
    package["binding"]["binding_digest"] = binding_digest(binding)
    package["manifest_digest"] = sha256_json(
        {
            "selected": [i["id"] for i in selected],
            "digests": [i["digest"] for i in selected],
            "binding": package["binding"],
            "status": package["status"],
        }
    )
    return package


def write_package(repo: Path, package: dict[str, Any]) -> Path:
    plan_id = package.get("plan_id") or "planning"
    todo = package.get("todo_id") or "request"
    epoch = package.get("epoch") or 1
    if package.get("phase") == "PLANNING" and not package.get("plan_id"):
        dest = repo / ".smc" / "context" / "requests" / str(package.get("request_id") or "REQ") / "package.json"
    else:
        dest = repo / ".smc" / "runs" / str(plan_id) / "context" / str(todo) / str(epoch) / "package.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(package, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return dest


def write_set_violation(package: dict[str, Any], changed: list[str]) -> list[str]:
    allowed = {posix(x) for x in package.get("write_set_ref") or []}
    return [posix(p) for p in changed if posix(p) not in allowed]
