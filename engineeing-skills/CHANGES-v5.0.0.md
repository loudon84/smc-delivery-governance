# GES 5.0.0 changes

This candidate introduces adaptive governed work while retaining the delivery state machine and evidence authority.

- Restore all original 75 payload entries, root upgrade/verify tools and complete regenerated inventories; add compatibility repairs and regression tests.
- Add NONE/LEAN/FULL routing, minimum PRD grounding checks, monotonic profile checks and v2 preplan domain contracts for frontend (React/Vue), backend and ops.
- Complete v3.7 seed → project wrapper → static validator → Test Asset → Cursor projection → completion dispatch. v3.3–v3.6 validators remain available; v3.6 remains a supported completion contract.
- Preserve installed v2 consumer metadata and policy digests on implicit-profile updates. Explicit profile changes require re-grounding/review of affected Plans.
- Bind v3.7 TDD to actual command exit/output receipts, matching RED/GREEN command, method epoch and file content (including tests). Declared events alone never satisfy the gate. A failed or stale latest cycle blocks completion.
- Bind debug root cause to earlier reproduction receipts; require fresh successful final verification and enforce root-before-fix ordering.
- Non-PASS Plan reviews remain FULL even when stale. DELTA snapshots require a matching PASS-record/hash binding; tampering or missing binding escalates FULL.
- Reuse original v1 method runtime for old Plan contracts. v1-to-v2 migration is explicit, reasoned and archives prior method metadata without promoting old evidence.
