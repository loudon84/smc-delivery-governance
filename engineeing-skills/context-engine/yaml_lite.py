"""Minimal YAML subset loader. GES Core does not depend on PyYAML."""
from __future__ import annotations

from typing import Any


def _parse_scalar(raw: str) -> Any:
    value = raw.strip()
    if value in {"", "~", "null", "Null", "NULL"}:
        return None
    if value in {"true", "True", "TRUE"}:
        return True
    if value in {"false", "False", "FALSE"}:
        return False
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [_parse_scalar(part) for part in inner.split(",")]
    try:
        if value.isdigit() or (value.startswith("-") and value[1:].isdigit()):
            return int(value)
    except ValueError:
        pass
    return value


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def loads(text: str) -> Any:
    lines: list[tuple[int, str]] = []
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        stripped = raw.split(" #", 1)[0].rstrip()
        lines.append((_indent(raw), stripped.lstrip()))
    if not lines:
        return {}
    value, _ = _parse_block(lines, 0, lines[0][0])
    return value


def _parse_block(lines: list[tuple[int, str]], index: int, indent: int) -> tuple[Any, int]:
    if index >= len(lines):
        return {}, index
    if lines[index][1].startswith("- "):
        return _parse_list(lines, index, indent)
    return _parse_map(lines, index, indent)


def _parse_map(lines: list[tuple[int, str]], index: int, indent: int) -> tuple[dict[str, Any], int]:
    out: dict[str, Any] = {}
    while index < len(lines):
        level, content = lines[index]
        if level < indent:
            break
        if level > indent:
            raise ValueError(f"YAML_INDENT_INVALID: {content}")
        if content.startswith("- "):
            break
        if ":" not in content:
            raise ValueError(f"YAML_MAPPING_INVALID: {content}")
        key, rest = content.split(":", 1)
        key = key.strip()
        rest = rest.strip()
        index += 1
        if rest:
            out[key] = _parse_scalar(rest)
            continue
        if index < len(lines) and lines[index][0] > indent:
            child, index = _parse_block(lines, index, lines[index][0])
            out[key] = child
        else:
            out[key] = None
    return out, index


def _parse_list(lines: list[tuple[int, str]], index: int, indent: int) -> tuple[list[Any], int]:
    out: list[Any] = []
    while index < len(lines):
        level, content = lines[index]
        if level < indent:
            break
        if not content.startswith("- "):
            break
        item = content[2:].strip()
        index += 1
        if item and ":" in item and not item.startswith("{") and not item.startswith("["):
            key, rest = item.split(":", 1)
            node: dict[str, Any] = {key.strip(): _parse_scalar(rest) if rest.strip() else None}
            if index < len(lines) and lines[index][0] > level:
                nested, index = _parse_block(lines, index, lines[index][0])
                if isinstance(nested, dict):
                    if rest.strip() == "":
                        node[key.strip()] = nested
                    else:
                        node.update(nested)
                else:
                    node[key.strip()] = nested
            out.append(node)
        elif item:
            out.append(_parse_scalar(item))
        else:
            if index < len(lines) and lines[index][0] > level:
                child, index = _parse_block(lines, index, lines[index][0])
                out.append(child)
            else:
                out.append(None)
    return out, index


def load(path) -> Any:
    from pathlib import Path

    return loads(Path(path).read_text(encoding="utf-8"))
