# Catalyst Canvas — Design Thinking Workspace

**Catalyst Canvas** is a Design Thinking workbench for framing problems, synthesizing insights, and turning ideas into testable experiments across the Catalyst suite.

## What it helps you do
- **Frame the problem**: POV (Point-of-View) statements and **HMW** (“How Might We…”) prompts
- **Understand users**: Personas, jobs-to-be-done, pain/gain maps
- **Map journeys**: Current vs. target journeys; moments-that-matter
- **Prioritize opportunities**: Impact × Confidence × Effort (ICE) grids; quick RICE scores
- **Plan experiments**: Hypotheses, success metrics, risks/assumptions, next actions
- **Export to analytics**: Hand off experiments and tags to **Catalyst Finance** and **Narrative Risk**

## Why it exists
Discovery is where strategy is won or lost. Canvas reduces thrash by giving teams a single place to capture insights, align on problem framing, and queue experiments for downstream analysis (e.g., elasticity, revenue/MR, narrative risk signals).

## Core artifacts (data model)
- `persona`: name, segment, needs, pains, gains
- `pov`: user + need + insight → POV statement
- `hmw`: HMW questions linked to POVs
- `journey`: stages, steps, pain points, opportunities
- `opportunity`: statement, assumptions, ICE/RICE scores
- `experiment`: hypothesis, metric(s), design, owner, status

> Artifacts can be exported as JSON/CSV for ingestion by other Catalyst modules.

## Quickstart
> Adjust commands to your stack (Vite/React, Next.js, or Node scripts).

```bash
# Install
npm install

# Run (dev)
npm run dev
# → open the printed URL (e.g., http://localhost:5173 or :3000)

# Build
npm run build

# Preview (optional)
npm run preview
