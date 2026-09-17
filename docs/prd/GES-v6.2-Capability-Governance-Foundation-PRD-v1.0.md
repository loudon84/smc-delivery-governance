---
prd_id: PRD-GES6.2-CAPABILITY-GOVERNANCE-FOUNDATION
status: BINDING_GRILLME
target_release: GES 6.0.0-alpha.4
title: GES 6.0.0-alpha.4 — 6.2 Foundation (Capability Governance)
version: "1.1"
branch: feat/ges-v6.1
product_version: 6.0.0-alpha.4
distribution_version: 1.2.1
updated_at: "2026-09-17"
change_type: ["BROWNFIELD_CHANGE", "PARALLEL_GOVERNANCE"]
marketing_name: "6.2 Foundation"
---

# GES 6.0.0-alpha.4 — 6.2 Foundation (Capability Governance)

Marketing name **6.2 Foundation**. Product version is **`6.0.0-alpha.4`**. This slice governs the **parallel** provider layer only. It does not thaw Composer, does not change Gate A/B, and is not 6.2 GA.

Binding source: grill-me Q1–Q28. Where this document previously said “v6.2 GA”, “Capability → Work → Evidence → Release”, “ges capability upgrade”, “Capability Install MAY network”, “`.ges/work/`”, “change evidence-snapshot / Release Gate”, “register codegraph/OpenSpec”, or “APPROVED_FOR_PLAN”, those sentences are superseded by §0.

# 0. Binding Grill-me Decisions

These rows are the implementation contract. A later section that conflicts with this table is stale.

| ID | Decision |
|---|---|
| Q1 | Product `6.0.0-alpha.4`. Marketing name **6.2 Foundation**. Not 6.2 GA / READY. |
| Q8 | Stay on `feat/ges-v6.1`. `__distribution_version__` stays `1.2.1`. |
| Q2 | Registry governs the **parallel** layer only (RTK and future providers). Composer `ges/catalog/capabilities.yaml`, `resolve_selection`, and frozen `lock.requested` MUST NOT change. |
| Q3 | **Foundation only**: overlay + lifecycle + compatibility framework + policy overlay + `ges capability` CLI. MUST NOT implement Work capability binding or Release Gate checks. |
| Q4 | Persist only a thin consumer overlay. Package catalog stays `ges/catalog/providers.yaml`. MUST NOT persist plan/status into `project.yaml`, `lock.json`, or `install-receipt.json`. MUST NOT write consumer `registry.yaml` or consumer `compatibility.yaml`. |
| Q17 | Overlay paths: `.ges/capabilities/installed.yaml` and `.ges/capabilities/policy.yaml`. MUST NOT create `.ges/policy.yaml`. Governance remains `.ges/governance/policy.yaml`. |
| Q18 | Overlay files are created only by `ges capability add` / `remove`. `ges init` MUST NOT create overlay. If overlay is missing on `add`, generate `policy.yaml` from resolver default level. |
| Q5 | `add` = write overlay + probe. MUST NOT download, install, rewrite PATH, or wrap Agent shell. Composer IDs MUST NOT be added. |
| Q9 | Register only `command-output.rtk`. Do not register codegraph, ponytail, caveman, comet, or Composer IDs. Spec Kit on init remains a **display mapping** of existing `speckit.*`. Do not invent `spec-kit`. |
| Q10 | Parallel states: `AVAILABLE → SELECTED → INSTALLED` plus probe `VERIFIED` / `NOT_READY` / `missing`. No `INSTALLING`. `INSTALLED` = row in `installed.yaml`. `VERIFIED` = **this** probe PASS. MUST NOT treat INSTALLED as VERIFIED. |
| Q7 / Q11 | New top-level `ges capability` with `list`, `add`, `remove`, `doctor <id>` only. No `upgrade`. No `ges doctor capability`. |
| Q21 | `list` prints id, resolver level, policy level (resolver if no overlay), installed?, probe status, reason. Human table + `--json`. May probe. MUST NOT write disk. |
| Q27 | `list` always exit 0, even if policy `required` is not installed. |
| Q19 | `remove` deletes only that id from `installed.yaml`. Policy row stays. Missing installed id is an error (not silent success). Last remove MUST NOT delete overlay files; installed may be an empty list; MUST NOT delete `policy.yaml`. |
| Q22 | Composer id → `COMPOSER_CAPABILITY_FROZEN` (not `RECONFIGURE_NOT_SUPPORTED`). Unknown parallel id → `CAPABILITY_NOT_FOUND`. `prohibited` → `CAPABILITY_PROHIBITED`. |
| Q23 | Repeat `add` of `command-output.rtk` is idempotent: probe again, refresh status/version, exit 0. Duplicate rows in `providers.yaml` remain loader BLOCK. |
| Q12 | Policy `required` missing MUST NOT set `ges doctor` overall to `BLOCKED`. |
| Q13 | Consumer policy **overrides** resolver level. Reason stays analyzer `kind`. `prohibited` + resolver recommended → do not add; `add` BLOCK. |
| Q26 | Non-default policy levels are **hand-edited** in `policy.yaml` only. No policy CLI. Invalid policy schema BLOCK. |
| Q28 | `ges capability doctor <id>` probes only, stdout `ges.capability-status.v1`, no disk write. Works without overlay. Unknown id → `CAPABILITY_NOT_FOUND`. Composer id → `COMPOSER_CAPABILITY_FROZEN`. |
| Q6 / Q16 | MUST NOT change `ges.evidence-snapshot.v1`. MUST NOT change Gate A/B. Capability evidence is stdout-only, reuse `ges.capability-status.v1`. No `.ges/capabilities/evidence/**`. |
| Q15 | Compatibility engine is framework-only this slice: read package `incompatible` (empty). OpenSpec is not implemented. |
| Q20 | `ges init` still prints Capability Recommendation before confirm. Missing RTK MUST NOT skip/fail apply. Completion MUST NOT mark missing RTK as FAIL. |
| Q14 / Q24 | Golden Consumer `E:\git\smc-copilot-desktop`. Independent runner (may extend `run_golden_capability`). Host `rtk` not required. `GOLDEN_*_BLOCKED` ≠ synthetic FAIL. Do not claim alpha.4 READY unless Golden PASSes. New `lat.md/ges6/capability-governance.md` and `capability-governance-tests.md` with `require-code-mention`. Existing ges6 bootstrap / governance / large-repo / capability-resolver suites MUST remain PASS. |
| Q25 | Inherited, not re-opened: `ges check` ignores RTK/overlay; preflight does not grow RTK; `ges doctor` still emits `capabilities[]`/`warnings[]`; recommended missing is WARNING and does not BLOCK overall; Windows `shutil.which("rtk")`; LLM calls = 0. |

