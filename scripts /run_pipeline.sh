# scripts/run_pipeline.sh
spark-submit src/bronze_ingestion.py
spark-submit src/silver_processing.py
spark-submit src/risk_engine.py
spark-submit src/gold_outputs.py
