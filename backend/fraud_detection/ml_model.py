import pandas as pd
import pickle
import json

def load_model(model_path="../data/fraud_model.pkl"):
    """Loads the trained fraud detection model & scaler."""
    with open(model_path, 'rb') as f:
        data = pickle.load(f)  # Load dictionary
    return data["model"], data["scaler"]  # Extract model & scaler

def predict_fraud(transaction):
    """Predicts fraud probability for a single transaction."""
    
    model, scaler = load_model("../data/fraud_model.pkl")
    # Define the required features for prediction
    required_features = ['amt', 'unix_time', 'lat', 'long', 'merch_lat', 'merch_long', 'city_pop']
    
    # Extract only the required features
    filtered_transaction = {key: transaction[key] for key in required_features}
    
    # Convert transaction to DataFrame & extract features
    transaction_df = pd.DataFrame([filtered_transaction])

    # Scale input data
    transaction_scaled = scaler.transform(transaction_df)

    # Predict fraud probability
    fraud_probability = model.predict_proba(transaction_scaled)[0][1]

    return fraud_probability
