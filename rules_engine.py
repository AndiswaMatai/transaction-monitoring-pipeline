"""
Lightweight anomaly/fraud rule engine. Each rule receives the current event
plus the customer's recent event history and returns an alert (or None).
Designed so new rules are a 5-line function, not a rewrite.
"""
from collections import defaultdict
from datetime import datetime, timedelta

LARGE_AMOUNT_THRESHOLD = 7000
VELOCITY_WINDOW_SECONDS = 120
VELOCITY_COUNT_THRESHOLD = 3


def rule_large_amount(event, history):
    if event["amount"] >= LARGE_AMOUNT_THRESHOLD:
        return {
            "rule": "LARGE_AMOUNT",
            "detail": f"{event['amount']} {event['currency']} exceeds threshold {LARGE_AMOUNT_THRESHOLD}",
        }
    return None


def rule_velocity(event, history):
    """Flags >= VELOCITY_COUNT_THRESHOLD events for the same customer within
    VELOCITY_WINDOW_SECONDS — a classic card-testing / fraud burst pattern."""
    ts = datetime.fromisoformat(event["ts"])
    window_start = ts - timedelta(seconds=VELOCITY_WINDOW_SECONDS)
    recent = [h for h in history if window_start <= datetime.fromisoformat(h["ts"]) <= ts]
    if len(recent) + 1 >= VELOCITY_COUNT_THRESHOLD:
        return {
            "rule": "VELOCITY",
            "detail": f"{len(recent) + 1} transactions within {VELOCITY_WINDOW_SECONDS}s for {event['customer_id']}",
        }
    return None


RULES = [rule_large_amount, rule_velocity]


class RulesEngine:
    def __init__(self):
        self.history_by_customer = defaultdict(list)

    def evaluate(self, event):
        history = self.history_by_customer[event["customer_id"]]
        alerts = []
        for rule in RULES:
            alert = rule(event, history)
            if alert:
                alerts.append({**alert, "event_id": event["event_id"], "customer_id": event["customer_id"]})
        history.append(event)
        return alerts
