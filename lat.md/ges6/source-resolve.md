# Source Resolve

Upstream Matt, Spec Kit and Superpowers trees are fetched only at immutable commit SHAs and cached outside the business repo.

Offline tests set `GES_SOURCE_CACHE` and `GES_SOURCE_OFFLINE=1`. Fetch and path containment are in [[ges/source_adapters/cache.py#ensure_source]].
