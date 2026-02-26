# app/routes.py
import io, json
import pandas as pd
from flask import (
 Blueprint, render_template, request, redirect, url_for, send_file
)
from .models import get_conn, init_db, ensure_migrations
from .services.pov_hmw import generate_pov, generate_hmw_from_pov
from .services.frameworks import get_framework_labels, matrix_quadrants
# --- Blueprint: point to TOP-LEVEL templates/ and (optional) static/ ---
bp = Blueprint(
 "core",
 __name__,
 template_folder="../templates",
 static_folder="../static",
)
# --- Ensure DB schema/migrations exist before any request runs ---
@bp.before_app_request
def _ensure_schema:
 try:
 init_db
 ensure_migrations
 except Exception:
 pass
# =========================
# Persona helpers (optional for global mode)
# =========================
def _latest_persona_id:
 c = get_conn
 row = c.execute("SELECT id FROM personas ORDER BY created_at DESC LIMIT 1").fetchone
 return row["id"] if row else None
def _last_pid_from_cookie:
 try:
 v = request.cookies.get("last_pid")
 return int(v) if v and v.isdigit else None
 except Exception:
 return None
def _preferred_pid:
 # Order of preference: explicit ?pid=... → cookie → latest in DB
 return request.args.get("pid", type=int) or _last_pid_from_cookie or _latest_persona_id
@bp.after_app_request
def _remember_pid(resp):
 # Whenever a route has a path parameter named "pid", remember it for nav
 try:
 va = request.view_args or {}
 pid = va.get("pid")
 if pid:
 resp.set_cookie("last_pid", str(pid), max_age=60 * 60 * 24 * 30, samesite="Lax")
 except Exception:
 pass
 return resp
@bp.app_context_processor
def _inject_nav_pid:
 # Expose nav_pid to templates; may be None in global mode
 pid = request.args.get("pid", type=int) or _last_pid_from_cookie
 return {"nav_pid": pid}
# =========================
# Home / Personas
# =========================
@bp.route("/")
def index:
 c = get_conn
 personas = c.execute("SELECT * FROM personas ORDER BY created_at DESC").fetchall
 # Your zip's homepage lives at templates/index.html
 return render_template("index.html", personas=personas)
@bp.route("/personas", methods=["GET", "POST"])
def personas:
 c = get_conn
 if request.method == "POST":
 name = (request.form.get("name") or "").strip
 role = (request.form.get("role") or "").strip
 segment = (request.form.get("segment") or "").strip
 goals = (request.form.get("goals") or "").strip
 pains = (request.form.get("pains") or "").strip
 notes = (request.form.get("notes") or "").strip
 c.execute(
 "INSERT INTO personas (name, role, segment, goals, pains, notes) VALUES (?,?,?,?,?,?)",
 (name, role, segment, goals, pains, notes),
 )
 c.commit
 return redirect(url_for("core.index"))
 return render_template("personas/edit.html")
@bp.route("/personas/<int:pid>")
def view_persona(pid):
 c = get_conn
 p = c.execute("SELECT * FROM personas WHERE id=?", (pid,)).fetchone
 em = c.execute("SELECT * FROM empathy_maps WHERE persona_id=? ORDER BY created_at DESC", (pid,)).fetchone
 pd = c.execute("SELECT * FROM problem_defs WHERE persona_id=? ORDER BY created_at DESC", (pid,)).fetchone
 return render_template("personas/view.html", p=p, em=em, pd=pd)
# =========================
# Empathy Map (works with or without persona)
# =========================
@bp.route("/personas/<int:pid>/empathy", methods=["GET", "POST"])
@bp.route("/empathy", defaults={"pid": None}, methods=["GET", "POST"])
def empathy(pid):
 c = get_conn
 if request.method == "POST":
 says = request.form.get("says", "")
 thinks = request.form.get("thinks", "")
 does = request.form.get("does", "")
 feels = request.form.get("feels", "")
 c.execute(
 "INSERT INTO empathy_maps (persona_id, says, thinks, does, feels) VALUES (?,?,?,?,?)",
 (pid, says, thinks, does, feels),
 )
 c.commit
 return redirect(url_for("core.empathy", pid=pid) if pid is not None else url_for("core.empathy"))
 p = c.execute("SELECT * FROM personas WHERE id=?", (pid,)).fetchone if pid else None
 if pid is None:
 em = c.execute(
 "SELECT * FROM empathy_maps WHERE persona_id IS NULL ORDER BY created_at DESC"
 ).fetchone
 else:
 em = c.execute(
 "SELECT * FROM empathy_maps WHERE persona_id=? ORDER BY created_at DESC",
 (pid,)
 ).fetchone
 return render_template("empathize/empathy_map.html", p=p, em=em)
