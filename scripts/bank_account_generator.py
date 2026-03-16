import json
import random
import sys
import time
from datetime import datetime

def generate_account():
    """Generates a synthetic bank account linked to a predicted customer range."""
    # Since customer_id is IDENTITY 1,1 in DB, we target the first batch of customers
    cust_id = random.randint(1, 50)
    
    # Unique ID generation for account_id (VARCHAR Primary Key)
    # Using timestamp + random to ensure 0 duplicates during the demo
    unique_id = f"ACC-{int(time.time() * 1000)}-{random.randint(10, 99)}"
    
    # Logical proportions for currency and status
    currencies = ['SGD'] * 7 + ['USD'] * 2 + ['MYR'] * 1
    statuses = ['ACTIVE'] * 8 + ['INACTIVE'] * 1 + ['DORMANT'] * 1
    
    # Rare 'FROZEN' status for fraud demo potential
    if random.random() < 0.02:
        status = 'FROZEN'
    else:
        status = random.choice(statuses)

    return {
        "account_id": unique_id,
        "customer_id": cust_id,
        "account_type": random.choice(['SAVINGS', 'CHECKING', 'CREDIT']),
        "balance": round(random.uniform(500.0, 50000.0), 2),
        "currency": random.choice(currencies),
        "status": status,
        "opened_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

def main():
    for _ in range(5):
        print(json.dumps(generate_account()))
    sys.stdout.flush()

if __name__ == "__main__":
    main()
