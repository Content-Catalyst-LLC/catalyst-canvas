#### Video Demo: https://youtu.be/e-bEHoF6c6w
#### Author: Tariq Ahmad — GitHub: tariqcontent — edX: tariq_262
#### City/Country: Chicago, IL — Recorded: September 22, 2025
## Description
Catalyst Canvas is a **web-based design thinking workspace** that guides teams (or solo students!) through the complete process of **Empathize → Define → Ideate → Prototype → Test**. It’s designed to remove blank-page anxiety and structure creative work with **personas, empathy maps, POV/HMW statements, content frameworks (AIDA, Hero’s Journey, JTBD, Content Matrix), prototyping tools (concept cards + storyboard), testing feedback**, and **exportable reports**. It also includes an optional **GA4 CSV importer** that generates data‑informed draft personas from Google Analytics exports.
The project solves a common classroom and workplace problem: brainstorming and planning sessions often stall because they are unstructured. Catalyst Canvas gives users **scaffolding and repeatable templates** so they can quickly frame problems, generate ideas, and prototype solutions.
The app is implemented in **Python (Flask)** with **SQLite** persistence and **Bootstrap** for the UI. It’s intentionally simple to deploy and demo.
## Features
- **Personas**: create, view, and edit.
- **Empathy Maps**: “Says / Thinks / Does / Feels” per persona.
- **Define**: generate **Point‑of‑View** statements and **How Might We…** prompts via simple templating.
- **Ideate with Frameworks**:
 - **AIDA** (Attention, Interest, Desire, Action) — quick idea cards + voting.
 - **Hero’s Journey** — multi-field input generates multiple idea cards.
 - **JTBD** — Functional/Emotional/Social jobs + Forces (push/pull/anxieties/habits).
 - **Content Matrix (2×2)** — place ideas into **Evergreen/Educational/Entertaining** vs **Timely** quadrants with a visual board.
- **Prototype**: Concept Cards and a **6‑panel Storyboard** builder.
- **Test**: Feedback Capture Grid and a simple iteration tracker.
- **Export**: JSON bundle and a printable **HTML Report** that summarizes the whole session.
- **GA4 CSV Import (optional)**: upload a small GA4 export to auto‑create several data‑driven persona drafts.
- **Demo Assets**: `/demo/ga4_sample.csv` and `/demo/catalyst_seed.sqlite3` for a smooth 3‑minute demo.
## File Guide
- `app.py` — entry point; creates the Flask app.
- `app/models.py` — SQLite schema and DB helpers; includes a tiny “migration” for the Content Matrix column.
- `app/routes.py` — all routes for Empathize/Define/Ideate/Prototype/Test, GA4 CSV import, JSON/HTML export, and the **/intro** slate.
- `app/services/pov_hmw.py` — POV + HMW text generation helpers (rule‑based templates).
- `app/services/frameworks.py` — framework metadata and guided prompts.
- `templates/` — Jinja2 HTML templates (Bootstrap). Notable:
 - `templates/index.html` — dashboard with Personas and GA4 import link.
 - `templates/personas/view.html` — persona overview + quick links to each stage.
 - `templates/empathize/empathy_map.html` — empathy map form.
 - `templates/define/define.html` — POV/HMW generator form.
 - `templates/ideate/ideate.html` — framework selector, guided prompts, idea add + voting.
 - `templates/ideate/matrix_board.html` — visual 2×2 matrix view.
 - `templates/prototype/prototype.html` — concept cards.
 - `templates/prototype/storyboard.html` — 6‑panel storyboard.
 - `templates/test/test.html` — feedback capture.
 - `templates/export/report.html` — printable project report.
- `.github/workflows/ci.yml` — simple GitHub Actions check that ensures the app imports.
- `Makefile` — `make run` and `make db-reset`.
- `requirements.txt` — dependencies (Flask, pandas).
- `demo/` — GA4 sample CSV and a pre‑seeded SQLite DB plus a `demo_reset.sh` script.
## How to Run
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
# or
make run
```
Open `http://127.0.0.1:5000`.
**Demo DB (optional):**
```bash
cd demo
./demo_reset.sh # copies demo DB into project root as catalyst.sqlite3
cd ..
make run
```
Open the slate page and tweak via query string or edit the template:
```
http://127.0.0.1:5000/intro?title=Catalyst+Canvas&name=YOUR+NAME&github=YOURGH&edx=YOUREDX&city=YourCity&country=YourCountry&date=September 22, 2025
```
## Design Decisions
- **SQLite** for simplicity and portability; no external services required.
- **Framework‑first ideation** to scaffold content generation and keep ideas aligned with audience/goal.
- **HTML report** rather than PDF library to avoid OS‑specific setup; browsers can print to PDF.
- **CSV import** instead of the GA4 API to avoid OAuth complexity; keeps the demo simple but demonstrates data‑driven personas.
- **No JavaScript framework** beyond Bootstrap for speed; drag‑and‑drop and more advanced UI could be added later.
## Potential Improvements
- Real-time collaboration and presence.
- TF‑IDF clustering for de‑duping ideas.
- Live GA4 API integration with OAuth.
- Richer storyboard (media uploads).
- Multi-user auth and sharing.
1. Record your 3‑minute video and upload to YouTube as **unlisted**. Put the URL above.
2. Ensure this `README.md` is in your project’s root.
3. From your project directory, run:
 ```bash
 ```