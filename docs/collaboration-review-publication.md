# Collaboration, Review, and Publication

## Roles

Owner, editor, contributor, reviewer, and viewer roles map to explicit capabilities. Flask enforces those capabilities at member-management, comment, review, approval, and publication endpoints.

## Review workflow

Review assignments identify scope, targets, assignees, due dates, instructions, required status, and completion. Comments retain thread, target, author, visibility, resolution, mentions, and timestamps. Approval records preserve decision, reviewer, scope, rationale, conditions, and decision time.

## Publication gates

A public artifact cannot be released while a required linked review is incomplete, a linked approval is absent or not approved, a rejected or changes-requested decision exists, or redaction review is not documented.

## Public-safe boundary

`catalyst-canvas-public-safe/1.0` packages include only selected public sections and source provenance. They omit members, comments, assignments, approvals, participant details, and private working notes. A SHA-256 checksum identifies the exported content.
