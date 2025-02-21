import pandas as pd
import joblib
from sklearn.metrics import precision_score, recall_score, f1_score

# Load the trained model
model = joblib.load("../../data/fraud_detection_model.pkl")

# Load the test dataset
test_data = pd.read_csv("../../data/fraudTest.csv")

# Separate features and target
X_test = test_data.drop(columns=["is_fraud"])
y_test = test_data["is_fraud"]

# Make predictions
y_pred = model.predict(X_test)

# Calculate metrics
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

# Print the results
print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
print(f"F1-Score: {f1:.4f}")