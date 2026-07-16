"""Stable Canvas Contract 1.1 JSON, Markdown, and print-report exporters."""

from __future__ import annotations

import html
import json
from typing import Any, Mapping

from .contract import validate_contract


def export_json(contract: Mapping[str, Any], *, pretty: bool = True) -> str:
    payload = validate_contract(contract)
    return json.dumps(
        payload,
        indent=2 if pretty else None,
        separators=None if pretty else (",", ":"),
        ensure_ascii=False,
        sort_keys=False,
    ) + "\n"


def _bullets(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "- None recorded"


def export_markdown(contract: Mapping[str, Any]) -> str:
    data = validate_contract(contract)
    persona = data["personas"][0]
    prototype = data["prototypes"][0] if data["prototypes"] else None
    test = data["tests"][0] if data["tests"] else None
    constraints = _bullets([item["statement"] for item in data["constraints"]])
    hmw = _bullets([item["question"] for item in data["how_might_we"]])
    prompts = _bullets([f"{item['label']}: {item['question']}" for item in data["framework"]["prompts"]])
    evidence = _bullets([f"{item['title']}: {item['summary']}" for item in data["evidence"]])
    assumptions = _bullets([item["statement"] for item in data["assumptions"]])
    reviews = _bullets([item["note"] for item in data["review_notes"]])
    audience = "\n".join([
        f"- **Primary:** {data['audience']['primary']}",
        f"- **Secondary:** {', '.join(data['audience']['secondary']) or 'None recorded'}",
        f"- **Affected:** {', '.join(data['audience']['affected']) or 'None recorded'}",
        f"- **Excluded:** {', '.join(data['audience']['excluded']) or 'None recorded'}",
    ])
    empathy = "\n".join(
        f"- **{key.title()}:** {'; '.join(values) or 'None recorded'}"
        for key, values in persona["empathy_map"].items()
    )
    attributes = _bullets([
        f"{item['category']}: {item['statement']} [{item['basis']}, {item['confidence']}]"
        for item in persona["attributes"]
    ])
    stakeholders = _bullets([
        f"{item['name']} — influence {item['influence']}/5, interest {item['interest']}/5, "
        f"impact {item['impact']}/5, {item['stance']}; responsibilities: "
        f"{'; '.join(item['responsibilities']) or 'none'}; tensions: "
        f"{'; '.join(item['tensions']) or 'none'}; strategy: "
        f"{item['engagement_strategy'] or 'not recorded'}"
        for item in data["stakeholders"]
    ])
    journey_sections = []
    for journey in data["journeys"]:
        stages = "\n".join(
            f"- **{stage['sequence']}. {stage['name']}:** "
            f"{'; '.join(stage['actions']) or 'No action recorded'} | "
            f"questions: {'; '.join(stage['questions']) or 'none'} | "
            f"friction: {'; '.join(stage['frictions']) or 'none'} | "
            f"opportunity: {'; '.join(stage['opportunities']) or 'none'} | "
            f"experiments: {', '.join(stage['experiment_ids']) or 'none'} | "
            f"owner: {stage['owner'] or 'unassigned'}"
            for stage in journey["stages"]
        )
        journey_sections.append(f"### {journey['title']}\n\n{journey['scenario']}\n\n{stages}")
    journeys = "\n\n".join(journey_sections) if journey_sections else "No journey recorded."
    behavioral_signals = _bullets([
        f"{item['metric']} ({item['segment']}): {item['value'] or 'value not recorded'} — "
        f"{item['interpretation'] or 'No interpretation'} [evidence hint; {item['limitation']}]"
        for item in data["behavioral_signals"]
    ])
    prototype_text = f"**{prototype['title']}** — {prototype['description']}" if prototype else "No prototype recorded."
    test_text = (
        "\n".join([
            f"- **Title:** {test['title']}", f"- **Signal:** {test['signal']}",
            f"- **Method:** {test['method']}", f"- **Learning goal:** {test['learning_goal']}",
        ]) if test else "No test recorded."
    )
    return f"""# {data['title']}

Contract: {data['schema_version']}  
Canvas ID: {data['canvas_id']}  
Revision ID: {data['revision_id']}  
Status: {data['status']}  
Updated: {data['updated_at']}  
Research readiness: {data['research_summary']['readiness']}

## Challenge

{data['challenge']}

## Audience

{audience}

## Goal

{data['goal']}

## Constraints

{constraints}

## Primary Persona

**{persona['name']}** — {persona['description']}

- **Role:** {persona['role']}
- **Context:** {persona['context']}
- **Jobs:** {', '.join(persona['jobs']) or 'None recorded'}
- **Goals:** {', '.join(persona['goals']) or 'None recorded'}
- **Needs:** {', '.join(persona['needs']) or 'None recorded'}
- **Pains:** {', '.join(persona['pains']) or 'None recorded'}
- **Gains:** {', '.join(persona['gains']) or 'None recorded'}
- **Behaviors:** {', '.join(persona['behaviors']) or 'None recorded'}
- **Barriers:** {', '.join(persona['barriers']) or 'None recorded'}
- **Motivations:** {', '.join(persona['motivations']) or 'None recorded'}
- **Accessibility:** {', '.join(persona['accessibility_needs']) or 'None recorded'}
- **Source / confidence / validation:** {persona['source_type']} / {persona['confidence']} / {persona['validation_status']}
- **Source notes:** {persona['source_notes'] or 'None recorded'}
- **Confidence notes:** {persona['confidence_notes'] or 'None recorded'}

### Empathy Map

{empathy}

### Attribute Basis

{attributes}

## Stakeholder Map

{stakeholders}

## Journey Maps

{journeys}

## Behavioral Signals

Analytics remain evidence hints and do not establish intent, identity, motivation, or demographic attributes.

{behavioral_signals}

## Point of View

{data['point_of_view']['statement']}

## How Might We

{hmw}

## Ideation Framework: {data['framework']['name']}

{prompts}

## Evidence

{evidence}

## Assumptions

{assumptions}

## Prototype

{prototype_text}

## Test Plan

{test_text}

## Review Notes

{reviews}

## Provenance

Generated by Catalyst Canvas {data['provenance']['generator_version']} from the {data['provenance']['source_surface']} surface.
"""

def export_print_html(contract: Mapping[str, Any]) -> str:
    data = validate_contract(contract)
    markdown = export_markdown(data)
    # A dependency-free, print-safe report. The Markdown source remains embedded for auditability.
    sections = []
    current_title = ""
    current_lines: list[str] = []
    for line in markdown.splitlines():
        if line.startswith("## "):
            if current_title:
                sections.append((current_title, current_lines))
            current_title = line[3:]
            current_lines = []
        elif not line.startswith("# ") and not line.startswith("Contract:") and not line.startswith("Canvas ID:") and not line.startswith("Revision ID:") and not line.startswith("Status:") and not line.startswith("Updated:"):
            current_lines.append(line)
    if current_title:
        sections.append((current_title, current_lines))

    section_html = "".join(
        f"<section><h2>{html.escape(title)}</h2><pre>{html.escape(chr(10).join(lines).strip())}</pre></section>"
        for title, lines in sections
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(data['title'])}</title>
<style>
body{{font-family:Arial,sans-serif;max-width:900px;margin:0 auto;padding:40px;color:#151515;line-height:1.5}}
header{{border-bottom:3px solid #6f1728;margin-bottom:32px}}h1{{font-size:32px;margin-bottom:8px}}h2{{font-size:20px;margin-top:28px}}
.meta{{color:#555;font-size:13px}}pre{{white-space:pre-wrap;font:inherit;margin:0}}@media print{{body{{padding:0}}}}
</style>
</head>
<body>
<header><h1>{html.escape(data['title'])}</h1><p class="meta">{html.escape(data['schema_version'])} · {html.escape(data['canvas_id'])} · revision {html.escape(data['revision_id'])}</p></header>
{section_html}
</body>
</html>
"""
