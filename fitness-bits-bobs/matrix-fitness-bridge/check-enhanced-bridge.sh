#!/bin/bash
# Enhanced Bridge Status Checker

echo "🔍 Enhanced Matrix Bridge Status"
echo "================================"

# Check services
echo "Service Status:"
echo -n "  Matrix Synapse: "
if systemctl is-active --quiet matrix-synapse; then
    echo "✅ Running"
else
    echo "❌ Not running"
fi

echo -n "  AI Service: "
if systemctl is-active --quiet matrix-fitness-ai; then
    echo "✅ Running"
else
    echo "❌ Not running"
fi

echo -n "  Enhanced Bridge: "
if systemctl is-active --quiet matrix-fitness-bridge-enhanced; then
    echo "✅ Running"
else
    echo "❌ Not running"
fi

echo
echo "API Health Checks:"

# Check AI service
echo -n "  AI Service API: "
if curl -s http://localhost:7000/health | grep -q "healthy"; then
    echo "✅ Healthy"
else
    echo "❌ Unhealthy"
fi

# Check Matrix
echo -n "  Matrix API: "
if curl -s http://localhost:8008/_matrix/client/versions > /dev/null; then
    echo "✅ Responding"
else
    echo "❌ Not responding"
fi

echo
echo "Recent Bridge Logs:"
sudo journalctl -u matrix-fitness-bridge-enhanced.service -n 5 --no-pager
