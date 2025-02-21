from flask import Flask
from database.db_setup import db

app = Flask(__name__)

# Configure SQLite Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///transactions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db.init_app(app)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    print("✅ Database setup complete!")
