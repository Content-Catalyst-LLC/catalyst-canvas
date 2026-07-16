# Framework and Ideation Studio

The v1.6.0 studio provides a structured path from problem framing to testable concepts without separating ideas from the evidence, assumptions, prompts, and people that produced them.

## Built-in framework packs

The registry contains AIDA, JTBD, Value Proposition Canvas, Message House, SWOT, PESTLE, 5W1H, Hero/Guide, Assumption Matrix, and Impact–Effort. Every pack is stored as data rather than hard-coded UI logic.

Each pack declares:

- intended uses and limitations;
- required inputs and output types;
- divergent and/or convergent mode support;
- prompt labels, questions, purposes, and output types.

## Custom frameworks and prompt packs

Organization-specific frameworks use the same record shape as built-ins. They can be entered in the Flask or WordPress studio, exported as `catalyst-canvas-framework-package/1.0`, and imported into another Canvas through the API or CLI.

Prompt packs are reusable groups of prompts independent of a framework. A session can combine one framework with one or more prompt packs.

## Ideation sessions

A session records its mode, framework, prompt packs, challenge, HMW questions, facilitator, participants, status, notes, and timestamps.

- **Divergent mode** supports generating distinct alternatives before evaluation.
- **Convergent mode** supports grouping, comparing, merging, voting, and selecting concepts.

## Idea records

Idea cards retain title, description, author, rationale, tags, votes, cluster, originating prompt, challenge, HMW question, evidence, assumptions, parent ideas, merge target, and prototype links.

Clusters retain membership, order, tags, description, and the rationale for grouping. Reordering is available through buttons and keyboard alternatives; drag-and-drop is not required.

## Lineage

The contract supports:

```text
challenge -> HMW -> framework/prompt -> idea -> cluster/merge -> prototype -> experiment
```

Lineage gaps remain visible in `ideation_summary.orphaned_lineage_count` rather than being silently inferred.

## Boundaries

Votes and selections express participant judgment. Catalyst Canvas does not treat them as objective rankings or proof of user value, feasibility, equity, impact, or readiness.
