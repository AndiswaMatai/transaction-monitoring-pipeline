# src/gold_outputs.py
from pyspark.sql.functions import count, sum

risk_df = spark.read.format("delta").load("delta/risk_scored")

# Alerts dataset
alerts = risk_df.filter(risk_df.risk_flag != "None")
alerts.write.format("delta").mode("overwrite").save("delta/alerts")

# KPI summary
kpi_df = (
    risk_df.groupBy("risk_flag")
    .agg(count("*").alias("txn_count"), sum("amount").alias("total_amount"))
)

kpi_df.write.format("delta").mode("overwrite").save("delta/gold_kpi")
