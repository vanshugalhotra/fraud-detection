import os
import pandas as pd
import pickle
import numpy as np
from imblearn.combine import SMOTETomek
from xgboost import XGBClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import RobustScaler
from sklearn.model_selection import train_test_split

class FraudDetectionEnsemble:
    def __init__(self, train_data_path):
        self.train_data_path = train_data_path
        self.xgb = XGBClassifier(n_estimators=500, max_depth=8, learning_rate=0.05, scale_pos_weight=200, colsample_bytree=0.8, subsample=0.8, random_state=42, early_stopping_rounds=20)
        self.rf = RandomForestClassifier(n_estimators=300, max_depth=12, class_weight="balanced", random_state=42)
        self.mlp = MLPClassifier(hidden_layer_sizes=(128, 64), activation='relu', solver='adam', alpha=0.003, batch_size=128, max_iter=200, random_state=42)
        self.knn = KNeighborsClassifier(n_neighbors=5)
        self.dt = DecisionTreeClassifier(max_depth=10, class_weight="balanced", random_state=42)
        self.lr = LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42)
        self.scaler = RobustScaler()

    def preprocess_data(self):
        df = pd.read_csv(self.train_data_path)
        df['datetime'] = pd.to_datetime(df['unix_time'], unit='s')
        df = df.sort_values(['cc_num', 'datetime'])
        
        df['hour'] = df['datetime'].dt.hour
        df['dayofweek'] = df['datetime'].dt.dayofweek
        df['transaction_distance'] = ((df['lat'] - df['merch_lat'])**2 + (df['long'] - df['merch_long'])**2)**0.5
        
        # Handle missing features
        if 'transaction_count_24h' not in df.columns:
            df['transaction_count_24h'] = 0  # Default value

        if 'hourly_transaction_count' not in df.columns:
            df['hourly_transaction_count'] = 0  # Default value
        
        if 'rolling_avg_amt' not in df.columns:
            df['rolling_avg_amt'] = df.groupby('cc_num')['amt'].transform(lambda x: x.rolling(window=5, min_periods=1).mean())
        
        if 'amount_deviation' not in df.columns:
            Q1 = df.groupby('cc_num')['amt'].transform(lambda x: x.quantile(0.25))
            Q3 = df.groupby('cc_num')['amt'].transform(lambda x: x.quantile(0.75))
            IQR = Q3 - Q1
            df['amount_deviation'] = abs(df['amt'] - df.groupby('cc_num')['amt'].transform('median')) / (IQR + 1)

        df['is_weekend'] = df['dayofweek'].isin([5, 6]).astype(int)
        df['log_amt'] = np.log1p(df['amt'])
        
        features = ['log_amt', 'hour', 'dayofweek', 'transaction_distance', 'city_pop', 'transaction_count_24h', 'hourly_transaction_count', 'rolling_avg_amt', 'amount_deviation', 'is_weekend']
        target = 'is_fraud'
        df.dropna(subset=features + [target], inplace=True)

        X, y = df[features], df[target]
        smote_tomek = SMOTETomek(sampling_strategy=0.3, random_state=42)
        X_resampled, y_resampled = smote_tomek.fit_resample(X, y)

        X_scaled = self.scaler.fit_transform(X_resampled)
        return X_scaled, y_resampled

    def train_and_save_model(self, model_path):
        X, y = self.preprocess_data()
        X_train, X_val, y_train, y_val = train_test_split(X, y, stratify=y, test_size=0.2, random_state=42)
        
        self.xgb.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
        self.rf.fit(X_train, y_train)
        self.mlp.fit(X_train, y_train)
        self.knn.fit(X_train, y_train)
        self.dt.fit(X_train, y_train)
        self.lr.fit(X_train, y_train)
        
        with open(model_path, 'wb') as f:
            pickle.dump({"xgb": self.xgb, "rf": self.rf, "mlp": self.mlp, "knn": self.knn, "dt": self.dt, "lr": self.lr, "scaler": self.scaler}, f)
        print(f"Model saved to `{model_path}`")

if __name__ == "__main__":
    fraud_detector = FraudDetectionEnsemble("../../data/fraudTrain.csv")
    fraud_detector.train_and_save_model("../../data/fraud_model.pkl")
