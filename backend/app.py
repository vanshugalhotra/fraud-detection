from flask import Flask, request, jsonify
from database.db_setup import db, Transaction
from fraud_detection.rule_based import detect_fraud  # Import the rule-based fraud detection function

app = Flask(__name__)

# Configure SQLite Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///transactions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

@app.route('/detect_fraud', methods=['POST'])
def detect_fraud_endpoint():
    data = request.get_json()

    try:
        # Calculate fraud score using the rule-based approach
        fraud_score = detect_fraud(data)  # Using the rule-based function to calculate fraud score

        # Prepare transaction data to store in the database
        transaction = Transaction(
            trans_date_trans_time=data['trans_date_trans_time'],
            cc_num=data['cc_num'],
            merchant=data['merchant'],
            category=data['category'],
            amt=data['amt'],
            first=data['first'],
            last=data['last'],
            gender=data['gender'],
            street=data['street'],
            city=data['city'],
            state=data['state'],
            zip=data['zip'],
            lat=data['lat'],
            long=data['long'],
            city_pop=data['city_pop'],
            job=data['job'],
            dob=data['dob'],
            trans_num=data['trans_num'],
            unix_time=data['unix_time'],
            merch_lat=data['merch_lat'],
            merch_long=data['merch_long'],
            is_fraud=data['is_fraud'],
            fraud_score=fraud_score  # Add the calculated fraud score
        )

        # Add the transaction object to the session and commit to save in the database
        db.session.add(transaction)
        db.session.commit()

        return jsonify({"message": "Transaction received and added successfully!", "fraud_score": fraud_score}), 200

    except Exception as e:
        return jsonify({"message": "Failed to process transaction", "error": str(e)}), 400

    
@app.route('/clear_db', methods=['POST'])
def clear_db():
    try:
        # Delete all transactions from the database
        db.session.query(Transaction).delete()
        db.session.commit()
        return jsonify({"message": "All transactions cleared successfully!"}), 200
    except Exception as e:
        return jsonify({"message": "Failed to clear database", "error": str(e)}), 400


# Create the tables in the database (if they don't exist)
with app.app_context():
    print("Creating database......")
    db.create_all()  # Create tables if they don't exist


if __name__ == '__main__':
    app.run(debug=True) 

print("✅ Database setup complete!")
