"""Runtime smoke tests for the Streamlit app and workspace navigation."""
import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest

APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


class StreamlitAppSmokeTests(unittest.TestCase):
    def test_app_starts_on_beginner_guide_and_all_workspaces_render(self):
        app = AppTest.from_file(str(APP_PATH), default_timeout=30).run()
        self.assertEqual(len(app.exception), 0, "\\n".join(str(item.value) for item in app.exception))
        self.assertTrue(any("uMap Styler" in item.value for item in app.title))
        self.assertEqual(app.sidebar.radio[0].value, "Beginner guide")
        self.assertTrue(any("Start here" in item.value for item in app.header))

        for workspace in [
            "Review ChatMap reports",
            "Prepare map for uMap",
            "Advanced tools",
        ]:
            app.sidebar.radio[0].set_value(workspace).run()
            self.assertEqual(
                len(app.exception), 0,
                f"{workspace}: " + "\\n".join(str(item.value) for item in app.exception),
            )

        app.sidebar.radio[0].set_value("Advanced tools").run()
        self.assertTrue(any("Combine Multiple GeoJSON Files" in item.value for item in app.header))


if __name__ == "__main__":
    unittest.main()
