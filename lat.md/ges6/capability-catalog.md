# Capability Catalog

The catalog declares every capability so ownership conflicts can fail before apply. Product Profile classes are required, recommended, optional and forbidden.

Initial requested is required plus recommended only. Optional needs `--enable`. Forbidden or required-exclude raises `DESIRED_STATE_INVALID`. Closure lives in [[ges/resolver/capability_graph.py#close_dependencies]] and [[ges/resolver/selection.py#resolve_selection]].
