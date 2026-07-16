"""Routes for the Catalyst Canvas project workspace."""

from __future__ import annotations

from typing import Any

from flask import (
    Blueprint,
    Response,
    current_app,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from catalyst_canvas.contract import CanvasContractError, clean_text, load_schema, new_id, strip_internal_fields, utc_now
from catalyst_canvas.migrations import migrate_payload
from catalyst_canvas.ledger import build_handoff_package
from catalyst_canvas.persona_templates import list_persona_templates
from catalyst_canvas.frameworks import export_framework_package, framework_registry, import_framework_package
from catalyst_canvas.ideation import merge_idea_records
from catalyst_canvas.prioritization import build_decision_handoff_package, normalize_sensitivity_views
from catalyst_canvas.experiments import build_experiment_handoff_package
from catalyst_canvas.collaboration import build_publication_package, member_can, publication_release_record
from catalyst_canvas.platform import build_exchange_package, verify_exchange_package, capability_manifest
from catalyst_canvas.workspaces import DEFAULT_WORKSPACE_ID, load_workspace_schema

from .models import SAMPLE_PERSONAS
from .services.canvas_engine import new_canvas, normalize_form, to_form, to_markdown, to_pretty_json, to_print_html
from .services.frameworks import all_frameworks, get_framework, get_framework_record
from .services.storage import (
    archive_project,
    create_project,
    create_workspace,
    duplicate_project,
    get_canvas,
    get_project,
    get_project_canvas,
    get_workspace,
    latest_canvas,
    list_projects,
    list_revisions,
    list_workspaces,
    list_research_assets,
    research_asset_counts,
    list_workspace_members,
    get_workspace_member,
    ensure_workspace_member,
    list_collaboration_records,
    collaboration_record_counts,
    list_platform_records,
    platform_record_counts,
    reuse_research_asset,
    project_counts,
    restore_project,
    restore_revision,
    save_canvas,
    update_project_metadata,
)

bp = Blueprint("canvas", __name__)


def db_path() -> str:
    return current_app.config["CANVAS_DB"]


def workspace_id() -> str:
    return str(session.get("workspace_id") or current_app.config.get("CANVAS_WORKSPACE_ID") or DEFAULT_WORKSPACE_ID)


def acting_user_id() -> str:
    return str(session.get("canvas_user_id") or current_app.config.get("CANVAS_USER_ID") or "local-user")


def current_member() -> dict[str, Any] | None:
    return get_workspace_member(db_path(), workspace_id(), acting_user_id())


def require_capability(capability: str):
    member = current_member()
    if not member_can(member, capability):
        return jsonify({"error": f"{capability} permission required"}), 403
    return None


def _project_in_workspace(project_id: str) -> dict[str, Any] | None:
    project = get_project(db_path(), project_id)
    if not project or project["workspace_id"] != workspace_id():
        return None
    return project



def public_project(project: dict[str, Any] | None) -> dict[str, Any] | None:
    if not project:
        return None
    return {key: value for key, value in project.items() if not key.startswith("_")}

def current_canvas() -> dict[str, Any]:
    project_id = session.get("project_id")
    if project_id and _project_in_workspace(str(project_id)):
        canvas = get_project_canvas(db_path(), str(project_id))
        if canvas:
            return canvas
    canvas = latest_canvas(db_path(), workspace_id=workspace_id())
    if canvas:
        session["project_id"] = canvas["_project_id"]
        return canvas
    return new_canvas()


def view_model(canvas: dict[str, Any]) -> dict[str, Any]:
    result = to_form(canvas, storage_id=canvas.get("_storage_id"))
    result["project_id"] = canvas.get("_project_id", "")
    result["workspace_id"] = canvas.get("_workspace_id", workspace_id())
    return result


def read_behavioral_signal_upload(upload: Any) -> str:
    """Validate and decode a behavioral-signal CSV upload."""
    filename = str(getattr(upload, "filename", "") or "")
    if not filename.lower().endswith(".csv"):
        raise ValueError("Behavioral signal uploads must be CSV files.")
    raw = upload.read(2_000_001)
    if len(raw) > 2_000_000:
        raise ValueError("Behavioral signal CSV files must be 2 MB or smaller.")
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("Behavioral signal CSV files must use UTF-8 encoding.") from exc


def save_from_form(canvas: dict[str, Any], *, change_note: str = "Canvas updated") -> tuple[int, str]:
    form_data = request.form.to_dict(flat=True)
    upload = request.files.get("behavioral_signal_file")
    if upload and upload.filename:
        form_data["behavioral_signal_csv"] = read_behavioral_signal_upload(upload)
    updated = normalize_form(form_data, canvas)
    project_id = str(canvas.get("_project_id") or session.get("project_id") or "")
    revision_storage_id = save_canvas(
        db_path(),
        updated,
        canvas.get("_storage_id"),
        project_id=project_id or None,
        workspace_id=workspace_id(),
        change_note=change_note,
    )
    saved = get_canvas(db_path(), revision_storage_id)
    if not saved:
        raise RuntimeError("Saved revision could not be reloaded")
    session["project_id"] = saved["_project_id"]
    return revision_storage_id, saved["_project_id"]


@bp.app_context_processor
def inject_workspace_context() -> dict[str, Any]:
    active_project = None
    project_id = session.get("project_id")
    if project_id:
        active_project = _project_in_workspace(str(project_id))
    return {
        "active_workspace": get_workspace(db_path(), workspace_id()),
        "active_project": active_project,
        "active_member": current_member(),
    }


@bp.route("/")
def index():
    query = request.args.get("q", "").strip()
    status = request.args.get("status", "active").strip().lower()
    if status not in {"active", "archived", "all"}:
        status = "active"
    return render_template(
        "index.html",
        projects=list_projects(
            db_path(),
            workspace_id=workspace_id(),
            query=query,
            status=status,
            limit=100,
        ),
        counts=project_counts(db_path(), workspace_id()),
        query=query,
        status=status,
        workspaces=list_workspaces(db_path()),
    )


@bp.route("/intro")
def intro():
    return render_template("intro.html")


@bp.route("/workspaces", methods=["POST"])
def workspace_create():
    workspace = create_workspace(
        db_path(),
        request.form.get("name", "Workspace"),
        description=request.form.get("description", ""),
    )
    session["workspace_id"] = workspace["workspace_id"]
    session.pop("project_id", None)
    return redirect(url_for("canvas.index"))


@bp.route("/workspaces/<workspace_identifier>/open", methods=["POST"])
def workspace_open(workspace_identifier: str):
    if get_workspace(db_path(), workspace_identifier):
        session["workspace_id"] = workspace_identifier
        session.pop("project_id", None)
    return redirect(url_for("canvas.index"))


@bp.route("/projects", methods=["POST"])
def project_create():
    title = request.form.get("title", "Untitled Canvas Project").strip() or "Untitled Canvas Project"
    canvas = new_canvas()
    canvas["title"] = title
    canvas["canvas_id"] = new_id("canvas")
    canvas["revision_id"] = new_id("revision")
    canvas["created_at"] = utc_now()
    canvas["updated_at"] = canvas["created_at"]
    project = create_project(
        db_path(),
        canvas,
        workspace_id=workspace_id(),
        title=title,
        description=request.form.get("description", ""),
        tags=request.form.get("tags", ""),
    )
    session["project_id"] = project["project_id"]
    return redirect(url_for("canvas.define"))


@bp.route("/projects/<project_id>/open")
def project_open(project_id: str):
    project = _project_in_workspace(project_id)
    if not project:
        return Response("Project not found\n", status=404, mimetype="text/plain")
    if project["status"] == "archived":
        return redirect(url_for("canvas.index", status="archived"))
    session["project_id"] = project_id
    return redirect(url_for("canvas.define"))


@bp.route("/projects/<project_id>/archive", methods=["POST"])
def project_archive(project_id: str):
    if not _project_in_workspace(project_id):
        return Response("Project not found\n", status=404, mimetype="text/plain")
    archive_project(db_path(), project_id)
    if session.get("project_id") == project_id:
        session.pop("project_id", None)
    return redirect(url_for("canvas.index", status="archived"))


@bp.route("/projects/<project_id>/restore", methods=["POST"])
def project_restore(project_id: str):
    if not _project_in_workspace(project_id):
        return Response("Project not found\n", status=404, mimetype="text/plain")
    restore_project(db_path(), project_id)
    session["project_id"] = project_id
    return redirect(url_for("canvas.index"))


@bp.route("/projects/<project_id>/duplicate", methods=["POST"])
def project_duplicate(project_id: str):
    if not _project_in_workspace(project_id):
        return Response("Project not found\n", status=404, mimetype="text/plain")
    duplicate = duplicate_project(db_path(), project_id, title=request.form.get("title") or None)
    if not duplicate:
        return Response("Project not found\n", status=404, mimetype="text/plain")
    session["project_id"] = duplicate["project_id"]
    return redirect(url_for("canvas.define"))


@bp.route("/projects/<project_id>/metadata", methods=["POST"])
def project_metadata(project_id: str):
    if not _project_in_workspace(project_id):
        return Response("Project not found\n", status=404, mimetype="text/plain")
    update_project_metadata(
        db_path(),
        project_id,
        title=request.form.get("title"),
        description=request.form.get("description"),
        tags=request.form.get("tags"),
    )
    return redirect(url_for("canvas.project_revisions", project_id=project_id))


@bp.route("/projects/<project_id>/revisions")
def project_revisions(project_id: str):
    project = _project_in_workspace(project_id)
    if not project:
        return Response("Project not found\n", status=404, mimetype="text/plain")
    return render_template(
        "projects/revisions.html",
        project=project,
        revisions=list_revisions(db_path(), project_id),
    )


@bp.route("/projects/<project_id>/revisions/<revision_id>/restore", methods=["POST"])
def revision_restore(project_id: str, revision_id: str):
    if not _project_in_workspace(project_id):
        return Response("Project not found\n", status=404, mimetype="text/plain")
    storage_id = restore_revision(db_path(), project_id, revision_id)
    if storage_id is None:
        return Response("Revision not found\n", status=404, mimetype="text/plain")
    session["project_id"] = project_id
    return redirect(url_for("canvas.project_revisions", project_id=project_id))


@bp.route("/define", methods=["GET", "POST"])
def define():
    canvas = current_canvas()
    if request.method == "POST":
        save_from_form(canvas, change_note="Problem framing updated")
        return redirect(url_for("canvas.empathy"))
    return render_template("define/define.html", canvas=view_model(canvas))


@bp.route("/empathy", methods=["GET", "POST"])
def empathy():
    canvas = current_canvas()
    if request.method == "POST":
        save_from_form(canvas, change_note="Empathy map updated")
        return redirect(url_for("canvas.ideate"))
    return render_template("empathize/empathy_map.html", canvas=view_model(canvas))


@bp.route("/ledger", methods=["GET", "POST"])
def evidence_ledger():
    canvas = current_canvas()
    project_id = str(canvas.get("_project_id") or session.get("project_id") or "")
    if request.method == "POST":
        try:
            save_from_form(canvas, change_note="Research evidence and assumption ledger updated")
        except ValueError as exc:
            return Response(str(exc) + "\n", status=400, mimetype="text/plain")
        return redirect(url_for("canvas.evidence_ledger"))
    return render_template(
        "research/ledger.html",
        canvas=view_model(canvas),
        contract=strip_internal_fields(canvas),
        project_id=project_id,
        assets=list_research_assets(db_path(), workspace_id=workspace_id(), query=request.args.get("q", "")),
        asset_counts=research_asset_counts(db_path(), workspace_id()),
        query=request.args.get("q", ""),
    )


@bp.route("/projects/<project_id>/research-handoff/<target>.json")
def research_handoff_export(project_id: str, target: str):
    if target not in {"knowledge_library", "research_librarian"}:
        return jsonify({"error": "unsupported target"}), 404
    if not _project_in_workspace(project_id):
        return jsonify({"error": "not found"}), 404
    canvas = get_project_canvas(db_path(), project_id)
    return jsonify(build_handoff_package(strip_internal_fields(canvas), target))


@bp.route("/api/ledger")
def ledger_api():
    canvas = current_canvas()
    return jsonify({
        "workspace_id": workspace_id(),
        "project_id": canvas.get("_project_id", ""),
        "ledger_summary": canvas.get("ledger_summary", {}),
        "sources": canvas.get("sources", []),
        "evidence": canvas.get("evidence", []),
        "claims": canvas.get("claims", []),
        "assumptions": canvas.get("assumptions", []),
        "research_questions": canvas.get("research_questions", []),
    })


@bp.route("/research", methods=["GET", "POST"])
def research_studio():
    canvas = current_canvas()
    project_id = str(canvas.get("_project_id") or session.get("project_id") or "")
    if request.method == "POST":
        try:
            save_from_form(canvas, change_note="Persona, stakeholder, and journey research updated")
        except ValueError as exc:
            return Response(str(exc) + "\n", status=400, mimetype="text/plain")
        return redirect(url_for("canvas.research_studio"))
    return render_template(
        "research/studio.html",
        canvas=view_model(canvas),
        contract=strip_internal_fields(canvas),
        assets=list_research_assets(db_path(), workspace_id=workspace_id(), query=request.args.get("q", "")),
        asset_counts=research_asset_counts(db_path(), workspace_id()),
        project_id=project_id,
        query=request.args.get("q", ""),
        persona_templates=list_persona_templates(),
    )


@bp.route("/research/compare")
def research_compare():
    asset_type = request.args.get("type", "persona")
    if asset_type not in {"persona", "journey"}:
        asset_type = "persona"
    assets = list_research_assets(db_path(), workspace_id=workspace_id(), asset_type=asset_type, query=request.args.get("q", ""))
    return render_template("research/compare.html", asset_type=asset_type, assets=assets, query=request.args.get("q", ""))


@bp.route("/projects/<project_id>/research-assets/<path:asset_key>/reuse", methods=["POST"])
def research_asset_reuse(project_id: str, asset_key: str):
    if not _project_in_workspace(project_id):
        return Response("Project not found\n", status=404, mimetype="text/plain")
    try:
        reuse_research_asset(db_path(), project_id, asset_key, workspace_id=workspace_id())
    except ValueError as exc:
        return Response(str(exc) + "\n", status=404, mimetype="text/plain")
    session["project_id"] = project_id
    return redirect(url_for("canvas.research_studio"))


@bp.route("/api/research/persona-templates")
def persona_templates_api():
    return jsonify({"templates": list_persona_templates()})


@bp.route("/api/research/assets")
def research_assets_api():
    asset_type = request.args.get("type", "all")
    assets = list_research_assets(
        db_path(), workspace_id=workspace_id(), asset_type=asset_type, query=request.args.get("q", "")
    )
    return jsonify({"workspace_id": workspace_id(), "counts": research_asset_counts(db_path(), workspace_id()), "assets": assets})


@bp.route("/personas")
def personas():
    return render_template("personas/index.html", personas=SAMPLE_PERSONAS)


@bp.route("/personas/<slug>")
def persona_view(slug: str):
    persona = next((item for item in SAMPLE_PERSONAS if item["slug"] == slug), None)
    if not persona:
        return redirect(url_for("canvas.personas"))
    return render_template("personas/view.html", persona=persona)


@bp.route("/personas/edit", methods=["GET", "POST"])
def persona_edit():
    canvas = current_canvas()
    if request.method == "POST":
        save_from_form(canvas, change_note="Persona updated")
        return redirect(url_for("canvas.empathy"))
    return render_template("personas/edit.html", canvas=view_model(canvas))


@bp.route("/personas/ga4-import")
def ga4_import():
    return render_template("personas/ga4_import.html")


@bp.route("/ideate", methods=["GET", "POST"])
def ideate():
    canvas = current_canvas()
    form_canvas = view_model(canvas)
    framework = request.values.get("framework", form_canvas.get("framework", "AIDA"))
    custom_frameworks = canvas.get("custom_frameworks", [])
    if request.method == "POST":
        try:
            save_from_form(canvas, change_note="Framework and ideation studio updated")
        except ValueError as exc:
            return Response(str(exc) + "\n", status=400, mimetype="text/plain")
        return redirect(url_for("canvas.ideate"))
    return render_template(
        "ideate/ideate.html",
        canvas=form_canvas,
        contract=strip_internal_fields(canvas),
        frameworks=all_frameworks(custom_frameworks),
        framework=framework,
        framework_record=get_framework_record(framework, custom_frameworks),
        prompts=get_framework(framework, custom_frameworks),
    )


@bp.route("/api/frameworks")
def frameworks_api():
    canvas = current_canvas()
    return jsonify({
        "contract": "catalyst-canvas-framework-registry/1.0",
        "active_framework_key": canvas.get("framework", {}).get("key", "AIDA"),
        "frameworks": list(framework_registry(canvas.get("custom_frameworks", [])).values()),
        "prompt_packs": canvas.get("prompt_packs", []),
    })


@bp.route("/projects/<project_id>/frameworks.json")
def framework_package_export(project_id: str):
    if not _project_in_workspace(project_id):
        return jsonify({"error": "not found"}), 404
    canvas = get_project_canvas(db_path(), project_id)
    return jsonify(export_framework_package(canvas.get("custom_frameworks", []), organization=canvas.get("owner_context", {}).get("organization", "")))


@bp.route("/api/frameworks/import", methods=["POST"])
def framework_package_import():
    canvas = current_canvas()
    payload = request.get_json(silent=True) or {}
    try:
        imported = import_framework_package(payload)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    updated = strip_internal_fields(canvas)
    existing = {item.get("key"): item for item in updated.get("custom_frameworks", [])}
    for item in imported:
        existing[item["key"]] = item
    updated["custom_frameworks"] = list(existing.values())
    updated["revision_id"] = new_id("revision")
    updated["updated_at"] = utc_now()
    from catalyst_canvas.engine import generate_canvas
    updated = generate_canvas(updated, source_surface="flask")
    save_canvas(db_path(), updated, project_id=canvas.get("_project_id"), workspace_id=workspace_id(), change_note="Framework package imported")
    return jsonify({"imported": [item["key"] for item in imported], "framework_count": len(updated["custom_frameworks"])})


@bp.route("/api/ideation")
def ideation_api():
    canvas = current_canvas()
    return jsonify({
        "workspace_id": workspace_id(),
        "project_id": canvas.get("_project_id", ""),
        "ideation_summary": canvas.get("ideation_summary", {}),
        "sessions": canvas.get("ideation_sessions", []),
        "ideas": canvas.get("ideas", []),
        "clusters": canvas.get("idea_clusters", []),
    })


@bp.route("/api/ideas/<idea_id>/vote", methods=["POST"])
def idea_vote(idea_id: str):
    canvas = current_canvas()
    updated = strip_internal_fields(canvas)
    voter_id = clean_text((request.get_json(silent=True) or {}).get("voter_id"), "anonymous")
    target = next((item for item in updated.get("ideas", []) if item.get("idea_id") == idea_id), None)
    if not target:
        return jsonify({"error": "idea not found"}), 404
    voters = list(target.get("voter_ids", []))
    if voter_id not in voters:
        voters.append(voter_id)
    target["voter_ids"] = voters
    target["vote_count"] = len(voters)
    target["updated_at"] = utc_now()
    updated["revision_id"] = new_id("revision")
    updated["updated_at"] = target["updated_at"]
    from catalyst_canvas.engine import generate_canvas
    updated = generate_canvas(updated, source_surface="flask")
    save_canvas(db_path(), updated, project_id=canvas.get("_project_id"), workspace_id=workspace_id(), change_note=f"Vote recorded for {idea_id}")
    return jsonify({"idea_id": idea_id, "vote_count": target["vote_count"]})


@bp.route("/api/ideas/merge", methods=["POST"])
def idea_merge():
    canvas = current_canvas()
    payload = request.get_json(silent=True) or {}
    source_ids = payload.get("source_ids") if isinstance(payload.get("source_ids"), list) else []
    target = payload.get("target") if isinstance(payload.get("target"), dict) else {}
    if len(source_ids) < 2 or not target.get("title"):
        return jsonify({"error": "Provide at least two source_ids and a target title."}), 400
    updated = strip_internal_fields(canvas)
    updated["ideas"] = merge_idea_records(updated.get("ideas", []), source_ids, target)
    updated["revision_id"] = new_id("revision")
    updated["updated_at"] = utc_now()
    from catalyst_canvas.engine import generate_canvas
    updated = generate_canvas(updated, source_surface="flask")
    save_canvas(db_path(), updated, project_id=canvas.get("_project_id"), workspace_id=workspace_id(), change_note="Ideas merged")
    merged = updated["ideas"][-1]
    return jsonify({"merged_idea": merged, "ideation_summary": updated["ideation_summary"]})


@bp.route("/prioritize", methods=["GET", "POST"])
def prioritize():
    canvas = current_canvas()
    if request.method == "POST":
        try:
            save_from_form(canvas, change_note="Prioritization and decision readiness updated")
        except ValueError as exc:
            return Response(str(exc) + "\n", status=400, mimetype="text/plain")
        return redirect(url_for("canvas.prioritize"))
    contract = strip_internal_fields(canvas)
    return render_template(
        "prioritize/prioritize.html",
        canvas=view_model(canvas),
        contract=contract,
        baseline=(contract.get("sensitivity_views") or [{}])[0],
    )


@bp.route("/api/prioritization")
def prioritization_api():
    canvas = current_canvas()
    return jsonify({
        "workspace_id": workspace_id(),
        "project_id": canvas.get("_project_id", ""),
        "decision_criteria": canvas.get("decision_criteria", []),
        "decision_options": canvas.get("decision_options", []),
        "sensitivity_views": canvas.get("sensitivity_views", []),
        "decision_notes": canvas.get("decision_notes", []),
        "decision_handoffs": canvas.get("decision_handoffs", []),
        "prioritization_summary": canvas.get("prioritization_summary", {}),
    })


@bp.route("/api/prioritization/sensitivity", methods=["POST"])
def prioritization_sensitivity_api():
    canvas = current_canvas()
    payload = request.get_json(silent=True) or {}
    scenario = {
        "scenario_id": clean_text(payload.get("scenario_id"), "sensitivity-preview"),
        "name": clean_text(payload.get("name"), "Sensitivity preview"),
        "description": clean_text(payload.get("description")),
        "weight_overrides": payload.get("weight_overrides") if isinstance(payload.get("weight_overrides"), list) else [],
    }
    views = normalize_sensitivity_views(
        [scenario],
        options=canvas.get("decision_options", []),
        criteria=canvas.get("decision_criteria", []),
        generated_at=utc_now(),
    )
    return jsonify({"baseline": views[0], "scenario": views[1]})


@bp.route("/projects/<project_id>/decision-handoff/<target>.json")
def decision_handoff_export(project_id: str, target: str):
    if target not in {"decision_studio", "workbench"}:
        return jsonify({"error": "unsupported target"}), 404
    if not _project_in_workspace(project_id):
        return jsonify({"error": "not found"}), 404
    canvas = get_project_canvas(db_path(), project_id)
    return jsonify(build_decision_handoff_package(strip_internal_fields(canvas), target))




@bp.route("/experiment", methods=["GET", "POST"])
def experiment_studio():
    canvas = current_canvas()
    if request.method == "POST":
        try:
            save_from_form(canvas, change_note="Prototype and experiment studio updated")
        except ValueError as exc:
            return Response(str(exc) + "\n", status=400, mimetype="text/plain")
        return redirect(url_for("canvas.experiment_studio"))
    contract = strip_internal_fields(canvas)
    return render_template(
        "experiment/studio.html",
        canvas=view_model(canvas),
        contract=contract,
    )


@bp.route("/api/experiments")
def experiments_api():
    canvas = current_canvas()
    return jsonify({
        "workspace_id": workspace_id(),
        "project_id": canvas.get("_project_id", ""),
        "prototypes": canvas.get("prototypes", []),
        "hypotheses": canvas.get("hypotheses", []),
        "experiment_plans": canvas.get("experiment_plans", []),
        "experiment_runs": canvas.get("experiment_runs", []),
        "learning_decisions": canvas.get("learning_decisions", []),
        "iteration_history": canvas.get("iteration_history", []),
        "experiment_handoffs": canvas.get("experiment_handoffs", []),
        "experiment_summary": canvas.get("experiment_summary", {}),
    })


@bp.route("/api/experiments/runs", methods=["POST"])
def experiment_run_create():
    canvas = current_canvas()
    payload = request.get_json(silent=True) or {}
    if not clean_text(payload.get("experiment_id")):
        return jsonify({"error": "experiment_id is required"}), 400
    updated = strip_internal_fields(canvas)
    updated.setdefault("experiment_runs", []).append(payload)
    updated["revision_id"] = new_id("revision")
    updated["updated_at"] = utc_now()
    from catalyst_canvas.engine import generate_canvas
    updated = generate_canvas(updated, source_surface="flask")
    save_canvas(
        db_path(), updated, project_id=canvas.get("_project_id"), workspace_id=workspace_id(),
        change_note=f"Experiment run recorded for {payload.get('experiment_id')}",
    )
    return jsonify({"run": updated["experiment_runs"][-1], "experiment_summary": updated["experiment_summary"]}), 201


@bp.route("/projects/<project_id>/experiment-handoff/<target>.json")
def experiment_handoff_export(project_id: str, target: str):
    if target not in {"research_lab", "workbench"}:
        return jsonify({"error": "unsupported target"}), 404
    if not _project_in_workspace(project_id):
        return jsonify({"error": "not found"}), 404
    canvas = get_project_canvas(db_path(), project_id)
    return jsonify(build_experiment_handoff_package(strip_internal_fields(canvas), target))


@bp.route("/collaborate", methods=["GET", "POST"])
def collaboration_studio():
    canvas = current_canvas()
    if request.method == "POST":
        denied = require_capability("edit")
        if denied:
            return denied
        try:
            save_from_form(canvas, change_note="Collaboration, review, and publication workspace updated")
        except ValueError as exc:
            return Response(str(exc) + "\n", status=400, mimetype="text/plain")
        return redirect(url_for("canvas.collaboration_studio"))
    contract = strip_internal_fields(canvas)
    return render_template(
        "collaboration/studio.html",
        canvas=view_model(canvas),
        contract=contract,
        members=list_workspace_members(db_path(), workspace_id()),
        records=list_collaboration_records(db_path(), workspace_id(), project_id=str(canvas.get("_project_id") or "")),
        record_counts=collaboration_record_counts(db_path(), workspace_id(), str(canvas.get("_project_id") or "")),
    )


@bp.route("/api/collaboration")
def collaboration_api():
    canvas = current_canvas()
    return jsonify({
        "workspace_id": workspace_id(),
        "project_id": canvas.get("_project_id", ""),
        "member": current_member(),
        "workspace_members": canvas.get("workspace_members", []),
        "review_assignments": canvas.get("review_assignments", []),
        "comments": canvas.get("comments", []),
        "approvals": canvas.get("approvals", []),
        "publication_records": canvas.get("publication_records", []),
        "release_history": canvas.get("release_history", []),
        "publication_handoffs": canvas.get("publication_handoffs", []),
        "collaboration_summary": canvas.get("collaboration_summary", {}),
    })


@bp.route("/api/workspaces/members", methods=["GET", "POST"])
def workspace_members_api():
    if request.method == "GET":
        return jsonify({"workspace_id": workspace_id(), "members": list_workspace_members(db_path(), workspace_id())})
    denied = require_capability("manage_members")
    if denied:
        return denied
    payload = request.get_json(silent=True) or {}
    member_id = clean_text(payload.get("member_id"))
    if not member_id:
        return jsonify({"error": "member_id is required"}), 400
    member = ensure_workspace_member(
        db_path(), workspace_id(), member_id, name=clean_text(payload.get("name"), member_id),
        organization=clean_text(payload.get("organization")), role=clean_text(payload.get("role"), "viewer"),
        status=clean_text(payload.get("status"), "active"),
    )
    return jsonify({"member": member}), 201


@bp.route("/api/comments", methods=["POST"])
def comment_create():
    denied = require_capability("comment")
    if denied:
        return denied
    canvas = current_canvas()
    payload = request.get_json(silent=True) or {}
    if not clean_text(payload.get("body")):
        return jsonify({"error": "body is required"}), 400
    updated = strip_internal_fields(canvas)
    payload.setdefault("author_id", acting_user_id())
    payload.setdefault("created_at", utc_now())
    payload.setdefault("updated_at", payload["created_at"])
    updated.setdefault("comments", []).append(payload)
    updated["revision_id"] = new_id("revision")
    updated["updated_at"] = utc_now()
    from catalyst_canvas.engine import generate_canvas
    updated = generate_canvas(updated, source_surface="flask")
    save_canvas(db_path(), updated, project_id=canvas.get("_project_id"), workspace_id=workspace_id(), change_note="Review comment added")
    return jsonify({"comment": updated["comments"][-1], "collaboration_summary": updated["collaboration_summary"]}), 201


@bp.route("/api/comments/<comment_id>/resolve", methods=["POST"])
def comment_resolve(comment_id: str):
    denied = require_capability("comment")
    if denied:
        return denied
    canvas = current_canvas(); updated = strip_internal_fields(canvas)
    target = next((item for item in updated.get("comments", []) if item.get("comment_id") == comment_id), None)
    if not target:
        return jsonify({"error": "comment not found"}), 404
    target.update({"status": "resolved", "resolved_by": acting_user_id(), "resolved_at": utc_now(), "updated_at": utc_now()})
    updated["revision_id"] = new_id("revision"); updated["updated_at"] = utc_now()
    from catalyst_canvas.engine import generate_canvas
    updated = generate_canvas(updated, source_surface="flask")
    save_canvas(db_path(), updated, project_id=canvas.get("_project_id"), workspace_id=workspace_id(), change_note=f"Comment {comment_id} resolved")
    return jsonify({"comment": next(item for item in updated["comments"] if item["comment_id"] == comment_id)})


@bp.route("/api/reviews", methods=["POST"])
def review_assignment_create():
    denied = require_capability("assign_review")
    if denied:
        return denied
    canvas=current_canvas(); payload=request.get_json(silent=True) or {}
    if not clean_text(payload.get("title")):
        return jsonify({"error":"title is required"}),400
    updated=strip_internal_fields(canvas); payload.setdefault("requested_by",acting_user_id()); payload.setdefault("created_at",utc_now())
    updated.setdefault("review_assignments",[]).append(payload); updated["revision_id"]=new_id("revision"); updated["updated_at"]=utc_now()
    from catalyst_canvas.engine import generate_canvas
    updated=generate_canvas(updated,source_surface="flask")
    save_canvas(db_path(),updated,project_id=canvas.get("_project_id"),workspace_id=workspace_id(),change_note="Review assignment created")
    return jsonify({"assignment":updated["review_assignments"][-1]}),201


@bp.route("/api/approvals", methods=["POST"])
def approval_create():
    denied = require_capability("approve")
    if denied:
        return denied
    canvas=current_canvas(); payload=request.get_json(silent=True) or {}; payload.setdefault("reviewer_id",acting_user_id()); payload.setdefault("created_at",utc_now())
    if clean_text(payload.get("decision")) not in {"pending","approved","changes_requested","rejected","abstained"}:
        return jsonify({"error":"invalid decision"}),400
    if payload.get("decision") != "pending": payload.setdefault("decided_at",utc_now())
    updated=strip_internal_fields(canvas); updated.setdefault("approvals",[]).append(payload); updated["revision_id"]=new_id("revision"); updated["updated_at"]=utc_now()
    from catalyst_canvas.engine import generate_canvas
    updated=generate_canvas(updated,source_surface="flask")
    save_canvas(db_path(),updated,project_id=canvas.get("_project_id"),workspace_id=workspace_id(),change_note="Approval decision recorded")
    return jsonify({"approval":updated["approvals"][-1],"collaboration_summary":updated["collaboration_summary"]}),201


def _publication_clear(contract: dict[str, Any], publication: dict[str, Any]) -> tuple[bool, list[str]]:
    reasons=[]
    assignments={item.get("assignment_id"):item for item in contract.get("review_assignments",[])}
    approvals={item.get("approval_id"):item for item in contract.get("approvals",[])}
    review_ids=publication.get("review_assignment_ids",[])
    approval_ids=publication.get("approval_ids",[])
    if review_ids and any(assignments.get(identifier,{}).get("status") != "complete" for identifier in review_ids): reasons.append("required reviews are incomplete")
    if not approval_ids: reasons.append("no publication approval is linked")
    elif any(approvals.get(identifier,{}).get("decision") != "approved" for identifier in approval_ids): reasons.append("linked approvals are not all approved")
    if publication.get("publication_type") != "internal_report" and not publication.get("redaction_notes"): reasons.append("public redaction review is not recorded")
    if any(item.get("decision") in {"rejected","changes_requested"} for item in contract.get("approvals",[])): reasons.append("an approval blocks publication")
    return not reasons,reasons


@bp.route("/api/publications/<publication_id>/publish", methods=["POST"])
def publication_publish(publication_id: str):
    denied = require_capability("publish")
    if denied:
        return denied
    canvas=current_canvas(); updated=strip_internal_fields(canvas)
    publication=next((item for item in updated.get("publication_records",[]) if item.get("publication_id")==publication_id),None)
    if not publication: return jsonify({"error":"publication not found"}),404
    clear,reasons=_publication_clear(updated,publication)
    if not clear: return jsonify({"error":"publication is not cleared","reasons":reasons}),409
    published_at=utc_now(); publication.update({"state":"published","published_at":published_at,"updated_at":published_at})
    updated["revision_id"]=new_id("revision"); updated["updated_at"]=published_at
    from catalyst_canvas.engine import generate_canvas
    updated=generate_canvas(updated,source_surface="flask")
    release=publication_release_record(updated,publication_id,published_by=acting_user_id(),generated_at=published_at,url=clean_text((request.get_json(silent=True) or {}).get("url")))
    updated["release_history"]=[*updated.get("release_history",[]),release]; updated["revision_id"]=new_id("revision")
    updated=generate_canvas(updated,source_surface="flask")
    save_canvas(db_path(),updated,project_id=canvas.get("_project_id"),workspace_id=workspace_id(),change_note=f"Publication {publication_id} released")
    return jsonify({"publication":next(item for item in updated["publication_records"] if item["publication_id"]==publication_id),"release":release,"collaboration_summary":updated["collaboration_summary"]}),201


@bp.route("/projects/<project_id>/publication/<target>.json")
def publication_export(project_id: str, target: str):
    if target not in {"wordpress","knowledge_library","public_api","download"}: return jsonify({"error":"unsupported target"}),404
    if not _project_in_workspace(project_id): return jsonify({"error":"not found"}),404
    canvas=get_project_canvas(db_path(),project_id)
    return jsonify(build_publication_package(strip_internal_fields(canvas),target,request.args.get("publication_id", "")))


@bp.route("/projects/<project_id>/public.json")
def public_safe_export(project_id: str):
    if not _project_in_workspace(project_id): return jsonify({"error":"not found"}),404
    canvas=get_project_canvas(db_path(),project_id)
    return jsonify(build_publication_package(strip_internal_fields(canvas),"public_api",request.args.get("publication_id", "")))


@bp.route("/platform")
def platform_studio():
    canvas = current_canvas()
    project_id = str(canvas.get("_project_id") or session.get("project_id") or "")
    return render_template(
        "platform/studio.html",
        canvas=view_model(canvas),
        contract=strip_internal_fields(canvas),
        project_id=project_id,
        records=list_platform_records(db_path(), workspace_id(), project_id=project_id),
        counts=platform_record_counts(db_path(), workspace_id(), project_id),
    )


@bp.route("/api/platform")
def platform_api():
    canvas = current_canvas()
    project_id = str(canvas.get("_project_id") or session.get("project_id") or "")
    return jsonify({
        "project_id": project_id,
        "platform_connections": canvas.get("platform_connections", []),
        "interoperability_profiles": canvas.get("interoperability_profiles", []),
        "workflow_links": canvas.get("workflow_links", []),
        "exchange_records": canvas.get("exchange_records", []),
        "platform_events": canvas.get("platform_events", []),
        "platform_summary": canvas.get("platform_summary", {}),
        "record_counts": platform_record_counts(db_path(), workspace_id(), project_id),
    })


@bp.route("/api/capabilities")
def capabilities_api():
    return jsonify(capability_manifest(strip_internal_fields(current_canvas())))


@bp.route("/projects/<project_id>/exchange/<target>.json")
def platform_exchange_export(project_id: str, target: str):
    if not _project_in_workspace(project_id):
        return jsonify({"error": "not found"}), 404
    canvas = get_project_canvas(db_path(), project_id)
    signing_key = current_app.config.get("CANVAS_EXCHANGE_SIGNING_KEY", "")
    package = build_exchange_package(
        strip_internal_fields(canvas),
        target,
        payload_type=request.args.get("payload_type", "full_canvas"),
        profile_id=request.args.get("profile_id", ""),
        signing_key=signing_key or None,
        created_by=acting_user_id(),
    )
    return jsonify(package)


@bp.route("/api/exchange/verify", methods=["POST"])
def platform_exchange_verify():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Expected a JSON exchange package."}), 400
    signing_key = current_app.config.get("CANVAS_EXCHANGE_SIGNING_KEY", "")
    result = verify_exchange_package(payload, signing_key or None)
    return jsonify(result), (200 if result["valid"] else 422)


@bp.route("/ideate/heros")
def heros():
    return render_template("ideate/heros.html", prompts=get_framework("Hero"))


@bp.route("/ideate/jtbd")
def jtbd():
    return render_template("ideate/jtbd.html", prompts=get_framework("JTBD"))


@bp.route("/ideate/matrix")
def matrix():
    return render_template("ideate/matrix.html", prompts=get_framework("Matrix"))


@bp.route("/ideate/matrix-board")
def matrix_board():
    return render_template("ideate/matrix_board.html", prompts=get_framework("Matrix"))


@bp.route("/prototype", methods=["GET", "POST"])
def prototype():
    canvas = current_canvas()
    if request.method == "POST":
        save_from_form(canvas, change_note="Prototype updated")
        return redirect(url_for("canvas.test_plan"))
    return render_template("prototype/prototype.html", canvas=view_model(canvas))


@bp.route("/prototype/storyboard")
def storyboard():
    return render_template("prototype/storyboard.html", canvas=view_model(current_canvas()))


@bp.route("/test", methods=["GET", "POST"])
def test_plan():
    canvas = current_canvas()
    if request.method == "POST":
        save_from_form(canvas, change_note="Test plan updated")
        return redirect(url_for("canvas.report"))
    return render_template("test/test.html", canvas=view_model(canvas))


@bp.route("/report")
def report():
    canvas = current_canvas()
    return render_template(
        "export/report.html",
        canvas=view_model(canvas),
        markdown=to_markdown(canvas),
        pretty_json=to_pretty_json(canvas),
    )


@bp.route("/api/workspaces")
def workspaces_api():
    return jsonify({"workspaces": list_workspaces(db_path()), "active_workspace_id": workspace_id()})


@bp.route("/api/projects")
def projects_api():
    status = request.args.get("status", "active")
    query = request.args.get("q", "")
    return jsonify({
        "workspace_id": workspace_id(),
        "projects": [public_project(item) for item in list_projects(
            db_path(), workspace_id=workspace_id(), status=status, query=query, limit=200
        )],
    })


@bp.route("/api/projects/<project_id>", methods=["GET", "PATCH"])
def project_api(project_id: str):
    project = _project_in_workspace(project_id)
    if not project:
        return jsonify({"error": "not found"}), 404
    if request.method == "PATCH":
        payload = request.get_json(silent=True) or {}
        project = update_project_metadata(
            db_path(),
            project_id,
            title=payload.get("title") if "title" in payload else None,
            description=payload.get("description") if "description" in payload else None,
            tags=payload.get("tags") if "tags" in payload else None,
        ) or project
    canvas = get_project_canvas(db_path(), project_id)
    return jsonify({"project": public_project(project), "canvas": strip_internal_fields(canvas) if canvas else None})


@bp.route("/api/projects/<project_id>/revisions")
def revisions_api(project_id: str):
    if not _project_in_workspace(project_id):
        return jsonify({"error": "not found"}), 404
    return jsonify({"project_id": project_id, "revisions": list_revisions(db_path(), project_id)})


@bp.route("/api/projects/<project_id>/autosave", methods=["POST"])
def project_autosave(project_id: str):
    project = _project_in_workspace(project_id)
    if not project:
        return jsonify({"error": "not found"}), 404
    if project["status"] == "archived":
        return jsonify({"error": "archived projects are read-only"}), 409
    current = get_project_canvas(db_path(), project_id)
    if not current:
        return jsonify({"error": "current Canvas not found"}), 404
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Expected a JSON object."}), 400
    try:
        if payload.get("schema_version"):
            result = migrate_payload(payload, source_surface="flask-autosave")
            updated = result.contract
            # An autosave is always a new revision, even when a client submits
            # the prior revision identifier.
            updated["canvas_id"] = current["canvas_id"]
            updated["revision_id"] = new_id("revision")
            updated["created_at"] = current["created_at"]
            updated["updated_at"] = utc_now()
        else:
            updated = normalize_form(payload, current)
        storage_id = save_canvas(
            db_path(),
            updated,
            project_id=project_id,
            workspace_id=workspace_id(),
            autosave=True,
            change_note="Autosave",
        )
    except (CanvasContractError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 422
    saved = get_canvas(db_path(), storage_id)
    return jsonify({
        "project_id": project_id,
        "revision_id": saved["revision_id"] if saved else "",
        "storage_id": storage_id,
        "saved_at": saved["updated_at"] if saved else utc_now(),
        "autosave": True,
    }), 201


@bp.route("/api/canvas/<int:canvas_id>.json")
def canvas_json(canvas_id: int):
    canvas = get_canvas(db_path(), canvas_id)
    if not canvas or canvas.get("_workspace_id") != workspace_id():
        return jsonify({"error": "not found"}), 404
    return jsonify(strip_internal_fields(canvas))


@bp.route("/api/canvas/import", methods=["POST"])
def canvas_import():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Expected a JSON object."}), 400
    try:
        result = migrate_payload(payload, source_surface="import")
        project = create_project(
            db_path(),
            result.contract,
            workspace_id=workspace_id(),
            title=result.contract["title"],
            change_note="Imported Canvas",
        )
    except CanvasContractError as exc:
        return jsonify({"error": str(exc)}), 422
    session["project_id"] = project["project_id"]
    return jsonify({
        "storage_id": project["_current_revision_storage_id"],
        "workspace_id": project["workspace_id"],
        "project_id": project["project_id"],
        "schema_version": result.contract["schema_version"],
        "canvas_id": result.contract["canvas_id"],
        "migrated_from": result.migrated_from,
        "warnings": result.warnings,
    }), 201


@bp.route("/api/contract/schema.json")
def contract_schema():
    return jsonify(load_schema())


@bp.route("/api/workspace-contract/schema.json")
def workspace_contract_schema():
    return jsonify(load_workspace_schema())


@bp.route("/export/<int:canvas_id>.md")
def canvas_markdown(canvas_id: int):
    canvas = get_canvas(db_path(), canvas_id)
    if not canvas or canvas.get("_workspace_id") != workspace_id():
        return Response("Not found\n", status=404, mimetype="text/plain")
    return Response(to_markdown(canvas), mimetype="text/markdown")


@bp.route("/export/<int:canvas_id>.html")
def canvas_print_report(canvas_id: int):
    canvas = get_canvas(db_path(), canvas_id)
    if not canvas or canvas.get("_workspace_id") != workspace_id():
        return Response("Not found\n", status=404, mimetype="text/plain")
    return Response(to_print_html(canvas), mimetype="text/html")


@bp.route("/projects/<project_id>/export.json")
def project_json_export(project_id: str):
    if not _project_in_workspace(project_id):
        return jsonify({"error": "not found"}), 404
    canvas = get_project_canvas(db_path(), project_id)
    return jsonify(strip_internal_fields(canvas))


@bp.route("/projects/<project_id>/export.md")
def project_markdown_export(project_id: str):
    if not _project_in_workspace(project_id):
        return Response("Not found\n", status=404, mimetype="text/plain")
    canvas = get_project_canvas(db_path(), project_id)
    return Response(to_markdown(canvas), mimetype="text/markdown")
