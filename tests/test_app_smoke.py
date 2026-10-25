"""Runtime smoke tests for the Streamlit app and workspace navigation."""
import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest

APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


class StreamlitAppSmokeTests(unittest.TestCase):
    def test_app_starts_in_chatmap_workspace_and_legacy_workspace_renders(self):
        app = AppTest.from_file(str(APP_PATH), default_timeout=30).run()
        self.assertEqual(len(app.exception), 0, "\n".join(str(item.value) for item in app.exception))
        self.assertTrue(any("uMap Styler" in item.value for item in app.title))
        self.assertEqual(app.sidebar.radio[0].value, "ChatMap review")

        app.sidebar.radio[0].set_value("GeoJSON / CSV / HTML tools").run()
        self.assertEqual(len(app.exception), 0, "\n".join(str(item.value) for item in app.exception))


if __name__ == "__main__":
    unittest.main()