# =========================
# Define (POV/HMW) — persona optional
# =========================
@bp.route("/personas/<int:pid>/define", methods=["GET", "POST"])
@bp.route("/define", defaults={"pid": None}, methods=["GET", "POST"])
def define(pid):
 c = get_conn
 if request.method == "POST":
 user = request.form.get("user", "")
 need = request.form.get("need", "")
 insight = request.form.get("insight", "")
 pov = generate_pov(user, need, insight)
 hmws = generate_hmw_from_pov(pov)
 c.execute(
 "INSERT INTO problem_defs (persona_id, pov, hmw) VALUES (?,?,?)",
 (pid, pov, "\n".join(hmws)),
 )
 c.commit
 return redirect(url_for("core.define", pid=pid) if pid is not None else url_for("core.define"))
 p = c.execute("SELECT * FROM personas WHERE id=?", (pid,)).fetchone if pid else None
 if pid is None:
 pd = c.execute(
 "SELECT * FROM problem_defs WHERE persona_id IS NULL ORDER BY created_at DESC"
 ).fetchone
 else:
 pd = c.execute(
 "SELECT * FROM problem_defs WHERE persona_id=? ORDER BY created_at DESC",
 (pid,)
 ).fetchone
 return render_template("define/define.html", p=p, pd=pd)
# =========================
# Ideate (Content Frameworks) — persona optional
# =========================
@bp.route("/personas/<int:pid>/ideate", methods=["GET", "POST"])
@bp.route("/ideate", defaults={"pid": None}, methods=["GET", "POST"])
def ideate(pid):
 c = get_conn
 framework = request.args.get("framework", "AIDA")
 title, fields = get_framework_labels(framework)
 if request.method == "POST":
 matrix_q = (request.form.get("matrix_quadrant") or "").strip
 if title == "JTBD":
 fj = (request.form.get("fj") or "").strip
 ej = (request.form.get("ej") or "").strip
 sj = (request.form.get("sj") or "").strip
 push = (request.form.get("push") or "").strip
 pull = (request.form.get("pull") or "").strip
 anx = (request.form.get("anx") or "").strip
 habits = (request.form.get("habits") or "").strip
 payloads = [
 ("JTBD: Functional", fj),
 ("JTBD: Emotional", ej),
 ("JTBD: Social", sj),
 ("JTBD: Forces/Push", push),
 ("JTBD: Forces/Pull", pull),
 ("JTBD: Forces/Anxieties", anx),
 ("JTBD: Forces/Habits", habits),
 ]
 for label, text in payloads:
 if text:
 c.execute(
 "INSERT INTO ideas (persona_id, stage, framework, text, matrix_quadrant) VALUES (?,?,?,?,?)",
 (pid, "ideate", title, f"{label} — {text}", ""),
 )
 c.commit
 elif title in ("Hero’s Journey", "Hero's Journey"):
 call = (request.form.get("call") or "").strip
 trials = (request.form.get("trials") or "").strip
 trans = (request.form.get("trans") or "").strip
 ret = (request.form.get("return") or "").strip
 payloads = [
 ("Call to Adventure", call),
 ("Trials", trials),
 ("Transformation", trans),
 ("Return with Elixir",ret),
 ]
 for label, text in payloads:
 if text:
 c.execute(
 "INSERT INTO ideas (persona_id, stage, framework, text, matrix_quadrant) VALUES (?,?,?,?,?)",
 (pid, "ideate", title, f"{label} — {text}", ""),
 )
 c.commit
 else:
 text = (request.form.get("idea") or "").strip
 if text:
 c.execute(
 "INSERT INTO ideas (persona_id, stage, framework, text, matrix_quadrant) VALUES (?,?,?,?,?)",
 (pid, "ideate", title, text, matrix_q),
 )
 c.commit
 # Voting
 if "vote" in request.form:
 idea_id = request.form.get("vote")
 c.execute("UPDATE ideas SET votes = votes + 1 WHERE id=?", (idea_id,))
 c.commit
 p = c.execute("SELECT * FROM personas WHERE id=?", (pid,)).fetchone if pid else None
 if pid is None:
 ideas = c.execute(
 "SELECT * FROM ideas WHERE persona_id IS NULL ORDER BY votes DESC, created_at DESC"
 ).fetchall
 else:
 ideas = c.execute(
 "SELECT * FROM ideas WHERE persona_id=? ORDER BY votes DESC, created_at DESC",
 (pid,)
 ).fetchall
 return render_template(
 "ideate/ideate.html",
 p=p, ideas=ideas, framework=title, fields=fields, quadrants=matrix_quadrants
 )
