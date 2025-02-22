import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import random
from streamlit_autorefresh import st_autorefresh
from datetime import datetime
from streamlit_echarts import st_echarts 

st.set_page_config(page_title='FRAUD DETECTION SYSTEM', layout='wide', page_icon='🔍')


st.markdown("### Team: Ustaad JI")
st.markdown("""
    <h1 style='text-align: center;'>🔍 REAL-TIME FRAUD DETECTION DASHBOARD </h1>
    <p style='text-align: center; font-size: 24px;'>“The Scam Stops Here – Be the Sherlock of Transactions”.</p>
""", unsafe_allow_html=True)


API_URL = "http://127.0.0.1:5000/transactions"

st_autorefresh(interval=1000)

if 'transactions_data' not in st.session_state:
    st.session_state.transactions_data = pd.DataFrame()


if 'scan_data' not in st.session_state:
    st.session_state.scan_data = {
        "angles": [i * (360 / 8) for i in range(8)],  
        "pulses": [],  
        "current_angle": 0  
    }
    
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

        # Ensure 'trans_date_trans_time' is a datetime column
        st.session_state.transactions_data['trans_date_trans_time'] = pd.to_datetime(
            st.session_state.transactions_data['trans_date_trans_time'],
            format='mixed',  # Handle mixed datetime formats
            errors='coerce'  # Coerce invalid parsing to NaT (Not a Time)
        )

        # Drop rows where 'trans_date_trans_time' is NaT (invalid datetime values)
        st.session_state.transactions_data = st.session_state.transactions_data.dropna(subset=['trans_date_trans_time'])

        # Extract hour and day of the week
        st.session_state.transactions_data['hour'] = st.session_state.transactions_data['trans_date_trans_time'].dt.hour
        st.session_state.transactions_data['day_of_week'] = st.session_state.transactions_data['trans_date_trans_time'].dt.day_name()

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

    
        st.markdown("###")
        st.markdown("###")
        # Layout: Table (left) & Radar (right)
        left_col, right_col = st.columns([2, 1])

        with left_col:
            st.markdown("### 📊 Live Transaction Data")
            display_data = st.session_state.transactions_data.iloc[::-1][["first", "last", "state", "amt", "category", "fraud_score", "is_fraud"]]
            display_data.rename(columns={"first": "Name", "last": "Last Name", "amt": "Amount", "category": "Category", "fraud_score": "Fraud Probability (%)"}, inplace=True)
            display_data["Fraud Probability (%)"] = (display_data["Fraud Probability (%)"] * 100).round(2).astype(str) + "%"

            # Function to highlight fraud transactions
            def highlight_fraud(row):
                if row["is_fraud"] == 1:
                    return ['background-color: #ff9999; color: black'] * len(row)  # Light red for fraud
                else:
                    return ['background-color: #ccffcc; color: black'] * len(row)  # Light green for non-fraud

            # Apply styling
            styled_data = display_data.style.apply(highlight_fraud, axis=1)

            # Drop the 'is_fraud' column before displaying the table
            styled_data = styled_data.hide(axis="index").hide(axis="columns", subset=["is_fraud"])

            # Display Styled Table
            st.dataframe(
                styled_data,
                width=800,
                height=400,
                use_container_width=True
            )

        with right_col:
            st.markdown("### 📡 Transaction Scanning Radar")

            # Update radar data with new transactions
            for _, row in new_transactions.iterrows():
                # Add a pulse for the new transaction
                st.session_state.scan_data['pulses'].append({
                    "radius": row['amt'],  # Use transaction amount as radius
                    "fraud": row['is_fraud'],  # Fraud status (0 or 1)
                    "angle": st.session_state.scan_data['current_angle'],  # Current scanning angle
                    "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3]  # Timestamp
                })

                # Update scanning angle
                st.session_state.scan_data['current_angle'] = (st.session_state.scan_data['current_angle'] + 10) % 360

            # Keep only the last 15 pulses
            st.session_state.scan_data['pulses'] = st.session_state.scan_data['pulses'][-15:]

            # Radar Graph Configuration
            radar_options = {
                "backgroundColor": "#1e1e1e",  # Dark background
                "polar": {
                    "center": ["50%", "50%"],  # Center the radar
                    "radius": "80%"  # Radius of the radar
                },
                "angleAxis": {
                    "show": False,  # Hide angle axis labels
                    "min": 0,
                    "max": 360,
                    "startAngle": st.session_state.scan_data['current_angle']  # Start angle for rotation
                },
                "radiusAxis": {
                    "show": False,  # Hide radius axis labels
                    "min": 0,
                    "max": 250  # Maximum radius value
                },
                "series": [
                    # Base radar grid
                    {
                        "type": "line",
                        "data": [[200, angle] for angle in st.session_state.scan_data['angles']],  # Grid lines
                        "coordinateSystem": "polar",
                        "lineStyle": {
                            "color": "#00ffaa33",  # Light green grid lines
                            "width": 1
                        },
                        "symbol": "none"  # No symbols on grid lines
                    },
                    # Scanning line
                    {
                        "type": "line",
                        "coordinateSystem": "polar",
                        "data": [
                            [0, st.session_state.scan_data['current_angle']],  # Start of scanning line
                            [250, st.session_state.scan_data['current_angle']]  # End of scanning line
                        ],
                        "lineStyle": {
                            "color": "#00ffaa",  # Bright green scanning line
                            "width": 2
                        },
                        "animationDuration": 0  # No animation for scanning line
                    },
                    # Transaction pulses
                    {
                        "type": "effectScatter",
                        "coordinateSystem": "polar",
                        "data": [
                            {
                                "value": [pulse['radius'], pulse['angle']],  # Pulse position
                                "symbolSize": pulse['radius'] / 2,  # Pulse size based on transaction amount
                                "itemStyle": {
                                    "color": {
                                        "type": "radial",  # Radial gradient for pulses
                                        "x": 0.5,
                                        "y": 0.5,
                                        "r": 0.5,
                                        "colorStops": [
                                            {
                                                "offset": 0,
                                                "color": "#ff0055" if pulse['fraud'] == 1 else "#00ffaa"  # Red for fraud, green for legit
                                            },
                                            {
                                                "offset": 1,
                                                "color": "#ff005500" if pulse['fraud'] == 1 else "#00ffaa00"  # Transparent outer edge
                                            }
                                        ]
                                    }
                                }
                            }
                            for pulse in st.session_state.scan_data['pulses']  # Loop through pulses
                        ],
                        "rippleEffect": {
                            "brushType": "stroke",  # Ripple effect type
                            "scale": 4  # Ripple scale
                        }
                    }
                ]
            }

            # Display the radar graph
            st_echarts(options=radar_options, height="400px", key="radar")

        st.markdown("###")
        st.markdown("###")
        # Add two pie charts side by side
        st.markdown("### 📌 Pie Charts")
        col1, col2 = st.columns(2)

        # Fraud vs Legit Transactions Pie Chart
        with col1:
            st.markdown("#### Fraud vs Legit Transactions")  # Title for the first pie chart
            fraud_pie_data = st.session_state.transactions_data["is_fraud"].replace({0: "Legit", 1: "Fraud"})
            fig_pie_fraud = px.pie(names=fraud_pie_data, hole=0.4, color=fraud_pie_data, color_discrete_map={"Fraud": "red", "Legit": "green"}, template='plotly_dark')
            st.plotly_chart(fig_pie_fraud, use_container_width=True)

        # Transaction Categories Pie Chart
        with col2:
            # Use HTML/CSS to center the title
            st.markdown("""
                <div style='text-align: center;'>
                    <h4>Transaction Categories</h4>
                </div>
            """, unsafe_allow_html=True)  # Title for the second pie chart
            category_pie_data = st.session_state.transactions_data["category"]
            fig_pie_category = px.pie(names=category_pie_data, hole=0.4, color=category_pie_data, template='plotly_dark')
            st.plotly_chart(fig_pie_category, use_container_width=True)

        st.markdown("###")
        st.markdown("###")
        # Heatmap for Transaction Frequency by Hour and Day
        st.markdown("### 📊 Transaction Frequency by Hour and Day")

        # Group data by day of the week and hour
        heatmap_data = st.session_state.transactions_data.groupby(['day_of_week', 'hour']).size().reset_index(name="count")

        # Pivot the data for the heatmap
        heatmap_data = heatmap_data.pivot(index='day_of_week', columns='hour', values='count')

        # Ensure the days of the week are ordered correctly
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        heatmap_data = heatmap_data.reindex(days_order)

        # Create the heatmap
        fig_heatmap = px.imshow(
            heatmap_data,
            labels=dict(x="Hour of Day", y="Day of Week", color="Transaction Count"),
            color_continuous_scale='Greens',  # Use a green color scale similar to GitHub
            template='plotly_dark',
            title="Transaction Frequency by Hour and Day"
        )

        # Customize the layout
        fig_heatmap.update_layout(
            xaxis_title="Hour of Day",
            yaxis_title="Day of Week",
            xaxis_nticks=24,  # Show all 24 hours on the x-axis
            yaxis_nticks=7,   # Show all 7 days on the y-axis
            coloraxis_colorbar=dict(title="Transactions"),  # Add a color bar title
            margin=dict(l=50, r=50, t=50, b=50),  # Adjust margins for a compact look
            width=800,  # Set the width of the heatmap
            height=500  # Set the height of the heatmap
        )

        # Add hover text for better interactivity
        fig_heatmap.update_traces(
            hovertemplate="<b>Day:</b> %{y}<br><b>Hour:</b> %{x}<br><b>Transactions:</b> %{z}<extra></extra>"
        )

        # Display the heatmap
        st.plotly_chart(fig_heatmap, use_container_width=True)

        st.markdown("###")
        st.markdown("###")

        # Add a new line chart for total transaction amount over time
        st.markdown("### 📈 Total Transaction Amount Over Time")
        time_series_data = st.session_state.transactions_data.groupby('trans_date_trans_time')['amt'].sum().reset_index()
        fig_line = px.line(
            time_series_data,
            x='trans_date_trans_time',
            y='amt',
            title='Total Transaction Amount Over Time',
            template='plotly_dark'
        )
        st.plotly_chart(fig_line, use_container_width=True)


        st.markdown("###")

        # Histogram for Transaction Amounts
        st.markdown("### 📊 Transaction Amount Distribution")
        fig_hist = px.histogram(st.session_state.transactions_data, x='amt', nbins=20, template='plotly_dark')
        st.plotly_chart(fig_hist, use_container_width=True)

        st.markdown("###")

        # Scatter Plot for Transaction Amount vs Fraud Probability
        st.markdown("### 📊 Transaction Amount vs Fraud Probability")
        fig_scatter = px.scatter(st.session_state.transactions_data, x='amt', y='fraud_score', color='is_fraud', color_discrete_map={0: "green", 1: "red"}, template='plotly_dark')
        st.plotly_chart(fig_scatter, use_container_width=True)

        st.markdown("###")

        # Map for Suspicious Transactions
        st.markdown("### 🗺️ Location of Suspicious Transactions")
        df = st.session_state.transactions_data.rename(columns={"lat": "latitude", "long": "longitude"})
        st.map(df[['latitude', 'longitude']])