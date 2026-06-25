# src/bronze_ingestion.py
from pyspark.sql import SparkSession

spark = SparkSession.builder.appName("BronzeIngestion").getOrCreate()

# Ingest JSON Lines (Kafka-style replay format)
raw_df = spark.read.json("data/transactions/*.json")

# Deduplicate using idempotency key
bronze_df = raw_df.dropDuplicates(["txn_id"])
bronze_df.write.format("delta").mode("overwrite").save("delta/bronze")
