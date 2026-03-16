# Dameng & Cloudera Real-Time Fraud Detection Lakehouse

This repository contains a full-stack enterprise data architecture integration between **Dameng DM8** (Operational Database) and **Cloudera CDP** (Data Lakehouse). 

It demonstrates a real-time banking ecosystem where synthetic transactions are generated, ingested into an **Apache Iceberg** lakehouse via **Apache NiFi**, and then used for live analytics, Machine Learning (CML), and AI-driven governance.

## 📂 Project Structure

- **[`docs/`](docs/)**: Enterprise-grade documentation.
    - **[`setup_and_configuration_guide.md`](docs/setup_and_configuration_guide.md)**: Technical installation and configuration steps.
    - **[`demo_walkthrough_guide.md`](docs/demo_walkthrough_guide.md)**: Scripted "point-and-click" walkthrough for the final presentation.
- **[`scripts/`](scripts/)**: Python automation and ML code.
    - `dameng_transaction_generator.py`: Core transaction simulator.
    - `bank_customer_generator.py`, `bank_account_generator.py`, `bank_merchant_generator.py`: KYC and ecosystem data generators.
    - `fraud_detection_training.py`: Robust PySpark training pipeline using Iceberg data.
    - `fraud_model_api.py`: Model inference script for CML Model API deployment.
- **[`sql/`](sql/)**: Database initialization scripts.
    - `dameng_setup.sql`: DDL for Dameng DM8 tables.
    - `iceberg_setup.sql`: DDL for Cloudera Iceberg analytical tables.

## 🚀 Key Features

1.  **Operational Core**: High-performance transaction processing on Dameng DM8.
2.  **Streaming Ingestion**: Real-time ELT using NiFi with dynamic SQL transformations and Iceberg "No-Refresh" landing.
3.  **Advanced Analytics**: Live fraud monitoring dashboards in Cloudera Data Visualization (CDV).
4.  **AI & Machine Learning**: Automated model training and REST API deployment in CML.
5.  **Data Sovereignty & Governance**: Tag-based security (Atlas/Ranger) and total auditability via Iceberg Time Travel.

## 🛠️ Requirements

- Dameng DM8 (on Linux)
- Cloudera CDP (NiFi, Iceberg, CML, CDV, Impala, Atlas/Ranger)
- Python 3.x with `pyspark`, `pandas`, and `scikit-learn`

---
*Developed for the HPE & Cloudera Modern Data Architecture Showcase.*
