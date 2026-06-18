# Transaction Monitoring Pipeline

An event-driven transaction monitoring pipeline: simulated stream ingestion, idempotent processing, and a rule-based fraud/anomaly engine — the same pattern used to support Kafka-based event ingestion alongside batch processing in a banking/fintech data platform.

## Why this exists

Payment events arrive at-least-once, out of order, and sometimes twice. A monitoring system that double-counts a duplicate delivery either double-fires an alert or misses a real fraud pattern. This project implements the idempotency and ordering guarantees that make event-driven monitoring trustworthy, then layers a small rules engine on top to demonstrate the kind of anomaly detection those guarantees exist to support.

## Architecture

```mermaid
flowchart LR
    A[Event Producer\n(simulated stream)] -->|events.jsonl| B[Consumer]
    B -->|is_new?| C[(Dedup Store\nSQLite)]
    B --> D[Rules Engine]
    D -->|LARGE_AMOUNT, VELOCITY| E[alerts.jsonl]
    B --> F[Data Quality:\ncompleteness, dedup rate]
```

| Component | File | Responsibility |
|---|---|---|
| Event producer | `src/event_producer.py` | Simulates an at-least-once event stream, including deliberate duplicate deliveries |
| Dedup store | `src/dedup_store.py` | Tracks processed `event_id`s so re-reads/replays never double-process |
| Rules engine | `src/rules_engine.py` | Pluggable fraud/anomaly rules (large amount, velocity/burst detection) |
| Consumer | `src/consumer.py` | Reads events in event-time order, applies idempotency, runs rules, reports data quality |

> This uses a file-based stream rather than a live Kafka broker so the project runs anywhere with no infrastructure to stand up — the idempotency and ordering logic is identical to what you'd write against a real Kafka consumer; only the transport changes.

## Tech stack

Python, SQLite, JSON Lines (the file format that maps directly onto how Kafka messages are typically logged/replayed).

## Running it

```bash
python src/event_producer.py   # generates data/events.jsonl, ~500 events incl. duplicates
python src/consumer.py
```

Sample output:

```
Events read:          515
Duplicates skipped:   15
Net events processed: 500
Completeness:         100.00%
Alerts raised:        39
   VELOCITY: 18
   LARGE_AMOUNT: 21
```

Run the tests:

```bash
python -m unittest discover -s tests -v
```

## What I'd add for production

- Swap the file-based producer/consumer for `confluent-kafka-python` against a real topic, keeping the dedup store and rules engine unchanged.
- Move the dedup store to a distributed cache (Redis) so multiple consumer instances share one idempotency guarantee.
- Stream alerts to a case-management queue instead of a flat file, with severity scoring and analyst feedback loops.

## License

MIT — feel free to reuse for your own learning.
