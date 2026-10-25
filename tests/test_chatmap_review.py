"""Regression tests for the pure ChatMap review-ledger helpers in app.py.

The app has Streamlit UI side effects at module import time, so load only the
pure helper-function AST nodes for deterministic unit tests.
"""
import ast
import copy
import hashlib
import html
import json
import unittest
from pathlib import Path

APP_PATH = Path(__file__).resolve().parents[1] / "app.py"
HELPERS = {
    "_canonical_json", "_fingerprint", "_source_properties",
    "_source_snapshot", "_review_id", "import_chatmap_geojson",
    "promote_incoming_source", "reviewed_geojson", "working_ledger_geojson",
    "load_working_ledger", "normalize_review_text", "inspect_text_quality",
    "find_text_inconsistencies", "apply_approved_text_replacements", "apply_approved_whitespace_cleanup",
}
NAMESPACE = {
    "json": json, "hashlib": hashlib, "copy": copy,
    "REVIEW_STATUSES": ("New", "Needs correction", "Verified", "Rejected"),
    "html_lib": html,
    "difflib": __import__("difflib"),
    "_REVIEW_KEYS": {"_review_id", "_review_status", "_review_notes",
                     "_source_fingerprint", "_source_snapshot", "_reviewed_properties"},
}
tree = ast.parse(APP_PATH.read_text(encoding="utf-8"))
nodes = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in HELPERS]
exec(compile(ast.Module(body=nodes, type_ignores=[]), str(APP_PATH), "exec"), NAMESPACE)


def load_html_renderer():
    tree = ast.parse(APP_PATH.read_text(encoding="utf-8"))
    function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "create_universal_html")
    namespace = {"html_lib": html}
    exec(compile(ast.Module(body=[function], type_ignores=[]), str(APP_PATH), "exec"), namespace)
    return namespace["create_universal_html"]

def feature(text="sampah menumpuk", coordinates=None, props=None, fid=None):
    properties = {"description": text, **(props or {})}
    item = {"type": "Feature", "geometry": {
        "type": "Point", "coordinates": coordinates or [109.0, -6.8]
    }, "properties": properties}
    if fid is not None:
        item["id"] = fid
    return item

def collection(*features):
    return {"type": "FeatureCollection", "features": list(features)}

