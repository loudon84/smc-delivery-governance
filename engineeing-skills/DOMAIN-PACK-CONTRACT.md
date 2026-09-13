# Domain Pack v2

Each pack declares preplan, engineering, review and verification providers, deterministic activation selectors, a policy lock and a Plan extension. Providers extend the canonical PRD/Plan; they never create competing state machines.

## Validation

preplan_section and preplan_validator bind domain intent before PRD approval. Each triggered Change ID must occur exactly once. Plan extension coverage uses the same activated changes. Shared table validation rejects missing rows/columns, duplicate IDs, malformed row shapes and unresolved placeholders. An explicit justified N/A is a decision, not a blank field.

## Compatibility and policy

The runtime reads Consumer Profile v2/v3 and Domain Pack v1/v2. Existing v2 consumers retain v1 metadata; v3 consumers use v2 packs and content-bound project policy. Plan v3.7 requires domain-activation.v2; legacy Plans require v1. New seed creation checks preplan readiness and never auto-approves unfinished intent. External policy fetching cannot change a blocking rule during execution.
