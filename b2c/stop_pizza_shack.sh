#!/bin/bash

# 🍕 Pizza Shack Complete Service Stop Script
# Unified service stopper for Pizza Shack project
# Stops: Pizza Shack Frontend + Pizza API + Pizza Agent AutoGen + Pizza Shack Riders

echo "🛑 Pizza Shack Complete Service Stack - Stopping Services"
echo "========================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Change to project directory
cd /Users/ashen/Desktop/wso2con/2025-CMB-iam-tutorial/b2c

# Stop services using PIDs if available
print_status "Stopping services using stored process IDs..."

if [ -f "logs/pizza-api.pid" ]; then
    API_PID=$(cat logs/pizza-api.pid)
    if kill -0 $API_PID 2>/dev/null; then
        print_status "Stopping Pizza API process (PID: $API_PID)..."
        kill $API_PID
    fi
    rm -f logs/pizza-api.pid
fi

if [ -f "logs/pizza-agent-autogen.pid" ]; then
    AGENT_PID=$(cat logs/pizza-agent-autogen.pid)
    if kill -0 $AGENT_PID 2>/dev/null; then
        print_status "Stopping Pizza Agent AutoGen process (PID: $AGENT_PID)..."
        kill $AGENT_PID
    fi
    rm -f logs/pizza-agent-autogen.pid
fi

if [ -f "logs/pizza-shack-frontend.pid" ]; then
    FRONTEND_PID=$(cat logs/pizza-shack-frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        print_status "Stopping Pizza Shack frontend process (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
    fi
    rm -f logs/pizza-shack-frontend.pid
fi

if [ -f "logs/pizza-shack-riders.pid" ]; then
    RIDERS_PID=$(cat logs/pizza-shack-riders.pid)
    if kill -0 $RIDERS_PID 2>/dev/null; then
        print_status "Stopping Pizza Shack Riders process (PID: $RIDERS_PID)..."
        kill $RIDERS_PID
    fi
    rm -f logs/pizza-shack-riders.pid
fi

# Also clean up old PID files
rm -f logs/api.pid logs/backend.pid logs/frontend.pid 2>/dev/null

# Kill processes by name (comprehensive cleanup)
print_status "Stopping all related processes by name..."
pkill -f "vite" 2>/dev/null || true
pkill -f "uvicorn.*8000" 2>/dev/null || true  # Pizza API
pkill -f "uvicorn.*8001" 2>/dev/null || true  # Pizza Agent AutoGen
pkill -f "pizza-agent-autogen" 2>/dev/null || true
pkill -f "websocket_service.py" 2>/dev/null || true  # Old agent (cleanup)
pkill -f "main.py" 2>/dev/null || true

# Wait for graceful shutdown
print_status "Waiting for graceful shutdown..."
sleep 3

# Force kill processes on specific ports if still running
for port in 5173 5174 8000 8001; do
    if check_port $port; then
        print_warning "Force killing process on port $port"
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
    fi
done

# Wait a moment for force kills to complete
sleep 2

# Final verification and status
print_status "Verifying all services stopped..."

SERVICES_STOPPED=true

if check_port 8000; then
    print_error "Pizza API still running on port 8000"
    SERVICES_STOPPED=false
fi

if check_port 8001; then
    print_error "Pizza Agent AutoGen still running on port 8001"
    SERVICES_STOPPED=false
fi

if check_port 5173; then
    print_error "Pizza Shack frontend still running on port 5173"
    SERVICES_STOPPED=false
fi

if check_port 5174; then
    print_error "Pizza Shack Riders still running on port 5174"
    SERVICES_STOPPED=false
fi

# Final status
if $SERVICES_STOPPED; then
    print_success "✅ All Pizza Shack services stopped successfully!"
else
    print_warning "⚠️  Some services may still be running. Try manual cleanup:"
    print_status "   sudo lsof -ti:8000,8001,5173,5174 | xargs kill -9"
fi

echo ""
print_status "📝 Service logs are preserved in the logs/ directory:"
print_status "   • Pizza API:            logs/pizza-api.log"
print_status "   • Pizza Agent AutoGen:  logs/pizza-agent-autogen.log"
print_status "   • Pizza Shack Frontend: logs/pizza-shack-frontend.log"
print_status "   • Pizza Shack Riders:   logs/pizza-shack-riders.log"

echo ""
print_status "🚀 To restart services:"
print_status "   ./start_pizza_shack.sh"

echo ""
print_status "🔍 To check status without starting:"
print_status "   ./start_pizza_shack.sh --status"