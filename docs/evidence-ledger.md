# Research, Evidence, and Assumption Ledger

The v1.5.0 ledger keeps research provenance and uncertainty visible while a Canvas moves from framing to prototype, experiment, review, and publication.

## Workflow

```text
research question
  → source
  → evidence excerpt or observation
  → claim or assumption
  → persona / stakeholder / journey / opportunity
  → prototype or experiment
  → review and handoff
```

## Source register

Record the source before relying on an excerpt or conclusion. Include enough information to identify where the material came from, who owns it, when it was created or accessed, and what limitations or rights conditions apply. `knowledge_library_record_id` can preserve the first-party library relationship without duplicating the source document.

## Evidence register

Evidence records should preserve the exact locator and citation when available. Quotes and observations should remain distinguishable from summaries and data points. Confidence describes the team's confidence in the record as captured; it does not convert an observation into a universal fact.

## Claim register

Claims make interpretation inspectable. Each material claim should identify supporting evidence and sources, uncertainty, limitations, contradictions, missing data, and review state. Unsupported, disputed, or outdated claims trigger warnings in Markdown and print exports.

## Assumption ledger

Assumptions are not hidden defaults. High-criticality assumptions should have an owner, consequence, test method, status, and experiment link. A supported or refuted assumption remains in the revision history rather than being erased.

## Research planning records

- **Research questions** keep unresolved questions explicit.
- **Interview guides** preserve purpose, audience, questions, ownership, and status.
- **Observation notes** preserve context, observer, time, source, evidence links, limitations, and tags.
- **Synthesis tags** help connect patterns without creating unsupported claims.

## Contradiction review

Evidence records can link to contradictory records. Claims can preserve contradiction notes and disputed states. The ledger does not automatically resolve disagreement; it makes the disagreement visible for review.

## Institutional handoffs

A project can export a research handoff for:

- `knowledge_library` — source registration, preservation, citation, and collection workflows;
- `research_librarian` — source discovery, research routing, gap review, and continuation.

The handoff package carries the current Canvas and revision IDs, challenge, goal, audience, ledger records, summary indicators, and provenance.

## Interpretation boundary

Counts and coverage labels describe what has been recorded and linked. They do not certify evidence, establish causality, assess participant credibility, or replace subject-matter, ethical, legal, or stakeholder review.
