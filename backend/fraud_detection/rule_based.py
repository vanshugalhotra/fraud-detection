import pandas as pd
from geopy.distance import geodesic

def detect_fraud(transaction):
    """
    Detect fraud based on rules and return a fraud score.
    :param transaction: Dictionary containing transaction details.
    :return: fraud_score (0 to 1)
    """
    fraud_score = 0

    # Define thresholds
    high_amount_threshold = 5000  # $5000
    location_threshold = 100  # 100 km

    # Ensure datetime conversion
    transaction_time = pd.to_datetime(transaction.get('trans_date_trans_time'))

    # Rule 1: High Amount
    if transaction.get('amt', 0) > high_amount_threshold:
        fraud_score += 0.4

    # Rule 2: Unusual Merchant Category
    high_risk_categories = ["Luxury Goods", "Casino", "Cryptocurrency Exchange"]
    if transaction.get("category") in high_risk_categories:
        fraud_score += 0.3

    # Rule 3: Location Mismatch
    user_location = (transaction.get('lat', 0), transaction.get('long', 0))
    merchant_location = (transaction.get('merch_lat', 0), transaction.get('merch_long', 0))
    
    if user_location and merchant_location:
        distance = geodesic(user_location, merchant_location).km
        if distance > location_threshold:
            fraud_score += 0.2

    # Rule 4: Large City Population (More fraud risk in high-population cities)
    if transaction.get('city_pop', 0) > 5_000_000:
        fraud_score += 0.1

    # Cap fraud_score at 1.0
    fraud_score = min(fraud_score, 1.0)

    return fraud_score
