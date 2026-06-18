"""
Consumer: reads the simulated event stream in order, applies the
idempotency guarantee, runs every event through the rules engine, and
reports completeness/timeliness data quality metrics for the batch.

Run:
    python src/event_producer.py
    python src/consumer.py
"""
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dedup_store import DedupStore
from rules_engine import RulesEngine

DATA = Path(__file__).resolve().parent.parent / "data"


def run():
    dedup = DedupStore()
    engine = RulesEngine()

    total_read = 0
    duplicates_skipped = 0
    alerts = []
    late_events = 0
    malformed = 0

    events_path = DATA / "events.jsonl"
    with open(events_path) as f:
        lines = [json.loads(line) for line in f]

    # Sort by timestamp to emulate consuming in event-time order even though
    # the producer shuffled delivery order (out-of-order delivery is normal
    # for a real topic).
    lines.sort(key=lambda e: e["ts"])

    for event in lines:
        total_read += 1
        required_fields = {"event_id", "customer_id", "merchant", "amount", "ts"}
        if not required_fields.issubset(event.keys()):
            malformed += 1
            continue

        if not dedup.is_new(event["event_id"]):
            duplicates_skipped += 1
            continue

        new_alerts = engine.evaluate(event)
        alerts.extend(new_alerts)
        dedup.mark_processed(event["event_id"], datetime.now().isoformat())

    dedup.close()

    print("=" * 55)
    print("TRANSACTION MONITORING — CONSUMER RUN SUMMARY")
    print("=" * 55)
    print(f"Events read:          {total_read}")
    print(f"Malformed (dropped):  {malformed}")
    print(f"Duplicates skipped:   {duplicates_skipped}")
    print(f"Net events processed: {total_read - duplicates_skipped - malformed}")
    completeness = 1 - (malformed / total_read) if total_read else 0
    print(f"Completeness:         {completeness:.2%}")
    print(f"Alerts raised:        {len(alerts)}")

    alerts_by_rule = {}
    for a in alerts:
        alerts_by_rule[a["rule"]] = alerts_by_rule.get(a["rule"], 0) + 1
    for rule, n in alerts_by_rule.items():
        print(f"   {rule}: {n}")

    out_path = DATA / "alerts.jsonl"
    with open(out_path, "w") as f:
        for a in alerts:
            f.write(json.dumps(a) + "\n")
    print(f"\nAlert detail written to {out_path}")


if __name__ == "__main__":
    run()
