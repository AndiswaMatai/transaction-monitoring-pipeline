# src/silver_processing.py
from pyspark.sql.functions import col, sha2, concat_ws

bronze_df = spark.read.format("delta").load("delta/bronze")

# Enrichment + deterministic transaction key
silver_df = (
    bronze_df
    .withColumn("txn_key", sha2(concat_ws("||", col("account_id"), col("txn_id")), 256))
    .filter(col("amount") >= 0)
)

silver_df.write.format("delta").mode("overwrite").save("delta/silver")

# src/risk_engine.py
from pyspark.sql.functions import col, when

silver_df = spark.read.format("delta").load("delta/silver")

# Rule-based risk detection
risk_df = (
    silver_df
    .withColumn("risk_flag",
        when(col("amount") > 10000, "HighValue")
        .when(col("velocity") > 5, "Velocity")
        .when(col("duplicate") == True, "Duplicate")
        .when(col("cross_border") == True, "CrossBorder")
        .otherwise("None"))
    .withColumn("severity_score",
        when(col("risk_flag") == "HighValue", 5)
        .when(col("risk_flag") == "Velocity", 4)
        .when(col("risk_flag") == "Duplicate", 3)
        .when(col("risk_flag") == "CrossBorder", 4)
        .otherwise(0))
)

risk_df.write.format("delta").mode("overwrite").save("delta/risk_scored")

