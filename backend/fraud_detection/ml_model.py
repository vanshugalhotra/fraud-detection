import pandas as pd
import pickle
import json

def load_model(model_path="../../data/fraud_model.pkl"):
    """Loads the trained fraud detection model & scaler."""
    with open(model_path, 'rb') as f:
        data = pickle.load(f)  # Load dictionary
    return data["model"], data["scaler"]  # Extract model & scaler

def predict_fraud(transaction, model, scaler):
    """Predicts fraud probability for a single transaction."""
    
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

# Load trained model & scaler
model, scaler = load_model("../../data/fraud_model.pkl")  # ✅ Now correctly unpacked

# Get user input
user_input = input("\n🔹 Enter transaction data in JSON format:\n")

try:
    # Convert JSON input to dictionary
    transaction_data = json.loads(user_input)

    # Predict fraud probability
    fraud_probability = predict_fraud(transaction_data, model, scaler)

    # Print fraud probability
    print(f"\n🔹 Fraud Probability: {fraud_probability:.4f}")

except json.JSONDecodeError:
    print("\n⚠ Invalid JSON format! Please enter a valid transaction JSON.")
except KeyError as e:
    print(f"\n⚠ Missing required field: {e}. Please provide all necessary fields.")