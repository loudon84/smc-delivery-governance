# External Adapter Capability Contract

GES v6 adapters report capability; they never own local Delivery or Roadmap truth.

## Required fields

| Field | Meaning |
|---|---|
| `adapter` | Adapter name (multica, hermes, cursor-cli, …) |
| `version` | Adapter/runtime version string |
| `request_id` / `result_id` | Correlated dispatch identities |
| `output_digest` | Digest of returned artifacts |
| `tool_access` | `ADVISORY` or `ENFORCED` |
| `token_availability` | `measured`, `estimated`, or `missing` |
| `status` | `planned`, `adapter_ready`, or `verified` |

## Rules

- External `DONE` is an execution report only; it cannot write local Roadmap DONE.
- Receipts for a stale context epoch are rejected (`CONTEXT_EPOCH_MISMATCH`).
- Duplicate `dispatch_id` is de-duplicated; it does not double-complete a Todo.
- Unverified adapters remain `planned` / `adapter_ready` and must not claim production ENFORCED isolation.
- Implementation helper: `context-engine/adapter.py` and `context-engine/dispatch.py`.
