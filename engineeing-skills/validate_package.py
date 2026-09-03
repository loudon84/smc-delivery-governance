#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILLS = ROOT / ".agents" / "skills"
EXPECTED = {
    "smc-plan-delivery": "1.0.0",
    "smc-plan-from-approved-prd-ponytail": "3.4.0",
    "smc-plan-validator": "1.3.0",
    "smc-plan-review": "1.1.0",
    "executing-plans": "4.1.0",
    "subagent-driven-development": "4.1.0",
    "smc-roadmap": "1.1.0",
    "using-superpowers": "4.1.0",
    "smc-architecture-decision": "1.0.0",
    "smc-architecture-review": "1.0.0",
    "smc-prd-grounding": "4.0.0",
    "smc-prd-review": "4.0.0",
    "smc-prd-converge": "3.0.0",
}
CORE_LINK_SKILLS = {"smc-plan-delivery"}
REQUIRED_PACKAGE_FILES = (
    ".agents/skills/smc-plan-delivery/scripts/evidence.py",
    ".agents/skills/smc-plan-delivery/scripts/completion_audit.py",
    ".agents/skills/smc-plan-delivery/scripts/commit_guard.py",
    ".agents/skills/smc-plan-delivery/scripts/delivery_state.py",
    ".agents/skills/smc-plan-delivery/scripts/readiness.py",
    ".agents/skills/smc-roadmap/scripts/validate_roadmap_v11.py",
    ".agents/skills/smc-roadmap/scripts/validate_roadmap.py",
    ".agents/skills/smc-roadmap/scripts/roadmap_update.py",
    ".agents/skills/smc-roadmap/scripts/roadmap_next.py",
    "project-integration/tools/agent-skills/validate_plan.py",
    "install.py",
    "rollback.py",
    "PACKAGE-MANIFEST.json",
    "SHA256SUMS",
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


def check_links(path: Path) -> list[str]:
    errors = []
    for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
        target = target.split("#", 1)[0].strip()
        if not target or target.startswith(("http://", "https://", "#", "/")) or "<" in target:
            continue
        resolved = (path.parent / target).resolve()
        if not resolved.exists():
            errors.append(f"missing local reference {path.relative_to(ROOT)} -> {target}")
    return errors


def run(cmd: list[str], cwd: Path, capture: bool = False) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        cmd,
        cwd=cwd,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=capture,
        env=env,
    )



def file_sha256(path: Path) -> str | None:
    if not path.is_file():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_release_integrity(errors: list[str]) -> None:
    sums = ROOT / "SHA256SUMS"
    if not sums.is_file():
        errors.append("SHA256SUMS missing")
        return
    seen: set[str] = set()
    for line in sums.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            digest, rel = line.split("  ", 1)
        except ValueError:
            errors.append(f"SHA256SUMS invalid line: {line}")
            continue
        rel = rel.strip().replace("\\", "/")
        if rel in seen:
            errors.append(f"SHA256SUMS duplicate: {rel}")
            continue
        seen.add(rel)
        actual = file_sha256(ROOT / rel)
        if actual != digest:
            errors.append(f"SHA256 mismatch {rel}: expected={digest} actual={actual}")
    manifest = ROOT / "PACKAGE-MANIFEST.json"
    if manifest.is_file():
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
            if data.get("package_version") != "4.1.0":
                errors.append("PACKAGE-MANIFEST version mismatch")
        except Exception as exc:
            errors.append(f"PACKAGE-MANIFEST invalid: {exc}")

