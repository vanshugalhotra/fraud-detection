import os
import requests
import random
import time
import json
from dotenv import load_dotenv
from datetime import datetime

speed = 4

load_dotenv()

transaction_limit = int(os.getenv("TRANSACTION_LIMIT", 50))  # Default 50 transactions
time_limit = int(os.getenv("TIME_LIMIT", 60))  # Default 60 seconds
api_url = os.getenv("API_URL", "http://localhost:5000/detect_fraud")

# Load transaction data from JSON files
with open("../data/fraud_transactions.json", "r") as f:
    fraud_data = json.load(f)

with open("../data/non_fraud_transactions.json", "r") as f:
    non_fraud_data = json.load(f)

# Combine and shuffle transactions
all_transactions = fraud_data + non_fraud_data
random.shuffle(all_transactions)

# Ensure transactions are not repeated
used_transactions = set()

def get_unique_transaction():
    while all_transactions:
        transaction = all_transactions.pop()  # Get a random transaction
        if transaction["trans_num"] not in used_transactions:
            used_transactions.add(transaction["trans_num"])
            return transaction
    return None  # No transactions left

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
        
        transaction = get_unique_transaction()
        if transaction is None:
            print("No more unique transactions available!")
            break

        send_transaction(transaction)
        transactions_sent += 1

        time.sleep(random.uniform(1, speed))

    print(f"Simulation complete! {transactions_sent} transactions sent.")

if __name__ == "__main__":
    start_simulation()
