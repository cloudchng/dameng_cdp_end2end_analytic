import json
import random
import sys
from datetime import datetime

def generate_merchant():
    """Generates a synthetic merchant profile."""
    categories = ['RETAIL', 'GROCERY', 'ENTERTAINMENT', 'ONLINE_MKT', 'LUXURY_GOODS', 'GAMING']
    names = {
        'RETAIL': ['Zara', 'H&M', 'Uniqlo'],
        'GROCERY': ['FairPrice', 'Cold Storage', 'Giant'],
        'ENTERTAINMENT': ['Netflix', 'Spotify', 'Disney+'],
        'ONLINE_MKT': ['Amazon', 'Lazada', 'Shopee'],
        'LUXURY_GOODS': ['Rolex', 'LV', 'Gucci'],
        'GAMING': ['Steam', 'PlayStation Store', 'Epic Games']
    }
    category = random.choice(categories)
    
    # merchant_id is omitted as it is an IDENTITY column in the DB
    return {
        "merchant_name": random.choice(names[category]),
        "category": category,
        "risk_level": 'HIGH' if random.random() < 0.1 else 'LOW',
        "city": random.choice(['Singapore', 'Kuala Lumpur', 'Jakarta', 'Bangkok']),
        "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

def main():
    for _ in range(5):
        print(json.dumps(generate_merchant()))
    sys.stdout.flush()

if __name__ == "__main__":
    main()
