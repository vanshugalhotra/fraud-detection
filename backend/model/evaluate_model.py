import pandas as pd
import numpy as np
import pickle
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import f1_score, accuracy_score, precision_score, recall_score, classification_report

# === Load Model & Scaler ===
def load_model(model_path):
    """Loads trained model, scaler, feature names, and best threshold from disk."""
    with open(model_path, 'rb') as f:
        data = pickle.load(f)
    return data["model"], data["scaler"], data["features"], data.get("best_threshold", 0.5)

# === Feature Engineering (Must Match Training) ===
def preprocess_data(df, feature_names):
    """Apply the same preprocessing steps used in training."""
    
    df['time_since_last_transaction'] = df.groupby('cc_num')['unix_time'].diff().fillna(0)
    df['distance'] = np.sqrt((df['lat'] - df['merch_lat'])**2 + (df['long'] - df['merch_long'])**2)
    df['amount_per_population'] = df['amt'] / (df['city_pop'] + 1)  # Avoid division by zero
    df['log_amt'] = np.log1p(df['amt'])  # Log transformation to normalize skew
    df['transaction_hour'] = (df['unix_time'] // 3600) % 24  # Extract hour of transaction
    df['day_of_week'] = (df['unix_time'] // (3600 * 24)) % 7  # Extract day of the week
    df['high_amount_flag'] = (df['amt'] > 200).astype(int)  # Flagging high-value transactions

    # Select only the required features
    df = df[feature_names].copy()

    return df

# === Load Test Data ===
def load_test_data(test_path, feature_names):
    """Loads test data and applies preprocessing."""
    df = pd.read_csv(test_path)
    df = preprocess_data(df, feature_names)
    return df

# === Evaluate Model ===
def evaluate_model(model, scaler, X_test, y_test, best_threshold):
    """Evaluates the model on test data and prints performance metrics."""
    
    # Scale the test data using the same scaler
    X_test_scaled = scaler.transform(X_test)

    # Predict probabilities
    y_test_prob = model.predict_proba(X_test_scaled)[:, 1]

    # Apply the best threshold
    y_test_pred = (y_test_prob > best_threshold).astype(int)

    # Calculate Metrics
    f1 = f1_score(y_test, y_test_pred)
    accuracy = accuracy_score(y_test, y_test_pred)
    precision = precision_score(y_test, y_test_pred)
    recall = recall_score(y_test, y_test_pred)

    print("\n🚀 Model Evaluation Results:")
    print(f"🔥 F1 Score: {f1:.4f}")
    print(f"🎯 Accuracy: {accuracy:.4f}")
    print(f"⚡ Precision: {precision:.4f}")
    print(f"🔁 Recall: {recall:.4f}")
    print("\n📌 Classification Report:\n", classification_report(y_test, y_test_pred))

    return y_test_pred, y_test_prob

# === Main Execution ===
if __name__ == "__main__":
    model_path = "../../data/fraud_model.pkl"  # Adjust path as needed
    test_path = "../../data/fraudTest.csv"  # Path to test dataset

    # Load Model, Scaler, and Feature Names
    model, scaler, feature_names, best_threshold = load_model(model_path)

    # Load and Preprocess Test Data
    df_test = pd.read_csv(test_path)
    X_test = preprocess_data(df_test, feature_names)
    y_test = df_test['is_fraud']  # True labels

    # Predict Fraud Cases and Evaluate Model
    y_test_pred, y_test_prob = evaluate_model(model, scaler, X_test, y_test, best_threshold)

    # Save predictions
    df_test['fraud_probability'] = y_test_prob
    df_test['predicted_fraud'] = y_test_pred

    # Save results
    output_path = "../../data/fraud_predictions.csv"
    df_test.to_csv(output_path, index=False)
    
    print(f"\n✅ Predictions saved to {output_path} 🚀")