class ChatMapReviewTests(unittest.TestCase):
    def setUp(self):
        self.importer = NAMESPACE["import_chatmap_geojson"]
        self.publish = NAMESPACE["reviewed_geojson"]


    def test_html_renderer_escapes_untrusted_names_and_values(self):
        rendered = load_html_renderer()({"<script>alert(1)</script>": "<img src=x onerror=alert(1)>"})
        self.assertNotIn("<script>", rendered)
        self.assertNotIn("<img src=x", rendered)
        self.assertIn("&lt;script&gt;", rendered)
        self.assertIn("&lt;img", rendered)

    def test_valid_import_and_repeat_is_idempotent(self):
        ledger, counts = self.importer(collection(feature()))
        self.assertEqual(counts["new"], 1)
        ledger2, counts2 = self.importer(collection(feature()), ledger)
        self.assertEqual(counts2["new"], 0)
        self.assertEqual(counts2["unchanged"], 1)
        self.assertEqual(len(ledger2), 1)

    def test_changed_report_same_unambiguous_geometry_becomes_conflict(self):
        old, _ = self.importer(collection(feature("sampah menumpuk", fid="report-1")))
        old["report-1"]["status"] = "Verified"
        changed, counts = self.importer(collection(feature("sampah sudah dibersihkan", fid="report-1")), old)
        self.assertEqual(counts["changed"], 1)
        self.assertTrue(changed["report-1"]["conflict"])
        self.assertEqual(changed["report-1"]["status"], "Needs correction")
        self.assertEqual(len(self.publish(changed)["features"]), 0)

    def test_missing_id_changed_properties_same_geometry_is_not_duplicate(self):
        old, _ = self.importer(collection(feature("awal")))
        changed, counts = self.importer(collection(feature("berubah")), old)
        self.assertEqual(len(changed), 1)
        self.assertEqual(counts["changed"], 1)
        self.assertTrue(next(iter(changed.values()))["conflict"])

    def test_only_verified_conflict_free_records_publish(self):
        ledger, _ = self.importer(collection(
            feature("a", fid="a"), feature("b", fid="b"), feature("c", fid="c")
        ))
        ledger["a"]["status"] = "Verified"
        ledger["b"]["status"] = "Rejected"
        ledger["c"]["status"] = "Verified"
        ledger["c"]["conflict"] = True
        result = self.publish(ledger)
        self.assertEqual([item["id"] for item in result["features"]], ["a"])

    def test_malformed_featurecollection_rejected(self):
        with self.assertRaises(ValueError):
            self.importer({"type": "Feature", "geometry": None})

    def test_invalid_feature_skipped_not_published(self):
        ledger, counts = self.importer(collection({"type": "NotFeature"}))
        self.assertEqual(counts["invalid"], 1)
        self.assertEqual(ledger, {})

    def test_malformed_geometry_is_skipped(self):
        bad = {"type": "Feature", "geometry": {"type": "NotAGeometry", "coordinates": []}, "properties": {}}
        ledger, counts = self.importer(collection(bad))
        self.assertEqual(counts["invalid"], 1)
        self.assertEqual(ledger, {})

    def test_ledger_roundtrip_and_invalid_status_rejected(self):
        ledger, _ = self.importer(collection(feature()))
        packed = NAMESPACE["working_ledger_geojson"](ledger)
        restored = NAMESPACE["load_working_ledger"](packed)
        self.assertEqual(restored, ledger)
        packed["records"][next(iter(ledger))]["status"] = "auto-approved"
        with self.assertRaises(ValueError):
            NAMESPACE["load_working_ledger"](packed)

    def test_accept_incoming_requires_conflict_and_demotes_to_review(self):
        ledger, _ = self.importer(collection(feature("before", fid="r1")))
        ledger["r1"]["status"] = "Verified"
        ledger, counts = self.importer(collection(feature("after", fid="r1")), ledger)
        self.assertEqual(counts["changed"], 1)
        self.assertTrue(ledger["r1"]["conflict"])
        self.assertEqual(ledger["r1"]["status"], "Needs correction")
        accepted = NAMESPACE["promote_incoming_source"](ledger, "r1")
        self.assertTrue(accepted)
        self.assertFalse(ledger["r1"]["conflict"])
        self.assertEqual(ledger["r1"]["status"], "Needs correction")


