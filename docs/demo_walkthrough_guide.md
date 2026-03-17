# Demo & Exploration Guide: Real-Time Fraud Detection

This document is **dual-purpose**: it provides an exact presentation script for presenters and a "Self-Navigation Map" for independent readers exploring the repository.

**Pre-requisite:** Ensure all components in the `setup_and_configuration_guide.md` are running.

---

## 1. The Introduction (The Operational Core)
*   **Goal:** Establish Dameng DM8 as the high-performance operational "heart."
*   **Navigation:** Open **DBeaver** (or your local DB client).
*   **Action (Presenter):** 
    1.  Connect to the **Dameng VM**.
    2.  Expand the `FINANCE_DEMO` schema.
    3.  Show the 4 core tables: `TRANSACTIONS`, `CUSTOMERS`, `MERCHANTS`, `ACCOUNTS`.
    4.  Run `SELECT COUNT(*) FROM TRANSACTIONS;` to show the current baseline.
*   **Talking Point (Presenter):** *"We are looking at our operational core. Every swipe, every transfer, and every KYC record lands here in Dameng DM8. It’s fast and robust, but we need Cloudera to turn this raw data into intelligent, bank-grade decisions."*
*   **💡 Self-Guided Note:** Check `sql/dameng_setup.sql` to see how these tables were initialized. This represents the bank's production database.

---

## 2. Ingestion Orchestration (NiFi UI)
*   **Goal:** Show NiFi as the "Enterprise Digital Nervous System."
*   **Navigation:** Go to **Cloudera Manager** -> **Cloudera Data Ingestion (NiFi)** -> **NiFi Web UI**.
*   **Action (Presenter):**
    1.  Enter the **Ingestion Hub** Canvas.
    2.  Point to the **QueryDatabaseTable** processors polling Dameng.
    3.  Highlight the **QueryRecord (SQL)** processor renaming columns (e.g., `location` to `city`).
    4.  Point to the **PutIceberg** processor writing to the Lakehouse.
*   **Talking Point (Presenter):** *"NiFi isn't just a mover; it's a transformer. It handles the security handshake, the data mapping, and the real-time landing into our Data Lakehouse—all without writing a single line of Java code."*
*   **💡 Self-Guided Note:** Explore the processors. Notice how Path B (Customers) includes an `UpdateRecord` processor that masks names (e.g., `Siong****`) before they ever touch the Lakehouse.

---

## 3. Real-Time Dashboards (Cloudera Data Visualization)
*   **Goal:** Show immediate business value from the Lakehouse.
*   **Navigation:** From **CDP Home**, select **Data Visualization** -> Open the **"Fraud Command Center"** Dashboard.
*   **Action (Presenter):**
    1.  Point to the **Green/Red Donut Chart** (Fraud Status).
    2.  Point to the **Top 5 Flagged Cities** Bar Chart.
*   **Talking Point (Presenter):** *"By landing data in Apache Iceberg, we've broken the 'Sync Gap.' Business analysts are no longer looking at 'yesterday's data'; they are looking at the pulse of the bank as it happens."*
*   **💡 Self-Guided Note:** Try clicking on a "Merchant Category" to see the dashboard ripple. This interactivity is powered by Impala querying Iceberg metadata sub-second.

---

## 4. Advanced AI & ML Modeling (Cloudera Machine Learning)
*   **Goal:** Show the "AI-Ready" Lakehouse.
*   **Navigation:** From **CDP Home**, select **Machine Learning (CML)** -> Open the **"Fraud_Detection_Ecosystem"** Project.
*   **Action (Presenter):**
    1.  Open `scripts/fraud_detection_training.py`. Highlight the line joining Iceberg tables.
    2.  Go to **Models** -> Open **FraudScoringAPI** -> Click **Test**.
    3.  Input a sample JSON (e.g., $50k transaction) and show the `FLAGGED` response.
*   **Talking Point (Presenter):** *"Because our data is in an open Lakehouse format, our Data Scientists can jump straight into Python and Spark. We've gone from a raw Dameng record to a deployed Model API in minutes."*
*   **💡 Self-Guided Note:** Check `scripts/fraud_model_api.py`. This is the inference code that provides the REST endpoint for real-time scoring.

---

## 5. Enterprise Guardrails: Security & Governance (SDX)
*   **Goal:** Prove the platform is "Bank-Grade."
*   **Navigation Path:** **Lineage (Atlas)** and **Security (Ranger)**.
*   **Action (Presenter):**
    1.  **Atlas**: Search for `customers`. Show the lineage graph from Dameng to Iceberg.
    2.  **Ranger**: Show a **Masking Policy** triggered by the `PII` tag on the `NAME` column. 
*   **Talking Point (Presenter):** *"Dameng provides the performance, but Cloudera SDX provides the 'Safety Net.' We have full lineage, dynamic security masking, and total historical auditability—elements critical for a modern, compliant bank."*
*   **💡 Self-Guided Note:** Run `DESCRIBE HISTORY dameng.transactions` in Hue/Impala. Every single write from NiFi creates a permanent, auditable "Snapshot ID" in Iceberg.

---

## 6. The Conclusion
*   **Action:** Bring back the **CDV Dashboard** on one screen and **CML Model API** on the other.
*   **Talking Point:** *"By integrating Dameng DM8 with the Cloudera Data Lakehouse, we haven't just built a database—we've built a sovereign, AI-ready data factory. This allows us to scale our operational banking while innovating with real-time intelligence."*
igence."*
