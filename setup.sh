#!/bin/bash

# Exit on any error
set -e

echo "Setting up the Fraud Detection project..."

# Step 1: Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Step 2: Start the backend
echo "Starting the backend..."
(cd backend && python app.py &)  # Run in background

# Step 3: Start the frontend
echo "Starting the frontend..."
(cd frontend && streamlit run dashboard.py)

echo "Setup complete. The application is running!"
