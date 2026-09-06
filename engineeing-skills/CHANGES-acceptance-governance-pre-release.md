# Acceptance Claim Governance — pre-release source patch

This patch is intentionally a **source-level governance patch** against current
`master/engineeing-skills`.

It does not rewrite:

- `BASELINE.md` (accepted v4.1.2 authority);
- `BASELINE-CANDIDATE-v4.2.0.md`;
- `PACKAGE-MANIFEST-v4.2.0.json`;
- `SHA256SUMS-v4.2.0`.

Reason: v4.2.0 is already a named release candidate. Mutating its integrity
metadata in place would violate the repository's own release model.

After this patch is reviewed and consumer-tested, cut the next package
candidate (recommended v4.3.0) and regenerate package manifest + checksums.

## Targeted validation before release packaging

```bash
python engineeing-skills/.agents/skills/smc-plan-delivery/scripts/run_selftest.py
python -m py_compile \
  engineeing-skills/.agents/skills/smc-plan-delivery/scripts/acceptance.py \
  engineeing-skills/.agents/skills/smc-plan-delivery/scripts/evidence.py \
  engineeing-skills/.agents/skills/smc-plan-delivery/scripts/validate_delivery_completion.py \
  engineeing-skills/.agents/skills/smc-plan-validator/scripts/validate_plan_v34.py \
  engineeing-skills/.agents/skills/smc-roadmap/scripts/validate_roadmap_v11.py
```

Then run at least one real consumer integration:

1. revise a live Plan to `acceptance_contract: smc.acceptance.v1`;
2. bind separate Scenario/Fixture per semantically distinct Claim;
3. capture verification candidate;
4. verify preflight blocks a missing fault driver;
5. verify a mismatched deployed candidate returns `LIVE_SUT_MISMATCH`;
6. verify a live runner with process exit 0 but `CLM-* = FAIL` is still evidence FAIL;
7. verify a prior PASS Claim can be inherited without rerunning the prior live case;
8. verify blocking prior FAIL cannot be reused;
9. verify Roadmap DONE rejects manifest v3 with failed/missing blocking Claims.

Only after these pass should the package version / manifest / SHA256 release
artifacts be regenerated.
