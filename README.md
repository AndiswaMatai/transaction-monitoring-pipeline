# Real-Time Transaction Monitoring & Risk Detection Platform

![Sector](https://img.shields.io/badge/Sector-Fintech-0f7a4b?style=flat)
![CI](https://img.shields.io/badge/CI-passing-0f7a4b?style=flat&logo=githubactions)
![Python](https://img.shields.io/badge/Python-3.12-blue?style=flat&logo=python)

**[← Back to live portfolio](https://andiswamatai.github.io)**

## 🧠 Business Context

Financial institutions process millions of transactions daily across multiple channels including cards, EFT, digital banking, and cross-border payments.

In such environments, ensuring transactional integrity and detecting fraudulent or suspicious activity in near real-time is critical.

Key challenges include:

- High-velocity transaction streams from multiple sources
- Duplicate or replayed events due to network retries
- Lack of consistent transaction identity across systems
- Increasing sophistication of fraud patterns
- Regulatory pressure for real-time monitoring and reporting

  ---
  
## 🎯 Solution Overview

This platform implements a real-time transaction monitoring and risk detection system designed to simulate enterprise-grade financial crime monitoring architecture.

The system provides:

- Event-driven ingestion layer for transaction streams
- Idempotency controls to eliminate duplicate transactions
- Pluggable rule-based risk detection engine
- Structured enrichment of transaction events
- Monitoring-ready outputs for downstream analytics and alerting systems
  
---

## Architecture

📡 Transaction Sources
- Payment Gateway Events
- Banking Transactions
- Card Swipes / Digital Payments

        ↓

⚡ Ingestion Layer
- Event Stream Capture (Kafka-style simulation)
- Deduplication (idempotency key logic)

        ↓

🔄 Processing Layer
- Spark-style transformations
- Transaction enrichment
- Rule engine evaluation

        ↓

🧠 Risk Engine
- Fraud rules engine (pluggable)
- Velocity checks
- Threshold anomalies
- Behavioural flags

        ↓

📊 Output Layer
- Alerts dataset
- Risk scored transactions
- Monitoring dashboards (Power BI / logs)

  ---

## 🧠 Risk Detection Engine

The system implements a modular rule-based engine that evaluates each transaction against configurable risk rules.

### Example rules:

- High-value transaction threshold breach
- Rapid transaction velocity from same account
- Duplicate transaction detection
- Cross-border anomaly flags
- Suspicious merchant category patterns

Each rule produces:
- Risk flag
- Severity score
- Rule metadata for auditability

---

## Tech stack

Python, SQLite, JSON Lines (the file format that maps directly onto how Kafka messages are typically logged/replayed).

## ⚙️ Data Engineering Patterns

This platform demonstrates enterprise data engineering concepts:

- Idempotent ingestion using deterministic transaction keys
- Event deduplication to prevent double processing
- Stateless rule evaluation for scalability
- Spark-style distributed transformation design
- Separation of ingestion, processing, and risk scoring layers

## 📊 Outputs

The system produces structured outputs for downstream consumption:

- Clean transaction stream
- Risk-scored transaction dataset
- Fraud alerts dataset
- Rule evaluation logs
- Monitoring-ready tables for BI tools
```



## License

MIT — feel free to reuse for your own learning
