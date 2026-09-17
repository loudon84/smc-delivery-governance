---
prd_id: PRD-GES6-CAPABILITY-RESOLVER-RTK-PROVIDER
status: BINDING_GRILLME
target_release: GES 6.0.0-alpha.3
title: GES v6.0-alpha.3 — RTK Provider + Capability Resolver PRD
version: "1.1"
branch: feat/ges-v6.1
product_version: 6.0.0-alpha.3
distribution_version: 1.2.1
updated_at: "2026-09-17"
change_type: ["BROWNFIELD_CHANGE", "DISCOVERY_LAYER"]
---

# GES v6.0-alpha.3 Capability Resolver + RTK Provider

Alpha.3 adds a **parallel capability discovery layer** and the first Execution Efficiency provider (`command-output.rtk`). It does not replace Composer catalog selection, does not thaw `lock.requested`, and does not change Gate A/B.

Binding source: grill-me Q1–Q22. Where this document previously said “install”, “pain+policy”, “wrap shell”, or “Golden PASS required”, those sentences are superseded by §0.

# 0. Binding Grill-me Decisions

These rows are the implementation contract. A later section that conflicts with this table is stale.

| ID | Decision |
|---|---|
| Q1 | Independent Alpha.3 slice on `feat/ges-v6.1`. |
| Q8 | Product version `6.0.0-alpha.3`. `__distribution_version__` stays `1.2.1`. |
| Q2 | Resolver is a **parallel discovery layer**. Composer `ges/catalog/capabilities.yaml`, `resolve_selection`, and frozen `lock.requested` MUST NOT change. Adding `command-output.rtk` MUST NOT raise `RECONFIGURE_NOT_SUPPORTED`. |
| Q9 | New catalog file `ges/catalog/providers.yaml`. ID stays `command-output.rtk`. Plan “Required: Spec Kit” is a **display mapping** onto the existing `speckit.*` closure. |
| Q20 | Register only `command-output.rtk`. `incompatible: []`. Do not register codegraph, ponytail, caveman, or Comet in this slice. |
| Q10 | Capability Plan is recomputed every init/doctor. MUST NOT persist into `project.yaml`, `lock.json`, or `install-receipt.json`. |
| Q3 / Q11 | RTK is **verify-only**. GES MUST NOT download, install, or rewrite PATH. GES MUST NOT wrap Agent shell or compress user command output. |
| Q12 | A-RTK-002 (exit code) and A-RTK-004 (full logs) are **RTK product contracts**, not this slice. No wrapper implementation. |
| Q4 / Q13 | `pain_profile` is **not** a stored file and **not** governance `policy.yaml`. Recommend RTK when `repository_lifecycle == brownfield` OR `layout == monorepo`. Reason is the existing analyzer `kind` (e.g. `brownfield-monorepo`). Pure `greenfield` + `single` → optional. LLM calls = 0. |
| Q14 | Missing RTK MUST NOT block `ges init` apply. Plan prints before confirm. After apply, doctor may WARNING. Completion text MUST NOT mark RTK missing as FAIL. |
| Q5 / Q19 | Doctor adds `capabilities[]` and reuses `warnings[]`. PATH miss → missing + WARNING. `rtk --version` nonzero/unparseable → that row `NOT_READY`. Success → `READY`. Overall MUST NOT become `BLOCKED` because a recommended provider is missing/invalid. `ges check` ignores RTK. Windows: `shutil.which` (covers `rtk.exe`). |
| Q6 / Q17 | stdout-only schemas `ges.capability-plan.v1` and `ges.capability-status.v1`. Additive optional `capabilities[]` on `ges.readiness.v1`; keep existing `warnings[]`. MUST NOT change `ges.evidence-snapshot.v1`. MUST NOT feed compressed output into Gate. |
| Q18 | No new top-level CLI. Human plan on `ges init`; machine status on `ges doctor` JSON. Preflight does not grow an RTK check. |
| Q7 / Q15 / Q21 | Golden Consumer is `E:\git\smc-copilot-desktop`. Independent runner `ges.acceptance.run_golden_capability`. Host `rtk` is **not** required. `GOLDEN_CAPABILITY_BLOCKED` ≠ synthetic FAIL. Do not claim slice READY unless Golden PASSes. |
| Q16 | OpenSpec / Comet / future providers are **out of scope**. Keep the one-Intent-owner rule as a non-implemented constraint. |
| Q22 | New `lat.md/ges6/capability-resolver.md` and `capability-resolver-tests.md` with `require-code-mention`. Existing ges6 bootstrap / governance / large-repo tests MUST remain PASS. |

