# Setup and Configuration Guide: Dameng & Cloudera Integration

This document provides the technical steps required to install Dameng DM8 on Linux, integrate it with Cloudera via Apache NiFi, and configure the downstream analytics and AI components (CML and CDV).

## Phase 1: Dameng DM8 Linux Installation & Verification

While Dameng provides a graphical installer, the following are the typical command-line steps for a standard Linux deployment.

### 1. OS Preparation & User Creation
1.  **Create the Database User and Group:** Dameng requires a dedicated user (typically `dmdba`).
    ```bash
    groupadd dinstall
    useradd -g dinstall -m -d /home/dmdba -s /bin/bash dmdba
    passwd dmdba
    ```
2.  **Configure OS Limits:** Edit `/etc/security/limits.conf` to increase file descriptors for `dmdba`:
    ```text
    dmdba soft nofile 65536
    dmdba hard nofile 65536
    ```
3.  **Prepare Directories:**
    ```bash
    mkdir -p /home/dmdba/dmdbms
    mkdir -p /home/dmdba/dmdata
    chown dmdba:dinstall -R /home/dmdba/
    chmod -R 755 /home/dmdba/
    ```

### 2. Software Installation
1.  **Mount the Installer ISO:**
    ```bash
    mount -o loop dm8_setup_linux.iso /mnt
    ```
2.  **Run the Installer (as `dmdba`):**
    Switch to the `dmdba` user and execute the command-line installer.
    ```bash
    su - dmdba
    cd /mnt
    ./DMInstall.bin -i
    ```
    *Follow the interactive prompts to install the binaries into `/home/dmdba/dmdbms`.*

### 3. Database Initialization (dminit)
1.  **Initialize the Database Instance:** Initialize the database instance manually via the CLI, pointing it to your high-capacity storage partition in `/home`.
    ```bash
    cd /home/dmdba/dmdbms/bin
    ./dminit path=/home/dmdba/dmdata SYSDBA_PWD=ClouderaVM123 SYSAUDITOR_PWD=ClouderaVM123
    ```
    *Result: Creates the control files, default tablespaces (SYSTEM, MAIN, ROLL), and log files in `/home/dmdba/dmdata/DAMENG`.*

### 4. Service Registration (Activation)
To "activate" the instance as a background service managed by the OS (systemd), use the root helper script. 
1.  **Register the Service (as `root`):** Run the script pointing specifically to the new `.ini` configuration file.
    ```bash
    /home/dmdba/dmdbms/script/root/dm_service_installer.sh -t dmserver -p DMSERVER -dm_ini /home/dmdba/dmdata/DAMENG/dm.ini
    ```
2.  **Start and Enable the Service:**
    ```bash
    systemctl start DmServiceDMSERVER
    systemctl enable DmServiceDMSERVER
    ```
    *(Note: `systemctl enable` ensures the service auto-starts whenever the VM is booted.)*

### 5. Headless Configuration & First Test (No-UI Management)
Since no Graphical User Interface (GUI) is available on the VM, use the `disql` command-line utility.

