import pickle
import numpy as np
import pandas as pd

def load_model(model_path="../data/fraud_model.pkl"):
    with open(model_path, 'rb') as f:
        data = pickle.load(f)
    return data["xgb"], data["rf"], data["mlp"], data["knn"], data["dt"], data["lr"], data["scaler"]

def preprocess_transaction(transaction, scaler):
    df = pd.DataFrame([transaction])
    
    # Convert date columns
    df['log_amt'] = np.log1p(df['amt'])
    df['hour'] = pd.to_datetime(df['trans_date_trans_time']).dt.hour
    df['dayofweek'] = pd.to_datetime(df['trans_date_trans_time']).dt.dayofweek
    df['is_weekend'] = df['dayofweek'].isin([5, 6]).astype(int)

    # Calculate distance between user location and merchant
    df['transaction_distance'] = ((df['lat'] - df['merch_lat'])**2 + (df['long'] - df['merch_long'])**2)**0.5

    # Handle missing features by estimating them
    df['hourly_transaction_count'] = 1  # Default value for a single transaction
    df['transaction_count_24h'] = 1     # Assume this is the first transaction
    df['rolling_avg_amt'] = df['amt']   # Assume rolling average is just the amount itself

    # Amount deviation (assume no deviation for new transactions)
    df['amount_deviation'] = 0  

    # Keep feature order the same as in training
    features = [
        'log_amt', 'hour', 'dayofweek', 'transaction_distance', 'city_pop', 
        'transaction_count_24h', 'hourly_transaction_count', 'rolling_avg_amt', 
        'amount_deviation', 'is_weekend'
    ]

    X = df[features]
    X_scaled = scaler.transform(X)
    return X_scaled

def predict_fraud(transaction, model_path="../data/fraud_model.pkl"):
    xgb, rf, mlp, knn, dt, lr, scaler = load_model(model_path)
    X_scaled = preprocess_transaction(transaction, scaler)
    
    fraud_score = (xgb.predict_proba(X_scaled)[:, 1] * 0.25 +
                   rf.predict_proba(X_scaled)[:, 1] * 0.2 +
                   mlp.predict_proba(X_scaled)[:, 1] * 0.15 +
                   knn.predict_proba(X_scaled)[:, 1] * 0.15 +
                   dt.predict_proba(X_scaled)[:, 1] * 0.15 +
                   lr.predict_proba(X_scaled)[:, 1] * 0.1)
    
    is_fraud = int(fraud_score > 0.5)
    return {"fraud_score": fraud_score[0], "is_fraud": is_fraud}
