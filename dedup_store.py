"""
Idempotency store: tracks event_ids already processed so the consumer can
safely re-read a topic (or replay a batch) without double-counting,
processing the same fraud check twice, or double-firing an alert.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "processed_events.db"


class DedupStore:
    def __init__(self, db_path=DB_PATH):
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS processed_events (event_id TEXT PRIMARY KEY, processed_ts TEXT)"
        )
        self.conn.commit()

    def is_new(self, event_id: str) -> bool:
        cur = self.conn.execute(
            "SELECT 1 FROM processed_events WHERE event_id = ?", (event_id,)
        )
        return cur.fetchone() is None

    def mark_processed(self, event_id: str, ts: str):
        self.conn.execute(
            "INSERT OR IGNORE INTO processed_events (event_id, processed_ts) VALUES (?, ?)",
            (event_id, ts),
        )
        self.conn.commit()

    def count(self) -> int:
        return self.conn.execute("SELECT COUNT(*) FROM processed_events").fetchone()[0]

    def close(self):
        self.conn.close()
