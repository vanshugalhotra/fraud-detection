import random
import string
import time
import requests
from datetime import datetime
from faker import Faker

# Initialize Faker to generate fake data
fake = Faker()

# Base URL of the Flask API
API_URL = 'http://localhost:5000/detect_fraud'

# List of example merchants for the simulation
merchants = ["Amazon", "eBay", "HelpMeFolks", "GambleShop", "BestBuy", "Walmart"]

# List of example job titles
jobs = ["Software Engineer", "Doctor", "Teacher", "Grocery Store Clerk", "Waiter", "Pilot"]

# Generate a random credit card number (dummy, not real)
def generate_cc_num():
    return ''.join(random.choices(string.digits, k=16))

# Generate a random transaction amount between 1 and 5000
def generate_amt():
    return round(random.uniform(1, 5000), 2)

# Generate a random transaction category
def generate_category():
    categories = ["Online Shopping", "Groceries", "Entertainment", "Travel", "Bills", "Gaming"]
    return random.choice(categories)

# Generate a random transaction number
def generate_trans_num():
    return "T" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

# Generate a random date and time for the transaction
def generate_trans_date():
    return fake.date_time_this_year().strftime('%Y-%m-%d %H:%M:%S')

# Generate random transaction data
def generate_transaction():
    transaction = {
        "trans_date_trans_time": generate_trans_date(),
        "cc_num": generate_cc_num(),
        "merchant": random.choice(merchants),
        "category": generate_category(),
        "amt": generate_amt(),
        "first": fake.first_name(),
        "last": fake.last_name(),
        "gender": random.choice(["M", "F"]),
        "street": fake.street_address(),
        "city": fake.city(),
        "state": fake.state(),
        "zip": fake.zipcode(),
        "lat": fake.latitude(),
        "long": fake.longitude(),
        "city_pop": random.randint(5000, 1000000),
        "job": random.choice(jobs),
        "dob": fake.date_of_birth(minimum_age=18, maximum_age=70).strftime('%Y-%m-%d'),
        "trans_num": generate_trans_num(),
        "unix_time": int(time.time()),  # Current Unix timestamp
        "merch_lat": fake.latitude(),
        "merch_long": fake.longitude(),
        "is_fraud": False  # Initially false
    }
    return transaction

# Send transaction data to the Flask API
def send_transaction(transaction):
    response = requests.post(API_URL, json=transaction)
    return response

if __name__ == "__main__":
    print("Transaction Simulator is running...")
    
    while True:
        # Generate a random transaction
        transaction = generate_transaction()
        
        # Send the transaction to the Flask API
        response = send_transaction(transaction)
        
        if response.status_code == 200:
            print(f"Transaction {transaction['trans_num']} sent successfully!")
        else:
            print(f"Failed to send transaction {transaction['trans_num']}: {response.json()}")
        
        # Sleep for a few seconds before sending the next transaction
        time.sleep(random.randint(2, 5))  # Random delay between 2 and 5 seconds
