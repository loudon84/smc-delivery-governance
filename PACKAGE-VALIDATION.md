# Package Validation

Generated package: `smc-delivery-governance v1.0.0`

Validated locally:

```text
python tools/validate_feature.py features/FEAT-SKILL-FIRST-001
→ FEATURE VALID

pytest -q
→ 3 passed

governance_sync.py --apply / --check
→ GOVERNANCE SYNC OK
```

Expected current example integration gate:

```text
INT-SKILL-FIRST-001
→ WAITING_CONSUMER
```

This is intentional because the example Consumer Work Package is still `IMPLEMENTING` while the Provider package is `DONE` and `SKILL-RUN-CONTRACT v1.2.1` is `CONSUMED`.
