from __future__ import annotations

import re
from pathlib import Path

from ges.catalog.loader import Capability, SourcePin
from ges.errors import SPEC_KIT_RENDER_FAILED, SPEC_KIT_RUNTIME_INCOMPLETE, SPEC_KIT_UNRESOLVED_TOKEN, GesError
from ges.source_adapters.base import ProjectedFile
from ges.source_adapters.cache import resolve_path
from ges.stagelog import RENDER, emit

SELECTED_COMMANDS = ("constitution", "specify", "clarify", "plan")

COMMAND_TOKENS = {
    "__SPECKIT_COMMAND_CONSTITUTION__": "speckit-constitution",
    "__SPECKIT_COMMAND_SPECIFY__": "speckit-specify",
    "__SPECKIT_COMMAND_CLARIFY__": "speckit-clarify",
    "__SPECKIT_COMMAND_PLAN__": "speckit-plan",
    "__SPECKIT_COMMAND_TASKS__": "speckit-tasks",
    "__SPECKIT_COMMAND_IMPLEMENT__": "speckit-implement",
    "__SPECKIT_COMMAND_CONVERGE__": "speckit-converge",
    "__SPECKIT_COMMAND_CHECKLIST__": "speckit-checklist",
    "__SPECKIT_COMMAND_ANALYZE__": "speckit-analyze",
}

TEMPLATE_SOURCES = {
    "constitution": "templates/constitution-template.md",
    "specify": "templates/spec-template.md",
    "plan": "templates/plan-template.md",
}

TOKEN_RE = re.compile(r"\{SCRIPT\}|__SPECKIT_COMMAND_[A-Z_]+__")


def script_rel(command: str) -> str:
    return f".specify/.ges/runtime/scripts/{command}.py"


def command_rel(command: str) -> str:
    return f".specify/.ges/commands/{command}.md"


def template_rel(name: str) -> str:
    return f".specify/.ges/runtime/templates/{Path(name).name}"


def resolver_script(command: str) -> bytes:
    return (
        "#!/usr/bin/env python3\n"
        "import json\n"
        "print(json.dumps({\n"
        '    "FEATURE_DIR": ".",\n'
        '    "FEATURE_SPEC": "",\n'
        '    "IMPL_PLAN": "",\n'
        '    "BRANCH": "",\n'
        '    "AVAILABLE_DOCS": [],\n'
        '    "TEMPLATE_CONTENT": "",\n'
        f'    "capability": "{command}",\n'
        "}))\n"
    ).encode("utf-8")


def render_command(raw: str, command: str) -> str:
    rendered = raw.replace("{SCRIPT}", script_rel(command))
    for token, name in COMMAND_TOKENS.items():
        rendered = rendered.replace(token, name)
    return rendered


def leftover_tokens(text: str) -> list[str]:
    return sorted(set(TOKEN_RE.findall(text)))


def validate_runtime(files: dict[str, bytes], commands: list[str]) -> None:
    required = [command_rel(item) for item in commands]
    required += [script_rel(item) for item in commands]
    missing = [rel for rel in required if rel not in files]
    if missing:
        raise GesError(
            SPEC_KIT_RUNTIME_INCOMPLETE,
            f"selected Spec Kit runtime missing: {missing[0]}",
            details={"missing": missing},
        )
    leftovers: dict[str, list[str]] = {}
    for rel in required:
        found = leftover_tokens(files[rel].decode("utf-8", errors="replace"))
        if found:
            leftovers[rel] = found
    if leftovers:
        first = next(iter(leftovers))
        raise GesError(
            SPEC_KIT_UNRESOLVED_TOKEN,
            f"unresolved Spec Kit token in {first}: {leftovers[first][0]}",
            details={"tokens": leftovers},
        )


def render_selected(pin: SourcePin, capabilities: list[Capability]) -> list[ProjectedFile]:
    emit(RENDER, "start", source=pin.id)
    commands = [
        cap.id.split(".", 1)[1]
        for cap in capabilities
        if cap.projection_type == "speckit-capability" and cap.id.split(".", 1)[1] in SELECTED_COMMANDS
    ]
    files: dict[str, bytes] = {}
    try:
        for command in commands:
            files[script_rel(command)] = resolver_script(command)
            source = next(cap.source_path for cap in capabilities if cap.id.endswith(f".{command}"))
            raw = resolve_path(pin, source).read_text(encoding="utf-8")
            files[command_rel(command)] = render_command(raw, command).encode("utf-8")
            template = TEMPLATE_SOURCES.get(command)
            if template:
                src = resolve_path(pin, template)
                dest = template_rel(template)
                files[dest] = render_command(src.read_text(encoding="utf-8"), command).encode("utf-8")
        validate_runtime(files, commands)
    except GesError:
        raise
    except Exception as exc:
        raise GesError(SPEC_KIT_RENDER_FAILED, f"Spec Kit render failed: {exc}") from exc
    emit(RENDER, "complete", commands=commands, files=len(files))
    return [
        ProjectedFile(
            relpath=rel,
            content=content,
            capability=f"speckit.{Path(rel).stem}" if rel.startswith(".specify/.ges/commands/") else None,
            source=pin.id,
            source_sha=pin.commit_sha,
            kind="specify" if "/commands/" in rel else "specify-runtime",
            ownership_type="FILE",
        )
        for rel, content in files.items()
    ]
