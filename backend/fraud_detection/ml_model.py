import pickle
import numpy as np
import pandas as pd

def load_model(model_path="../../data/fraud_model.pkl"):
    with open(model_path, 'rb') as f:
        data = pickle.load(f)
    return data["xgb"], data["rf"], data["mlp"], data["knn"], data["dt"], data["lr"], data["scaler"]

def preprocess_transaction(transaction, scaler):
    df = pd.DataFrame([transaction])
    df['log_amt'] = np.log1p(df['amt'])
    df['hour'] = pd.to_datetime(df['trans_date_trans_time']).dt.hour
    df['dayofweek'] = pd.to_datetime(df['trans_date_trans_time']).dt.dayofweek
    df['transaction_distance'] = ((df['lat'] - df['merch_lat'])**2 + (df['long'] - df['merch_long'])**2)**0.5
    df['is_weekend'] = df['dayofweek'].isin([5, 6]).astype(int)
    
    features = ['log_amt', 'hour', 'dayofweek', 'transaction_distance', 'city_pop', 'is_weekend']
    X = df[features]
    X_scaled = scaler.transform(X)
    return X_scaled

def predict_fraud(transaction, model_path="../../data/fraud_model.pkl"):
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