Implied, not re-litigated: no LLM; Gate A/B unread capability status; no READY claim without Golden.

# 1. Background

GES v6.0 already closed Composer bootstrap (Matt, Spec Kit, Superpowers), Governance Backplane, and Git-aware Business Source Guard v2.

Alpha.3 upgrades **discovery**, not install:

```text
Repo Facts (analyzer kind / lifecycle / layout)
        ↓
Capability Resolver  (parallel, ephemeral)
        ↓
Capability Plan + Provider Status
        ↓
ges init text / ges doctor JSON
        ↓
Governance Gate   (unchanged; does not read RTK)
```

First provider: **Command Output / RTK**, verify-only.

# 2. Product Boundary

## Capability Resolver

Responsible for:

- reading analyzer-repeatable repo facts;
- applying deterministic rules;
- emitting an ephemeral Capability Plan;
- emitting per-provider status for doctor.

Not responsible for:

- PRD generation;
- plan execution;
- code generation;
- Gate verdicts;
- mutating Composer requested/closed sets;
- persisting a second capability SOT.

## RTK Provider

Position: Execution Efficiency **discovery target**.

This slice is responsible for:

- detecting `rtk` on PATH;
- reading version via `rtk --version`;
- classifying missing / invalid / READY.

This slice is **not** responsible for:

- installing RTK;
- wrapping shell;
- compressing command output;
- changing test results, Evidence snapshots, or Gates;
- modifying business source.

# 3. Architecture

```text
GES
├── Governance          Work / Artifact / Evidence / Gate   (Alpha.2, frozen semantics)
├── Intent              Spec Kit                            (Composer)
├── Engineering Method  Superpowers                         (Composer)
├── Repository Intel    Matt                                (Composer)
├── Capability Resolver parallel discovery                  (Alpha.3)
└── Execution Efficiency
    └── RTK Provider    verify-only                         (Alpha.3)
```

Composer adapters remain `matt` / `spec-kit` / `superpowers` only.

# 4. Provider Catalog

File: `ges/catalog/providers.yaml`.

MUST NOT add `command-output.rtk` to `ges/catalog/capabilities.yaml`.

```yaml
schema: ges.providers.v1
providers:
  - id: command-output.rtk
    category: execution-efficiency
    provider: rtk
    default_level: recommended
    incompatible: []
    health_checks:
      - binary
      - version
      - integration
```

This slice registers **only** that row. `incompatible` is empty.

Display levels on the Plan:

| Level | Meaning in Alpha.3 |
|---|---|
| required | Informational mapping of Composer-required intent (Spec Kit). Not a new install. |
| recommended | Verify if present; missing is WARNING. |
| optional | Shown, not required to verify. |
| incompatible | Empty this slice. |

# 5. Capability Resolver

## Input (binding)

```yaml
repository:
  lifecycle: brownfield | greenfield    # analyzer
  layout: monorepo | single             # analyzer
  kind: <existing repo-profile kind>    # e.g. brownfield-monorepo
```

MUST NOT invent stored `pain_profile` fields (`command_noise`, `navigation_cost`, `over_engineering`). MUST NOT read governance `policy.yaml` for pain.

## Output

Schema `ges.capability-plan.v1` (stdout / doctor embed, not a consumer file):

```yaml
schema: ges.capability-plan.v1
required:
  - speckit          # display mapping of existing speckit.* closure; not a new ID
recommended:
  - command-output.rtk
optional: []
incompatible: []
reasons:
  command-output.rtk: brownfield-monorepo
```

Rules:

- deterministic and unit-testable;
- LLM calls = 0;
- every recommended provider MUST have a reason (A-CR-003);
- reason for RTK is the analyzer `kind`.

