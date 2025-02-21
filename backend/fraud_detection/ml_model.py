import joblib
import pandas as pd

def load_model(model_path="../data/fraud_detection_model.pkl"):
    """
    Load the trained fraud detection model.
    """
    return joblib.load(model_path)

def preprocess_transaction(transaction, model):
    """
    Preprocess the transaction data using the same pipeline as training.
    """
    # Convert transaction to DataFrame
    df = pd.DataFrame([transaction])

    # Ensure all required features exist
    categorical_features = ["merchant", "category", "gender", "city", "state", "job"]
    numerical_features = ["amt", "lat", "long", "city_pop", "unix_time", "merch_lat", "merch_long"]
    
    # Select only necessary features
    df = df[numerical_features + categorical_features]
    
    # Apply the preprocessing pipeline from the trained model
    X_processed = model.named_steps["preprocessor"].transform(df)

    return X_processed

def predict_fraud(transaction, model_path="../data/fraud_detection_model.pkl"):
    """
    Predict whether a transaction is fraudulent.
    Returns a fraud score and a fraud decision (0 or 1).
    """
    try:
        # Load the trained model
        model = load_model(model_path)
        
        # Preprocess the transaction
        X = preprocess_transaction(transaction, model)
        
        # Predict fraud probability
        fraud_score = model.named_steps["classifier"].predict_proba(X)[:, 1][0]  # Probability of fraud

        # Determine if the transaction is fraudulent (threshold: 0.5)
        is_fraud = int(fraud_score > 0.5)

        return {"fraud_score": float(fraud_score), "is_fraud": is_fraud}
    
    except Exception as e:
        return {
            "error": str(e),
            "message": "Failed to process transaction"
        }