# =========================
# Prototype — persona optional
# =========================
@bp.route("/personas/<int:pid>/prototype", methods=["GET", "POST"])
@bp.route("/prototype", defaults={"pid": None}, methods=["GET", "POST"])
def prototype(pid):
 c = get_conn
 if request.method == "POST":
 title = (request.form.get("title") or "").strip
 desc = (request.form.get("description") or "").strip
 if title:
 c.execute(
 "INSERT INTO prototypes (persona_id, title, description, type) VALUES (?,?,?,?)",
 (pid, title, desc, "concept_card"),
 )
 c.commit
 return redirect(url_for("core.prototype", pid=pid) if pid is not None else url_for("core.prototype"))
 p = c.execute("SELECT * FROM personas WHERE id=?", (pid,)).fetchone if pid else None
 if pid is None:
 protos = c.execute(
 "SELECT * FROM prototypes WHERE persona_id IS NULL ORDER BY created_at DESC"
 ).fetchall
 else:
 protos = c.execute(
 "SELECT * FROM prototypes WHERE persona_id=? ORDER BY created_at DESC",
 (pid,)
 ).fetchall
 return render_template("prototype/prototype.html", p=p, protos=protos)
# =========================
# Test — persona optional
# =========================
@bp.route("/personas/<int:pid>/test", methods=["GET", "POST"])
@bp.route("/test", defaults={"pid": None}, methods=["GET", "POST"])
def test_stage(pid):
 c = get_conn
 if request.method == "POST":
 proto_id = request.form.get("prototype_id")
 worked = request.form.get("worked", "")
 didnt = request.form.get("didnt", "")
 questions = request.form.get("questions", "")
 ideas = request.form.get("ideas", "")
 if proto_id:
 c.execute(
 "INSERT INTO feedback (prototype_id, worked, didnt, questions, ideas) VALUES (?,?,?,?,?)",
 (proto_id, worked, didnt, questions, ideas),
 )
 c.execute("INSERT INTO iterations (prototype_id, status) VALUES (?,?)", (proto_id, "test"))
 c.commit
 return redirect(url_for("core.test_stage", pid=pid) if pid is not None else url_for("core.test_stage"))
 p = c.execute("SELECT * FROM personas WHERE id=?", (pid,)).fetchone if pid else None
 if pid is None:
 protos = c.execute(
 "SELECT * FROM prototypes WHERE persona_id IS NULL ORDER BY created_at DESC"
 ).fetchall
 else:
 protos = c.execute(
 "SELECT * FROM prototypes WHERE persona_id=? ORDER BY created_at DESC",
 (pid,)
 ).fetchall
 return render_template("test/test.html", p=p, protos=protos)
# =========================
# Export (JSON) — persona-scoped unchanged
# =========================
@bp.route("/export/persona/<int:pid>.json")
def export_persona(pid):
 c = get_conn
 p = c.execute("SELECT * FROM personas WHERE id=?", (pid,)).fetchone
 em = c.execute("SELECT * FROM empathy_maps WHERE persona_id=? ORDER BY created_at DESC", (pid,)).fetchone
 pd = c.execute("SELECT * FROM problem_defs WHERE persona_id=? ORDER BY created_at DESC", (pid,)).fetchone
 ideas = c.execute("SELECT * FROM ideas WHERE persona_id=? ORDER BY created_at DESC", (pid,)).fetchall
 protos = c.execute("SELECT * FROM prototypes WHERE persona_id=? ORDER BY created_at DESC", (pid,)).fetchall
 out = {
 "persona": dict(p) if p else None,
 "empathy_map": dict(em) if em else None,
 "problem_def": dict(pd) if pd else None,
 "ideas": [dict(x) for x in ideas],
 "prototypes": [dict(x) for x in protos],
 }
 buf = io.BytesIO(json.dumps(out, indent=2).encode("utf-8"))
 return send_file(buf, mimetype="application/json", as_attachment=True, download_name=f"persona_{pid}.json")
