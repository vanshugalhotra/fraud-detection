from flask_sqlalchemy import SQLAlchemy

# Initialize SQLAlchemy
db = SQLAlchemy()

# Define Transaction Model
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Auto-incremented ID
    trans_date_trans_time = db.Column(db.String, nullable=False)
    cc_num = db.Column(db.String, nullable=False)
    merchant = db.Column(db.String, nullable=False)
    category = db.Column(db.String, nullable=False)
    amt = db.Column(db.Float, nullable=False)
    first = db.Column(db.String, nullable=False)
    last = db.Column(db.String, nullable=False)
    gender = db.Column(db.String, nullable=False)
    street = db.Column(db.String, nullable=False)
    city = db.Column(db.String, nullable=False)
    state = db.Column(db.String, nullable=False)
    zip = db.Column(db.Integer, nullable=False)
    lat = db.Column(db.Float, nullable=False)
    long = db.Column(db.Float, nullable=False)
    city_pop = db.Column(db.Integer, nullable=False)
    job = db.Column(db.String, nullable=False)
    dob = db.Column(db.String, nullable=False)
    trans_num = db.Column(db.String, nullable=False, unique=True)
    unix_time = db.Column(db.Integer, nullable=False)
    merch_lat = db.Column(db.Float, nullable=False)
    merch_long = db.Column(db.Float, nullable=False)
    is_fraud = db.Column(db.Boolean, nullable=False)  # Fraud label (True/False)

    def __repr__(self):
        return f"<Transaction {self.trans_num} - Fraud: {self.is_fraud}>"
