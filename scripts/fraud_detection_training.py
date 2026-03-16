import os
import pandas as pd
import pickle
from pyspark.sql import SparkSession
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
import cml.data_v1 as cmldata

# Sample in-code customization of spark configurations
#from pyspark import SparkContext
#SparkContext.setSystemProperty('spark.executor.cores', '1')
#SparkContext.setSystemProperty('spark.executor.memory', '2g')

CONNECTION_NAME = "PvCBaseCluster1"
conn = cmldata.get_connection(CONNECTION_NAME)
spark = conn.get_spark_session()

# 1. Initialize Spark Session with Iceberg Support
spark = SparkSession.builder \
    .appName("Fraud_Detection_Robust_Pipeline") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.iceberg.spark.SparkSessionCatalog") \
    .config("spark.sql.catalog.spark_catalog.type", "hive") \
    .config("spark.sql.iceberg.handle-timestamp-without-timezone", "true") \
    .config("spark.sql.autoBroadcastJoinThreshold", "20MB") \
    .getOrCreate()

print("--- Step 1: Dynamic Metadata Discovery ---")

try:
    # Dynamically find IDs to ensure the join works even if data is refreshed
    min_tx_res = spark.sql("SELECT MIN(CAST(user_id AS INT)) FROM spark_catalog.dameng.transactions").collect()
    min_cust_res = spark.sql("SELECT MIN(CAST(customer_id AS INT)) FROM spark_catalog.dameng.customers").collect()
    
    min_tx_id = min_tx_res[0][0] if min_tx_res else None
    min_cust_id = min_cust_res[0][0] if min_cust_res else None

    if min_tx_id is None or min_cust_id is None:
        raise ValueError("One or both source tables are empty. Cannot proceed.")

    # Calculate offset dynamically
    dynamic_offset = min_cust_id - min_tx_id
    print(f"Computed Key Offset: {dynamic_offset}")

    # 2. Robust SQL Extraction
    # We cast everything to simple types in SQL to minimize Driver-side overhead
    query = f"""
    SELECT 
        CAST(t.amount AS DOUBLE) as amount, 
        CAST(t.tx_time AS STRING) as tx_time_str, 
        CAST(c.age AS INT) as age, 
        CAST(c.credit_limit AS DOUBLE) as credit_limit, 
        t.status
    FROM spark_catalog.dameng.transactions t
    JOIN spark_catalog.dameng.customers c 
      ON (CAST(t.user_id AS INT) + {dynamic_offset}) = CAST(c.customer_id AS INT)
    """

    # 3. Driver-Safe Data Collection
    # By using .collect() and asDict(), we bypass the 'SerializationProxy' executor crash
    print("Extracting data via Driver-Side collection...")
    rows = spark.sql(query).collect()
    
    # Convert to Pandas immediately
    pdf = pd.DataFrame([r.asDict() for r in rows])

    if pdf.empty:
        print("Warning: Join resulted in 0 rows. Check data overlap.")
    else:
        # 4. Feature Engineering & Pre-processing
        # Fix the unit-less datetime issue for Pandas compatibility
        pdf['tx_time'] = pd.to_datetime(pdf['tx_time_str']).dt.tz_localize(None)
        pdf['tx_hour'] = pdf['tx_time'].dt.hour
        pdf['is_fraud'] = pdf['status'].apply(lambda x: 1 if x == 'FLAGGED' else 0)

        # Select model features
        X = pdf[['amount', 'age', 'credit_limit', 'tx_hour']]
        y = pdf['is_fraud']

        # 5. Model Training (Random Forest)
        print(f"--- Step 2: Training Model on {len(pdf)} rows ---")
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        rf_model = RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42)
        rf_model.fit(X_train, y_train)

        # 6. Evaluation
        print("\n" + "="*40)
        print("FINAL MODEL PERFORMANCE REPORT")
        print("="*40)
        print(classification_report(y_test, rf_model.predict(X_test)))

        # 7. Persistence for CML Model API
        os.makedirs("models", exist_ok=True)
        model_filename = "models/fraud_model.pkl"
        with open(model_filename, "wb") as f:
            pickle.dump(rf_model, f)
            
        print(f"--- Step 3: Success! Model saved to {model_filename} ---")

except Exception as e:
    print(f"Critical Pipeline Failure: {str(e)}")

finally:
    spark.stop()