# =========================
# Optional extra tools (from your zip) — still persona optional
# =========================
@bp.route("/personas/<int:pid>/jtbd", methods=["GET","POST"])
@bp.route("/jtbd", defaults={"pid": None}, methods=["GET","POST"])
def jtbd(pid):
 c = get_conn
 if request.method == "POST":
 functional = request.form.get("job_functional", "")
 emotional = request.form.get("job_emotional", "")
 social = request.form.get("job_social", "")
 c.execute(
 "INSERT INTO ideas (persona_id, stage, framework, text) VALUES (?,?,?,?)",
 (pid, "ideate", "JTBD",
 f"Functional: {functional}\nEmotional: {emotional}\nSocial: {social}")
 )
 c.commit
 return redirect(url_for("core.jtbd", pid=pid) if pid is not None else url_for("core.jtbd"))
 p = c.execute("SELECT * FROM personas WHERE id=?", (pid,)).fetchone if pid else None
 return render_template("ideate/jtbd.html", p=p)
@bp.route("/personas/<int:pid>/heros", methods=["GET","POST"])
@bp.route("/heros", defaults={"pid": None}, methods=["GET","POST"])
def heros(pid):
 c = get_conn
 if request.method == "POST":
 call = request.form.get("call", "")
 trials = request.form.get("trials", "")
 transform = request.form.get("transform", "")
 ret = request.form.get("return", "")
 text = f"Call: {call}\nTrials: {trials}\nTransformation: {transform}\nReturn: {ret}"
 c.execute(
 "INSERT INTO ideas (persona_id, stage, framework, text) VALUES (?,?,?,?)",
 (pid, "ideate", "HeroJourney", text)
 )
 c.commit
 return redirect(url_for("core.heros", pid=pid) if pid is not None else url_for("core.heros"))
 p = c.execute("SELECT * FROM personas WHERE id=?", (pid,)).fetchone if pid else None
 return render_template("ideate/heros.html", p=p)
@bp.route("/personas/<int:pid>/matrix", methods=["GET","POST"])
@bp.route("/matrix", defaults={"pid": None}, methods=["GET","POST"])
def matrix(pid):
 c = get_conn
 if request.method == "POST":
 eg_ed = request.form.get("eg_ed", "")
 timely_ed = request.form.get("timely_ed", "")
 eg_ent = request.form.get("eg_ent", "")
 timely_ent= request.form.get("timely_ent", "")
 text = f"EG-Edu: {eg_ed}\nTimely-Edu: {timely_ed}\nEG-Ent: {eg_ent}\nTimely-Ent: {timely_ent}"
 c.execute(
 "INSERT INTO ideas (persona_id, stage, framework, text) VALUES (?,?,?,?)",
 (pid, "ideate", "ContentMatrix", text)
 )
 c.commit
 return redirect(url_for("core.matrix", pid=pid) if pid is not None else url_for("core.matrix"))
 p = c.execute("SELECT * FROM personas WHERE id=?", (pid,)).fetchone if pid else None
 return render_template("ideate/matrix.html", p=p)
