import random

def detect_fraud(transaction):
    """
    Simple rule-based fraud detection.
    Returns a fraud score (0 to 1) and a fraud decision (True/False).
    """
    fraud_score = 0

    # Rule 1: High-value transactions
    if transaction['amt'] > 5000:
        fraud_score += 0.4
    
    # Rule 2: Transactions far from home
    lat_diff = abs(transaction['lat'] - transaction['merch_lat'])
    long_diff = abs(transaction['long'] - transaction['merch_long'])
    if lat_diff > 1 or long_diff > 1:
        fraud_score += 0.3

    # Rule 3: Unusual merchant category
    risky_categories = ["Gambling", "Cryptocurrency", "Luxury Goods"]
    if transaction['category'] in risky_categories:
        fraud_score += 0.3

    # Final fraud decision
    is_fraud = fraud_score > 0.5

    return round(fraud_score, 2), is_fraud
