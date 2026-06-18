"""
Run with: python -m unittest discover -s tests -v
"""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from dedup_store import DedupStore
from rules_engine import RulesEngine


class TestRulesEngine(unittest.TestCase):
    def setUp(self):
        self.engine = RulesEngine()

    def test_large_amount_triggers_alert(self):
        event = {"event_id": "e1", "customer_id": "C1", "amount": 9000, "currency": "ZAR", "ts": "2026-06-01T08:00:00"}
        alerts = self.engine.evaluate(event)
        self.assertTrue(any(a["rule"] == "LARGE_AMOUNT" for a in alerts))

    def test_small_amount_no_alert(self):
        event = {"event_id": "e1", "customer_id": "C1", "amount": 50, "currency": "ZAR", "ts": "2026-06-01T08:00:00"}
        alerts = self.engine.evaluate(event)
        self.assertEqual(alerts, [])

    def test_velocity_rule_triggers_on_burst(self):
        base_ts = "2026-06-01T08:00:0{}"
        customer = "C2"
        for i in range(2):
            self.engine.evaluate({
                "event_id": f"e{i}", "customer_id": customer, "amount": 50,
                "currency": "ZAR", "ts": base_ts.format(i),
            })
        # third event within the velocity window should trigger
        alerts = self.engine.evaluate({
            "event_id": "e2", "customer_id": customer, "amount": 50,
            "currency": "ZAR", "ts": base_ts.format(5),
        })
        self.assertTrue(any(a["rule"] == "VELOCITY" for a in alerts))


class TestDedupStore(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.store = DedupStore(db_path=Path(self.tmpdir.name) / "test.db")

    def tearDown(self):
        self.store.close()
        self.tmpdir.cleanup()

    def test_new_event_is_new(self):
        self.assertTrue(self.store.is_new("abc"))

    def test_processed_event_is_not_new(self):
        self.store.mark_processed("abc", "2026-06-01T00:00:00")
        self.assertFalse(self.store.is_new("abc"))

    def test_count_increments(self):
        self.store.mark_processed("a", "t")
        self.store.mark_processed("b", "t")
        self.assertEqual(self.store.count(), 2)


if __name__ == "__main__":
    unittest.main()
