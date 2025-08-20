#!/bin/bash
# Phase 2 Setup Script - Enhanced Matrix Bridge with AI Integration

set -e

# Configuration
BRIDGE_DIR="$HOME/fitness-bits-bobs/matrix-fitness-bridge"
AI_DIR="$HOME/Desktop/fitness-dashboard-frontend/matrix-fitness-ai"
USER=$(whoami)

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if AI service is running
    if curl -s http://localhost:7000/health > /dev/null; then
        print_success "AI service is running"
    else
        print_error "AI service not running! Start it first with: sudo systemctl start matrix-fitness-ai"
        exit 1
    fi
    
    # Check if Matrix bridge directory exists
    if [ ! -d "$BRIDGE_DIR" ]; then
        print_error "Matrix bridge directory not found: $BRIDGE_DIR"
        exit 1
    fi
    
    # Check if original bridge is running
    if systemctl is-active --quiet matrix-fitness-bridge; then
        print_status "Stopping original bridge service..."
        sudo systemctl stop matrix-fitness-bridge.service
        sudo systemctl stop matrix-fitness-listener.service
    fi
    
    print_success "Prerequisites check passed"
}

# Backup existing bridge
backup_existing_bridge() {
    print_status "Backing up existing bridge..."
    
    cd "$BRIDGE_DIR"
    
    # Create backup directory
    backup_dir="backup-$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$backup_dir"
    
    # Backup existing files
    cp matrix_aws_bridge.py "$backup_dir/" 2>/dev/null || true
    cp simple_matrix_webhook.py "$backup_dir/" 2>/dev/null || true
    cp .env "$backup_dir/" 2>/dev/null || true
    
    print_success "Backup created in $BRIDGE_DIR/$backup_dir"
}

# Install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    cd "$BRIDGE_DIR"
    
    # Activate virtual environment
    source bridge-env/bin/activate
    
    # Update requirements
    cat > requirements-enhanced.txt << 'EOF'
matrix-nio[e2e]==0.20.2
aiohttp==3.8.6
requests==2.31.0
python-dotenv==1.0.0
asyncio-mqtt==0.11.1
EOF
    
    # Install dependencies
    pip install --break-system-packages -r requirements-enhanced.txt
    
    print_success "Dependencies installed"
}

# Create enhanced bridge configuration
create_enhanced_config() {
    print_status "Creating enhanced configuration..."
    
    cd "$BRIDGE_DIR"
    
    # Update .env file with AI service configuration
    if [ -f .env ]; then
        # Backup existing .env
        cp .env .env.backup
        
        # Add AI configuration if not present
        if ! grep -q "ENABLE_AI_PARSING" .env; then
            cat >> .env << 'EOF'

# AI Service Configuration
ENABLE_AI_PARSING=true
AI_SERVER_URL=http://localhost:7000
AI_TIMEOUT=10

# Enhanced Features
SMART_ROUTING=true
ENHANCED_CONFIRMATIONS=true
EOF
        fi
    else
        print_error ".env file not found in $BRIDGE_DIR"
        exit 1
    fi
    
    print_success "Enhanced configuration created"
}

# Create enhanced bridge service
create_enhanced_service() {
    print_status "Creating enhanced bridge service..."
    
    # Copy the enhanced bridge code to the bridge directory
    # (User needs to copy the Python code from the artifact)
    print_warning "You need to copy the enhanced bridge code to: $BRIDGE_DIR/enhanced_matrix_bridge.py"
    
    # Create new systemd service
    sudo tee /etc/systemd/system/matrix-fitness-bridge-enhanced.service > /dev/null << EOF
[Unit]
Description=Enhanced Matrix Fitness Bridge with AI Integration
After=network.target matrix-synapse.service matrix-fitness-ai.service
Wants=matrix-synapse.service matrix-fitness-ai.service

[Service]
Type=simple
User=$USER
WorkingDirectory=$BRIDGE_DIR
Environment=PATH=$BRIDGE_DIR/bridge-env/bin
Environment=PYTHONPATH=$BRIDGE_DIR
ExecStart=$BRIDGE_DIR/bridge-env/bin/python enhanced_matrix_bridge.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Resource limits
MemoryMax=512M
CPUQuota=50%

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd
    sudo systemctl daemon-reload
    
    print_success "Enhanced service created"
}

# Create monitoring and testing tools
create_tools() {
    print_status "Creating monitoring and testing tools..."
    
    cd "$BRIDGE_DIR"
    
    # Create bridge status checker
    cat > check-enhanced-bridge.sh << 'EOF'
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
EOF
    
    chmod +x check-enhanced-bridge.sh
    
    # Create test message sender
    cat > test-enhanced-bridge.py << 'EOF'
#!/usr/bin/env python3
"""
Test the enhanced Matrix bridge with various message types
"""

import asyncio
import sys
from nio import AsyncClient

async def send_test_messages():
    """Send test workout messages"""
    client = AsyncClient("http://localhost:8008", "@pi-user:pi-fitness.local")
    
    # Login (you'll need to enter password)
    password = input("Enter pi-user password: ")
    await client.login(password)
    
    room_id = "!DrpxcCGaUYuUbViiLw:pi-fitness.local"
    
    test_messages = [
        "Bench press 80kg 4x8",  # Structured - should use AI or AWS
        "Had a great workout today! Managed to bench 80kg for 4 sets of 8 reps, then did some squats at 100kg for 3 sets of 10",  # Free-form - should use AI
        "Quick run this morning, 5km in about 25 minutes, felt good!",  # Cardio free-form - should use AI
        "BP 80kg 4x8, SQ 100kg 3x10, DL 120kg 1x5",  # Multiple structured exercises
    ]
    
    print("Sending test messages...")
    for i, message in enumerate(test_messages, 1):
        print(f"\n{i}. Sending: {message}")
        await client.room_send(
            room_id=room_id,
            message_type="m.room.message",
            content={"msgtype": "m.text", "body": message}
        )
        await asyncio.sleep(3)  # Wait between messages
    
    await client.close()
    print("\nTest messages sent! Check Matrix room for responses.")

if __name__ == "__main__":
    asyncio.run(send_test_messages())
EOF
    
    chmod +x test-enhanced-bridge.py
    
    print_success "Monitoring and testing tools created"
}

