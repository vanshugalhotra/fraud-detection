import lime
import lime.lime_tabular

# Initialize LIME Explainer
explainer = lime.lime_tabular.LimeTabularExplainer(
    X_transformed,
    mode="classification",
    feature_names=numerical_features + list(model.named_steps["preprocessor"].named_transformers_["cat"].get_feature_names_out()),
    class_names=["Not Fraud", "Fraud"],
    discretize_continuous=True
)

# Explain a single instance
idx = 0  # Index of a sample transaction
explanation = explainer.explain_instance(
    X_transformed[idx],
    model.named_steps["classifier"].predict_proba
)

# Show explanation
explanation.show_in_notebook()