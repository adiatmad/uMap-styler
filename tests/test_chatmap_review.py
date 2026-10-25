"""Regression tests for the pure ChatMap review-ledger helpers in app.py.

The app has Streamlit UI side effects at module import time, so load only the
pure helper-function AST nodes for deterministic unit tests.
"""
import ast
import copy
import hashlib
import json
import unittest
from pathlib import Path

APP_PATH = Path(__file__).resolve().parents[1] / "app.py"
HELPERS = {
    "_canonical_json", "_fingerprint", "_source_properties", "_geometry_key",
    "_source_snapshot", "_review_id", "import_chatmap_geojson",
    "promote_incoming_source", "reviewed_geojson", "working_ledger_geojson",
    "load_working_ledger",
}
NAMESPACE = {
    "json": json, "hashlib": hashlib, "copy": copy,
    "REVIEW_STATUSES": ("New", "Needs correction", "Verified", "Rejected"),
    "_REVIEW_KEYS": {"_review_id", "_review_status", "_review_notes",
                     "_source_fingerprint", "_source_snapshot", "_reviewed_properties"},
}
tree = ast.parse(APP_PATH.read_text(encoding="utf-8"))
nodes = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in HELPERS]
exec(compile(ast.Module(body=nodes, type_ignores=[]), str(APP_PATH), "exec"), NAMESPACE)

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
        ledger, counts = self.importer(collection(feature("after", fid="r1")), ledger)
        self.assertEqual(counts["changed"], 1)
        self.assertTrue(ledger["r1"]["conflict"])
        self.assertEqual(ledger["r1"]["status"], "Needs correction")
        accepted = NAMESPACE["promote_incoming_source"](ledger, "r1")
        self.assertTrue(accepted)
        self.assertFalse(ledger["r1"]["conflict"])
        self.assertEqual(ledger["r1"]["status"], "Needs correction")

if __name__ == "__main__":
    unittest.main()