# Create helper commands
create_helper_commands() {
    print_status "Creating helper commands..."
    
    # Add to bashrc if not already there
    if ! grep -q "# Enhanced Matrix Bridge Commands" "$HOME/.bashrc"; then
        cat >> "$HOME/.bashrc" << 'EOF'

# Enhanced Matrix Bridge Commands
alias bridge-status='~/matrix-fitness-bridge/check-enhanced-bridge.sh'
alias bridge-logs='sudo journalctl -u matrix-fitness-bridge-enhanced.service -f'
alias bridge-restart='sudo systemctl restart matrix-fitness-bridge-enhanced.service'
alias bridge-test='cd ~/matrix-fitness-bridge && python test-enhanced-bridge.py'
alias bridge-start='sudo systemctl start matrix-fitness-bridge-enhanced.service'
alias bridge-stop='sudo systemctl stop matrix-fitness-bridge-enhanced.service'
EOF
        print_success "Helper commands added to bashrc"
    fi
}

# Test the enhanced bridge
test_bridge() {
    print_status "Testing enhanced bridge setup..."
    
    cd "$BRIDGE_DIR"
    
    # Check if enhanced bridge file exists
    if [ ! -f "enhanced_matrix_bridge.py" ]; then
        print_error "Enhanced bridge file not found!"
        print_warning "Copy the Python code from the artifact to: $BRIDGE_DIR/enhanced_matrix_bridge.py"
        return 1
    fi
    
    # Test Python syntax
    source bridge-env/bin/activate
    if python -m py_compile enhanced_matrix_bridge.py; then
        print_success "Enhanced bridge syntax is valid"
    else
        print_error "Enhanced bridge has syntax errors"
        return 1
    fi
    
    # Test imports
    if python -c "import enhanced_matrix_bridge" 2>/dev/null; then
        print_success "Enhanced bridge imports work"
    else
        print_error "Enhanced bridge import failed"
        return 1
    fi
    
    print_success "Bridge setup tests passed"
}

# Final setup and start
final_setup() {
    print_status "Completing enhanced bridge setup..."
    
    # Disable old services
    sudo systemctl disable matrix-fitness-bridge.service 2>/dev/null || true
    sudo systemctl disable matrix-fitness-listener.service 2>/dev/null || true
    
    # Enable new service
    sudo systemctl enable matrix-fitness-bridge-enhanced.service
    
    print_success "Enhanced bridge is ready!"
}

# Print usage instructions
print_usage() {
    echo
    echo "🎉 Phase 2 Setup Complete!"
    echo "=========================="
    echo
    echo "📋 What's Installed:"
    echo "  ✅ Enhanced Matrix bridge with AI integration"
    echo "  ✅ Smart message routing (AI vs AWS)"
    echo "  ✅ Free-form text processing capability"
    echo "  ✅ Enhanced confirmation messages"
    echo "  ✅ Monitoring and testing tools"
    echo
    echo "📁 Important Files:"
    echo "  • Enhanced bridge: $BRIDGE_DIR/enhanced_matrix_bridge.py"
    echo "  • Configuration: $BRIDGE_DIR/.env"
    echo "  • Status checker: $BRIDGE_DIR/check-enhanced-bridge.sh"
    echo "  • Test script: $BRIDGE_DIR/test-enhanced-bridge.py"
    echo
    echo "🔧 Useful Commands:"
    echo "  bridge-status     - Check all services"
    echo "  bridge-logs       - View live logs"
    echo "  bridge-restart    - Restart the bridge"
    echo "  bridge-test       - Send test messages"
    echo
    echo "🚀 Next Steps:"
    echo "  1. Copy enhanced bridge code to: $BRIDGE_DIR/enhanced_matrix_bridge.py"
    echo "  2. Start the bridge: bridge-start"
    echo "  3. Check status: bridge-status"
    echo "  4. Test with: bridge-test"
    echo "  5. Send workout messages in Element app!"
    echo
    echo "💡 Message Examples:"
    echo "  📱 Structured: 'Bench press 80kg 4x8'"
    echo "  📱 Free-form: 'Great workout today! Bench 80kg 4x8, squats 100kg 3x10'"
    echo "  📱 Cardio: 'Morning run for 30 minutes, felt amazing!'"
    echo
}

# Main execution
main() {
    echo "🚀 Phase 2: Enhanced Matrix Bridge Setup"
    echo "========================================"
    echo
    echo "This will integrate your fast AI service with Matrix"
    echo "enabling free-form workout text processing!"
    echo
    read -p "Continue with setup? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled"
        exit 0
    fi
    
    check_prerequisites
    backup_existing_bridge
    install_dependencies
    create_enhanced_config
    create_enhanced_service
    create_tools
    create_helper_commands
    test_bridge
    final_setup
    print_usage
}

# Error handling
handle_error() {
    print_error "Setup failed at step: $1"
    echo "Check the logs and try running the script again"
    exit 1
}

trap 'handle_error "${BASH_COMMAND}"' ERR

# Run main function
main "$@"
