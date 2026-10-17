from datetime import datetime, timezone
import unittest
from cosmora.pilot import event_window, sample_times, compare_positions


class TransitPilotTests(unittest.TestCase):
    def test_date_only_uses_uncertainty_window_not_invented_noon(self):
        start, end = event_window({"date_start":"1955-03-30","date_precision":"day"})
        self.assertEqual(start.isoformat(),"1955-03-29T10:00:00+00:00")
        self.assertEqual(end.isoformat(),"1955-03-31T14:00:00+00:00")
        values = sample_times(start,end)
        self.assertEqual(values[0],start)
        self.assertEqual(values[-1],end)
        self.assertGreater(len(values),1)

    def test_year_only_event_stays_queued(self):
        self.assertIsNone(event_window({"date_start":"1954","date_precision":"year"}))

    def test_major_aspect_wraps_around_zero(self):
        natal={"SUN":{"longitude":359.0,"house":8}}
        transits={"SATURN":{"longitude":1.0,"house":4}}
        rows=compare_positions(natal,transits)
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]["aspect"],"conjunction")
        self.assertAlmostEqual(rows[0]["orb_deg"],2.0)
        self.assertEqual(rows[0]["natal_house"],8)

    def test_no_aspect_outside_predeclared_orb(self):
        rows=compare_positions({"SUN":{"longitude":0.0,"house":1}},
                               {"SATURN":{"longitude":10.0,"house":1}})
        self.assertEqual(rows,[])

    def test_date_range_preserves_full_interval(self):
        start,end=event_window({"date_start":"1938-11-01","date_end":"1938-11-15","date_precision":"day_range"})
        self.assertEqual((end-start).total_seconds()/3600,388.0)




class PolicyIntegrityTests(unittest.TestCase):
    def test_changed_comparison_policy_is_rejected(self):
        import tempfile
        from pathlib import Path
        from cosmora.pilot import initialize_pilot, guard_policy
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/"pilot.db"
            initialize_pilot(path)
            policy={"angles":{"conjunction":0},"orb_degrees":3,"sample_hours":6,"envelope_hours":14}
            guard_policy(path,policy)
            guard_policy(path,policy)
            with self.assertRaises(ValueError):
                guard_policy(path,dict(policy,orb_degrees=5))

if __name__=="__main__":
    unittest.main()
