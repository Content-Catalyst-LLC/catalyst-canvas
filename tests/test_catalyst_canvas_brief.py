import unittest

from python.catalyst_canvas_brief import CanvasInput, build_canvas_brief, export_payload
from python.catalyst_canvas_version import __version__


class CatalystCanvasBriefCompatibilityTests(unittest.TestCase):
    def test_brief_contains_reviewable_fields(self):
        brief = build_canvas_brief(CanvasInput(
            challenge="Teams overstate impact claims",
            audience="Sustainability lead",
            goal="build traceable reporting",
            constraint="thin data",
            framework="JTBD",
        ))
        self.assertIn("Sustainability lead", brief.title)
        self.assertEqual(len(brief.hmw), 4)
        self.assertEqual(len(brief.ideas), 4)
        self.assertIn("review", brief.boundary.lower())

    def test_export_payload_uses_canonical_version(self):
        payload = export_payload(CanvasInput(
            challenge="A messy planning process",
            audience="Founder",
            goal="prioritize experiments",
            constraint="limited time",
            framework="AIDA",
        ))
        self.assertEqual(payload["tool"], "Catalyst Canvas Demo")
        self.assertEqual(payload["version"], __version__)
        self.assertIn("inputs", payload)
        self.assertIn("canvas", payload)


if __name__ == "__main__":
    unittest.main()
