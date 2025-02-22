# Real-Time Fraud Detection System

## 🚀 Tagline: "The Scam Stops Here – Be the Sherlock of Transactions"

### 🏆 *Goal:*
Build a system to detect fraudulent transactions in real-time, leveraging machine learning and interpretable AI techniques to provide precise and actionable insights.

---

FRAUD-DETECTION/
├── backend/
│   ├── database/
│   │   ├── _pycache_/
│   │   ├── db_setup.py
│   │   ├── models.py
│   │   └── transactions.db
│   ├── fraud_detection/
│   │   ├── _pycache_/
│   │   ├── ml_model.py
│   │   ├── rule_based.py
│   │   └── instance/
│   ├── model/
│   │   ├── checkF1.py
│   │   ├── evaluate_model.py
│   │   ├── generate_model.py
│   │   └── app.py
│   ├── app.py
│   └── config.py
├── data/
│   ├── fraud_detection_model/
│   ├── fraud_model.pkl
│   ├── fraud_transactions.json
│   ├── fraud.json
│   ├── fraudTest.csv
│   ├── fraudTrain.csv
│   ├── non_fraud_transactions/
│   └── non_fraud.json
├── model/
│   ├── app.py
│   ├── config.py
│   ├── insert_historical_data.py
│   ├── requirements.txt
│   └── test.py
└── README.md


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
git clone https://github.com/your-repo/fraud-detection.git
cd fraud-detection/backend/fraud_detection


2. Install required packages:
bash
pip install -r requirements.txt


3. Set up your data and model files in the `data/` directory.

---

## ⚙ **Usage:**

### 🚨 **Run Real-Time Detection:**
bash
python live_detection.py


### 🧠 **SHAP Explanation:**
bash
python shap_explain.py


### 🟢 **LIME Explanation:**
bash
python lime_explain.py
```

---

## 📊 *Model Interpretability:*

### 🟠 *SHAP (SHapley Additive Explanations):*
- *Global Interpretability:* Feature importance plots.
- *Local Interpretability:* Force plots for single transactions.

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