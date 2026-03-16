import json
import random
import sys
from datetime import datetime

def generate_transaction():
    """Generates a single random transaction record linked to customers and merchants."""
    # Assume 1-50 range for existing users and merchants in the system
    users = range(1, 51)
    merchants = range(1, 101) # More merchants than users
    locations = ['Singapore', 'Kuala Lumpur', 'Jakarta', 'Bangkok', 'Manila']
    statuses = ['COMPLETED', 'PENDING', 'FLAGGED', 'COMPLETED', 'COMPLETED']
    
    # Anomaly detection logic
    is_fraud = random.random() < 0.1
    amount = round(random.uniform(10.0, 500.0), 2)
    if is_fraud:
        amount = round(random.uniform(15000.0, 50000.0), 2)
    
    status = random.choice(statuses)
    if amount > 10000:
        status = 'FLAGGED'

    # Note: tx_id is omitted as it is an IDENTITY column in the DB
    return {
        "user_id": random.choice(users),
        "merchant_id": random.choice(merchants),
        "amount": amount,
        "tx_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "status": status,
        "location": random.choice(locations)
    }

def main():
    # Generate a batch of 5 records per run (NiFi timing controls the flow)
    records = [generate_transaction() for _ in range(5)]
    
    # Print each as a JSON line for PutDatabaseRecord to process in batch
    for r in records:
        print(json.dumps(r))
    
    sys.stdout.flush()

if __name__ == "__main__":
    main()
