#!/bin/bash

# B-Transfer Status Checker
# Copyright (c) 2025 Balsim Technologies. All rights reserved.

echo "🔍 Checking B-Transfer Server Status..."
echo "======================================"

# Check if server is running
if lsof -ti:8081 > /dev/null 2>&1; then
    echo "✅ Server is running on port 8081"
    
    # Get server info
    if curl -s http://localhost:8081/health > /dev/null 2>&1; then
        echo "✅ Server is responding to health checks"
        
        # Get server details
        SERVER_INFO=$(curl -s http://localhost:8081/health)
        VERSION=$(echo $SERVER_INFO | grep -o '"version":"[^"]*"' | cut -d'"' -f4)
        STATUS=$(echo $SERVER_INFO | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
        
        echo "📊 Server Version: $VERSION"
        echo "📊 Server Status: $STATUS"
        echo "🌐 Access URLs:"
        echo "   - Local: http://localhost:8081"
        echo "   - Network: http://$(hostname -I | awk '{print $1}'):8081"
    else
        echo "❌ Server is running but not responding to health checks"
    fi
else
    echo "❌ Server is not running"
    echo "💡 To start the server, run: ./start_server.sh"
fi

echo "======================================" 