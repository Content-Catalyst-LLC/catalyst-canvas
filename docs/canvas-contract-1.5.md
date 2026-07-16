# Canvas Contract 1.5

Canvas Contract 1.5 is the canonical document contract for Catalyst Canvas v1.8.0.

## Identifier

```text
catalyst-canvas/1.5
```

The authoritative schema is `schemas/catalyst_canvas_contract_1_5.schema.json`.

## Additions over Contract 1.4

Contract 1.5 adds:

- versioned `prototypes`;
- falsifiable `hypotheses`;
- governed `experiment_plans`;
- observed `experiment_runs`;
- explicit `learning_decisions`;
- `iteration_history`;
- Research Lab and Workbench `experiment_handoffs`;
- a descriptive `experiment_summary`.

The existing `tests` collection remains for compatibility with older clients. It is not the authoritative experiment ledger.

## Experiment plan structure

An experiment plan records an objective, method, status, owner, linked prototypes and hypotheses, assumptions, evidence, research questions, participant plan, metrics, safeguards, dates, dependencies, blockers, and artifacts.

Participant plans preserve target count, participant segments, recruitment, inclusion and exclusion criteria, consent, compensation, and accessibility accommodations.

Metrics preserve type, threshold, unit, collection method, baseline, target, basis, confidence, and evidence links.

Safeguards preserve risks, mitigations, stop conditions, data handling, and ethics-review status.

## Results and learning

Experiment runs preserve participant count, result state, metric results, observations, evidence, limitations, incidents, artifacts, and recorder metadata. Learning decisions use `continue`, `iterate`, `pivot`, `stop`, `escalate`, or `retest`. Iteration records preserve the change from one prototype version to the next and the learning that caused it.

## Migrations

Contracts 1.0 through 1.4 are normalized into Contract 1.5. Migration records the source contract in provenance and adds a review warning. Unknown future versions are rejected.

## Boundary

Experiment readiness describes recorded workflow coverage. It does not establish causal validity, statistical power, safety, desirability, feasibility, viability, or impact.
