# Real-Time Fraud Detection System

## 🚀 Tagline: "The Scam Stops Here – Be the Sherlock of Transactions"

### 🏆 *Goal:*
Build a system to detect fraudulent transactions in real-time, leveraging machine learning and interpretable AI techniques to provide precise and actionable insights.

---

![Project Structure](https://raw.githubusercontent.com/vanshugalhotra/fraud-detection/main/structure.png)



---

## ⚡ **Key Features:**
- **Real-Time Anomaly Detection:** Process live transaction data and flag suspicious activities.
- **ML Models:** Implemented models like Random Forest, XGBoost, and Logistic Regression.
- **Model Interpretability:** Explainable AI with **SHAP** and **LIME**.
- **Visualization:** Dynamic charts for live fraud alerts.

---

## 🔧 **Installation:**
1. Clone the repository:
bash
https://github.com/vanshugalhotra/fraud-detection

    - execute ```setup.sh```


2. Install required packages:

pip install -r requirements.txt


3. Set up your data and model files in the `data/` directory.

---

## ⚙ **Usage:**

### 🚨 **Run Real-Time Detection:**
bash
python live_detection.py


### 🧠 **SHAP Explanation:**
```
python shap_explain.py
```

### 🟢 **LIME Explanation:**
```
python lime_explain.py
```

---

## 📊 *Model Interpretability:*

### 🟠 *SHAP (SHapley Additive Explanations):*
- *Global Interpretability:* Feature importance plots.
- *Local Interpretability:* Force plots for single transactions.

## SHAP Analysis
![SHAP Analysis](https://raw.githubusercontent.com/vanshugalhotra/fraud-detection/main/shap.png)

### 🟢 *LIME (Local Interpretable Model-Agnostic Explanations):*
- Generates local explanations for specific instances.
- Highlights the most influential features for a fraud prediction.

---

## 🏅 *Evaluation Metrics:*
- *Accuracy*
- *Precision / Recall*
- *F1-Score*
- *AUC-ROC Curve*

---

## 📚 *References:*
- [Kaggle Credit Card Fraud Dataset](https://www.kaggle.com/datasets)
- [PCI DSS Guidelines](https://www.pcisecuritystandards.org)
- [Stripe API Docs](https://stripe.com/docs/api)

---

## 👩‍💻 *Contributing:*
Feel free to fork this repository and submit a pull request. Let’s fight fraud together!

---