## Recommend rule (binding)

- `lifecycle == brownfield` OR `layout == monorepo` → `command-output.rtk` is **recommended**.
- `lifecycle == greenfield` AND `layout == single` → **optional**.
- Same facts MUST yield the same plan (A-CR-001).

# 6. RTK Verify Contract

Capability identity:

```yaml
id: command-output.rtk
category: execution-efficiency
provider: rtk
```

This slice probe (no wrapper):

```text
shutil.which("rtk")  →  missing | found
rtk --version        →  parse version or invalid
integration          →  probe exit 0 and version non-empty
```

| Case | capability-status | doctor |
|---|---|---|
| PATH has no `rtk` | `missing` | WARNING; overall unchanged by this row |
| binary present, `--version` fails or unparseable | `NOT_READY` | that row `NOT_READY`; overall not BLOCKED |
| `--version` succeeds | `READY` | no RTK WARNING |

Forbidden in this slice:

- change command results;
- hide failures;
- affect Gate;
- wrap Agent → Shell → RTK → compressed context.

A-RTK-002 / A-RTK-004 remain future RTK-runtime contracts.

# 7. GES Doctor

`ges.readiness.v1` gains optional `capabilities[]` (additive). Existing `warnings[]` is reused. `run_doctor` MUST emit both.

`ges check` MUST ignore RTK and MUST NOT fail because RTK is missing.

Example capability row:

```json
{
  "capability_id": "command-output.rtk",
  "provider": "rtk",
  "status": "READY",
  "version": "…",
  "health_checks": [
    {"name": "binary", "status": "PASS"},
    {"name": "version", "status": "PASS"},
    {"name": "integration", "status": "PASS"}
  ]
}
```

Missing recommended provider:

- WARNING;
- MUST NOT set doctor overall to FAIL/BLOCKED;
- unless a **future** explicit policy says otherwise (not this slice).

# 8. ges init Integration

```text
ges init
  → repository analysis
  → Composer compose (unchanged freeze)
  → Capability Resolver (ephemeral)
  → print Capability Recommendation
  → confirm
  → apply Composer plan
  → ges check (no RTK)
  → ges doctor (capabilities[] + warnings[])
```

Missing RTK MUST NOT block apply. `GES_APPLY_OK` remains valid.

Human print (no CodeGraph in this slice):

```text
Capability Recommendation

Required:
  ✓ Spec Kit

Recommended:
  ○ command-output.rtk    (reason: brownfield-monorepo)

Optional:
  (none)
```

Use `✓` when status is READY; `○` when missing/optional; do not print a FAIL line for missing RTK.

No new top-level command (`ges capability …` is out of scope).

# 9. Evidence Contract

Two stdout-only schemas:

- `ges.capability-plan.v1` — plan + reasons
- `ges.capability-status.v1` — one provider row (id, provider, status, version, health_checks)

MUST NOT persist command output, file bytes, or secrets.

MUST NOT enlarge `ges.evidence-snapshot.v1`.

MUST NOT persist plan/status into project/lock/receipt.

External Golden evidence MAY store copies **outside** the GES candidate tree.

# 10. Governance Boundary

RTK is Execution Layer discovery, not Governance Evidence.

Correct:

```text
command execution → exit code + full log (owner: runtime / future wrapper)
                 → GES Gate evidence still CI + review only
```

Forbidden:

```text
compressed RTK output → Gate PASS
```

Gate A/B, Work, Policy, and `ges.evidence-snapshot.v1` stay Alpha.2 semantics.

# 11. Conflict Contract (non-implemented this slice)

## Spec Kit / OpenSpec

One Intent owner. One SOT. This slice does not add OpenSpec.

## Comet

Comet is an Execution Harness Profile, not a normal provider. This slice does not register `execution.comet`.

# 12. Acceptance Criteria

## Capability Resolver

### A-CR-001

Same analyzer facts produce the same plan.

### A-CR-002

Resolver LLM calls = 0.

### A-CR-003

Every recommended provider has a reason.

### A-CR-004

Brownfield or monorepo → RTK recommended; greenfield-single → optional.

### A-CR-005

