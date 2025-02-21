import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
import time


# Set Streamlit Theme to Dark Mode
st.set_page_config(page_title='FRAUD DETECTION SYSTEM', layout='wide', page_icon='🔍')

# Title
st.markdown("""
    <h1 style='text-align: center;'>🔍 REAL-TIME FRAUD DETECTION DASHBOARD </h1>
    <p style='text-align: center; font-size: 24px;'>“The Scam Stops Here – Be the Sherlock of Transactions”.</p>
""", unsafe_allow_html=True)

# API URL
API_URL = "http://127.0.0.1:5000/transactions"

# Refresh interval (in seconds)
REFRESH_INTERVAL = 5

# Function to Fetch Live Transactions
@st.cache_data(ttl=5)
def fetch_live_transactions():
    try:
        response = requests.get(API_URL, timeout=5)
        response.raise_for_status()
        data = response.json().get("transactions", [])
        return pd.DataFrame(data)
    except requests.RequestException as e:
        st.warning(f"⚠️ API Connection Error: {e}")
        return pd.DataFrame()

data = fetch_live_transactions()
if not data.empty:
    data.columns = data.columns.str.strip()  # Strip column names

    if "is_fraud" not in data.columns:
        st.error("⚠️ 'is_fraud' column is missing from API response!")
        st.write("Received Data:", data.head())  # Debugging step
    else:
        data["is_fraud"] = data["is_fraud"].astype(int)  # Convert is_fraud to integer (0 or 1)

        # Fraud Insights
        fraud_count = data[data["is_fraud"] == 1].shape[0]
        total_transactions = data.shape[0]
        fraud_percentage = (fraud_count / total_transactions) * 100 if total_transactions > 0 else 0
        avg_transaction = f"₹{data['amt'].mean():.2f}"

                # 🌟 Metrics Display
        # Styled Metrics Display
        st.markdown("""
            <style>
            .metrics-container {
            display: flex;
            justify-content: center;
            gap: 60px; /* Space between metrics */
            margin-top: 20px; /* Push it slightly down */
        }
        .metric-box {
            text-align: center;
            font-size: 20px;
            font-weight: bold;
            padding: 15px;
            background-color: #d3d3d3; /* Dark background for contrast */
            border-radius: 10px;
            width: 300px;
            box-shadow: 4px 4px 15px rgba(255, 255, 255, 0.2);
            color: white;
        }
        .metric-value {
            font-size: 30px;
            font-weight: bold;
            color: #ff4d4d; /* Red for fraud transactions */
            display: block;
            margin-top: 5px;
        
        }
        .safe-metric {
            color: #2ecc71; /* Green for safe transactions */
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown(f"""
            <div class='metrics-container'>
                <div class='metric-box'>
                    Total Transactions <br>
                    <span class='metric-value'>{total_transactions}</span>
                </div>
                <div class='metric-box'>
                    Fraudulent Transactions <br>
                    <span class='metric-value'>{fraud_count} ({fraud_percentage:.2f}%)</span>
                </div>
                <div class='metric-box'>
                    Avg Transaction Amount <br>
                    <span class='metric-value safe-metric'>{avg_transaction}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)


        
        

        # Layout: Table (left) & Pie Chart (right)
        left_col, right_col = st.columns([2, 1])

        with left_col:
            st.markdown("### 📊 Live Transaction Data")

            with st.container():
                display_data = data[["first", "last", "state", "amt", "category", "fraud_score"]]
                display_data.rename(columns={
                    "first": "Name", 
                    "last": "Last Name", 
                    "amt": "Amount", 
                    "category": "Category", 
                    "fraud_score": "Fraud Score"
                }, inplace=True)

                # Function to highlight fraud transactions
                def highlight_fraud(row):
                    return ['background-color: #ff9999; color: black' if data.loc[row.name, "is_fraud"] == 1 else 'background-color: #ccffcc; color: black' for _ in row]

                styled_data = display_data.style.apply(highlight_fraud, axis=1)

                # Display Styled Table with fixed height
                st.dataframe(styled_data,width=300,height=300, use_container_width=True)

        with right_col:
            st.markdown("### 📌 Fraud vs Legit Transactions")
            st.markdown("""
                <div style="display: flex; justify-content: center; align-items: center;">
            """, unsafe_allow_html=True)
            
            fraud_pie_data = data["is_fraud"].replace({0: "Legit", 1: "Fraud"})
            fig_pie = px.pie(
                names=fraud_pie_data,  
                hole=0.4, 
                color=fraud_pie_data,
                color_discrete_map={"Fraud": "red", "Legit": "green"},
                template='plotly_dark'
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            

st.subheader("📝 Live Transaction Details")
st.dataframe(data[['trans_date_trans_time', 'merchant', 'category', 'amt', 'fraud_score', 'is_fraud']])

# Bar Graph for Recent Transactions
st.subheader("📊 Transaction Trends")
fig = px.bar(data, x='trans_date_trans_time', y='amt', color='category', title='Recent Transaction Amounts')
st.plotly_chart(fig)

# Map for Suspicious Transactions
st.subheader("🗺️ Location of Suspicious Transactions")
df = data.rename(columns={"lat": "latitude", "long": "longitude"})
st.map(df[['latitude', 'longitude']])

# Auto Refresh Every 5 seconds
time.sleep(2)

