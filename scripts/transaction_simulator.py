import os
import requests
import random
import time
from dotenv import load_dotenv
from faker import Faker
from datetime import datetime

load_dotenv()

transaction_limit = int(os.getenv("TRANSACTION_LIMIT", 50))  # Default 50 transactions
time_limit = int(os.getenv("TIME_LIMIT", 60))  # Default 60 seconds
api_url = os.getenv("API_URL", "http://localhost:5000/detect_fraud")


fake = Faker()

fraud_score = random.uniform(0, 1)  # Random fraud score between 0 and 1
def generate_fake_transaction():
    transaction = {
        "trans_date_trans_time": str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        "cc_num": str(random.randint(4000000000000000, 4999999999999999)),
        "merchant": fake.company(),
        "category": random.choice(["Online Shopping", "Groceries", "Electronics", "Clothing"]),
        "amt": round(float(random.uniform(1, 5000)), 2),  # Ensure it's a float
        "first": fake.first_name(),
        "last": fake.last_name(),
        "gender": random.choice(["M", "F"]),
        "street": fake.street_address(),
        "city": fake.city(),
        "state": fake.state(),
        "zip": random.randint(10000, 99999),
        "lat": float(fake.latitude()),  # Ensure it's a float
        "long": float(fake.longitude()),  # Ensure it's a float
        "city_pop": random.randint(1000, 1000000),
        "job": fake.job(),
        "dob": fake.date_of_birth(minimum_age=18, maximum_age=80).strftime("%Y-%m-%d"),
        "trans_num": fake.uuid4(),
        "unix_time": int(time.time()),
        "merch_lat": float(fake.latitude()),  
        "merch_long": float(fake.longitude()),  
        "is_fraud": random.choice([True, False]),
        "fraud_score": fraud_score  
    }
    return transaction

# Function to send transaction data to the API
def send_transaction(transaction):
    try:
        response = requests.post(api_url, json=transaction)
        if response.status_code == 200:
            print(f"Transaction {transaction['trans_num']} sent successfully!")
        else:
            print(f"Failed to send transaction {transaction['trans_num']}: {response.text}")
    except Exception as e:
        print(f"Error sending transaction {transaction['trans_num']}: {str(e)}")

# Main simulation function
def start_simulation():
    transactions_sent = 0
    start_time = time.time()  # Start time for the simulation

    while transactions_sent < transaction_limit:
        current_time = time.time()

        # Check if the time limit has exceeded
        if current_time - start_time > time_limit:
            print(f"Time limit of {time_limit} seconds reached!")
            break
        
        transaction = generate_fake_transaction() 
        send_transaction(transaction)  
        transactions_sent += 1

        time.sleep(random.uniform(1, 3))  

    print(f"Simulation complete! {transactions_sent} transactions sent.")

if __name__ == "__main__":
    start_simulation()
