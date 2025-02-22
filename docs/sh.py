import shap
import joblib
import pandas as pd

# Load model and sample data
model = joblib.load("../data/fraud_detection_model.pkl")
data = pd.read_csv("../data/fraudTrain.csv")

# Define features
categorical_features = ["merchant", "category", "gender", "city", "state", "job"]
numerical_features = ["amt", "lat", "long", "city_pop", "unix_time", "merch_lat", "merch_long"]
X = data[numerical_features + categorical_features]

# Apply preprocessing pipeline
X_transformed = model.named_steps["preprocessor"].transform(X)

# Convert sparse matrix to dense array
if hasattr(X_transformed, "toarray"):
    X_transformed = X_transformed.toarray()

# Initialize SHAP Explainer
explainer = shap.Explainer(model.named_steps["classifier"], X_transformed)
shap_values = explainer(X_transformed)

# Visualize feature importance
shap.summary_plot(shap_values, X_transformed)
