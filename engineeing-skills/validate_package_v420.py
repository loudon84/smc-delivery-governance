#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILLS = ROOT / ".agents" / "skills"
PACKAGE_VERSION = "4.2.0"
EXPECTED = {
    "smc-plan-delivery": "1.1.0",
    "smc-plan-from-approved-prd-ponytail": "3.5.0",
    "smc-plan-validator": "1.4.0",
    "smc-plan-review": "1.1.0",
    "executing-plans": "4.2.0",
    "subagent-driven-development": "4.2.0",
    "smc-roadmap": "1.2.0",
    "using-superpowers": "4.2.0",
    "smc-architecture-decision": "1.0.0",
    "smc-architecture-review": "1.0.0",
    "smc-prd-grounding": "4.0.0",
    "smc-prd-review": "4.0.0",
    "smc-prd-converge": "3.0.0",
}
REQUIRED_PACKAGE_FILES = (
    ".agents/skills/smc-plan-delivery/scripts/workspace.py",
    ".agents/skills/smc-plan-delivery/scripts/execution_context.py",
    ".agents/skills/smc-plan-delivery/scripts/evidence.py",
    ".agents/skills/smc-plan-delivery/scripts/completion_audit.py",
    ".agents/skills/smc-plan-delivery/scripts/commit_guard.py",
    ".agents/skills/smc-plan-delivery/scripts/delivery_state.py",
    ".agents/skills/smc-plan-delivery/scripts/readiness.py",
    ".agents/skills/smc-plan-validator/scripts/validate_plan_v34.py",
    ".agents/skills/smc-plan-from-approved-prd-ponytail/scripts/create_plan_seed_v34.py",
    ".agents/skills/smc-roadmap/scripts/validate_roadmap_v11.py",
    ".agents/skills/smc-roadmap/scripts/validate_roadmap.py",
    ".agents/skills/smc-roadmap/scripts/roadmap_update.py",
    "project-integration/tools/agent-skills/validate_plan.py",
    "install_v420.py",
    "rollback.py",
    f"PACKAGE-MANIFEST-v{PACKAGE_VERSION}.json",
    f"SHA256SUMS-v{PACKAGE_VERSION}",
)


def fm(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("missing frontmatter")
    end = next((i for i, x in enumerate(lines[1:], 1) if x.strip() == "---"), -1)
    if end < 0:
        raise ValueError("unterminated frontmatter")
    out: dict[str, str] = {}
    for line in lines[1:end]:
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip().strip('"\'')
    return out


def file_sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd: list[str], cwd: Path, capture: bool = False) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy(); env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(cmd, cwd=cwd, text=True, encoding="utf-8", errors="replace", capture_output=capture, env=env)


def check_links(path: Path) -> list[str]:
    errors: list[str] = []
    for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
        target = target.split("#", 1)[0].strip()
        if not target or target.startswith(("http://", "https://", "#", "/")) or "<" in target:
            continue
        if not (path.parent / target).resolve().exists():
            errors.append(f"missing local reference {path.relative_to(ROOT)} -> {target}")
    return errors


def verify_release_integrity(errors: list[str]) -> None:
    sums = ROOT / f"SHA256SUMS-v{PACKAGE_VERSION}"
    manifest = ROOT / f"PACKAGE-MANIFEST-v{PACKAGE_VERSION}.json"
    if not sums.is_file() or not manifest.is_file():
        errors.append("versioned v4.2 release integrity files missing")
        return
    expected: dict[str, str] = {}
    for line in sums.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try: digest, rel = line.split("  ", 1)
        except ValueError:
            errors.append(f"invalid sums line: {line}"); continue
        rel = rel.strip().replace("\\", "/")
        if rel in expected:
            errors.append(f"duplicate sums path: {rel}"); continue
        expected[rel] = digest
        actual = file_sha256(ROOT / rel)
        if actual != digest:
            errors.append(f"SHA256 mismatch {rel}: expected={digest} actual={actual}")
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"manifest invalid: {exc}"); return
    if data.get("package_version") != PACKAGE_VERSION:
        errors.append("PACKAGE-MANIFEST v4.2 version mismatch")
    rows = {str(x.get("path")): x for x in data.get("files", []) if isinstance(x, dict)}
    if set(rows) != set(expected):
        errors.append("PACKAGE-MANIFEST/SHA256SUMS path-set mismatch")
    for rel, digest in expected.items():
        row = rows.get(rel, {})
        if row.get("sha256") != digest:
            errors.append(f"manifest digest mismatch: {rel}")


