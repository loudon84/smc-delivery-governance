# GES 5.0.0 Candidate

This is a repaired candidate built from the v4.4.1 locked baseline and the supplied v5 upgrade payload. Missing source files were reconstructed; historical hashes were not fabricated. Bundle ORIGINAL-MANIFEST.json records the original expectations; regenerated manifest.json and SHA256SUMS describe actual repaired bytes.

## Acceptance boundary

Package tests establish governance runtime and installation invariants, not production business acceptance. BASELINE.md remains the authority for accepted release status. Consumer dry runs, their configured project validators and representative in-flight Plan checks are required before rollout. No historical Plan or review result is silently promoted or bulk rewritten.
