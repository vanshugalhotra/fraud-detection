import json
import pickle
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import os


def load_model(model_path="../data/fraud_model.pkl"):
    """Loads the trained fraud detection model and scaler."""
    with open(model_path, 'rb') as f:
        data = pickle.load(f)
    
    if not isinstance(data, dict):
        raise ValueError(f"Loaded data is not a dictionary. Got type: {type(data)}")

    expected_keys = {"model", "scaler", "features", "best_threshold"}
    missing_keys = expected_keys - data.keys()
    if missing_keys:
        raise KeyError(f"Missing keys in loaded model: {missing_keys}")

    return data["model"], data["scaler"], data["features"], data["best_threshold"]


# Load model & scaler
model, scaler, feature_names, best_threshold = load_model()

# === Compute Derived Features ===
def compute_derived_features(transaction):
    """Computes additional features required for prediction."""
    transaction['distance'] = np.sqrt((transaction['lat'] - transaction['merch_lat'])**2 +
                                      (transaction['long'] - transaction['merch_long'])**2)
    transaction['amount_per_population'] = transaction['amt'] / (transaction['city_pop'] + 1)
    transaction['log_amt'] = np.log1p(transaction['amt'])
    transaction['transaction_hour'] = (transaction['unix_time'] // 3600) % 24
    transaction['day_of_week'] = (transaction['unix_time'] // (3600 * 24)) % 7
    transaction['high_amount_flag'] = int(transaction['amt'] > 200)

    # Add a default value for 'time_since_last_transaction'
    transaction['time_since_last_transaction'] = transaction.get('time_since_last_transaction', 0)
    
    return transaction


def predict_fraud(json_input):
    """Predicts fraud probability from JSON input."""
    try:
        if isinstance(json_input, str):  
            transaction = json.loads(json_input)  
        else:  
            transaction = json_input 

        transaction = compute_derived_features(transaction)

        missing_features = [feat for feat in feature_names if feat not in transaction]
        if missing_features:
            return {"error": f"Missing features: {missing_features}"}

        transaction_df = pd.DataFrame([transaction])
        transaction_scaled = scaler.transform(transaction_df[feature_names])

        fraud_probability = model.predict_proba(transaction_scaled)[0][1]
        fraud_label = int(fraud_probability > best_threshold)

        return {
            "fraud_score": float(fraud_probability),
            "is_fraud": fraud_label
        }
    
    except Exception as e:
        return {"error": str(e)}

