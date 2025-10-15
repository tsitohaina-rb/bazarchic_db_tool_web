#!/bin/bash

# Bazarchic Database Web Tool Startup Script

echo "🚀 Starting Bazarchic Database Web Tool..."
echo "=========================================="

# Activate virtual environment
source .venv/bin/activate

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create a .env file with your database credentials."
    exit 1
fi

# Start Flask application
echo "✅ Virtual environment activated"
echo "🌐 Starting Flask server..."
echo "📍 Access the application at: http://localhost:5000"
echo "OK"

python app.py
