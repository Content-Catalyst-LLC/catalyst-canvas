import unittest

from python.catalyst_canvas_core import generate_brief
from python.catalyst_canvas_version import CONTRACT_VERSION, __version__


class CatalystCanvasCoreCompatibilityTests(unittest.TestCase):
    def test_generate_brief_contains_core_fields_and_contract(self):
        brief = generate_brief({
            "challenge": "Improve impact reporting",
            "audience": "Program director",
            "goal": "Create a reviewable brief",
            "constraint": "Limited data",
            "framework": "JTBD",
        })
        self.assertEqual(brief.version, __version__)
        self.assertEqual(brief.challenge, "Improve impact reporting")
        self.assertEqual(brief.framework, "JTBD")
        self.assertEqual(brief.contract["schema_version"], CONTRACT_VERSION)
        self.assertGreaterEqual(len(brief.how_might_we), 3)

    def test_unknown_framework_falls_back_to_aida(self):
        brief = generate_brief({"framework": "Unknown"})
        self.assertEqual(brief.framework, "AIDA")

    def test_markdown_export_has_contract_metadata(self):
        brief = generate_brief({"challenge": "Test challenge"})
        markdown = brief.to_markdown()
        self.assertIn("# Catalyst Canvas Brief", markdown)
        self.assertIn("Contract: catalyst-canvas/1.1", markdown)
        self.assertIn("## Challenge", markdown)
        self.assertIn("## Review Notes", markdown)


if __name__ == "__main__":
    unittest.main()
