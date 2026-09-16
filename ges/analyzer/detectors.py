from __future__ import annotations

from pathlib import Path


def exists(repo: Path, rel: str) -> bool:
    return (repo / rel).exists()


def detect_agents(repo: Path) -> list[str]:
    agents: list[str] = []
    if exists(repo, ".cursor") or exists(repo, ".cursor/"):
        agents.append("cursor")
    if exists(repo, ".codex") or exists(repo, ".codex/"):
        agents.append("codex")
    if exists(repo, ".hermes") or exists(repo, ".hermes/"):
        agents.append("hermes")
    return agents


def detect_languages(repo: Path) -> list[str]:
    found: list[str] = []
    mapping = [
        ("typescript", ("tsconfig.json", "tsconfig.base.json")),
        ("javascript", ("package.json",)),
        ("python", ("pyproject.toml", "setup.py", "requirements.txt")),
        ("go", ("go.mod",)),
        ("rust", ("Cargo.toml",)),
        ("java", ("pom.xml", "build.gradle", "build.gradle.kts")),
    ]
    for name, files in mapping:
        if any(exists(repo, item) for item in files):
            found.append(name)
    nested_ts = any(
        (repo / root).glob("*/tsconfig*.json")
        for root in ("apps", "packages", "services")
        if (repo / root).is_dir()
    ) or any(repo.glob("*/tsconfig*.json"))
    if "typescript" not in found and nested_ts:
        found.insert(0, "typescript")
    if "javascript" in found and "typescript" in found:
        found = [item for item in found if item != "javascript"]
    return found


def detect_package_managers(repo: Path) -> list[str]:
    found: list[str] = []
    mapping = [
        ("pnpm", "pnpm-lock.yaml"),
        ("yarn", "yarn.lock"),
        ("npm", "package-lock.json"),
        ("poetry", "poetry.lock"),
        ("pip", "requirements.txt"),
        ("cargo", "Cargo.lock"),
    ]
    for name, marker in mapping:
        if exists(repo, marker):
            found.append(name)
    return found


def detect_frameworks(repo: Path) -> list[str]:
    found: list[str] = []
    if exists(repo, "nx.json"):
        found.append("nx")
    if exists(repo, "turbo.json"):
        found.append("turbo")
    if exists(repo, "angular.json"):
        found.append("angular")
    pkg = repo / "package.json"
    if pkg.is_file():
        text = pkg.read_text(encoding="utf-8", errors="replace")
        for name in ("next", "react", "vue", "nestjs", "express"):
            if f'"{name}"' in text:
                found.append(name)
    return found


def detect_monorepo(repo: Path) -> bool:
    markers = (
        "pnpm-workspace.yaml",
        "lerna.json",
        "nx.json",
        "turbo.json",
    )
    if any(exists(repo, marker) for marker in markers):
        return True
    app_roots = sum(1 for name in ("apps", "services", "packages") if (repo / name).is_dir())
    return app_roots >= 2


def detect_brownfield(repo: Path) -> bool:
    source_roots = ("apps", "services", "src", "packages", "contracts")
    if any((repo / name).is_dir() and any((repo / name).iterdir()) for name in source_roots if (repo / name).exists()):
        return True
    for marker in ("package.json", "pyproject.toml", "go.mod", "Cargo.toml"):
        if exists(repo, marker):
            return True
    return False


def detect_spec_kit(repo: Path) -> bool:
    return exists(repo, ".specify")


def detect_legacy_ges(repo: Path) -> bool:
    markers = (
        ".smc/ges-install-lock.json",
        ".smc/ges-install-receipt.json",
        ".agents/ges",
        ".smc/ges-bootstrap-receipt.json",
    )
    return any(exists(repo, marker) for marker in markers)


def detect_ci(repo: Path) -> list[str]:
    found: list[str] = []
    if (repo / ".github" / "workflows").is_dir():
        found.append("github-actions")
    if exists(repo, ".gitlab-ci.yml"):
        found.append("gitlab-ci")
    if exists(repo, "azure-pipelines.yml"):
        found.append("azure-pipelines")
    return found


def detect_existing(repo: Path) -> dict[str, bool]:
    return {
        "AGENTS.md": exists(repo, "AGENTS.md"),
        "CLAUDE.md": exists(repo, "CLAUDE.md"),
        ".agents": exists(repo, ".agents"),
        ".cursor": exists(repo, ".cursor"),
        ".codex": exists(repo, ".codex"),
        ".specify": exists(repo, ".specify"),
        ".smc": exists(repo, ".smc"),
        "CONTEXT.md": exists(repo, "CONTEXT.md"),
        "CONTEXT-MAP.md": exists(repo, "CONTEXT-MAP.md"),
        "docs/adr": exists(repo, "docs/adr"),
    }
