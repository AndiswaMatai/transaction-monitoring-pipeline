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
