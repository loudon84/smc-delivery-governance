# SMC Plan Contract v4.0

v4.0 is v3.7 plus a required context-binding extension for GES v6. It keeps delivery truth,
Single Writer, freshness and `post_review` unchanged.

## Required frontmatter

```yaml
plan_contract: smc.plan.v4.0
plan_id: <stable-id>
governance_profile: LEAN | FULL
commit_policy: post_review
acceptance_contract: smc.acceptance.v1
domain_contract: smc.ges.domain-activation.v2
consumer_profile: <id@version>
domain_policy_digest: sha256:<digest>
context_binding: required
```

## Required capabilities

- All v3.7 ledgers, ownership, domain intent binding and adaptive profile rules.
- `context_binding: required` — execution consumes a READY Context Package bound to Plan semantic hash, source content, Registry and policy digests.
- Write set remains Canonical Plan ownership; a Context Package read set never grants writes.

## Compatibility

v6 runtime executes only `smc.plan.v4.0`. In-flight v3.6/v3.7 Plans are rejected with `CONTEXT_LEGACY_PLAN_UNSUPPORTED`. Historical completed Plans remain read-only evidence. Validators for v3.3–v3.7 must reject Plans that declare required `context_binding`.
