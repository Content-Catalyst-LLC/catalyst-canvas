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

from catalyst_canvas.contract import CanvasContractError, load_schema, new_id, strip_internal_fields, utc_now
from catalyst_canvas.migrations import migrate_payload
from catalyst_canvas.ledger import build_handoff_package
from catalyst_canvas.persona_templates import list_persona_templates
from catalyst_canvas.workspaces import DEFAULT_WORKSPACE_ID, load_workspace_schema

from .models import SAMPLE_PERSONAS
from .services.canvas_engine import new_canvas, normalize_form, to_form, to_markdown, to_pretty_json, to_print_html
from .services.frameworks import all_frameworks, get_framework
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
    framework = request.values.get("framework", view_model(canvas).get("framework", "AIDA"))
    prompts = get_framework(framework)
    if request.method == "POST":
        save_from_form(canvas, change_note="Ideation framework updated")
        return redirect(url_for("canvas.prototype"))
    return render_template(
        "ideate/ideate.html",
        canvas=view_model(canvas),
        frameworks=all_frameworks(),
        framework=framework,
        prompts=prompts,
    )


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
