import json
import os
import random
from flask import Flask
from database.db_setup import Transaction, db  # Using the original database
from fraud_detection.ml_model import predict_fraud

# Ensure the backend directory exists
os.makedirs("backend", exist_ok=True)

app = Flask(__name__)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///transactions.db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Get only the valid column names from the Transaction model
TRANSACTION_FIELDS = {column.name for column in Transaction.__table__.columns}

def process_and_insert_data():
    try:
        with open("../data/fraud.json") as fraud_file, open("../data/non_fraud.json") as non_fraud_file:
            fraud_data = json.load(fraud_file)
            non_fraud_data = json.load(non_fraud_file)

        all_data = fraud_data + non_fraud_data  # Combine both datasets
        
        # ✅ Shuffle data to mix fraud and non-fraud transactions
        random.shuffle(all_data)

        processed_transactions = []
        total_inserted = 0

        with app.app_context():
            db.create_all()  # Ensure tables exist
            
            for txn in all_data:
                try:
                    fraud_result = predict_fraud(txn)  # Run fraud detection
                    
                    # Add fraud details
                    txn["fraud_score"] = float(fraud_result.get("fraud_score", -1))
                    txn["is_fraud"] = bool(int(fraud_result.get("is_fraud", 0)))

                    # Filter out unwanted fields
                    filtered_txn = {key: value for key, value in txn.items() if key in TRANSACTION_FIELDS}

                    processed_transactions.append(Transaction(**filtered_txn))
                    total_inserted += 1

                except Exception as e:
                    print(f"[ERROR] Skipping transaction {txn.get('trans_num', 'UNKNOWN')} - {str(e)}")

            # Bulk insert processed transactions
            if processed_transactions:
                db.session.bulk_save_objects(processed_transactions)
                db.session.commit()
                print(f"✅ Data processed and inserted successfully! Total records added: {total_inserted}")

    except Exception as e:
        print(f"❌ Error processing transactions: {str(e)}")

if __name__ == "__main__":
    process_and_insert_data()
