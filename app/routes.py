"""Routes for the local Catalyst Canvas Flask adapter."""

from __future__ import annotations

from flask import Blueprint, Response, current_app, jsonify, redirect, render_template, request, session, url_for

from catalyst_canvas.contract import CanvasContractError, load_schema, strip_internal_fields
from catalyst_canvas.migrations import migrate_payload

from .models import SAMPLE_PERSONAS
from .services.canvas_engine import new_canvas, normalize_form, to_form, to_markdown, to_pretty_json, to_print_html
from .services.frameworks import all_frameworks, get_framework
from .services.storage import get_canvas, latest_canvas, list_canvases, save_canvas

bp = Blueprint("canvas", __name__)


def db_path() -> str:
    return current_app.config["CANVAS_DB"]


def current_canvas() -> dict:
    canvas_id = session.get("canvas_id")
    if canvas_id:
        canvas = get_canvas(db_path(), int(canvas_id))
        if canvas:
            return canvas
    canvas = latest_canvas(db_path())
    if canvas:
        session["canvas_id"] = canvas["_storage_id"]
        return canvas
    return new_canvas()


def view_model(canvas: dict) -> dict:
    return to_form(canvas, storage_id=canvas.get("_storage_id"))


def save_from_form(canvas: dict) -> int:
    updated = normalize_form(request.form, canvas)
    return save_canvas(db_path(), updated, canvas.get("_storage_id"))


@bp.route("/")
def index():
    canvas = current_canvas()
    return render_template("index.html", canvases=list_canvases(db_path()), canvas=view_model(canvas))


@bp.route("/intro")
def intro():
    return render_template("intro.html")


@bp.route("/define", methods=["GET", "POST"])
def define():
    canvas = current_canvas()
    if request.method == "POST":
        session["canvas_id"] = save_from_form(canvas)
        return redirect(url_for("canvas.empathy"))
    return render_template("define/define.html", canvas=view_model(canvas))


@bp.route("/empathy", methods=["GET", "POST"])
def empathy():
    canvas = current_canvas()
    if request.method == "POST":
        session["canvas_id"] = save_from_form(canvas)
        return redirect(url_for("canvas.ideate"))
    return render_template("empathize/empathy_map.html", canvas=view_model(canvas))


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
        session["canvas_id"] = save_from_form(canvas)
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
        session["canvas_id"] = save_from_form(canvas)
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
        session["canvas_id"] = save_from_form(canvas)
        return redirect(url_for("canvas.test_plan"))
    return render_template("prototype/prototype.html", canvas=view_model(canvas))


@bp.route("/prototype/storyboard")
def storyboard():
    return render_template("prototype/storyboard.html", canvas=view_model(current_canvas()))


@bp.route("/test", methods=["GET", "POST"])
def test_plan():
    canvas = current_canvas()
    if request.method == "POST":
        session["canvas_id"] = save_from_form(canvas)
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


@bp.route("/api/canvas/<int:canvas_id>.json")
def canvas_json(canvas_id: int):
    canvas = get_canvas(db_path(), canvas_id)
    if not canvas:
        return jsonify({"error": "not found"}), 404
    return jsonify(strip_internal_fields(canvas))


@bp.route("/api/canvas/import", methods=["POST"])
def canvas_import():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Expected a JSON object."}), 400
    try:
        result = migrate_payload(payload, source_surface="import")
        storage_id = save_canvas(db_path(), result.contract)
    except CanvasContractError as exc:
        return jsonify({"error": str(exc)}), 422
    session["canvas_id"] = storage_id
    return jsonify({
        "storage_id": storage_id,
        "schema_version": result.contract["schema_version"],
        "canvas_id": result.contract["canvas_id"],
        "migrated_from": result.migrated_from,
        "warnings": result.warnings,
    }), 201


@bp.route("/api/contract/schema.json")
def contract_schema():
    return jsonify(load_schema())


@bp.route("/export/<int:canvas_id>.md")
def canvas_markdown(canvas_id: int):
    canvas = get_canvas(db_path(), canvas_id)
    if not canvas:
        return Response("Not found\n", status=404, mimetype="text/plain")
    return Response(to_markdown(canvas), mimetype="text/markdown")


@bp.route("/export/<int:canvas_id>.html")
def canvas_print_report(canvas_id: int):
    canvas = get_canvas(db_path(), canvas_id)
    if not canvas:
        return Response("Not found\n", status=404, mimetype="text/plain")
    return Response(to_print_html(canvas), mimetype="text/html")