def copy_tree(src: Path, dst: Path) -> None:
    if not src.is_dir(): return
    for path in src.rglob("*"):
        if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc": continue
        rel = path.relative_to(src); out = dst / rel; out.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(path, out)


def tree_bytes(path: Path) -> dict[str, bytes]:
    if not path.is_dir(): return {}
    return {p.relative_to(path).as_posix(): p.read_bytes() for p in path.rglob("*") if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc"}


def installer_smoke(errors: list[str]) -> None:
    with tempfile.TemporaryDirectory() as td:
        project = Path(td) / "repo"; project.mkdir(); subprocess.run(["git", "init", "-q", str(project)], check=True)
        required = [
            ".agents/skills/smc-plan-validator/scripts/validate_plan.py",
            ".agents/skills/smc-plan-review/scripts/assess_plan_review.py",
            ".agents/skills/smc-plan-from-approved-prd-ponytail/scripts/validate_generation_integrity.py",
            ".agents/skills/smc-plan-from-approved-prd-ponytail/references/ponytail-minimality.md",
            ".agents/skills/smc-plan-from-approved-prd-ponytail/references/ownership-aware-slicing.md",
            ".agents/skills/smc-plan-from-approved-prd-ponytail/references/generation-integrity-gates.md",
            ".agents/skills/smc-plan-from-approved-prd-ponytail/references/source-basis.md",
            ".agents/skills/smc-roadmap/scripts/validate_roadmap.py",
            ".agents/skills/smc-roadmap/scripts/roadmap_update.py",
            ".agents/skills/code-review-and-quality/SKILL.md",
            ".agents/references/prd-contract.md",
            ".agents/references/evidence-contract.md",
            ".agents/references/architecture-convergence.md",
        ]
        for rel in required:
            p = project / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text("# baseline\n", encoding="utf-8")
        # Declared Cursor mirror with intentional drift: v4.2 must repair it but
        # must not make Cursor a Core requirement for consumers that omit it.
        (project / ".cursor/skills/code-review-and-quality").mkdir(parents=True, exist_ok=True)
        (project / ".cursor/skills/code-review-and-quality/SKILL.md").write_text("# stale mirror\n", encoding="utf-8")
        (project / ".cursor/references").mkdir(parents=True, exist_ok=True)
        result = run([sys.executable, str(ROOT / "install_v420.py"), str(project), "--apply", "--skip-project-validator"], ROOT, capture=True)
        if result.returncode:
            errors.append("installer smoke failed: " + (result.stdout + result.stderr).replace("\n", " | ")); return
        for rel in (
            ".agents/skills/smc-plan-delivery/SKILL.md",
            ".agents/skills/smc-plan-delivery/scripts/workspace.py",
            ".agents/skills/smc-plan-validator/scripts/validate_plan_v34.py",
            "tools/agent-skills/validate_plan.py",
        ):
            if not (project / rel).is_file(): errors.append(f"installer smoke missing output: {rel}")
        if tree_bytes(project / ".agents/skills") != tree_bytes(project / ".cursor/skills"):
            errors.append("declared Cursor skill mirror not repaired")
        if tree_bytes(project / ".agents/references") != tree_bytes(project / ".cursor/references"):
            errors.append("declared Cursor reference mirror not repaired")
        rollback = run([sys.executable, str(ROOT / "rollback.py"), str(project), "--apply"], ROOT, capture=True)
        if rollback.returncode:
            errors.append("rollback smoke failed: " + (rollback.stdout + rollback.stderr).replace("\n", " | "))

    # Second consumer: no Cursor mirror. Core install must not manufacture or
    # require one just because NodeSkClaw declares one.
    with tempfile.TemporaryDirectory() as td:
        project = Path(td) / "repo"; project.mkdir(); subprocess.run(["git", "init", "-q", str(project)], check=True)
        for rel in required:
            p = project / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text("# baseline\n", encoding="utf-8")
        result = run([sys.executable, str(ROOT / "install_v420.py"), str(project), "--apply", "--skip-project-validator"], ROOT, capture=True)
        if result.returncode:
            errors.append("non-Cursor consumer install smoke failed: " + (result.stdout + result.stderr).replace("\n", " | "))
        elif (project / ".cursor").exists():
            errors.append("Core installer manufactured undeclared .cursor mirror")


def main() -> int:
    errors: list[str] = []
    if not SKILLS.is_dir(): errors.append(".agents/skills missing")
    for skill, version in EXPECTED.items():
        path = SKILLS / skill / "SKILL.md"
        if not path.is_file(): errors.append(f"{skill}: SKILL.md missing"); continue
        try: meta = fm(path)
        except ValueError as exc: errors.append(f"{skill}: {exc}"); continue
        if meta.get("name") != skill: errors.append(f"{skill}: frontmatter name mismatch")
        if meta.get("version") != version: errors.append(f"{skill}: version={meta.get('version')} expected={version}")
        if skill == "smc-plan-delivery": errors.extend(check_links(path))

    for rel in REQUIRED_PACKAGE_FILES:
        if not (ROOT / rel).is_file(): errors.append(f"required package file missing: {rel}")

    contract = SKILLS / "smc-plan-from-approved-prd-ponytail/references/plan-contract-v3.md"
    text = contract.read_text(encoding="utf-8") if contract.is_file() else ""
    for token in ("smc.plan.v3.4", "content", "deterministic", "Evidence Policy", "plan_id", "IMPLEMENTED_AND_PROVEN"):
        if token not in text: errors.append(f"Plan contract missing token: {token}")

    workspace_contract = SKILLS / "smc-plan-delivery/references/workspace-contract.md"
    wtext = workspace_contract.read_text(encoding="utf-8") if workspace_contract.is_file() else ""
    for token in ("PLAN_OWNED", "AMBIENT_PREEXISTING", "DELIVERY_TARGET_CONFLICT", "scope_fingerprint", "ambient_fingerprint"):
        if token not in wtext: errors.append(f"Workspace contract missing token: {token}")

    context_contract = SKILLS / "smc-plan-delivery/references/execution-context-contract.md"
    ctext = context_contract.read_text(encoding="utf-8") if context_contract.is_file() else ""
    for token in ("resume", "ledger", "continuation", "Completion Gate"):
        if token.lower() not in ctext.lower(): errors.append(f"Execution context contract missing token: {token}")

    for path in ROOT.rglob("*.py"):
        if "__pycache__" in path.parts: continue
        try: compile(path.read_text(encoding="utf-8"), str(path), "exec")
        except Exception as exc: errors.append(f"compile failed {path.relative_to(ROOT)}: {exc}")

    delivery = run([sys.executable, str(SKILLS / "smc-plan-delivery/scripts/run_selftest.py")], ROOT, capture=True)
    if delivery.returncode: errors.append("delivery self-test failed: " + (delivery.stdout + delivery.stderr).replace("\n", " | "))
    roadmap = run([sys.executable, str(SKILLS / "smc-roadmap/scripts/test_roadmap_v11.py"), "-q"], ROOT, capture=True)
    if roadmap.returncode: errors.append("roadmap self-test failed: " + (roadmap.stdout + roadmap.stderr).replace("\n", " | "))

    wrapper = ROOT / "project-integration/tools/agent-skills/validate_plan.py"
    if not wrapper.is_file(): errors.append("project validate_plan wrapper missing")
    else:
        wt = wrapper.read_text(encoding="utf-8")
        if "validate_plan_v34.py" not in wt or "validate_plan_v33.py" not in wt:
            errors.append("integration wrapper does not route v3.4 + legacy v3.3")

    verify_release_integrity(errors)
    installer_smoke(errors)
    if errors:
        print("PACKAGE VALIDATION FAILED", file=sys.stderr); print("\n".join(errors), file=sys.stderr); return 1
    print(f"PACKAGE VALIDATION PASS — {len(EXPECTED)} pipeline skills, 32 delivery tests, 4 Roadmap tests, declared-mirror + no-Cursor installer smoke, rollback smoke PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
