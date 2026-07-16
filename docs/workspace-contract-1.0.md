# Workspace Project Contract 1.0

The Workspace Project Contract describes project metadata around a versioned Canvas document.

It records stable workspace and project identifiers, title, description, tags, lifecycle status, current Canvas and revision identifiers, revision count, and timestamps.

The workspace contract does not duplicate the full Canvas. In v2.0.0, Canvas payloads validate against `catalyst-canvas/2.0`; Contracts 1.0–1.6 migrate on read, import, save, or reuse.

The workspace research-asset library indexes personas, stakeholders, journeys, sources, evidence, claims, assumptions, research questions, interview guides, observations, prototypes, hypotheses, experiment plans, experiment runs, learning decisions, and iterations. Reusing an asset creates a new immutable Canvas revision rather than modifying the source project.
