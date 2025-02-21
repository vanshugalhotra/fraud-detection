import os
import pandas as pd
import pickle
from imblearn.over_sampling import SMOTE
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

class MLFraudDetection:
    def __init__(self, data_path):
        self.data_path = data_path
        self.model = None
        self.scaler = None  # For scaling features

    def preprocess_data(self):
        """Prepares the dataset for training with SMOTE & Scaling."""
        df = pd.read_csv(self.data_path)

        # Select features & target
        features = ['amt', 'unix_time', 'lat', 'long', 'merch_lat', 'merch_long', 'city_pop']
        target = 'is_fraud'

        # Drop missing values
        df.dropna(subset=features + [target], inplace=True)

        # Extract features (X) and target (y)
        X = df[features]
        y = df[target]

        # Apply SMOTE to balance classes
        smote = SMOTE(sampling_strategy=0.1, random_state=42)  # Increase fraud cases
        X_resampled, y_resampled = smote.fit_resample(X, y)

        # Scale features
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X_resampled)

        return X_scaled, y_resampled

    def train_and_save_model(self, model_path):
        """Trains a model with balanced data and saves it."""
        X, y = self.preprocess_data()

        # Split into training & testing sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

        # Train a tuned RandomForest model
        self.model = RandomForestClassifier(n_estimators=200, random_state=42, class_weight="balanced")
        self.model.fit(X_train, y_train)

        # Evaluate model
        y_pred = self.model.predict(X_test)
        print("\n📌 Model Evaluation:")
        print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
        print(f"Precision: {precision_score(y_test, y_pred):.4f}")
        print(f"Recall: {recall_score(y_test, y_pred):.4f}  🔥")
        print(f"F1 Score: {f1_score(y_test, y_pred):.4f}  🔥")

        # Save the trained model & scaler
        with open(model_path, 'wb') as f:
            pickle.dump({"model": self.model, "scaler": self.scaler}, f)

        print(f"\n✅ Model saved to {model_path}")

# Train & Save Model
if __name__ == "__main__":
    fraud_detector = MLFraudDetection("../../data/fraudTest.csv")  # Load dataset
    fraud_detector.train_and_save_model("../../data/fraud_model.pkl")  # Train & save model