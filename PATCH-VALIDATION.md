# Patch Validation

Patch: `SMC-DELIVERY-GOVERNANCE-v1.2.1-CLOSED-LOOP-v1`

Base:

```text
repository: loudon84/smc-delivery-governance
branch: master
commit: 66e9345681822527ad7611f3c46a66e5d445ea92
```

## Static validation

- Python files compiled: **PASS**
- JSON parsed: **PASS**
- YAML parsed: **PASS**
- Patch manifest file SHA-256 verification: **PASS**
- Patch contains only changed/new files, not a repository snapshot: **PASS**

Python errors:

```text
none
```

JSON errors:

```text
none
```

YAML errors:

```text
none
```

Manifest errors:

```text
none
```

## Required live validation after overlay

The following require credentials / actual project repositories and therefore must run after applying the patch:

```text
1. cleanup_sample_sot.py
2. upgrade_source_prd_artifact.py
3. pytest -q
4. git diff --exit-code after pytest
5. verify_state_invariants.py
6. create annotated governance-kit-v1.2.1
7. release workflow creates canonical Bundle
8. governance_sync into real nodeskclaw / smc-copilot clones
9. verify_remote_bootstrap for both repositories
10. real project Delivery Receipts
11. GitHub Actions acceptance artifact + central attestation verification
12. real INT-SKILL-FIRST-001 runner using protected integration secrets
13. immutable IntegrationRun PASS
14. Feature DONE through central reconciler only
```

A v1.2.1 release must not be declared `Closed Loop v1` until all 14 live checks pass.
