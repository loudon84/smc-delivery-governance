# Clarification Contract v1

Clarification reduces downstream rework; it is not a product interview loop.

## Candidate categories

- functional scope / out-of-scope;
- domain/data lifecycle;
- critical UX flow and loading/empty/error states;
- security/privacy/authorization;
- integration failure behavior;
- performance/reliability/operational constraints;
- acceptance/verification ambiguity;
- frontend layout/component/state ownership when frontend is activated.

## Budget

Maximum five accepted questions per clarification session. Ask one question at a time. Questions
must have material implementation or verification impact. If no material ambiguity exists, ask
zero questions.

## Ledger

```markdown
## Clarification Ledger
| ID | Category | Impact | Question | Answer | Affects | Status |
|---|---|---|---|---|---|---|
| Q01 | UX | HIGH | ... | ... | AC-02 | CLOSED |
```

All HIGH clarification rows must be CLOSED before initial PRD Review. A clarification that exposes
a hard FULL trigger upgrades `governance_profile` before review.
