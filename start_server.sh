#!/bin/bash

# B-Transfer Server Startup Script
# Copyright (c) 2025 Balsim Technologies. All rights reserved.

echo "🚀 Starting B-Transfer Server..."

# Check if port 8081 is in use
if lsof -ti:8081 > /dev/null 2>&1; then
    echo "⚠️  Port 8081 is already in use. Stopping existing process..."
    lsof -ti:8081 | xargs kill -9
    sleep 2
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if required packages are installed
echo "🔍 Checking dependencies..."
python3 -c "import flask, cryptography" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Installing required packages..."
    pip3 install -r requirements.txt
fi

# Start the server
echo "🚀 Launching B-Transfer Server..."
python3 b_transfer_server.py 