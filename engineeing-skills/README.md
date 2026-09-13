# GES 5.0.0 repaired candidate

GES remains the sole owner of Architecture → PRD → Plan → Delivery truth. This package is a repository-local overlay, not a second workflow engine.

New work uses Work Router NONE/LEAN/FULL, reviewed domain design intent and Plan v3.7. Existing v3.6 Plans remain on their contract. Test Asset Catalog remains the cross-Roadmap owner of reusable test drivers; each execution creates evidence, not another driver.

## Entry points

Validate with `python validate_package.py`. Install into a consumer with `python install.py <project>` (dry run), then `python install.py <project> --apply`. Installation requires the consumer-owned legacy validator, review and verification skills; it does not manufacture them.

See [APPLY-v5.0.0.md](APPLY-v5.0.0.md), [CONSUMER-INTEGRATION.md](CONSUMER-INTEGRATION.md), [DOMAIN-PACK-CONTRACT.md](DOMAIN-PACK-CONTRACT.md), [docs/GES-5-ARCHITECTURE.md](docs/GES-5-ARCHITECTURE.md) and [CHANGES-v5.0.0.md](CHANGES-v5.0.0.md).

## Validation boundary

The package gate runs inherited delivery, roadmap, context, v1 method and adaptive-review regressions, v5 runtime and domain tests, plus actual generic fixture installation and rollback. A fixture legacy validator proves adapter compatibility only; real consumer validators and product acceptance remain mandatory in consumer projects. Candidate status is not changed to an accepted production baseline by this upgrade.
