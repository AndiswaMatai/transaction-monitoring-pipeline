"""
Simulates an event-driven transaction stream (the pattern a real Kafka
topic would carry). Writes newline-delimited JSON events to data/events.jsonl,
including a handful of deliberately duplicated events so the consumer's
idempotency guarantee has something real to prove.
"""
import json
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

random.seed(7)
DATA = Path(__file__).resolve().parent.parent / "data"
DATA.mkdir(parents=True, exist_ok=True)

MERCHANTS = ["Takealot", "Uber", "Checkers", "Netflix", "Shell", "Pick n Pay", "Woolworths"]
CUSTOMERS = [f"CUST{1000+i}" for i in range(25)]


def make_event(ts):
    customer = random.choice(CUSTOMERS)
    amount = round(random.expovariate(1 / 450), 2)
    # occasionally simulate a velocity-fraud pattern: a burst of large amounts
    is_burst = random.random() < 0.04
    if is_burst:
        amount = round(random.uniform(8000, 25000), 2)
    return {
        "event_id": str(uuid.uuid4()),
        "customer_id": customer,
        "merchant": random.choice(MERCHANTS),
        "amount": amount,
        "currency": "ZAR",
        "ts": ts.isoformat(),
    }


def run(n_events=500, duplicate_rate=0.03):
    start = datetime(2026, 6, 1, 8, 0, 0)
    events = []
    t = start
    for _ in range(n_events):
        t += timedelta(seconds=random.randint(1, 40))
        events.append(make_event(t))

    # Inject duplicate deliveries (at-least-once delivery is the whole reason
    # the consumer needs to be idempotent).
    duplicates = random.sample(events, int(n_events * duplicate_rate))
    events.extend(duplicates)
    random.shuffle(events)

    out_path = DATA / "events.jsonl"
    with open(out_path, "w") as f:
        for e in events:
            f.write(json.dumps(e) + "\n")

    print(f"wrote {len(events)} events ({len(duplicates)} duplicates) to {out_path}")


if __name__ == "__main__":
    run()