Implied: no LLM; no `.ges/work/` tree; no Release Gate capability check; marketing “6.2” ≠ product 6.2.0.

# 1. Background

GES already closed Composer bootstrap, Alpha.2 Work/Policy/Evidence/Gate, and Alpha.3 parallel discovery (`providers.yaml`, ephemeral plan, RTK verify-only).

This slice adds **governance of that parallel layer**: a consumer overlay, a small lifecycle, and `ges capability` commands. It does not replace Composer Desired State.

# 2. Product Goal

Give each **parallel** provider:

- identity in `ges/catalog/providers.yaml`
- consumer selection in `installed.yaml`
- consumer policy in `policy.yaml`
- probe evidence on stdout
- list/add/remove/doctor-id without thawing Composer

# 3. Product Boundary

GES this slice owns:

- package provider catalog (still only `command-output.rtk`)
- `.ges/capabilities/installed.yaml` + `policy.yaml`
- parallel lifecycle + empty incompatible matrix
- `ges capability list|add|remove|doctor`

GES this slice does not own:

- Composer selection / projection / `lock.requested`
- binary install or PATH
- Agent shell wrap / output compression
- Gate A/B verdicts or `ges.evidence-snapshot.v1`
- Work registry (stays `.ges/governance/works/`)
- code generation, model pick, IDE, business requirements
- OpenSpec, CodeGraph, Ponytail, Caveman, Comet

# 4. Architecture

```text
GES
├── Composer              capabilities.yaml + lock.requested   (frozen)
├── Parallel discovery    providers.yaml + ephemeral plan      (Alpha.3)
├── Parallel governance   installed.yaml + policy.yaml + CLI   (this slice)
├── Work / Evidence / Gate .ges/governance/**                  (Alpha.2, unread)
└── command-output.rtk    verify-only probe
```

# 5. Package Catalog vs Consumer Overlay

Package (read-only in the GES distribution):

```text
ges/catalog/providers.yaml    # only command-output.rtk; incompatible: []
```

Consumer (created on first `add`/`remove` only):

```text
.ges/capabilities/installed.yaml
.ges/capabilities/policy.yaml
```

`installed.yaml` records selected parallel ids (INSTALLED).  
`policy.yaml` records required / recommended / optional / prohibited.  
Default policy level on first create = resolver level. Later edits are hand-only.

MUST NOT write capability overlay into `lock.json`.

# 6. Lifecycle

```text
AVAILABLE → SELECTED → INSTALLED
                 ↘ probe → VERIFIED | NOT_READY | missing
```

No `INSTALLING`. `DEPRECATED` / `REMOVED` are out of scope except `remove` dropping the installed row.

# 7. Compatibility

Read `incompatible` from the package catalog. This slice’s matrix is empty.  
Composer ownership conflicts stay in Composer (`CAPABILITY_OWNERSHIP_CONFLICT`).  
OpenSpec is not implemented.

