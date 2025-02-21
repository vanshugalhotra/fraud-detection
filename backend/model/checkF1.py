import pandas as pd
import pickle
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, roc_curve

def load_model(model_path="../../data/fraud_model.pkl"):
    with open(model_path, 'rb') as f:
        data = pickle.load(f)
    return data["xgb"], data["rf"], data["mlp"], data["knn"], data["dt"], data["lr"], data["scaler"]

def load_test_data(test_data_path, scaler):
    df = pd.read_csv(test_data_path)
    df['datetime'] = pd.to_datetime(df['unix_time'], unit='s')
    df = df.sort_values(['cc_num', 'datetime'])

    df['hour'] = df['datetime'].dt.hour
    df['dayofweek'] = df['datetime'].dt.dayofweek
    df['transaction_distance'] = ((df['lat'] - df['merch_lat'])**2 + (df['long'] - df['merch_long'])**2)**0.5
    df['transaction_count_24h'] = df.groupby('cc_num')['datetime'].diff().dt.total_seconds().lt(86400).groupby(df['cc_num']).cumsum().fillna(0)
    df['hourly_transaction_count'] = df.groupby(['cc_num', 'hour'])['amt'].transform('count').fillna(0)
    df['rolling_avg_amt'] = df.groupby('cc_num')['amt'].transform(lambda x: x.rolling(window=5, min_periods=1).mean()).fillna(0)

    Q1 = df.groupby('cc_num')['amt'].transform(lambda x: x.quantile(0.25)).fillna(0)
    Q3 = df.groupby('cc_num')['amt'].transform(lambda x: x.quantile(0.75)).fillna(0)
    IQR = Q3 - Q1
    df['amount_deviation'] = abs(df['amt'] - df.groupby('cc_num')['amt'].transform('median')) / (IQR + 1)

    df['is_weekend'] = df['dayofweek'].isin([5, 6]).astype(int)
    df['log_amt'] = np.log1p(df['amt'])

    # Ensure all features used in training are present
    features = ['log_amt', 'hour', 'dayofweek', 'transaction_distance', 'city_pop', 
                'transaction_count_24h', 'hourly_transaction_count', 'rolling_avg_amt', 
                'amount_deviation', 'is_weekend']
    target = 'is_fraud'

    df.dropna(subset=features + [target], inplace=True)

    X_test = scaler.transform(df[features])
    y_test = df[target].values
    return X_test, y_test

def evaluate_model(xgb, rf, mlp, knn, dt, lr, X_test, y_test):
    y_pred_probs = (xgb.predict_proba(X_test)[:, 1] * 0.25 +
                    rf.predict_proba(X_test)[:, 1] * 0.2 +
                    mlp.predict_proba(X_test)[:, 1] * 0.15 +
                    knn.predict_proba(X_test)[:, 1] * 0.15 +
                    dt.predict_proba(X_test)[:, 1] * 0.15 +
                    lr.predict_proba(X_test)[:, 1] * 0.1)

    fpr, tpr, thresholds = roc_curve(y_test, y_pred_probs)
    optimal_idx = np.argmax(tpr - fpr)
    threshold = thresholds[optimal_idx]

    y_pred = (y_pred_probs > threshold).astype(int)

    print("\n📌 Model Evaluation on `fraudTest.csv`:")
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print(f"Precision: {precision_score(y_test, y_pred):.4f}")
    print(f"Recall: {recall_score(y_test, y_pred):.4f}")
    print(f"F1 Score: {f1_score(y_test, y_pred):.4f}")
    print("\nClassification Report:\n", classification_report(y_test, y_pred))

if __name__ == "__main__":
    xgb, rf, mlp, knn, dt, lr, scaler = load_model("../../data/fraud_model.pkl")
    X_test, y_test = load_test_data("../../data/fraudTest.csv", scaler)
    evaluate_model(xgb, rf, mlp, knn, dt, lr, X_test, y_test)
