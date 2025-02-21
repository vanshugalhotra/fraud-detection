from database.db_setup import db, Transaction
from app import app

with app.app_context():
    transactions = Transaction.query.all()
    print(transactions)
