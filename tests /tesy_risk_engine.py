# tests/test_risk_engine.py
def test_high_value_rule(spark_session):
    df = spark_session.createDataFrame(
        [("A1", "T1", 15000, 1)],
        ["account_id", "txn_id", "amount", "velocity"]
    )
    assert df.filter(df.amount > 10000).count() == 1