**1. Log in to the Instance**
Ensure your service is running, then connect using the default administrator account (`SYSDBA`).
```bash
cd /home/dmdba/dmdbms/bin
./disql SYSDBA/ClouderaVM123@localhost:5236
```
*(Note: If configuring from an external Linux shell where `$` is interpreted, you may need to escape it as `\$`. Inside `disql` execution, it's literal.)*

**2. Create a Tablespace**
A tablespace is the physical storage container (file) for your specific project's data.
```sql
CREATE TABLESPACE "FINANCE_DATA" DATAFILE '/home/dmdba/dmdata/DAMENG/FINANCE_01.DBF' SIZE 128 AUTOEXTEND ON NEXT 64;
```
*(Note: `SIZE 128` is only the **initial** size in MB. `AUTOEXTEND ON NEXT 64` ensures that when the file is full, it will automatically grow in 64MB increments. This ensures your storage scales automatically with your data growth.)*

**3. Create a User (Schema)**
In Dameng, creating a user automatically creates a "Schema" of the same name.
```sql
CREATE USER "FINANCE_DEMO" IDENTIFIED BY "<YOUR_PASSWORD>" DEFAULT TABLESPACE "FINANCE_DATA";
```

**4. Grant Permissions**
Give the new user enough power to actually do work:
```sql
GRANT "PUBLIC", "RESOURCE", "SOI" TO "FINANCE_DEMO";
```
*(PUBLIC/RESOURCE: Basic roles for creating tables and sequences. SOI: Allows the user to query system views.)*

**5. Test Your New "DB" & Create Transaction Table**
Disconnect from `SYSDBA` and log in as your new user to create your first table.
```bash
# Exit disql first by typing 'exit'
./disql FINANCE_DEMO/ClouderaVM123@localhost:5236
```

#### **1.2 Create the Banking Ecosystem Tables**
Copy and paste this SQL into DBeaver to initialize your operational environment.

```sql
-- 1. TRANSACTIONS (Core Activity)
CREATE TABLE FINANCE_DEMO.TRANSACTIONS (
    TX_ID BIGINT IDENTITY(1,1) PRIMARY KEY,
    USER_ID INT,
    MERCHANT_ID INT,
    AMOUNT DECIMAL(10,2),
    TX_TIME TIMESTAMP,
    STATUS VARCHAR(20),
    LOCATION VARCHAR(50)
);

-- 2. CUSTOMERS (KYC Profiles)
CREATE TABLE FINANCE_DEMO.CUSTOMERS (
    CUSTOMER_ID INT IDENTITY(1,1) PRIMARY KEY,
    NAME VARCHAR(100),
    AGE INT,
    CREDIT_LIMIT DECIMAL(10,2),
    RISK_PROFILE VARCHAR(20),
    CREATED_AT TIMESTAMP
);

-- 3. MERCHANTS (Business Context)
CREATE TABLE FINANCE_DEMO.MERCHANTS (
    MERCHANT_ID INT IDENTITY(1,1) PRIMARY KEY,
    MERCHANT_NAME VARCHAR(100),
    CATEGORY VARCHAR(50),
    RISK_LEVEL VARCHAR(20),
    CITY VARCHAR(50),
    CREATED_AT TIMESTAMP
);

-- 4. ACCOUNTS (Financial Standing)
CREATE TABLE FINANCE_DEMO.ACCOUNTS (
    ACCOUNT_ID VARCHAR(20) PRIMARY KEY,
    CUSTOMER_ID INT,
    ACCOUNT_TYPE VARCHAR(20),
    BALANCE DECIMAL(15,2),
    CURRENCY VARCHAR(10),
    STATUS VARCHAR(20),
    OPENED_AT TIMESTAMP
);
```

**Step 5.2: Insert Sample Data**
Insert some manual records to verify everything is working before starting the automation script.
```sql
INSERT INTO transactions (user_id, amount, status, location) VALUES (1001, 150.50, 'COMPLETED', 'New York');
INSERT INTO transactions (user_id, amount, status, location) VALUES (1002, 25000.00, 'FLAGGED', 'London');
INSERT INTO transactions (user_id, amount, status, location) VALUES (1003, 75.00, 'PROCESSING', 'Singapore');
COMMIT;
```

**Step 5.3: Proof of Result**
Verify the records are correctly stored in Dameng:
```sql
SELECT * FROM transactions;
```
*Expected Output: You should see the 3 rows you just inserted. Your database is now fully prepared to receive the Python simulation script and the NiFi pipeline!*

---

---

## Phase 2: Cloudera Integration & Data Pipeline (NiFi)

Since Dameng DMHS is an Enterprise-only tool and may require a commercial license, we recommend the following **free, communal alternative** using Cloudera's built-in NiFi and the standard Dameng JDBC driver.

### 1. NiFi JDBC Driver Setup
1.  **Obtain Driver**: Find the `DmJdbcDriver18.jar` file in your VM at `/home/dmdba/dmdbms/drivers/jdbc/DmJdbcDriver18.jar`.
2.  **Upload to NiFi**: Copy this `.jar` to all NiFi nodes in your Cloudera cluster (e.g., to `/opt/cloudera/parcels/CDP_RUNTIME/lib/nifi/lib/`).
3.  **Create Connection Pool**: 
    *   In NiFi, add a `DBCPConnectionPool` controller service.
    *   **Database Connection URL**: `jdbc:dm://<YOUR_DAMENG_IP>:5236`
    *   **Database Driver Class Name**: `dm.jdbc.driver.DmDriver`
    *   **Database Driver Location(s)**: The path where you uploaded the `.jar`.
    *   **User/Password**: `FINANCE_DEMO / <YOUR_PASSWORD>`

#### 2. NiFi Parameter Context Setup (The "Demo Brain")
To handle the full ecosystem, we use parameters for each generator script:

1.  **Right-click canvas** -> **Parameters**.
2.  **Add Parameters to `Dameng_Demo_Context`**:
    *   `tx_gen`: **[transactions](../scripts/dameng_transaction_generator.py)**
    *   `cust_gen`: **[customers](../scripts/bank_customer_generator.py)**
    *   `merch_gen`: **[merchants](../scripts/bank_merchant_generator.py)**
    *   `acc_gen`: **[accounts](../scripts/bank_account_generator.py)**

### 3. Apache NiFi Workflow Configuration (Enterprise Banking)

#### **Pipeline 1: Connectivity Verification**
*Goal: Prove NiFi can interact with Dameng DM8 via JDBC.*

1.  **Add `GenerateFlowFile`**:
    *   **Scheduling**: `Timer Driven`, `5 min`.
    *   *Purpose: Acts as the trigger for the query.*
2.  **Add `ExecuteSQL`**:
    *   **Database Connection Pooling Service**: `DBCPConnectionPool`.
    *   **SQL Select Query**: `SELECT * FROM FINANCE_DEMO.transactions LIMIT 3;`
    *   **Relationship**: Connect `success` to `LogAttribute`.
3.  **Add `LogAttribute`**:
    *   **Log Level**: `info`.
    *   *Purpose: View the output in the NiFi Bulletin Board or logs.*

#### **Pipeline 2: Ecosystem Simulator (Simulator -> Dameng via JDBC)**
*Goal: Dynamically generate and write synthetic banking data into Dameng.*

1.  **Orchestration Block**: Create this flow for each dataset (`tx`, `cust`, `merch`, `acc`).
    *   **`GenerateFlowFile`**: Scheduling: `5 sec`.
    *   **`ReplaceText`**:
        *   **Replacement Value**: `#{tx_gen}` (use the appropriate parameter for each flow).
        *   **Replacement Strategy**: `Always Replace`.
        *   **Evaluation Mode**: `Entire text` (CRITICAL: Required for multi-line script handling).
    *   **`ExecuteStreamCommand`**:
        *   **Command Path**: `python3`.
        *   **Command Arguments**: `-`.
        *   **Ignore STDIN**: `false`.
    *   **Relationship**: Connect `output stream` to the next step.
3.  **Batching Logic**: Each script is now programmed to generate **5 records per trigger**. This reduces overhead and creates a better visual flow in NiFi.
2.  **Add `PutDatabaseRecord` (The Writer)**:
    *   **Record Reader**: `JsonTreeReader` (Configure it to expect JSON).
    *   **Statement Type**: `INSERT`.
    *   **Database Connection Pooling Service**: `DBCPConnectionPool`.
    *   **Table Name**: Set explicitly (e.g., `transactions`, `customers`).
    *   **Relationship**: Terminate `success` and `failure`.

**Common Iceberg Metadata Service (`HiveCatalogService`)**
To enable Iceberg landing, configure this controller service once in NiFi:
*   **Hive Metastore URI**: `thrift://cloudera-pvc-bm.tdcldr.com:9083`
*   **Default Warehouse Location**: `/warehouse/tablespace/managed/hive`
*   **Hadoop Configuration Resources**: `/etc/hadoop/conf/core-site.xml, /etc/hadoop/conf/hdfs-site.xml, /etc/hadoop/conf/hive-site.xml`
    *   *(Tip: Download `hive-site.xml` from Cloudera Manager and upload to NiFi server).*

**Common `PutIceberg` Configuration (Lakehouse Landing)**
For all four paths below, use these properties in your `PutIceberg` processors:
*   **Record Reader**: `ParquetReader`
*   **Catalog Service**: `HiveCatalogService`
*   **Catalog Namespace**: `dameng`
*   **File Format**: `PARQUET`
*   **Kerberos User Service**: `KerberosKeytabUserService`

**Controller Services: JSON Writers Configuration**
To handle the code-centric `QueryRecord` approach, you need four distinct `JsonRecordSetWriter` services.

**Common Writer Settings (Apply to All):**
*   **Schema Write Strategy**: `Do Not Write Schema`
*   **Schema Access Strategy**: `Use 'Schema Text' Property`
*   **Timestamp Format**: Blank (using logical types)
*   **Output Grouping**: `Array`
*   **Suppress Null Values**: `Never Suppress`

**1. `Iceberg_Transactions_Writer` Schema:**
```json
{
  "type": "record",
  "name": "transactions",
  "fields": [
    { "name": "tx_id", "type": "long" },
    { "name": "user_id", "type": "int" },
    { "name": "merchant_id", "type": "int" },
    { "name": "amount", "type": "double" },
    { "name": "tx_time", "type": { "type": "long", "logicalType": "timestamp-micros" } },
    { "name": "status", "type": "string" },
    { "name": "city", "type": ["null", "string"], "default": null }
  ]
}
```

**2. `Iceberg_Customers_Writer` Schema:**
```json
{
  "type": "record",
  "name": "customers",
  "fields": [
    { "name": "customer_id", "type": "int" },
    { "name": "name", "type": "string" },
    { "name": "age", "type": "int" },
    { "name": "credit_limit", "type": "double" },
    { "name": "risk_profile", "type": "string" },
    { "name": "created_at", "type": { "type": "long", "logicalType": "timestamp-micros" } }
  ]
}
```

**3. `Iceberg_Merchants_Writer` Schema:**
```json
{
  "type": "record",
  "name": "merchants",
  "fields": [
    { "name": "merchant_id", "type": "int" },
    { "name": "merchant_name", "type": "string" },
    { "name": "category", "type": "string" },
    { "name": "risk_level", "type": "string" },
    { "name": "city", "type": "string" },
    { "name": "created_at", "type": { "type": "long", "logicalType": "timestamp-micros" } }
  ]
}
```

**4. `Iceberg_Accounts_Writer` Schema:**
```json
{
  "type": "record",
  "name": "accounts",
  "fields": [
    { "name": "account_id", "type": "string" },
    { "name": "customer_id", "type": "int" },
    { "name": "account_type", "type": "string" },
    { "name": "balance", "type": "double" },
    { "name": "currency", "type": "string" },
    { "name": "status", "type": "string" },
    { "name": "opened_at", "type": { "type": "long", "logicalType": "timestamp-micros" } }
  ]
}
```

#### **Pipeline 3: The "Actual World" Sync (Dameng -> NiFi -> Lakehouse)**
*Goal: Showcase NiFi's variety by applying different transformations for each dataset then landing as Parquet.*

**Path A: TRANSACTIONS (SQL-Powered Mapping & Type Casting)**
1.  **`QueryDatabaseTable`**:
    *   **Properties**: `Table Name` -> `TRANSACTIONS`; `Maximum-value Columns` -> `TX_ID`.
2.  **`QueryRecord` (Unified SQL Engine)**:
    *   **Properties**: `Record Reader` -> `AvroReader`; `Record Writer` -> `Iceberg_Transactions_Writer`.
    *   **Success Relationship Query**:
    ```sql
    SELECT 
      CAST(TX_ID AS BIGINT) AS tx_id,
      CAST(USER_ID AS INT) AS user_id,
      CAST(MERCHANT_ID AS INT) AS merchant_id,
      CAST(AMOUNT AS DOUBLE) AS amount, 
      CAST(TX_TIME AS TIMESTAMP) AS tx_time,
      STATUS AS status,
      LOCATION AS city
    FROM FLOWFILE
    ```
3.  **`PutIceberg`**:
    *   **Properties**: `Table Name` -> `transactions`; *(Use Common Iceberg Configuration above)*.
    *   **Settings**: Terminate `success` and `failure`.

**Path B: CUSTOMERS (PII Hashing & SQL Transformation)**
1.  **`QueryDatabaseTable`**:
    *   **Properties**: `Table Name` -> `CUSTOMERS`; `Maximum-value Columns` -> `CUSTOMER_ID`.
2.  **`UpdateAttribute` (Governance Tagging)**:
    *   **Properties**: `is_pii` = `true`.
3.  **`UpdateRecord` (PII Masking)**:
    *   **Properties**: `Record Reader` -> `AvroReader`; `Record Writer` -> `JsonRecordSetWriter`.
    *   **Replacement Value Strategy**: `Literal Value`.
    *   *Click '+' and add:* `/NAME` -> `${field.value:replaceFirst('(?s)(.*).{4}$', '$1****')}`.
4.  **`QueryRecord` (Analytical Cast)**:
    *   **Properties**: `Record Reader` -> `JsonTreeReader`; `Record Writer` -> `Iceberg_Customers_Writer`.
    *   **Success Query**:
    ```sql
    SELECT 
      CAST(CUSTOMER_ID AS INT) AS customer_id,
      NAME AS name, 
      CAST(AGE AS INT) AS age,
      CAST(CREDIT_LIMIT AS DOUBLE) AS credit_limit,
      RISK_PROFILE AS risk_profile,
      CAST(CREATED_AT AS TIMESTAMP) AS created_at
    FROM FLOWFILE
    ```
5.  **`PutIceberg`**:
    *   **Properties**: `Table Name` -> `customers`; *(Use Common Iceberg Configuration above)*.

**Path C: MERCHANTS (SQL Transformation)**
1.  **`QueryDatabaseTable`**:
    *   **Properties**: `Table Name` -> `MERCHANTS`; `Maximum-value Columns` -> `MERCHANT_ID`.
2.  **`QueryRecord`**:
    *   **Properties**: `Record Reader` -> `AvroReader`; `Record Writer` -> `Iceberg_Merchants_Writer`.
    *   **Success Query**:
    ```sql
    SELECT 
      CAST(MERCHANT_ID AS INT) AS merchant_id,
      MERCHANT_NAME AS merchant_name,
      CATEGORY AS category, 
      RISK_LEVEL AS risk_level,
      CITY AS city,
      CAST(CREATED_AT AS TIMESTAMP) AS created_at
    FROM FLOWFILE
    ```
3.  **`PutIceberg`**:
    *   **Properties**: `Table Name` -> `merchants`; *(Use Common Iceberg Configuration above)*.

**Path D: ACCOUNTS (SQL Transformation)**
1.  **`QueryDatabaseTable`**:
    *   **Properties**: `Table Name` -> `ACCOUNTS`; `Maximum-value Columns` -> `ACCOUNT_ID`.
2.  **`QueryRecord`**:
    *   **Properties**: `Record Reader` -> `AvroReader`; `Record Writer` -> `Iceberg_Accounts_Writer`.
    *   **Success Query**:
    ```sql
    SELECT 
      CAST(ACCOUNT_ID AS VARCHAR) AS account_id,
      CAST(CUSTOMER_ID AS INT) AS customer_id,
      ACCOUNT_TYPE AS account_type,
      CAST(BALANCE AS DOUBLE) AS balance,
      CURRENCY AS currency,
      STATUS AS status,
      CAST(OPENED_AT AS TIMESTAMP) AS opened_at
    FROM FLOWFILE
    ```
3.  **`PutIceberg`**:
    *   **Properties**: `Table Name` -> `accounts`; *(Use Common Iceberg Configuration above)*.

#### **Final Setup: Iceberg Analytical Tables**
`PutIceberg` requires the target table to exist in the Metastore first. Run these commands in **Impala** or **Hue** before starting the NiFi flow:

```sql
CREATE DATABASE IF NOT EXISTS dameng;

-- 1. Path A: TRANSACTIONS
CREATE TABLE dameng.transactions (
    tx_id BIGINT,
    user_id INT,
    merchant_id INT,
    amount DOUBLE,
    tx_time TIMESTAMP,
    status STRING,
    city STRING 
) STORED AS ICEBERG;

-- 2. Path B: CUSTOMERS
CREATE TABLE dameng.customers (
    customer_id INT,
    name STRING,
    age INT,
    credit_limit DOUBLE,
    risk_profile STRING,
    created_at TIMESTAMP
) STORED AS ICEBERG;

-- 3. Path C: MERCHANTS
CREATE TABLE dameng.merchants (
    merchant_id INT,
    merchant_name STRING,
    category STRING,
    risk_level STRING,
    city STRING,
    created_at TIMESTAMP
) STORED AS ICEBERG;

-- 4. Path D: ACCOUNTS
CREATE TABLE dameng.accounts (
    account_id STRING,
    customer_id INT,
    account_type STRING,
    balance DOUBLE,
    currency STRING,
    status STRING,
    opened_at TIMESTAMP
) STORED AS ICEBERG;
```

#### **4. Troubleshooting Common Validation Errors**

If you see yellow exclamation marks on your processors, here is how to clear them:

*   **Error: "References Parameters but no Parameter Context is set"**
    *   **Fix**: You must link your Parameter Context to the Process Group.
    *   **Steps**: Right-click on the canvas (or your parent Process Group) -> **Configure** -> **Parameters** -> Select `Dameng_Demo_Context` from the dropdown -> **Apply**.
*   **Error: "Relationship 'failure' is not connected and not auto-terminated"**
    *   **Fix**: NiFi requires all relationships to be handled.
    *   **Steps**: Right-click the Processor (e.g., `ReplaceText` or `UpdateAttribute`) -> **Configure** -> **Settings**. Under the **Automatically Terminate Relationships** list, check the box for `failure` (and `success` if you aren't connecting it downstream).
*   **Error: "Command Path is invalid" (For ExecuteStreamCommand)**
    *   **Fix**: Ensure `python3` is in the system path or use the full path (e.g., `/usr/bin/python3`).
1.  **Connection Test**: Run Pipeline 1 to prove Dameng is ready.
2.  **The 'Wowed' Moment**: Start Pipeline 2.
    *   Explain: *"As I start this, NiFi triggers our simulator. The data is intercepted, transformed (renaming 'location' to 'origin_city'), and then routed to TWO places: back into our operational Dameng DB and forward into our Cloudera Lakehouse."*

---

## Phase 3: Visual Analytics (Cloudera Data Visualization)

With Phase 2 landing real-time data into Iceberg, Phase 3 focuses on turning that data into business intelligence using **Cloudera Data Visualization (CDV)**.

#### **1. Data Connection & Dataset Setup**
1.  **Open CDV**: Navigate to the Cloudera Data Visualization interface from your CDP home screen.
2.  **Create Data Connection**:
    *   Go to **Data** -> **Connections**. Click **New Connection**.
    *   **Type**: Select `Impala`.
    *   **Hiveserver2 Host**: Enter your Master Node IP/Hostname.
    *   **Authentication**: Match your CDP environment (e.g., Kerberos).
3.  **Create Dataset**:
    *   Go to **Data** -> **Datasets**. Click **New Dataset**.
    *   Select your connection. **Database**: `dameng`.
    *   **Tables**: Select `transactions`, `customers`, `merchants`, and `accounts`.
    *   Click **Create**. CDV detects the `DOUBLE` and `TIMESTAMP` fields automatically.

#### **2. Dashboard Designs (Step-by-Step)**

**Dashboard 1: Real-Time Fraud Command Center**
*Objective*: Monitor live transaction flows and identify geographic fraud hotspots.

1.  **Visual 1: Live Transaction Monitor (KPI Counter)**
    *   **Type**: `KPI / Metric`.
    *   **Measure**: `Record Count` (Aggregation: **Count**).
2.  **Visual 2: Fraud vs. Approved (Donut Chart)**
    *   **Type**: `Donut Chart`.
    *   **Dimension**: `status` (No aggregation).
    *   **Measure**: `Record Count` (Aggregation: **Count**).
    *   **Styles**: Assign **Red** to `FLAGGED` and **Green** to `COMPLETED`.
3.  **Visual 3: Top 5 Flagged Cities (Horizontal Bar Chart)**
    *   **Type**: `Bar Chart`.
    *   **Dimension**: `city` (No aggregation).
    *   **Measure**: `Record Count` (Aggregation: **Count**).
    *   **Filters**: `status` = 'FLAGGED'.
    *   **Sort**: `Measure Descending`.

**Dashboard 2: Customer Risk 360**
*Objective*: Analyze customer demographics and credit standing.

1.  **Visual 1: Demographic Risk Assessment (Stacked Bar)**
    *   **Type**: `Bar Chart`.
    *   **Dimension (X-Axis)**: `risk_profile`.
    *   **Measure (Y-Axis)**: `Record Count` (Aggregation: **Count**).
2.  **Visual 2: Age vs. Credit Limit (Scatter Plot)**
    *   **Type**: `Scatter Plot`.
    *   **X-Axis**: `age`. (Change from Measure to **Dimension** to see individual points).
    *   **Y-Axis**: `credit_limit`. (Change from Measure to **Dimension**).
    *   **Color**: `risk_profile` (Dimension).
    *   *Tip: Since Age is an integer, treating it as a Dimension tells CDV not to "Sum" all ages together, but to plot each unique age/limit combination.*
3.  **Assemble Dashboard**: Name it "Customer Risk 360".

**Dashboard 3: Merchant & Account Monitoring**
*Objective*: Identify problematic merchant categories and monitor account liquidity.

1.  **Visual 1: Merchant Risk Levels (Pie Chart)**
    *   **Type**: `Pie Chart`.
    *   **Dimension**: `risk_level`.
    *   **Measure**: `Record Count` (Aggregation: **Count**).
2.  **Visual 2: Account Balances by Type (Bar Chart)**
    *   **Type**: `Bar Chart`.
    *   **Dimension (X-Axis)**: `account_type`.
    *   **Measure (Y-Axis)**: `balance` (Change Aggregation to **Average**).
3.  **Assemble Dashboard**: Click **New Dashboard**, name it "Ecosystem Health", and place the visuals.

---

## Phase 4: Advanced AI (CML & GenAI)

This phase turns your Lakehouse data into predictive intelligence using **Cloudera Machine Learning (CML)**.

### 1. CML Project Setup & Lakehouse Security
1.  **Create Project**: 
    *   In CML, click **New Project**.
    *   Name: `Fraud_Detection_Ecosystem`.
    *   Setup: Upload all generators and the two new scripts: `fraud_detection_training.py` and `fraud_model_api.py`.
2.  **Lakehouse Security (SDX Integration)**:
    *   CML sessions automatically inherit your CDP user credentials.
    *   **Governance Proof**: If you apply a PII masking policy in **Apache Ranger** to the `customers` table, the PySpark job in CML will see masked data (e.g., `NAME` as `John****`), demonstrating seamless security from Lakehouse to AI.

### 2. Model Training (CML Experiments)
*Goal: Use PySpark to join Iceberg tables and train a Random Forest classifier.*

1.  **Start a Session**: Python 3.x, Spark Runtime.
2.  **External Connection**: Ensure you have a Connection named `PvCBaseCluster1` configured in CML to provide the Spark Session.
3.  **Run Training**: Run **[fraud_detection_training.py](../scripts/fraud_detection_training.py)**.
    *   *Robust Features*: This script uses dynamic ID discovery to handle key offsets and driver-side collection to prevent executor crashes.
3.  **Monitor Experiments**: CML tracks every run, saving your model accuracy metrics and the resulting `.pkl` artifact for deployment.

### 3. Model Deployment (CML Model APIs)
*Goal: Deploy a production-grade Rest API to scoring transactions in real-time.*

1.  **Go to Models** -> **New Model**.
2.  **Configuration**:
    *   **Name**: `FraudScoringAPI`.
    *   **File**: `scripts/fraud_model_api.py`.
    *   **Function**: `predict`.
    *   **Runtime**: Select a standard Python runtime.
3.  **Deploy**: CML builds a dockerized container and provides a REST endpoint.
4.  **Test Score**:
    *   Input: `{"amount": 25000.0, "age": 45, "credit_limit": 5000.0, "tx_hour": 14}`
    *   Response: `FLAGGED` (due to high amount vs low limit).

### 4. GenAI: The Fraud Explainer
1.  **Mechanism**: Connect your CML project to a Pre-warmed LLM (using Cloudera AI Inference).
2.  **Logic**: Send the result from the `FraudScoringAPI` to the LLM with the prompt: *"Explain why a $25k transaction for a customer with a $5k limit was flagged."*
3.  **Result**: Natural language justification for banking auditors.

---

## Phase 5: Enterprise Governance & Guardrails (SDX)

This phase showcases how the Cloudera Shared Data Experience (SDX) protects and audits the data landed from Dameng.

### 1. Data Lineage & Audit (Apache Atlas)
*Goal: Prove the "Social Security" of your data.*
1.  **Bridging NiFi PII**:
    *   In Phase 2, Path B, you added the attribute `is_pii = true`.
    *   **Atlas Navigation**: Open Atlas and search for `customers`. Find the column `NAME`.
    *   **Tagging**: Click **Add Classification** -> Select `PII`.
    *   *Explanation*: NiFi's `is_pii` attribute is the "Trigger" in your pipeline, but applying the `PII` classification in Atlas is what activates the enterprise-wide security guardrails.
2.  **View Lineage**: Show the graph proving data came from `Dameng (JDBC)` -> `NiFi` -> `Iceberg`.
3.  **Tags**: Apply a `PII` tag to the `user_id` column.

### 2. Dynamic Data Masking (Apache Ranger)
*Goal: Enforce "Need-to-Know" access without changing the data.*
1.  **Open Ranger**: Navigate to Hadoop SQL (Impala) policies.
2.  **Access Policy**: Enable full access for the `admin` user.
3.  **Masking Policy**: 
    *   Target: `dameng.customers` table, `NAME` column.
    *   Condition: If user is in the `analyst` group.
    *   Type: `Partial Mask: show last 4`.
4.  **Verify**: Query the table in Hue as different users to show the real-time masking.

### 3. Iceberg "Time Travel" & Snapshots
*Goal: Perform point-in-time audits of your operational data.*
1.  **History Query**: In Hue/Impala, run:
    ```sql
    DESCRIBE HISTORY dameng.transactions;
    ```
    *This identifies the snapshot IDs generated by NiFi's continuous writes.*
2.  **Time Travel**: Query the table as it existed before a specific fraud spike:
    ```sql
    SELECT * FROM dameng.transactions FOR SYSTEM_TIME AS OF '2026-03-15 10:00:00';
    ```

### 4. Iceberg Branching (Zero-Copy Cloning)
*Goal: Test new models without affecting production analytics.*
1.  **Create Branch**:
    ```sql
    ALTER TABLE dameng.transactions CREATE BRANCH 'dev_test';
    ```
2.  **Benefit**: Your CML dev team can now update data in the `dev_test` branch without affecting the main CDV Dashboard.
