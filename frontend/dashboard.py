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

# Auto-refresh every 2 seconds
st_autorefresh(interval=2000, limit=100)

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
    # Ensure 'is_fraud' column exists
    if "is_fraud" not in data.columns:
        st.error("⚠️ 'is_fraud' column is missing from API response!")
        st.write("Received Data:", data.head())  # Debugging step
    else:
        data["is_fraud"] = data["is_fraud"].astype(int)  # Convert is_fraud to integer (0 or 1)

        # Fraud Insights
        fraud_count = data[data["is_fraud"] == 1].shape[0]
        total_transactions = data.shape[0]
        fraud_percentage = (fraud_count / total_transactions) * 100 if total_transactions > 0 else 0
        total_amount = f"₹{data['amt'].sum():,.2f}"  # Total transaction amount

        # 🌟 Metrics Display
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
                background-color: #2c3e50; /* Dark background for contrast */
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
                    Total Transaction Amount <br>
                    <span class='metric-value safe-metric'>{total_amount}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Layout: Table (left) & Pie Chart (right)
        left_col, right_col = st.columns([2, 1])

        with left_col:
            st.markdown("### 📊 Live Transaction Data")

            # Prepare table data
            display_data = data[["first", "last", "state", "amt", "category", "fraud_score"]]
            display_data.rename(columns={
                "first": "Name", 
                "last": "Last Name", 
                "amt": "Amount", 
                "category": "Category", 
                "fraud_score": "Fraud Probability (%)"
            }, inplace=True)

            # Convert fraud_score to percentage with 2 decimal places
            display_data["Fraud Probability (%)"] = (display_data["Fraud Probability (%)"] * 100).round(2).astype(str) + "%"

            # Reverse the index to show latest entries at the top
            display_data = display_data.iloc[::-1]

            # Function to highlight fraud transactions
            def highlight_fraud(row):
                if data.loc[row.name, "is_fraud"] == 1:
                    return ['background-color: #ff9999; color: black'] * len(row)  # Light red for fraud
                else:
                    return ['background-color: #ccffcc; color: black'] * len(row)  # Light green for non-fraud

            # Apply styling
            styled_data = display_data.style.apply(highlight_fraud, axis=1)

            # Custom CSS for table
            st.markdown("""
                <style>
                .stDataFrame {
                    border-radius: 10px;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                }
                .stDataFrame th {
                    background-color: #2c3e50;
                    color: white;
                    font-weight: bold;
                }
                .stDataFrame td {
                    background-color: #34495e;
                    color: white;
                }
                </style>
            """, unsafe_allow_html=True)

            # Display Styled Table
            st.dataframe(
                styled_data,
                width=300,
                height=300,
                use_container_width=True
            )

        with right_col:
            st.markdown("### 📌 Fraud vs Legit Transactions")
            fraud_pie_data = data["is_fraud"].replace({0: "Legit", 1: "Fraud"})
            fig_pie = px.pie(
                names=fraud_pie_data,  
                hole=0.4, 
                color=fraud_pie_data,
                color_discrete_map={"Fraud": "red", "Legit": "green"},
                template='plotly_dark'
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        # Time-Series Line Chart for Transaction Amounts
        st.markdown("### 📈 Transaction Amount Over Time")
        data['trans_date_trans_time'] = pd.to_datetime(data['trans_date_trans_time'])
        fig_line = px.line(
            data, 
            x='trans_date_trans_time', 
            y='amt', 
            color='category', 
            title='Transaction Amount Over Time',
            template='plotly_dark',
            labels={'amt': 'Amount (₹)', 'trans_date_trans_time': 'Time'},
            hover_data={'amt': ':.2f'}
        )
        st.plotly_chart(fig_line, use_container_width=True)

        # Histogram for Transaction Amounts
        st.markdown("### 📊 Transaction Amount Distribution")
        fig_hist = px.histogram(
            data, 
            x='amt', 
            nbins=20, 
            title='Distribution of Transaction Amounts',
            template='plotly_dark',
            labels={'amt': 'Amount (₹)'},
            hover_data={'amt': ':.2f'}
        )
        st.plotly_chart(fig_hist, use_container_width=True)

        # Scatter Plot for Transaction Amount vs Fraud Probability
        st.markdown("### 📊 Transaction Amount vs Fraud Probability")
        fig_scatter = px.scatter(
            data, 
            x='amt', 
            y='fraud_score', 
            color='is_fraud',
            color_discrete_map={0: "green", 1: "red"},
            title='Transaction Amount vs Fraud Probability',
            template='plotly_dark',
            labels={'amt': 'Amount (₹)', 'fraud_score': 'Fraud Probability'},
            hover_data={'amt': ':.2f', 'fraud_score': ':.2f'}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

        # Map for Suspicious Transactions
        st.markdown("### 🗺️ Location of Suspicious Transactions")
        df = data.rename(columns={"lat": "latitude", "long": "longitude"})
        st.map(df[['latitude', 'longitude']])