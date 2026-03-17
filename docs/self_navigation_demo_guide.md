# Self-Navigation Guide: Exploring the Fraud Detection Demo

Welcome! This guide is designed for readers who want to explore the **Dameng & Cloudera Fraud Detection Ecosystem** independently. Use this document to navigate the various components and understand the flow of data and intelligence.

---

## 🏗️ The Story
You are looking at a "Modern Banking Hub." The goal is to ingest high-frequency transaction data from an operational database (**Dameng DM8**), transform it in real-time, and apply "Bank-Grade" intelligence and governance within the **Cloudera Data Lakehouse**.

---

## 🧭 Navigation Paths

### 1. The Operational Core (Dameng DM8)
*Where the data begins.*
- **What to look for**: Check `sql/dameng_setup.sql`.
- **Insight**: This represents the bank's core system. It handles the "raw" balance and transaction records before they are ever touched by analytics.

### 2. The Digital Nervous System (Apache NiFi)
*How the data moves.*
- **Open NiFi Canvas**: Look for the `Banking_Ingestion_Hub` process group.
- **What to explore**:
    - **Path A (Transactions)**: Notice the `QueryRecord` processor. It renames columns (e.g., `location` to `city`) and casts types to prepare for Iceberg.
    - **Path B (Customers)**: Find the `UpdateRecord` processor. It uses a regex to mask customer names (e.g., `Siong****`) before they land in the Lakehouse.
    - **The landing**: See the `PutIceberg` processors. These write data in **Parquet** format directly into the Lakehouse metadata layer.

### 3. The Real-Time Dashboard (Cloudera Data Visualization)
*How the bank sees the data.*
- **Navigate to CDV**: Open the **"Fraud Command Center"** Dashboard.
- **Key Visuals to Inspect**:
    - **Fraud vs Approved**: A donut chart showing the split of transactions.
    - **Top Flagged Cities**: A bar chart identifying geographic hotspots for fraud.
    - **Interactive Filtering**: Try clicking on a specific "Merchant Category" to see how the entire dashboard ripples with real-time updates.

### 4. Continuous Intelligence (Cloudera Machine Learning)
*How the bank predicts fraud.*
- **Open CML**: Locate the `Fraud_Detection_Ecosystem` project.
- **Key Files**: 
    - `scripts/fraud_detection_training.py`: See how it joins Iceberg tables to build a feature set.
    - `scripts/fraud_model_api.py`: This is the active REST API.
- **Action**: Go to **Models** -> **Test**. Try sending a large transaction amount ($50,000) and watch the model instantly return a `status: FLAGGED` response.

### 5. Enterprise Guardrails (SDX)
*How the bank protects the data.*
- **Audit Lineage (Atlas)**: Search for the `customers` table. View the "Lineage" tab to see the "Birth-to-Death" path of the data from NiFi to Iceberg.
- **Security (Ranger)**: Look for "Tag-Based Masking." Even without a database-level change, Ranger ensures that an analyst sees masked PII data while an admin sees the full record.
- **Time Travel (Impala)**: Run `DESCRIBE HISTORY dameng.transactions`. This proves that every single change in the database has a permanent, auditable "Snapshot ID."

---

## 🏁 Summary for the Reader
This demo proves that **Dameng DM8** and **Cloudera** aren't just connected—they are integrated. 
- You’ve seen **Operational Data** flow into **Analytical Intelligence**.
- you’ve seen **Real-Time Visibility** meet **Enterprise Governance**.

*For a full technical deep-dive, refer to the [Setup & Configuration Guide](setup_and_configuration_guide.md).*
