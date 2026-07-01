import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from catalyst_canvas_core import generate_brief


def test_generate_brief_contains_core_fields():
    brief = generate_brief({
        "challenge": "Improve impact reporting",
        "audience": "Program director",
        "goal": "Create a reviewable brief",
        "constraint": "Limited data",
        "framework": "JTBD",
    })
    assert brief.challenge == "Improve impact reporting"
    assert brief.framework == "JTBD"
    assert "Program director" in brief.persona["name"]
    assert len(brief.how_might_we) >= 3
    assert len(brief.assumptions) >= 3


def test_unknown_framework_falls_back_to_aida():
    brief = generate_brief({"framework": "Unknown"})
    assert brief.framework == "AIDA"


def test_markdown_export_has_key_sections():
    brief = generate_brief({"challenge": "Test challenge"})
    md = brief.to_markdown()
    assert "# Catalyst Canvas Brief" in md
    assert "## Challenge" in md
    assert "## Review Questions" in md
