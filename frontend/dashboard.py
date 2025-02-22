import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from streamlit_autorefresh import st_autorefresh
from datetime import datetime

# Set Streamlit Theme to Dark Mode
st.set_page_config(page_title='FRAUD DETECTION SYSTEM', layout='wide', page_icon='🔍')

# Title
st.markdown("""
    <h1 style='text-align: center;'>🔍 REAL-TIME FRAUD DETECTION DASHBOARD </h1>
    <p style='text-align: center; font-size: 24px;'>“The Scam Stops Here – Be the Sherlock of Transactions”.</p>
""", unsafe_allow_html=True)

# API URL
API_URL = "http://127.0.0.1:5000/transactions"

# Auto-refresh every 1 second
st_autorefresh(interval=1000)

# Initialize session state for transactions data
if 'transactions_data' not in st.session_state:
    st.session_state.transactions_data = pd.DataFrame()

# Function to Fetch Live Transactions
def fetch_live_transactions():
    try:
        response = requests.get(API_URL, timeout=5)
        response.raise_for_status()
        data = response.json().get("transactions", [])
        return pd.DataFrame(data)
    except requests.RequestException as e:
        st.warning(f"⚠️ API Connection Error: {e}")
        return pd.DataFrame()

# Fetch data
data = fetch_live_transactions()

if not data.empty:
    if "is_fraud" not in data.columns:
        st.error("⚠️ 'is_fraud' column is missing from API response!")
        st.write("Received Data:", data.head())
    else:
        data["is_fraud"] = data["is_fraud"].astype(int)
        data.reset_index(drop=True, inplace=True)
        data.index += 1

        # Append only new transactions to session state
        if not st.session_state.transactions_data.empty:
            # Identify new transactions by comparing with existing data
            new_transactions = data[~data["trans_num"].isin(st.session_state.transactions_data["trans_num"])]
        else:
            new_transactions = data  # First run, all transactions are new

        # Append new transactions to session state
        st.session_state.transactions_data = pd.concat([st.session_state.transactions_data, new_transactions], ignore_index=True)

        # Fraud Insights
        fraud_count = st.session_state.transactions_data[st.session_state.transactions_data["is_fraud"] == 1].shape[0]
        total_transactions = st.session_state.transactions_data.shape[0]
        fraud_percentage = (fraud_count / total_transactions) * 100 if total_transactions > 0 else 0
        total_amount = f"₹{st.session_state.transactions_data['amt'].sum():,.2f}"

        # 🌟 Metrics Display
        st.markdown(f"""
            <div style='display: flex; justify-content: center; gap: 60px; margin-top: 20px;'>
                <div style='text-align: center; font-size: 20px; font-weight: bold; padding: 15px; background-color: #2c3e50; border-radius: 10px; width: 300px; box-shadow: 4px 4px 15px rgba(255, 255, 255, 0.2); color: white;'>
                    Total Transactions <br>
                    <span style='font-size: 30px; font-weight: bold; color: #ff4d4d;'>{total_transactions}</span>
                </div>
                <div style='text-align: center; font-size: 20px; font-weight: bold; padding: 15px; background-color: #2c3e50; border-radius: 10px; width: 300px; box-shadow: 4px 4px 15px rgba(255, 255, 255, 0.2); color: white;'>
                    Fraudulent Transactions <br>
                    <span style='font-size: 30px; font-weight: bold; color: #ff4d4d;'>{fraud_count} ({fraud_percentage:.2f}%)</span>
                </div>
                <div style='text-align: center; font-size: 20px; font-weight: bold; padding: 15px; background-color: #2c3e50; border-radius: 10px; width: 300px; box-shadow: 4px 4px 15px rgba(255, 255, 255, 0.2); color: white;'>
                    Total Transaction Amount <br>
                    <span style='font-size: 30px; font-weight: bold; color: #2ecc71;'>{total_amount}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Layout: Table (left) & Pie Chart (right)
        left_col, right_col = st.columns([2, 1])

        with left_col:
            st.markdown("### 📊 Live Transaction Data")
            display_data = st.session_state.transactions_data.iloc[::-1][["first", "last", "state", "amt", "category", "fraud_score"]]
            display_data.rename(columns={"first": "Name", "last": "Last Name", "amt": "Amount", "category": "Category", "fraud_score": "Fraud Probability (%)"}, inplace=True)
            display_data["Fraud Probability (%)"] = (display_data["Fraud Probability (%)"] * 100).round(2).astype(str) + "%"
            st.dataframe(display_data, width=800, height=400)

        with right_col:
            st.markdown("### 📌 Fraud vs Legit Transactions")
            fraud_pie_data = st.session_state.transactions_data["is_fraud"].replace({0: "Legit", 1: "Fraud"})
            fig_pie = px.pie(names=fraud_pie_data, hole=0.4, color=fraud_pie_data, color_discrete_map={"Fraud": "red", "Legit": "green"}, template='plotly_dark')
            st.plotly_chart(fig_pie, use_container_width=True)

        # Time-Series Line Chart for Transaction Amounts
        st.markdown("### 📈 Transaction Amount Over Time")
        st.session_state.transactions_data['trans_date_trans_time'] = pd.to_datetime(st.session_state.transactions_data['trans_date_trans_time'])
        fig_line = px.line(st.session_state.transactions_data, x='trans_date_trans_time', y='amt', color='category', template='plotly_dark')
        st.plotly_chart(fig_line, use_container_width=True)

        # Histogram for Transaction Amounts
        st.markdown("### 📊 Transaction Amount Distribution")
        fig_hist = px.histogram(st.session_state.transactions_data, x='amt', nbins=20, template='plotly_dark')
        st.plotly_chart(fig_hist, use_container_width=True)

        # Scatter Plot for Transaction Amount vs Fraud Probability
        st.markdown("### 📊 Transaction Amount vs Fraud Probability")
        fig_scatter = px.scatter(st.session_state.transactions_data, x='amt', y='fraud_score', color='is_fraud', color_discrete_map={0: "green", 1: "red"}, template='plotly_dark')
        st.plotly_chart(fig_scatter, use_container_width=True)

        # Map for Suspicious Transactions
        st.markdown("### 🗺️ Location of Suspicious Transactions")
        df = st.session_state.transactions_data.rename(columns={"lat": "latitude", "long": "longitude"})
        st.map(df[['latitude', 'longitude']])