Emitting the plan does not mutate `lock.requested` or raise `RECONFIGURE_NOT_SUPPORTED`.

## RTK (this slice)

### A-RTK-001

Probe binary / version / integration per §6.

### A-RTK-002

**DEFERRED.** RTK product contract: wrapper preserves exit code. Not implemented here.

### A-RTK-003

RTK status MUST NOT change Gate A/B verdicts or `ges.evidence-snapshot.v1`.

### A-RTK-004

**DEFERRED.** RTK product contract: full logs remain traceable after compression. Not implemented here.

## GES Integration

### A-GES-CAP-001

`ges doctor` JSON includes `capabilities[]` (and `warnings[]` when missing).

### A-GES-CAP-002

`ges init` prints a Capability Recommendation before confirm.

### A-GES-CAP-003

Recommended missing is WARNING, not BLOCK, and does not fail `ges check`.

### A-GES-CAP-004

No new top-level CLI command.

# 13. Failure Contract

| Failure | Result |
|---|---|
| RTK missing | WARNING; apply continues |
| RTK invalid | that row `NOT_READY`; overall not BLOCKED |
| provider schema invalid | BLOCK implementation / test FAIL |
| nondeterministic resolver | FAIL |
| writing plan into lock/requested | FAIL (forbidden) |
| wrapping shell / installing RTK | FAIL (forbidden) |
| capability status written into Gate evidence | FAIL (forbidden) |
| Golden not run or BLOCKED | not PASS; not slice READY |

`capability conflict` BLOCK does not apply: `incompatible` is empty.

# 14. Test Strategy

## Synthetic (required)

- rule matching (A-CR-001/003/004/005);
- provider schema;
- missing / invalid / READY probe table;
- doctor `capabilities[]` / `warnings[]` without overall BLOCKED;
- init prints plan and still applies;
- Gate evidence schema unchanged;
- Composer freeze + existing ges6 bootstrap / governance / large-repo suites PASS.

Lat:

- `lat.md/ges6/capability-resolver.md`
- `lat.md/ges6/capability-resolver-tests.md` with `require-code-mention: true`

## Golden

Consumer: `E:\git\smc-copilot-desktop`

Runner: `ges.acceptance.run_golden_capability`

Oracles (host `rtk` **not** required):

- Composer/bootstrap regression unchanged;
- Capability Plan printed;
- missing RTK → WARNING;
- Gate A/B unread RTK.

If the runner cannot execute: `GOLDEN_CAPABILITY_BLOCKED`. That is not a synthetic FAIL and is not slice READY.

# 15. Future Capability (not this slice)

Later resolver targets may include:

- `repo-intelligence.codegraph`
- `code-quality.ponytail`
- `conversation.caveman`
- `execution.comet`

Constraint remains: one capability, one owner, one SOT. This slice MUST NOT register them.

# 16. Definition of Done

- [ ] `ges/catalog/providers.yaml` with only `command-output.rtk`
- [ ] Schemas `ges.capability-plan.v1` + `ges.capability-status.v1`
- [ ] Additive `capabilities[]` on `ges.readiness.v1`
- [ ] Deterministic resolver (brownfield/monorepo rule)
- [ ] RTK PATH/`--version` probe only
- [ ] `ges init` prints plan; missing RTK does not block apply
- [ ] `ges doctor` JSON includes capabilities/warnings; check ignores RTK
- [ ] No lock/project/receipt persistence
- [ ] No wrapper; A-RTK-002/004 deferred
- [ ] Gate / evidence-snapshot unchanged
- [ ] lat + `@lat` synthetic tests PASS
- [ ] Existing ges6 suites PASS
- [ ] Golden runner exists; slice READY only if that runner PASSes

# 17. Final Engineering Contract

Old (superseded) story: fixed Composer install → Provider Installation → Gate.

Binding Alpha.3 story:

```text
Composer freeze (unchanged)
        +
Repo Facts → Capability Plan (ephemeral)
        +
RTK verify (optional WARNING)
        ↓
stdout plan/status + doctor JSON
        ↓
Governance Gate (unchanged)
```

Do not claim Alpha.3 / Capability Resolver READY until Golden on `smc-copilot-desktop` PASSes.