def installer_smoke(errors: list[str]) -> None:
    with tempfile.TemporaryDirectory() as td:
        project = Path(td) / "repo"
        project.mkdir()
        subprocess.run(["git", "init", "-q", str(project)], check=True)
        # Minimal current-baseline shape required by installer preflight.
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
            path = project / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("# baseline\n", encoding="utf-8")
        (project / ".cursor/skills").mkdir(parents=True, exist_ok=True)
        result = run([sys.executable, str(ROOT / "install.py"), str(project), "--apply", "--skip-project-validator"], ROOT, capture=True)
        if result.returncode:
            errors.append("installer smoke failed: " + (result.stdout + result.stderr).replace("\n", " | "))
            return
        for rel in (
            ".agents/skills/smc-plan-delivery/SKILL.md",
            ".cursor/skills/smc-plan-delivery/SKILL.md",
            ".agents/skills/smc-roadmap/scripts/validate_roadmap_v11.py",
            "tools/agent-skills/validate_plan.py",
        ):
            if not (project / rel).is_file():
                errors.append(f"installer smoke missing output: {rel}")
        ignore = (project / ".gitignore").read_text(encoding="utf-8")
        for token in (".smc/evidence/", ".smc/reviews/", ".smc/runs/"):
            if token not in ignore:
                errors.append(f"installer smoke .gitignore missing: {token}")

        rollback = run([sys.executable, str(ROOT / "rollback.py"), str(project), "--apply"], ROOT, capture=True)
        if rollback.returncode:
            errors.append("rollback smoke failed: " + (rollback.stdout + rollback.stderr).replace("\n", " | "))
        else:
            if (project / ".agents/skills/smc-plan-delivery/SKILL.md").exists():
                errors.append("rollback smoke failed to remove newly-created smc-plan-delivery")
            baseline = (project / ".agents/skills/smc-plan-validator/scripts/validate_plan.py").read_text(encoding="utf-8")
            if baseline != "# baseline\n":
                errors.append("rollback smoke failed to restore overwritten baseline file")


def main() -> int:
    errors: list[str] = []
    if not SKILLS.is_dir():
        errors.append(".agents/skills missing")
    for skill, ver in EXPECTED.items():
        path = SKILLS / skill / "SKILL.md"
        if not path.is_file():
            errors.append(f"{skill}: SKILL.md missing")
            continue
        try:
            meta = fm(path)
        except ValueError as exc:
            errors.append(f"{skill}: {exc}")
            continue
        if meta.get("name") != skill:
            errors.append(f"{skill}: frontmatter name mismatch")
        if meta.get("version") != ver:
            errors.append(f"{skill}: version={meta.get('version')} expected={ver}")
        if skill in CORE_LINK_SKILLS:
            errors.extend(check_links(path))

    for rel in REQUIRED_PACKAGE_FILES:
        if not (ROOT / rel).is_file():
            errors.append(f"required package file missing: {rel}")

    contract = SKILLS / "smc-plan-from-approved-prd-ponytail" / "references" / "plan-contract-v3.md"
    text = contract.read_text(encoding="utf-8") if contract.is_file() else ""
    for token in ("smc.plan.v3.3", "Evidence Policy", "plan_id", "todos", "IMPLEMENTED_AND_PROVEN"):
        if token not in text:
            errors.append(f"Plan contract missing token: {token}")

    evidence_contract = SKILLS / "smc-plan-delivery" / "references" / "evidence-contract.md"
    evidence_text = evidence_contract.read_text(encoding="utf-8") if evidence_contract.is_file() else ""
    for token in ("docs_agent/evidence/<plan-id>-evidence.json", "smc-evidence:<plan-id>@sha256", "working-tree content"):
        if token not in evidence_text:
            errors.append(f"Evidence contract missing token: {token}")

    for path in ROOT.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        try:
            compile(path.read_text(encoding="utf-8"), str(path), "exec")
        except Exception as exc:
            errors.append(f"compile failed {path.relative_to(ROOT)}: {exc}")

    delivery_test = SKILLS / "smc-plan-delivery" / "scripts" / "run_selftest.py"
    result = run([sys.executable, str(delivery_test)], ROOT, capture=True)
    if result.returncode:
        errors.append("smc-plan-delivery self-test failed: " + (result.stdout + result.stderr).replace("\n", " | "))

    roadmap_test = SKILLS / "smc-roadmap" / "scripts" / "test_roadmap_v11.py"
    result = run([sys.executable, str(roadmap_test), "-v"], ROOT, capture=True)
    if result.returncode:
        errors.append("smc-roadmap v1.1 self-test failed: " + (result.stdout + result.stderr).replace("\n", " | "))

    verify_release_integrity(errors)

    wrapper = ROOT / "project-integration" / "tools" / "agent-skills" / "validate_plan.py"
    if not wrapper.is_file():
        errors.append("project validate_plan integration wrapper missing")
    elif "validate_plan_v33.py" not in wrapper.read_text(encoding="utf-8"):
        errors.append("integration wrapper does not route v3.3")

    installer_smoke(errors)

    if errors:
        print("PACKAGE VALIDATION FAILED", file=sys.stderr)
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"PACKAGE VALIDATION PASS — {len(EXPECTED)} pipeline skills, 11 delivery tests, 3 Roadmap tests, installer + rollback smoke PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
