# Harness Projection

Shared skills land in `.agents/skills/`. Cursor is the Alpha.1 required harness. AGENTS.md maps each work stage to a concrete skill name.

Same path plus different content is `PROJECTION_PATH_CONFLICT`. Selected Spec Kit skills are official `.cursor/skills/speckit-*` copies, not GES wrappers. Marker upsert is [[ges/harness_adapters/agents_md.py#apply_marker]]. Structural discovery is [[ges/cursor_probe.py#structural_discovery]]. Runtime discovery parses Cursor CLI `--output-format json` and unwraps the `type=result` envelope.
