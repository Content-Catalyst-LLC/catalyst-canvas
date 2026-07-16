"""Stable Canvas Contract 2.0 JSON, Markdown, print, publication, and exchange-ready exporters."""

from __future__ import annotations

import html
import json
from typing import Any, Mapping

from .contract import validate_contract
from .collaboration import build_publication_package


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
    sessions = _bullets([f"{item['title']} [{item['mode']}/{item['status']}] — framework: {item['framework_key']}; facilitator: {item['facilitator'] or 'unassigned'}" for item in data["ideation_sessions"]])
    ideas = _bullets([f"{item['idea_id']} — {item['title']} [{item['status']}; {item['vote_count']} votes] — lineage: {item['challenge_id']} → {item['hmw_id']} → {item['prompt_id']} → {', '.join(item['prototype_ids']) or 'prototype not linked'}; author: {item['author']}; rationale: {item['rationale']}" for item in data["ideas"]])
    clusters = _bullets([f"{item['sequence']}. {item['name']} — ideas: {', '.join(item['idea_ids']) or 'none'}; rationale: {item['rationale'] or 'not recorded'}" for item in data["idea_clusters"]])
    custom_frameworks = _bullets([f"{item['key']} — {item['name']} [{item['category']}]" for item in data["custom_frameworks"]])
    prompt_packs = _bullets([f"{item['prompt_pack_id']} — {item['name']}: {len(item['prompts'])} prompts" for item in data["prompt_packs"]])
    decision_criteria = _bullets([f"{item['criterion_id']} — {item['name']} [weight {item['weight']}; {item['direction']}; {'gate' if item['is_gate'] else 'weighted'}] — {item['description']}" for item in data["decision_criteria"]])
    decision_options = _bullets([f"{item['option_id']} — {item['title']} [{item['recommendation_state']}; weighted {item['weighted_score']:.2f}; ICE {item['ice']['score']:.2f}; RICE {item['rice']['score']:.2f}] — basis/confidence: {item['value_basis']}/{item['confidence']}; owner: {item['owner'] or 'unassigned'}; deadline: {item['decision_deadline'] or 'not recorded'}; rationale: {item['decision_rationale'] or 'not recorded'}; blockers: {'; '.join(item['blockers']) or 'none'}" for item in data["decision_options"]])
    sensitivity_views = _bullets([f"{item['name']}: " + "; ".join(f"#{rank['rank']} {rank['option_id']} ({rank['score']:.2f}, delta {rank['delta_from_baseline']})" for rank in item['rankings']) for item in data["sensitivity_views"]])
    decision_notes = _bullets([f"[{item['note_type']}/{item['status']}] {item['note']} — options: {', '.join(item['option_ids']) or 'none'}" for item in data["decision_notes"]])
    decision_handoffs = _bullets([f"{item['target']} [{item['status']}] — {item['purpose'] or 'No purpose recorded'}; options: {', '.join(item['option_ids']) or 'all recorded alternatives'}" for item in data["decision_handoffs"]])
    prototypes = _bullets([f"{item['prototype_id']} — {item['title']} v{item['version']} [{item['prototype_type']}/{item['fidelity']}/{item['status']}] — owner: {item['owner'] or 'unassigned'}; success: {item['success_definition'] or 'not recorded'}; limitations: {'; '.join(item['known_limitations']) or 'none'}" for item in data["prototypes"]])
    hypotheses = _bullets([f"{item['hypothesis_id']} [{item['hypothesis_type']}/{item['status']}/{item['confidence']}] — {item['statement']} — falsification: {item['falsification_condition'] or 'not recorded'}" for item in data["hypotheses"]])
    experiment_plans = _bullets([f"{item['experiment_id']} — {item['title']} [{item['status']}] — objective: {item['objective']}; method: {item['method']}; participants: {item['participant_plan']['target_count']}; metrics: {', '.join(metric['name'] for metric in item['metrics']) or 'none'}; blockers: {'; '.join(item['blockers']) or 'none'}" for item in data["experiment_plans"]])
    experiment_runs = _bullets([f"{item['run_id']} — {item['experiment_id']} [{item['status']}/{item['result_state']}] — participants: {item['participant_count']}; {item['summary'] or 'No summary recorded'}" for item in data["experiment_runs"]])
    learning_decisions = _bullets([f"{item['learning_decision_id']} [{item['outcome']}] — {item['rationale'] or 'No rationale recorded'}; next: {'; '.join(item['next_actions']) or 'none'}" for item in data["learning_decisions"]])
    iteration_history = _bullets([f"{item['iteration_id']} — {item['prototype_id']} {item['from_version'] or '?'} → {item['to_version'] or '?'}: {item['change_summary'] or 'No change summary'} — {item['reason'] or 'No reason recorded'}" for item in data["iteration_history"]])
    experiment_handoffs = _bullets([f"{item['target']} [{item['status']}] — {item['purpose'] or 'No purpose recorded'}; experiments: {', '.join(item['experiment_ids']) or 'none'}" for item in data["experiment_handoffs"]])
    sources = _bullets([f"{item['source_id']} — {item['title']} [{item['source_type']}] {item['url']}".strip() for item in data["sources"]])
    evidence = _bullets([f"{item['evidence_id']} — {item['title']}: {item['summary'] or item['quote']} (source: {item['source_id'] or 'unlinked'})" for item in data["evidence"]])
    claims = _bullets([f"[{item['state']}] {item['statement']} — evidence: {', '.join(item['evidence_ids']) or 'none'}; assumptions: {', '.join(item['assumption_ids']) or 'none'}; uncertainty: {item['uncertainty'] or 'not recorded'}" for item in data["claims"]])
    assumptions = _bullets([f"[{item['criticality']}/{item['status']}] {item['statement']} — owner: {item['owner'] or 'unassigned'}; test: {item['test_method'] or 'not recorded'}; consequence: {item['consequence'] or 'not recorded'}" for item in data["assumptions"]])
    research_questions = _bullets([f"[{item['priority']}/{item['status']}] {item['question']} — owner: {item['owner'] or 'unassigned'}" for item in data["research_questions"]])
    interview_guides = _bullets([f"{item['title']} ({item['status']}): {'; '.join(item['questions']) or 'No questions recorded'}" for item in data["interview_guides"]])
    observations = _bullets([f"{item['title']}: {item['note']} — observer: {item['observer'] or 'not recorded'}" for item in data["observation_notes"]])
    handoffs = _bullets([f"{item['target']} [{item['status']}]: {item['purpose'] or item['context_note']}" for item in data["handoffs"]])
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
    members = _bullets([f"{item['name']} ({item['member_id']}) — {item['role']} [{item['status']}]" for item in data["workspace_members"]])
    assignments = _bullets([f"{item['assignment_id']} — {item['title']} [{item['status']}] — reviewer: {', '.join(item['assignee_ids']) or 'unassigned'}; due: {item['due_at'] or 'not recorded'}; sections: {', '.join(item['target_ids']) or 'whole canvas'}" for item in data["review_assignments"]])
    comments = _bullets([f"{item['comment_id']} [{item['status']}/{item['visibility']}] — {item['body']} — author: {item['author_id'] or 'unknown'}; section: {item['section_path'] or 'general'}" for item in data["comments"]])
    approvals = _bullets([f"{item['approval_id']} [{item['decision']}] — approver: {item['reviewer_id'] or 'unassigned'}; scope: {item['scope']}; rationale: {item['rationale'] or 'none'}" for item in data["approvals"]])
    publications = _bullets([f"{item['publication_id']} — {item['title']} [{item['state']}/{item['channel']}] — type: {item['publication_type']}; reviews: {', '.join(item['review_assignment_ids']) or 'none'}; approvals: {', '.join(item['approval_ids']) or 'none'}; redactions: {'; '.join(item['redaction_notes']) or 'none'}" for item in data["publication_records"]])
    releases = _bullets([f"{item['release_id']} — {item['publication_id']} v{item['version']} [{item['state']}] — published: {item['published_at'] or 'not published'}; checksum: {item['checksum'] or 'not recorded'}" for item in data["release_history"]])
    publication_handoffs = _bullets([f"{item['target']} [{item['status']}] — publication: {', '.join(item['publication_ids']) or 'not selected'}; purpose: {item['purpose'] or 'not recorded'}" for item in data["publication_handoffs"]])
    platform_connections = _bullets([f"{item['display_name']} [{item['direction']}/{item['status']}] — auth: {item['auth_mode']}; capabilities: {', '.join(item['capabilities']) or 'none'}; verified: {item['last_verified_at'] or 'not verified'}" for item in data["platform_connections"]])
    interoperability_profiles = _bullets([f"{item['profile_id']} — {item['name']} v{item['version']} [{item['status']}] — contracts: {', '.join(item['supported_contracts']) or 'none'}" for item in data["interoperability_profiles"]])
    workflow_links = _bullets([f"{item['link_id']} — {item['from_product']}:{item['from_record_id'] or '?'} → {item['to_product']}:{item['to_record_id'] or '?'} [{item['relation']}/{item['status']}]" for item in data["workflow_links"]])
    exchange_records = _bullets([f"{item['exchange_id']} — {item['target_product']} [{item['payload_type']}/{item['status']}] — signature: {item['signature_algorithm']}; source revision: {item['source_revision_id'] or 'not recorded'}" for item in data["exchange_records"]])
    platform_events = _bullets([f"{item['event_id']} — {item['event_type']} by {item['producer']} at {item['occurred_at']} — correlation: {item['correlation_id'] or 'none'}" for item in data["platform_events"]])
    return f"""# {data['title']}

Contract: {data['schema_version']}  
Canvas ID: {data['canvas_id']}  
Revision ID: {data['revision_id']}  
Status: {data['status']}  
Updated: {data['updated_at']}  
Research readiness: {data['research_summary']['readiness']}  
Evidence coverage: {data['ledger_summary']['evidence_coverage']}  
Assumption exposure: {data['ledger_summary']['assumption_exposure']}  
Ideas: {data['ideation_summary']['idea_count']} · Clusters: {data['ideation_summary']['cluster_count']} · Votes: {data['ideation_summary']['vote_count']}  
Decision readiness: {data['prioritization_summary']['readiness']} · Options: {data['prioritization_summary']['option_count']} · Incomplete scores: {data['prioritization_summary']['incomplete_score_count']}  
Experiment readiness: {data['experiment_summary']['readiness']} · Experiments: {data['experiment_summary']['experiment_count']} · Completed runs: {data['experiment_summary']['completed_run_count']}  
Collaboration readiness: {data['collaboration_summary']['readiness']} · Open comments: {data['collaboration_summary']['open_comment_count']} · Pending reviews: {data['collaboration_summary']['required_review_open_count']} · Published releases: {data['collaboration_summary']['published_count']}  
Platform readiness: {data['platform_summary']['readiness']} · Connections: {data['platform_summary']['connection_count']} · Verified: {data['platform_summary']['verified_connection_count']} · Exchanges: {data['platform_summary']['exchange_count']}

## Publication and Review Warning

{_bullets([f"{item['claim_id']}: {item['statement']} [{item['state']}]" for item in data['claims'] if item['state'] in {'unsupported','disputed','outdated'}]) if data['ledger_summary']['unsupported_or_disputed_count'] else 'No unsupported, disputed, or outdated claims are recorded.'}

{data['ledger_summary']['indicator_note']}

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

{data['framework']['description']}

{prompts}

**Intended uses:** {', '.join(data['framework']['intended_uses']) or 'None recorded'}  
**Limitations:** {', '.join(data['framework']['limitations']) or 'None recorded'}

## Custom Framework Library

{custom_frameworks}

## Reusable Prompt Packs

{prompt_packs}

## Ideation Sessions

{sessions}

## Idea Cards and Lineage

{ideas}

{data['ideation_summary']['indicator_note']}

## Idea Clusters

{clusters}

## Decision Criteria

{decision_criteria}

## Decision Alternatives and Scores

{decision_options}

{data['prioritization_summary']['indicator_note']}

## Sensitivity Views

{sensitivity_views}

## Decision Notes

{decision_notes}

## Decision Handoffs

{decision_handoffs}

## Source Register

{sources}

## Evidence Register

{evidence}

## Claim Register

{claims}

## Assumption Register

{assumptions}

## Research Questions

{research_questions}

## Interview Guides

{interview_guides}

## Observation Notes

{observations}

## Synthesis Tags

{_bullets(data['synthesis_tags'])}

## Research Handoffs

{handoffs}

## Prototype Portfolio

{prototypes}

## Hypotheses

{hypotheses}

## Experiment Plans

{experiment_plans}

{data['experiment_summary']['indicator_note']}

## Experiment Runs and Results

{experiment_runs}

## Learning Decisions

{learning_decisions}

## Prototype Iteration History

{iteration_history}

## Experiment Handoffs

{experiment_handoffs}

## Legacy Prototype Summary

{prototype_text}

## Legacy Test Plan

{test_text}

## Review Notes

{reviews}

## Workspace Members

{members}

## Review Assignments

{assignments}

## Collaboration Comments

{comments}

## Publication Approvals

{approvals}

## Publication Records

{publications}

{data['collaboration_summary']['indicator_note']}

## Release History

{releases}

## Publication Handoffs

{publication_handoffs}

## Connected Product Registry

{platform_connections}

## Interoperability Profiles

{interoperability_profiles}

## Cross-Product Workflow Links

{workflow_links}

## Exchange Records

{exchange_records}

## Platform Events

{platform_events}

{data['platform_summary']['indicator_note']}

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


def export_publication_json(contract: Mapping[str, Any], *, target: str = "public_json", pretty: bool = True) -> str:
    package = build_publication_package(validate_contract(contract), target)
    return json.dumps(package, indent=2 if pretty else None, ensure_ascii=False, sort_keys=False) + "\n"


def export_publication_markdown(contract: Mapping[str, Any]) -> str:
    package = build_publication_package(validate_contract(contract), "public_markdown")
    publication = package["publication"]
    lines = [
        f"# {publication['title']}",
        "",
        f"Publication contract: {package['publication_contract']}  ",
        f"Source Canvas: {package['source']['canvas_id']}  ",
        f"Source revision: {package['source']['revision_id']}  ",
        f"Version: {publication['version']}  ",
        "",
    ]
    for key, value in package["content"].items():
        lines.extend([f"## {str(key).replace('_', ' ').title()}", ""])
        if isinstance(value, (dict, list)):
            lines.extend(["```json", json.dumps(value, indent=2, ensure_ascii=False), "```", ""])
        else:
            lines.extend([str(value), ""])
    lines.extend(["## Publication Boundary", "", package["boundary"], ""])
    return "\n".join(lines)


def export_publication_html(contract: Mapping[str, Any]) -> str:
    data = validate_contract(contract)
    package = build_publication_package(data, "public_html")
    markdown = export_publication_markdown(data)
    title = html.escape(package["publication"]["title"])
    body = html.escape(markdown)
    return (
        "<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
        f"<title>{title}</title>"
        "<style>body{font:16px/1.55 system-ui,sans-serif;max-width:900px;margin:3rem auto;padding:0 1.5rem}"
        "pre{white-space:pre-wrap;background:#f4f4f4;padding:1rem}@media print{body{margin:0;max-width:none}}</style>"
        f"</head><body><pre>{body}</pre></body></html>\n"
    )
