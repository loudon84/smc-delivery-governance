---
name: code-review-and-quality
description: >-
  Consumer-owned implementation review skill. Use after code changes to produce
  a semantic review verdict before claiming delivery complete. GES routes
  implementation review here; customize for project standards.
---

# Code Review and Quality

Consumer-owned baseline stub installed by GES `--seed-consumer-skills`. Replace
with project review standards; Core never overwrites this path after it exists.

## When to use

- After implementation work, before claiming a Plan Todo complete
- Before merge when GES routes "implementation review" to this skill

## Required output

Produce an explicit verdict: `PASS`, `PASS_WITH_FINDINGS`, or `FAIL`.

Cite concrete file paths and risks. Do not rubber-stamp without reading the
diff. Domain pack findings feed into this final verdict; they do not replace it.

## Quality bar

1. Correctness against the approved Plan / PRD slice
2. Regression and test evidence freshness
3. Security / data-boundary risks for the change
4. Maintainability of the touched surface
