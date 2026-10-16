from contextlib import closing
import sqlite3
import tempfile
import unittest
from pathlib import Path

from cosmora.charts import placement, save_chart, render_svg
from cosmora.knowledge import initialize_graph, import_candidates, import_events, export_graph


class PlacementTests(unittest.TestCase):
    def test_whole_sign_and_decan_boundaries(self):
        self.assertEqual(placement(32.5, 9)["house"], 5)
        self.assertEqual(placement(9.999999, 9)["decan"], 1)
        self.assertEqual(placement(10.0, 9)["decan"], 2)
        self.assertEqual(placement(20.0, 9)["decan"], 3)
        self.assertEqual(placement(360.0, 9)["sign"], "Aries")
        self.assertEqual(placement(306.38, 9)["modern_sign_ruler"], "Uranus")

    def test_unknown_ascendant_does_not_assign_houses(self):
        self.assertIsNone(placement(32.0, None)["house"])

    def test_svg_escapes_labels(self):
        chart = {"chart_id": "test", "input": {"person_id": "<script>"},
                 "placements": {"SUN": placement(32.0, 9)}}
        svg = render_svg(chart)
        self.assertNotIn("<script>", svg)
        self.assertIn("&lt;script&gt;", svg)


class StorageTests(unittest.TestCase):
    def test_personal_chart_is_idempotent_and_not_training_eligible(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "personal.db"
            chart = {"chart_id": "abc", "input": {"person_id": "personal-test"},
                     "profile": {}, "engine": {}, "placements": {"SUN": placement(32.0, 9)}}
            save_chart(path, chart)
            save_chart(path, chart)
            with closing(sqlite3.connect(path)) as db:
                self.assertEqual(db.execute("SELECT COUNT(*) FROM chart_runs").fetchone()[0], 1)
                self.assertEqual(db.execute("SELECT COUNT(*) FROM chart_placements").fetchone()[0], 1)
                self.assertEqual(db.execute("SELECT training_eligible FROM chart_runs").fetchone()[0], 0)

    def test_candidates_and_events_stay_pending_and_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "research.db"
            people = [{"candidate_id": "person-1", "name": "Example", "field": "Science",
                       "region": "Example", "biography_url": "https://example.org/bio",
                       "status": "verified", "training_eligible": True}]
            events = [{"event_id": "event-1", "person": "Example", "event_type": "award",
                       "date_start": "1990", "date_end": None, "date_precision": "year",
                       "source_url": "https://example.org/award"}]
            for _ in range(2):
                import_candidates(path, people)
                import_events(path, events)
            with closing(sqlite3.connect(path)) as db:
                self.assertEqual(db.execute("SELECT COUNT(*) FROM research_subjects").fetchone()[0], 1)
                self.assertEqual(db.execute("SELECT status FROM research_subjects").fetchone()[0], "pending")
                self.assertEqual(db.execute("SELECT COUNT(*) FROM research_event_leads").fetchone()[0], 1)
                self.assertEqual(db.execute("SELECT COUNT(*) FROM chart_runs").fetchone()[0], 0)
            graph = export_graph(path)
            self.assertTrue(any(e["relation"] == "HAS_EVENT_LEAD" for e in graph["edges"]))
            self.assertFalse(any(n["kind"] == "doctrine" for n in graph["nodes"]))

    def test_unmatched_event_rolls_back(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "research.db"
            initialize_graph(path)
            with self.assertRaises(ValueError):
                import_events(path, [{"event_id": "bad", "person": "Unknown"}])
            with closing(sqlite3.connect(path)) as db:
                self.assertEqual(db.execute("SELECT COUNT(*) FROM research_event_leads").fetchone()[0], 0)


class EphemerisTests(unittest.TestCase):
    def test_missing_data_fails_instead_of_falling_back(self):
        from cosmora.charts import calculate_chart
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileNotFoundError):
                calculate_chart({"person_id": "test", "utc": "2000-01-01T12:00:00Z",
                                 "latitude": 0.0, "longitude": 0.0}, directory)

    def test_naive_timestamp_is_rejected(self):
        from cosmora.charts import calculate_chart
        with self.assertRaises(ValueError):
            calculate_chart({"person_id": "test", "utc": "2000-01-01T12:00:00",
                             "latitude": 0.0, "longitude": 0.0}, ".")




class IntegrityRegressionTests(unittest.TestCase):
    def test_duplicate_names_with_different_ids_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "research.db"
            common = {"name": "Same Person", "biography_url": "https://example.org/bio"}
            import_candidates(path, [dict(common, candidate_id="original")])
            with self.assertRaises(ValueError):
                import_candidates(path, [dict(common, candidate_id="different-id")])
            with closing(sqlite3.connect(path)) as db:
                self.assertEqual(db.execute("SELECT COUNT(*) FROM research_subjects").fetchone()[0], 1)
                self.assertEqual(db.execute("SELECT COUNT(*) FROM graph_nodes WHERE kind='subject'").fetchone()[0], 1)

    def test_calculator_does_not_claim_user_confirmation(self):
        from types import SimpleNamespace
        from unittest.mock import patch
        from cosmora.charts import BODIES, calculate_chart
        fake = SimpleNamespace(
            version="test-only", __version__="test-only",
            set_ephe_path=lambda path: None, julday=lambda *args: 2451545.0,
            houses=lambda *args: (tuple(float(i * 30) for i in range(12)), (0.0, 270.0)),
            calc_ut=lambda *args: ((10.0, 0.0, 1.0, 0.1, 0.0, 0.0), 258),
            FLG_SWIEPH=2, FLG_SPEED=256, FLG_MOSEPH=4,
            **dict.fromkeys(BODIES, 0),
        )
        with tempfile.TemporaryDirectory() as directory:
            for name in ("sepl_18.se1", "semo_18.se1", "seas_18.se1"):
                (Path(directory) / name).write_bytes(b"test-only-data")
            with patch.dict("sys.modules", {"swisseph": fake}):
                chart = calculate_chart(
                    {"person_id": "unconfirmed-synthetic-input", "utc": "2000-01-01T12:00:00Z",
                     "latitude": 0, "longitude": 0}, directory)
        self.assertEqual(chart["validation_status"], "calculated_unverified")

if __name__ == "__main__":
    unittest.main()
