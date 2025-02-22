from flask import Flask, request, jsonify
from database.db_setup import db, Transaction
from fraud_detection.ml_model import predict_fraud
import traceback

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
        fraud_result = predict_fraud(data)
        fraud_score = float(fraud_result["fraud_score"])  # Convert to float
        is_fraud = int(fraud_result["is_fraud"])  # Convert to int
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
            is_fraud=is_fraud,
            fraud_score=fraud_score  # Add the calculated fraud score
        )

        # Add the transaction object to the session and commit to save in the database
        db.session.add(transaction)
        db.session.commit()

        return jsonify({"message": "Transaction received and added successfully!", "fraud_score": fraud_score}), 200

    except Exception as e:
        # Capture the full traceback
        error_traceback = traceback.format_exc()
        return jsonify({
            "message": "Failed to process transaction",
            "error": str(e),
            "traceback": error_traceback  # Include the full traceback in the response
        }), 400

    
@app.route('/clear_db', methods=['POST'])
def clear_db():
    try:
        # Delete all transactions from the database
        db.session.query(Transaction).delete()
        db.session.commit()
        return jsonify({"message": "All transactions cleared successfully!"}), 200
    except Exception as e:
        return jsonify({"message": "Failed to clear database", "error": str(e)}), 400



@app.route('/transactions', methods=['GET'])
def get_transactions():
    """
    Fetch transactions from the database and return as JSON.
    """
    try:
        # Fetch latest 50 transactions (modify as needed)
        transactions = Transaction.query.order_by(Transaction.trans_date_trans_time.desc()).limit(1000).all()
        
        # Convert transactions to a list of dictionaries
        transactions_list = [
            {
                "trans_date_trans_time": t.trans_date_trans_time,
                "cc_num": t.cc_num,
                "merchant": t.merchant,
                "category": t.category,
                "amt": t.amt,
                "first": t.first,
                "last": t.last,
                "gender": t.gender,
                "street": t.street,
                "city": t.city,
                "state": t.state,
                "zip": t.zip,
                "lat": t.lat,
                "long": t.long,
                "city_pop": t.city_pop,
                "job": t.job,
                "dob": t.dob,
                "trans_num": t.trans_num,
                "unix_time": t.unix_time,
                "merch_lat": t.merch_lat,
                "merch_long": t.merch_long,
                "fraud_score": t.fraud_score,
                "is_fraud": t.is_fraud,
            }
            for t in transactions
        ]

        return jsonify({"transactions": transactions_list}), 200

    except Exception as e:
        return jsonify({"message": "Failed to fetch transactions", "error": str(e)}), 500


# Create the tables in the database (if they don't exist)
with app.app_context():
    print("Creating database......")
    db.create_all()  # Create tables if they don't exist


if __name__ == '__main__':
    app.run(debug=True) 

print("✅ Database setup complete!")
