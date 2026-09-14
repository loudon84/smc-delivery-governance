# GES 6.0.0 candidate

GES remains the sole owner of Architecture → PRD → Plan → Delivery truth. This package is a repository-local overlay, not a second workflow engine.

New work uses Plan `smc.plan.v4.0` with required `context_binding`, Context Registry under `.agents/ges/context/`, and the Context Optimization Engine. In-flight v3.6/v3.7 Plans are rejected by the v6 runtime. Historical completed Plans remain read-only evidence.

## Entry points

Validate with `python validate_package.py`. Install into a consumer with `python install.py <project>` (dry run), then `python install.py <project> --apply`. Run Context Engine tests with `python context-engine/run_selftest.py`.

See [CHANGES-v6.0.0.md](CHANGES-v6.0.0.md), [BASELINE-CANDIDATE-v6.0.0.md](BASELINE-CANDIDATE-v6.0.0.md) and [CONSUMER-INTEGRATION.md](CONSUMER-INTEGRATION.md).

## Validation boundary

The package gate runs delivery, roadmap, context-engine, bootstrap and install/rollback regressions. Real Pilot/Benchmark remain `NOT_EXECUTED`. Candidate status is not an accepted production baseline.
