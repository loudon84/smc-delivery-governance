# Capability Catalog

The catalog declares every capability, including excluded ones, so ownership conflicts can fail before apply.

Each capability has source, path, owner domain, requires and conflicts. Resolver closure and pair checks live in [[ges/resolver/capability_graph.py#close_dependencies]] and [[ges/resolver/capability_graph.py#detect_conflicts]].