class TextQualityReviewTests(unittest.TestCase):
    def setUp(self):
        self.normalize = NAMESPACE["normalize_review_text"]
        self.inspect = NAMESPACE["inspect_text_quality"]
        self.cluster = NAMESPACE["find_text_inconsistencies"]
        self.apply = NAMESPACE["apply_approved_text_replacements"]

    def test_whitespace_normalization_is_conservative(self):
        self.assertEqual(self.normalize("  sampah   plastik\\n"), "sampah plastik")
        self.assertEqual(self.normalize("Kaliwlingi"), "Kaliwlingi")
        self.assertEqual(self.normalize("e-mail / WhatsApp!"), "e-mail / WhatsApp!")

    def test_quality_scan_suggests_but_does_not_mutate_properties(self):
        props = {"description": "  sampah   plastik  ", "location": "Kaliwlingi"}
        original = copy.deepcopy(props)
        issues = self.inspect(props)
        self.assertEqual(props, original)
        self.assertTrue(any(i["field"] == "description" and i["suggestion"] == "sampah plastik" for i in issues))
        self.assertFalse(any(i["field"] == "location" for i in issues))

    def test_inconsistency_clusters_find_formatting_and_likely_typo(self):
        records = {
            "1": {"reviewed_properties": {"waste_type": "Sampah Plastik"}, "status": "New"},
            "2": {"reviewed_properties": {"waste_type": "sampah plastik"}, "status": "Verified"},
            "3": {"reviewed_properties": {"waste_type": "sampah plstik"}, "status": "New"},
            "4": {"reviewed_properties": {"waste_type": "Sampah Plastik"}, "status": "New"},
        }
        findings = self.cluster(records, threshold=0.82)
        self.assertTrue(any(set(f["values"]) == {"Sampah Plastik", "sampah plastik"} and f["kind"] == "formatting" for f in findings))
        self.assertTrue(any(set(f["values"]) == {"sampah plastik", "sampah plstik"} and f["kind"] == "possible_typo" for f in findings))
        self.assertTrue(all("similarity" in f and "canonical" in f for f in findings))

    def test_bulk_replacement_requires_explicit_mapping_and_demotes_verified(self):
        records = {
            "1": {"source": {"properties": {"category": "sampah plstik"}}, "reviewed_properties": {"category": "sampah plstik"}, "status": "Verified", "conflict": False},
            "2": {"source": {"properties": {"category": "sampah plstik"}}, "reviewed_properties": {"category": "sampah plstik"}, "status": "New", "conflict": False},
            "3": {"source": {"properties": {"category": "sampah plstik"}}, "reviewed_properties": {"category": "sampah plstik"}, "status": "Verified", "conflict": True},
            "4": {"source": {"properties": {"category": "sampah plstik"}}, "reviewed_properties": {"category": "sampah plstik"}, "status": "Rejected", "conflict": False},
        }
        changed = self.apply(records, "category", {"sampah plstik": "sampah plastik"})
        self.assertEqual(changed, 2)
        self.assertEqual(records["1"]["reviewed_properties"]["category"], "sampah plastik")
        self.assertEqual(records["1"]["status"], "Needs correction")
        self.assertEqual(records["2"]["status"], "Needs correction")
        self.assertEqual(records["3"]["reviewed_properties"]["category"], "sampah plstik")
        self.assertEqual(records["4"]["status"], "Rejected")
        self.assertEqual(records["1"]["source"]["properties"]["category"], "sampah plstik")


    def test_approved_whitespace_cleanup_is_explicit_and_review_gated(self):
        records = {
            "1": {"source": {"properties": {"description": "  Sampah   plastik "}}, "reviewed_properties": {"description": "  Sampah   plastik "}, "status": "Verified", "conflict": False},
            "2": {"source": {"properties": {"description": "  Sampah   plastik "}}, "reviewed_properties": {"description": "  Sampah   plastik "}, "status": "New", "conflict": False},
            "3": {"source": {"properties": {"description": "  Sampah   plastik "}}, "reviewed_properties": {"description": "  Sampah   plastik "}, "status": "Verified", "conflict": True},
            "4": {"source": {"properties": {"description": "  Sampah   plastik "}}, "reviewed_properties": {"description": "  Sampah   plastik "}, "status": "Rejected", "conflict": False},
        }
        changed = NAMESPACE["apply_approved_whitespace_cleanup"](records)
        self.assertEqual(changed, 2)
        self.assertEqual(records["1"]["reviewed_properties"]["description"], "Sampah plastik")
        self.assertEqual(records["1"]["status"], "Needs correction")
        self.assertEqual(records["3"]["reviewed_properties"]["description"], "  Sampah   plastik ")
        self.assertEqual(records["4"]["reviewed_properties"]["description"], "  Sampah   plastik ")
        self.assertEqual(records["1"]["source"]["properties"]["description"], "  Sampah   plastik ")

    def test_bulk_replacement_rejects_invalid_inputs(self):
        records = {"1": {"reviewed_properties": {"category": "old"}, "status": "New", "conflict": False}}
        with self.assertRaises(ValueError):
            self.apply(records, "", {"old": "new"})
        with self.assertRaises(ValueError):
            self.apply(records, "category", {"old": ""})

if __name__ == "__main__":
    unittest.main()
