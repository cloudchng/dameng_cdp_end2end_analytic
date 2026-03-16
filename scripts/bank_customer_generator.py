import json
import random
import sys
from datetime import datetime

def generate_customer():
    """Generates a synthetic customer profile with high name variety."""
    first_names = ['James', 'Mary', 'Robert', 'Patricia', 'John', 'Jennifer', 'Michael', 'Linda', 'William', 'Elizabeth']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
    risk_profiles = ['LOW', 'MEDIUM', 'HIGH']
    
    full_name = f"{random.choice(first_names)} {random.choice(last_names)}"
    
    # customer_id is omitted as it is an IDENTITY column in the DB
    return {
        "name": full_name,
        "age": random.randint(18, 75),
        "credit_limit": random.choice([5000, 10000, 25000, 50000, 100000]),
        "risk_profile": random.choice(risk_profiles),
        "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

def main():
    # 5 records per run
    for _ in range(5):
        print(json.dumps(generate_customer()))
    sys.stdout.flush()

if __name__ == "__main__":
    main()
