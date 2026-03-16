# Demo Walkthrough Guide: Real-Time Fraud Detection

This document provides the exact presentation script and "point-and-click" steps to showcase the integrated Dameng, Cloudera, and HPE Data Architecture.

**Pre-requisite:** Ensure all components in the `setup_and_configuration_guide.md` are running.

---

## 1. The Introduction (The Operational Core)
*   **Goal:** Establish Dameng DM8 as the high-performance operational "heart."
*   **Navigation:** Open **DBeaver** (or your local DB client).
*   **Action:** 
    1.  Connect to the **Dameng VM**.
    2.  Expand the `FINANCE_DEMO` schema.
    3.  Show the 4 core tables: `TRANSACTIONS`, `CUSTOMERS`, `MERCHANTS`, `ACCOUNTS`.
    4.  Run `SELECT COUNT(*) FROM TRANSACTIONS;` to show the current baseline.
*   **Talking Point:** *"We are looking at our operational core. Every swipe, every transfer, and every KYC record lands here in Dameng DM8. It’s fast and robust, but we need Cloudera to turn this raw data into intelligent, bank-grade decisions."*

---

## 2. Ingestion Orchestration (NiFi UI)
*   **Goal:** Show NiFi as the "Enterprise Digital Nervous System."
*   **Navigation:** 
    1.  Go to **Cloudera Manager** -> **Cloudera Data Ingestion (NiFi)**.
    2.  Click the **NiFi Web UI** link.
*   **Action:**
    1.  Enter the **Ingestion Hub** Canvas.
    2.  Point to the **QueryDatabaseTable** processors. *"These processors are using JDBC to pull from Dameng every few seconds."*
    3.  Point to the **QueryRecord (SQL Transformation)** processor. *"Notice we don't just dump data. We use standard SQL mid-flight to normalize 'LOCATION' into 'city', ensuring it's ready for our dashboards."*
    4.  Point to the **PutIceberg** processor. *"This is the landing zone. We are converting Dameng records into Iceberg Parquet files instantly."*
*   **Talking Point:** *"NiFi isn't just a mover; it's a transformer. It handles the security handshake, the data mapping, and the real-time landing into our Data Lakehouse—all without writing a single line of Java code."*

---

## 3. Real-Time Dashboards (Cloudera Data Visualization)
*   **Goal:** Show immediate business value from the Lakehouse.
*   **Navigation:**
    1.  From the **CDP Home Page**, select **Data Visualization**.
    2.  Open the **"Fraud Command Center"** Dashboard.
*   **Action:**
    1.  Point to the **Green/Red Donut Chart**. *"As data flows into Iceberg, this updates instantly—no manual refresh needed."*
    2.  Point to the **Top 5 Flagged Cities** Bar Chart. *"We are seeing exactly where the risk is concentrated in Southeast Asia right now."*
*   **Talking Point:** *"By landing data in Apache Iceberg, we've broken the 'Sync Gap.' Business analysts are no longer looking at 'yesterday's data'; they are looking at the pulse of the bank as it happens."*

---

## 4. Advanced AI & ML Modeling (Cloudera Machine Learning)
*   **Goal:** Show the "AI-Ready" Lakehouse.
*   **Navigation:**
    1.  From **CDP Home**, select **Machine Learning (CML)**.
    2.  Open the **"Fraud_Detection_Ecosystem"** Project.
*   **Action:**
    1.  Open **[fraud_detection_training.py](../scripts/fraud_detection_training.py)**. 
    2.  Highlight the line `spark.table("dameng.transactions")`. *"The model trains directly on the Iceberg tables we just landed via NiFi."*
    3.  Go to **Models** -> Open **FraudScoringAPI**.
    4.  Click **Test** and input a sample JSON (e.g., $50k transaction). Show it returning `status: FLAGGED`.
*   **Talking Point:** *"Because our data is in an open Lakehouse format, our Data Scientists can jump straight into Python and Spark to build predictive models. We've gone from a raw Dameng record to a deployed Model API in minutes."*

---

## 5. Enterprise Guardrails: Security & Governance (SDX)
*   **Goal:** Prove the platform is "Bank-Grade."
*   **Navigation:**
    1.  **Lineage**: Open **Apache Atlas** (via Cloudera Manager/Data Catalog).
    2.  **Security**: Open **Apache Ranger** (via Cloudera Manager/Security).
*   **Action:**
    1.  **Atlas**: Search for `customers` and click **Lineage**. Show the path from Dameng to Iceberg.
    2.  **Tag Identification**: Point to the `PII` tag on the `NAME` column. 
    *   **Explanation**: *"Remember our NiFi pipeline? We tagged this as 'is_pii' during ingestion. That metadata is now reflected here as a global 'PII' classification."*
    3.  **Ranger**: Show a **Masking Policy** triggered by the `PII` tag. *"Because Atlas has classified this as PII, Ranger enforces security automatically across the entire Lakehouse."*
    3.  **Iceberg History**: Open **Hue** -> **Impala**. Run `DESCRIBE HISTORY dameng.transactions`. *"We can time-travel back to any snapshot in history to audit what happened."*
*   **Talking Point:** *"Dameng provides the performance, but Cloudera SDX provides the 'Safety Net.' We have full lineage, dynamic security masking, and total historical auditability—elements that are critical for a modern, compliant bank."*

---

## 6. The Conclusion
*   **Action:** Bring back the **CDV Dashboard** on one screen and **CML Model API** on the other.
*   **Talking Point:** *"By integrating Dameng DM8 with the Cloudera Data Lakehouse, we haven't just built a database—we've built a sovereign, AI-ready data factory. This allows us to scale our operational banking while innovating with real-time intelligence."*
