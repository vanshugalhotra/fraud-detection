# generate_model.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report
import joblib

# Load the dataset
data = pd.read_csv("../../data/fraudTrain.csv")

# Preprocessing
# Separate features and target
X = data.drop(columns=["is_fraud"])
y = data["is_fraud"]

# Define categorical and numerical features
categorical_features = ["merchant", "category", "gender", "city", "state", "job"]
numerical_features = ["amt", "lat", "long", "city_pop", "unix_time", "merch_lat", "merch_long"]

# Preprocessing pipeline
preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numerical_features),
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
    ]
)

# Define the model
model = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(class_weight="balanced", random_state=42)),
    ]
)

# Train the model
model.fit(X, y)

# Save the trained model
joblib.dump(model, "../../data/fraud_detection_model.pkl")

print("Model trained and saved as 'fraud_detection_model.pkl'")