@bp.route("/personas/import/ga4", methods=["GET","POST"])
def import_ga4:
 if request.method == "POST":
 file = request.files.get("csv")
 if not file or file.filename == "":
 return render_template("personas/ga4_import.html", error="Please choose a CSV file.")
 try:
 df = pd.read_csv(file)
 except Exception as e:
 return render_template("personas/ga4_import.html", error=f"Could not read CSV: {e}")
 # Normalize columns
 for col in ["deviceCategory","sessionDefaultChannelGroup","country","sessions","engagedSessions","averageSessionDuration","conversions"]:
 if col not in df.columns:
 df[col] = None
 grouped = df.groupby(
 ["deviceCategory","sessionDefaultChannelGroup","country"], dropna=False
 ).agg({
 "sessions":"sum","engagedSessions":"sum","averageSessionDuration":"mean","conversions":"sum"
 }).reset_index.sort_values("sessions", ascending=False)
 c = get_conn
 created =
 for _, row in grouped.head(5).iterrows:
 name = f"{(row['deviceCategory'] or 'Unknown').title} {(row['sessionDefaultChannelGroup'] or 'Visitor').title}"[:50]
 role = "Auto Persona (GA4 CSV)"
 segment = f"{row['deviceCategory'] or ''} / {row['sessionDefaultChannelGroup'] or ''} / {row['country'] or ''}"
 goals = "Research solutions; Compare options"
 pains = "Overwhelmed by choices; Needs clarity"
 notes = f"sessions={int(row['sessions'] or 0)}, engaged={int(row['engagedSessions'] or 0)}, avgDur={(float(row['averageSessionDuration'] or 0)):.1f}, conversions={int(row['conversions'] or 0)}"
 c.execute(
 "INSERT INTO personas (name, role, segment, goals, pains, notes) VALUES (?,?,?,?,?,?)",
 (name, role, segment, goals, pains, notes)
 )
 created.append(name)
 c.commit
 return render_template("personas/ga4_import.html", created=created)
 return render_template("personas/ga4_import.html")
# =========================
# HTML Report — works for persona or global
# =========================
@bp.route("/export/report/<int:pid>.html")
@bp.route("/export/report.html", defaults={"pid": None})
def export_report(pid):
 c = get_conn
 p = c.execute("SELECT * FROM personas WHERE id=?", (pid,)).fetchone if pid else None
 if pid is None:
 em = c.execute("SELECT * FROM empathy_maps WHERE persona_id IS NULL ORDER BY created_at DESC").fetchone
 pd = c.execute("SELECT * FROM problem_defs WHERE persona_id IS NULL ORDER BY created_at DESC").fetchone
 ideas = c.execute("SELECT * FROM ideas WHERE persona_id IS NULL ORDER BY votes DESC, created_at DESC").fetchall
 protos = c.execute("SELECT * FROM prototypes WHERE persona_id IS NULL ORDER BY created_at DESC").fetchall
 feedback = c.execute(
 """SELECT f.*, p.title AS proto_title
 FROM feedback f
 LEFT JOIN prototypes p ON p.id = f.prototype_id
 WHERE p.persona_id IS NULL
 ORDER BY f.created_at DESC"""
 ).fetchall
 else:
 em = c.execute("SELECT * FROM empathy_maps WHERE persona_id=? ORDER BY created_at DESC", (pid,)).fetchone
 pd = c.execute("SELECT * FROM problem_defs WHERE persona_id=? ORDER BY created_at DESC", (pid,)).fetchone
 ideas = c.execute("SELECT * FROM ideas WHERE persona_id=? ORDER BY votes DESC, created_at DESC", (pid,)).fetchall
 protos = c.execute("SELECT * FROM prototypes WHERE persona_id=? ORDER BY created_at DESC", (pid,)).fetchall
 feedback = c.execute(
 """SELECT f.*, p.title AS proto_title
 FROM feedback f
 LEFT JOIN prototypes p ON p.id = f.prototype_id
 WHERE p.persona_id=?
 ORDER BY f.created_at DESC""",
 (pid,)
 ).fetchall
 return render_template(
 "export/report.html",
 p=p,
 em=em,
 pd=pd,
 ideas=ideas,
 protos=protos,
 feedback=feedback,
 )
# =========================
# Root redirectors (compat) — prefer pid if present, else global
# =========================
@bp.route("/empathize")
def empathize_root:
 pid = _preferred_pid
 return redirect(url_for("core.empathy", pid=pid)) if pid else redirect(url_for("core.empathy"))
@bp.route("/define_root")
def define_root:
 pid = _preferred_pid
 return redirect(url_for("core.define", pid=pid)) if pid else redirect(url_for("core.define"))
@bp.route("/ideate_root")
def ideate_root:
 pid = _preferred_pid
 return redirect(url_for("core.ideate", pid=pid)) if pid else redirect(url_for("core.ideate"))
@bp.route("/prototype_root")
def prototype_root:
 pid = _preferred_pid
 return redirect(url_for("core.prototype", pid=pid)) if pid else redirect(url_for("core.prototype"))
@bp.route("/test_root")
def test_root:
 pid = _preferred_pid
 return redirect(url_for("core.test_stage", pid=pid)) if pid else redirect(url_for("core.test_stage"))