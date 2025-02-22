import pandas as pd
import numpy as np
import pickle
from imblearn.over_sampling import SMOTE
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, classification_report, precision_recall_curve
import xgboost as xgb

# Load Data
def load_data(train_path):
    df = pd.read_csv(train_path)

    # Feature Engineering: Additional derived features
    df['time_since_last_transaction'] = df.groupby('cc_num')['unix_time'].diff().fillna(0)
    df['distance'] = np.sqrt((df['lat'] - df['merch_lat'])**2 + (df['long'] - df['merch_long'])**2)
    df['amount_per_population'] = df['amt'] / (df['city_pop'] + 1)
    df['log_amt'] = np.log1p(df['amt'])  
    df['transaction_hour'] = (df['unix_time'] // 3600) % 24
    df['day_of_week'] = (df['unix_time'] // (3600 * 24)) % 7
    df['high_amount_flag'] = (df['amt'] > 200).astype(int)

    # Features & Target
    features = ['amt', 'unix_time', 'lat', 'long', 'merch_lat', 'merch_long', 'city_pop', 
                'time_since_last_transaction', 'distance', 'amount_per_population', 'log_amt',
                'transaction_hour', 'day_of_week', 'high_amount_flag']
    target = 'is_fraud'

    # Remove NaNs
    df.dropna(subset=features + [target], inplace=True)

    X = df[features]
    y = df[target]

    return X, y, features

# Train XGBoost Model
def train_xgboost(X_train, y_train):
    model = xgb.XGBClassifier(
        n_estimators=700, 
        learning_rate=0.03, 
        max_depth=8, 
        min_child_weight=2, 
        subsample=0.8, 
        colsample_bytree=0.8,
        gamma=0.2, 
        scale_pos_weight=15,
        use_label_encoder=False, 
        eval_metric="logloss"
    )
    model.fit(X_train, y_train)
    return model

# Load and Process Data
train_path = "../../data/fraudTrain.csv"
X, y, feature_names = load_data(train_path)

# Handle Imbalanced Data with SMOTE
smote = SMOTE(sampling_strategy=0.4, random_state=42)
X_resampled, y_resampled = smote.fit_resample(X, y)

# Split Data
X_train, X_val, y_train, y_val = train_test_split(X_resampled, y_resampled, test_size=0.2, random_state=42)

# Standardize Features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_val_scaled = scaler.transform(X_val)

# Train Model
model = train_xgboost(X_train_scaled, y_train)

# Find Best Threshold
y_val_prob = model.predict_proba(X_val_scaled)[:, 1]
precision, recall, thresholds = precision_recall_curve(y_val, y_val_prob)
f1_scores = 2 * (precision * recall) / (precision + recall + 1e-9)
best_threshold = thresholds[np.argmax(f1_scores)]

# Evaluate Model
y_val_pred = (y_val_prob > best_threshold).astype(int)
f1 = f1_score(y_val, y_val_pred)

# Print Results
print(f"\n🚀 Model Trained with Best F1 Score: {f1:.4f}")
print(f"🔥 Best Threshold: {best_threshold:.4f}")
print("\n📌 Classification Report:\n", classification_report(y_val, y_val_pred))

# Save Model
model_path = "../../data/fraud_model.pkl"
with open(model_path, 'wb') as f:
    pickle.dump({"model": model, "scaler": scaler, "features": feature_names, "best_threshold": best_threshold}, f)

print(f"\n✅ Model saved to {model_path} 🚀")
