"""Routes for the local Catalyst Canvas Flask demo."""

from __future__ import annotations

from flask import Blueprint, Response, current_app, jsonify, redirect, render_template, request, session, url_for

from .models import SAMPLE_PERSONAS
from .services.canvas_engine import normalize_form, to_markdown, to_pretty_json
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
        session["canvas_id"] = canvas["id"]
        return canvas
    return normalize_form({
        "title": "Sample Catalyst Canvas Brief",
        "challenge": "A sustainability team needs to turn broad impact goals into testable work.",
        "audience": "sustainability managers and cross-functional project leads",
        "goal": "create a reviewable experiment plan",
        "constraint": "limited data quality and competing stakeholder expectations",
        "persona_name": "Sustainability Manager",
        "persona_needs": "a clearer way to connect goals, evidence, experiments, and reporting outputs",
        "persona_pains": "fragmented data, unclear ownership, and pressure to communicate before evidence is ready",
        "evidence": "Stakeholder interviews, current reporting artifacts, available indicators, and known data gaps.",
        "assumption": "A lightweight Canvas workflow can reduce ambiguity before heavier analytics work begins.",
        "prototype": "A one-page decision brief with claim, source, assumption, experiment, and review sections.",
        "test_plan": "Run the Canvas with one project team and compare clarity before and after the workshop.",
        "success_signal": "The team can identify one testable next step and one unsupported claim to revise.",
        "risk_note": "Do not convert workshop confidence into proof of impact.",
        "review_note": "Require evidence notes before moving from prototype to public claim.",
    })


@bp.route("/")
def index():
    return render_template("index.html", canvases=list_canvases(db_path()), canvas=current_canvas())


@bp.route("/intro")
def intro():
    return render_template("intro.html")


@bp.route("/define", methods=["GET", "POST"])
def define():
    canvas = current_canvas()
    if request.method == "POST":
        updated = normalize_form(request.form, canvas)
        canvas_id = save_canvas(db_path(), updated, canvas.get("id"))
        session["canvas_id"] = canvas_id
        return redirect(url_for("canvas.empathy"))
    return render_template("define/define.html", canvas=canvas)


@bp.route("/empathy", methods=["GET", "POST"])
def empathy():
    canvas = current_canvas()
    if request.method == "POST":
        updated = normalize_form(request.form, canvas)
        canvas_id = save_canvas(db_path(), updated, canvas.get("id"))
        session["canvas_id"] = canvas_id
        return redirect(url_for("canvas.ideate"))
    return render_template("empathize/empathy_map.html", canvas=canvas)


@bp.route("/personas")
def personas():
    return render_template("personas/index.html", personas=SAMPLE_PERSONAS)


@bp.route("/personas/<slug>")
def persona_view(slug: str):
    persona = next((p for p in SAMPLE_PERSONAS if p["slug"] == slug), None)
    if not persona:
        return redirect(url_for("canvas.personas"))
    return render_template("personas/view.html", persona=persona)


@bp.route("/personas/edit", methods=["GET", "POST"])
def persona_edit():
    canvas = current_canvas()
    if request.method == "POST":
        updated = normalize_form(request.form, canvas)
        canvas_id = save_canvas(db_path(), updated, canvas.get("id"))
        session["canvas_id"] = canvas_id
        return redirect(url_for("canvas.empathy"))
    return render_template("personas/edit.html", canvas=canvas)


@bp.route("/personas/ga4-import")
def ga4_import():
    return render_template("personas/ga4_import.html")


@bp.route("/ideate", methods=["GET", "POST"])
def ideate():
    canvas = current_canvas()
    framework = request.values.get("framework", "HERO")
    prompts = get_framework(framework)
    if request.method == "POST":
        updated = normalize_form(request.form, canvas)
        canvas_id = save_canvas(db_path(), updated, canvas.get("id"))
        session["canvas_id"] = canvas_id
        return redirect(url_for("canvas.prototype"))
    return render_template("ideate/ideate.html", canvas=canvas, frameworks=all_frameworks(), framework=framework, prompts=prompts)


@bp.route("/ideate/heros")
def heros():
    return render_template("ideate/heros.html", prompts=get_framework("HERO"))


@bp.route("/ideate/jtbd")
def jtbd():
    return render_template("ideate/jtbd.html", prompts=get_framework("JTBD"))


@bp.route("/ideate/matrix")
def matrix():
    return render_template("ideate/matrix.html", prompts=get_framework("Assumption Matrix"))


@bp.route("/ideate/matrix-board")
def matrix_board():
    return render_template("ideate/matrix_board.html", prompts=get_framework("Assumption Matrix"))


@bp.route("/prototype", methods=["GET", "POST"])
def prototype():
    canvas = current_canvas()
    if request.method == "POST":
        updated = normalize_form(request.form, canvas)
        canvas_id = save_canvas(db_path(), updated, canvas.get("id"))
        session["canvas_id"] = canvas_id
        return redirect(url_for("canvas.test_plan"))
    return render_template("prototype/prototype.html", canvas=canvas)


@bp.route("/prototype/storyboard")
def storyboard():
    return render_template("prototype/storyboard.html", canvas=current_canvas())


@bp.route("/test", methods=["GET", "POST"])
def test_plan():
    canvas = current_canvas()
    if request.method == "POST":
        updated = normalize_form(request.form, canvas)
        canvas_id = save_canvas(db_path(), updated, canvas.get("id"))
        session["canvas_id"] = canvas_id
        return redirect(url_for("canvas.report"))
    return render_template("test/test.html", canvas=canvas)


@bp.route("/report")
def report():
    canvas = current_canvas()
    return render_template("export/report.html", canvas=canvas, markdown=to_markdown(canvas), pretty_json=to_pretty_json(canvas))


@bp.route("/api/canvas/<int:canvas_id>.json")
def canvas_json(canvas_id: int):
    canvas = get_canvas(db_path(), canvas_id)
    if not canvas:
        return jsonify({"error": "not found"}), 404
    return jsonify(canvas)


@bp.route("/export/<int:canvas_id>.md")
def canvas_markdown(canvas_id: int):
    canvas = get_canvas(db_path(), canvas_id)
    if not canvas:
        return Response("Not found\n", status=404, mimetype="text/plain")
    return Response(to_markdown(canvas), mimetype="text/markdown")