# 8. Policy

```yaml
required: []
recommended: []
optional: []
prohibited: []
```

| Level | Overlay / CLI | `ges doctor` overall |
|---|---|---|
| required | shown on `list`; does not fail `list` exit | MUST NOT BLOCK |
| recommended | WARNING on doctor if missing/not ready | MUST NOT BLOCK |
| optional | no extra check | unchanged |
| prohibited | `add` → `CAPABILITY_PROHIBITED` | MUST NOT BLOCK |

Policy overrides resolver. Reason string remains analyzer `kind`.

# 9. Resolver

Unchanged Alpha.3 rules: brownfield OR monorepo → RTK recommended; greenfield+single → optional; LLM = 0; same facts → same plan; plan still ephemeral.

# 10. Evidence

Stdout `ges.capability-status.v1` from `add` (after probe), `list` (optional probe), and `ges capability doctor <id>`.

Forbidden: persist command output, secrets, source bytes; persist capability evidence under `.ges`; feed status into Gate.

# 11. CLI

```text
ges capability list [--json]
ges capability add <id>
ges capability remove <id>
ges capability doctor <id>
```

`ges init` still prints Capability Recommendation before confirm.

# 12. Failure Contract

| Failure | Result |
|---|---|
| Composer id on add/doctor | `COMPOSER_CAPABILITY_FROZEN` |
| unknown parallel id | `CAPABILITY_NOT_FOUND` |
| prohibited add | `CAPABILITY_PROHIBITED` |
| remove missing installed id | error (not silent) |
| invalid policy schema | BLOCK |
| duplicate row in `providers.yaml` | BLOCK |
| required not installed | `list` shows it; exit 0; doctor overall unchanged |
| recommended missing | doctor WARNING; overall unchanged |
| RTK binary missing | status `missing` |
| `rtk --version` fail | `NOT_READY` |
| Golden missing/dirty/unrun | `GOLDEN_*_BLOCKED` ≠ synth FAIL |

# 13. Acceptance Criteria

### A-CAP-REG-001

`command-output.rtk` is the only parallel id.

### A-CAP-REG-002

Duplicate id in `providers.yaml` BLOCK.

### A-CAP-LIFE-001

`add` writes installed and probes; no INSTALLING.

### A-CAP-LIFE-002

Composer `add` is `COMPOSER_CAPABILITY_FROZEN`. Repeat `add` is idempotent.

### A-CAP-COMP-001 / 002

Empty incompatible matrix loads; no fabricated OpenSpec conflict.

### A-CAP-POLICY-001

Hand-edited `required` does not BLOCK doctor overall or `list` exit.

### A-CAP-POLICY-002

Recommended missing remains doctor WARNING.

### A-CAP-EVID-001

`doctor <id>` emits `ges.capability-status.v1` and writes no files.

### A-CAP-EVID-002

Capability status is not written into `ges.evidence-snapshot.v1`.

### A-CAP-RESOLVE-001 / 002

Same facts → same plan; LLM = 0 (Alpha.3, still required).

# 14. Test Strategy

Synthetic: overlay create-on-add, remove-installed-only, list columns/exit 0, Composer frozen, policy override, idempotent add, empty incompatible, doctor-id no-write.

Regression: bootstrap, governance, large-repo, capability-resolver MUST PASS.

Golden: `E:\git\smc-copilot-desktop`; host rtk not required; BLOCKED ≠ synth FAIL.

Lat: `lat.md/ges6/capability-governance.md`, `capability-governance-tests.md` with `require-code-mention: true`.

# 15. Future (not this slice)

- Work `required_capabilities` / Release Gate
- `upgrade`
- registering codegraph / ponytail / caveman / comet
- OpenSpec
- thawing Composer
- product 6.2.0 / READY banner

# 16. Definition of Done

- [ ] Product version `6.0.0-alpha.4`
- [ ] Overlay paths + schemas; no lock/receipt writes
- [ ] `ges capability list|add|remove|doctor`
- [ ] RTK verify-only; Composer add frozen
- [ ] Empty incompatible matrix
- [ ] Doctor overall unchanged by required/recommended RTK
- [ ] Gate / evidence-snapshot unchanged
- [ ] lat + `@lat` tests PASS; existing ges6 suites PASS
- [ ] Golden runner exists; slice READY only if that runner PASSes

# 17. Final Engineering Contract

```text
Composer freeze
        +
Resolver ephemeral plan (Alpha.3)
        +
Consumer overlay + ges capability (this slice)
        ↓
stdout status (ges.capability-status.v1)
        ↓
Gate unread (Alpha.2)
```

Do not claim 6.2 Foundation / alpha.4 READY until Golden on `smc-copilot-desktop` PASSes.
