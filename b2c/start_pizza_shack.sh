#!/bin/bash

# 🍕 Pizza Shack Complete Service Management Script
# Unified service starter for Pizza Shack project using NEW pizza-agent-autogen
# Starts: Pizza Shack Frontend + Pizza API + Pizza Agent AutoGen + Pizza Shack Riders

set -e  # Exit on any error

echo "🍕 Pizza Shack Complete Service Stack (Enhanced)"
echo "==============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Function to print colored output
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

print_header() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to kill existing services
cleanup_services() {
    print_header "Step 1: Stopping all existing services..."
    
    # Kill existing processes by name
    pkill -f "vite" 2>/dev/null || true
    pkill -f "uvicorn" 2>/dev/null || true
    pkill -f "websocket_service.py" 2>/dev/null || true  # Old agent
    pkill -f "pizza-agent-autogen" 2>/dev/null || true   # New agent
    pkill -f "main.py" 2>/dev/null || true
    pkill -f "pizza-api" 2>/dev/null || true
    
    # Wait for graceful shutdown
    sleep 3
    
    # Force kill processes on specific ports if still running
    for port in 5173 5174 8000 8001; do
        if check_port $port; then
            print_warning "Force killing process on port $port"
            lsof -ti:$port | xargs kill -9 2>/dev/null || true
        fi
    done
    
    sleep 2
    print_success "All existing services stopped"
}

# Function to create logs directory
create_logs_dir() {
    cd /Users/ashen/Desktop/wso2con/2025-CMB-iam-tutorial/b2c
    mkdir -p logs
    print_status "Logs directory ready: logs/"
}

# Function to start Pizza API (Backend)
start_pizza_api() {
    print_header "Step 2: Starting Pizza API (FastAPI)..."
    
    cd /Users/ashen/Desktop/wso2con/2025-CMB-iam-tutorial/b2c/pizza-api
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment for Pizza API..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    if [ ! -f "venv/.deps_installed" ]; then
        print_status "Installing Pizza API dependencies..."
        pip install -r requirements.txt > ../logs/api-install.log 2>&1
        touch venv/.deps_installed
    fi
    
    # Create .env file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_status "Creating .env configuration for Pizza API..."
        cat > .env << EOF
# Pizza API Configuration
DATABASE_URL=sqlite:///./pizza_shack.db
LOG_LEVEL=INFO
ALLOWED_ORIGINS=http://localhost:5173
CORS_ALLOW_CREDENTIALS=true
EOF
    fi
    
    # Start the Pizza API
    print_status "Starting Pizza API on port 8000..."
    nohup uvicorn main:app --host 0.0.0.0 --port 8000 --reload > ../logs/pizza-api.log 2>&1 &
    API_PID=$!
    
    # Wait for API to start
    print_status "Waiting for Pizza API to initialize..."
    for i in {1..30}; do
        if check_port 8000; then
            print_success "✅ Pizza API started at http://localhost:8000/"
            echo $API_PID > ../logs/pizza-api.pid
            cd /Users/ashen/Desktop/wso2con/2025-CMB-iam-tutorial/b2c
            return 0
        fi
        sleep 1
    done
    
    print_error "❌ Pizza API failed to start within 30 seconds"
    cd /Users/ashen/Desktop/wso2con/2025-CMB-iam-tutorial/b2c
    return 1
}

# Function to start Pizza Agent AutoGen (NEW)
start_pizza_agent_autogen() {
    print_header "Step 3: Starting Pizza Agent AutoGen (NEW Enhanced Agent)..."
    
    cd /Users/ashen/Desktop/wso2con/2025-CMB-iam-tutorial/b2c/pizza-agent-autogen
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment for Pizza Agent AutoGen..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies
    if [ ! -f "venv/.deps_installed" ]; then
        print_status "Installing Pizza Agent AutoGen dependencies..."
        pip install -r requirements.txt > ../logs/agent-autogen-install.log 2>&1
        touch venv/.deps_installed
    fi
    
    # Ensure .env file exists (should already be configured)
    if [ ! -f ".env" ]; then
        print_warning ".env file not found, creating default configuration..."
        cat > .env << EOF
# Azure OpenAI Configuration (REQUIRED for AI mode)
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com
AZURE_OPENAI_API_VERSION=2025-01-01-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o

# Asgardeo Configuration  
ASGARDEO_CLIENT_ID=your_client_id
ASGARDEO_CLIENT_SECRET=your_client_secret
ASGARDEO_TENANT_DOMAIN=https://api.asgardeo.io/t/your-org
ASGARDEO_REDIRECT_URI=http://localhost:8001/callback

# Pizza API Configuration
PIZZA_API_BASE_URL=http://localhost:8000

# Agent Authentication
AGENT_ID=pizza-agent-autogen
AGENT_NAME=pizza_agent_autogen
AGENT_SECRET=demo_secret

# Demo Mode - Set to true to use rule-based responses, false for Azure OpenAI
DEMO_MODE=true

# Server Configuration
HOST=0.0.0.0
PORT=8001

# WebSocket Base URL
WS_BASE_URL=ws://localhost:8001
EOF
        print_warning "⚠️  Created default .env file - configure with your credentials for full functionality"
    fi
    
    # Start the Pizza Agent AutoGen service
    print_status "Starting Pizza Agent AutoGen on port 8001..."
    nohup uvicorn app.service:app --host 0.0.0.0 --port 8001 --reload > ../logs/pizza-agent-autogen.log 2>&1 &
    AGENT_PID=$!
    
    # Wait for agent to start
    print_status "Waiting for Pizza Agent AutoGen to initialize..."
    for i in {1..30}; do
        if check_port 8001; then
            print_success "✅ Pizza Agent AutoGen started at http://localhost:8001/"
            echo $AGENT_PID > ../logs/pizza-agent-autogen.pid
            cd /Users/ashen/Desktop/wso2con/2025-CMB-iam-tutorial/b2c
            return 0
        fi
        sleep 1
    done
    
    print_error "❌ Pizza Agent AutoGen failed to start within 30 seconds"
    cd /Users/ashen/Desktop/wso2con/2025-CMB-iam-tutorial/b2c
    return 1
}

# Function to start Pizza Shack Riders App
start_pizza_shack_riders() {
    print_header "Step 4: Starting Pizza Shack Riders App (React + Vite)..."
    
    cd /Users/ashen/Desktop/wso2con/2025-CMB-iam-tutorial/b2c/pizza-shack-riders
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_status "Installing riders app dependencies..."
        npm install > ../logs/riders-install.log 2>&1
    fi
    
    # Start the riders development server
    print_status "Starting Pizza Shack Riders app on port 5174..."
    nohup npm run dev > ../logs/pizza-shack-riders.log 2>&1 &
    RIDERS_PID=$!
    
    # Wait for riders app to start
    print_status "Waiting for riders app to initialize..."
    for i in {1..30}; do
        if check_port 5174; then
            print_success "✅ Pizza Shack Riders app started at http://localhost:5174/"
            echo $RIDERS_PID > ../logs/pizza-shack-riders.pid
            cd /Users/ashen/Desktop/wso2con/2025-CMB-iam-tutorial/b2c
            return 0
        fi
        sleep 1
    done
    
    print_error "❌ Riders app failed to start within 30 seconds"
    cd /Users/ashen/Desktop/wso2con/2025-CMB-iam-tutorial/b2c
    return 1
}

# Function to start Pizza Shack Frontend
start_pizza_shack_frontend() {
    print_header "Step 5: Starting Pizza Shack Frontend (React + Vite)..."
    
    cd /Users/ashen/Desktop/wso2con/2025-CMB-iam-tutorial/b2c/pizza-shack
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_status "Installing frontend dependencies..."
        npm install > ../logs/frontend-install.log 2>&1
    fi
    
    # Ensure .env file is configured for Enhanced ChatBot
    if ! grep -q "VITE_CHAT_MODE" .env 2>/dev/null; then
        print_status "Configuring Enhanced ChatBot environment..."
        cat >> .env << EOF

# Enhanced ChatBot Configuration
# Chat mode: 'websocket' or 'rest' - determines communication method with agent
VITE_CHAT_MODE=websocket

# Agent service URL - points to new pizza-agent-autogen
VITE_AGENT_URL=http://localhost:8001
EOF
    fi
    
    # Start the frontend development server
    print_status "Starting Pizza Shack frontend on port 5173..."
    nohup npm run dev > ../logs/pizza-shack-frontend.log 2>&1 &
    FRONTEND_PID=$!
    
    # Wait for frontend to start
    print_status "Waiting for frontend to initialize..."
    for i in {1..30}; do
        if check_port 5173; then
            print_success "✅ Pizza Shack frontend started at http://localhost:5173/"
            echo $FRONTEND_PID > ../logs/pizza-shack-frontend.pid
            cd /Users/ashen/Desktop/wso2con/2025-CMB-iam-tutorial/b2c
            return 0
        fi
        sleep 1
    done
    
    print_error "❌ Frontend failed to start within 30 seconds"
    cd /Users/ashen/Desktop/wso2con/2025-CMB-iam-tutorial/b2c
    return 1
}

# Function to perform comprehensive health checks
health_checks() {
    print_header "Step 6: Performing service health checks..."
    
    sleep 3  # Give services time to fully initialize
    
    # Check Pizza API
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Pizza API: Healthy ✅"
    else
        print_warning "Pizza API: Not responding ⚠️"
    fi
    
    # Check Pizza Agent AutoGen  
    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        print_success "Pizza Agent AutoGen: Healthy ✅"
        
        # Test agent functionality
        response=$(curl -s -X POST http://localhost:8001/chat \
            -H 'Content-Type: application/json' \
            -d '{"message": "hello", "session_id": "health-check"}' | jq -r '.response' 2>/dev/null)
        if [[ "$response" == *"Pizza Shack"* ]]; then
            print_success "Pizza Agent AutoGen: Chat functionality working ✅"
        fi
    else
        print_warning "Pizza Agent AutoGen: Not responding ⚠️"
    fi
    
    # Check Frontend
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
        print_success "Pizza Shack Frontend: Healthy ✅"
    else
        print_warning "Pizza Shack Frontend: Not responding ⚠️"
    fi
    
    # Check Riders App
    if curl -s http://localhost:5174 > /dev/null 2>&1; then
        print_success "Pizza Shack Riders: Healthy ✅"
    else
        print_warning "Pizza Shack Riders: Not responding ⚠️"
    fi
}

# Function to show service status and usage information
show_status() {
    echo ""
    echo "🍕 Pizza Shack Complete Service Stack Status:"
    echo "============================================="
    
    echo ""
    print_header "Service URLs:"
    if check_port 5173; then
        print_success "🌐 Pizza Shack App:    http://localhost:5173/"
    else
        print_error "🌐 Pizza Shack App:    Not running"
    fi
    
    if check_port 5174; then
        print_success "🏍️  Pizza Shack Riders: http://localhost:5174/"
    else
        print_error "🏍️  Pizza Shack Riders: Not running"
    fi
    
    if check_port 8001; then
        print_success "🤖 Agent AutoGen:      http://localhost:8001/"
        print_status "    • Frontend UI:      http://localhost:8001/"
        print_status "    • API Docs:         http://localhost:8001/docs"
        print_status "    • Health Check:     http://localhost:8001/health"
    else
        print_error "🤖 Agent AutoGen:      Not running"
    fi
    
    if check_port 8000; then
        print_success "🔧 Pizza API:          http://localhost:8000/"
        print_status "    • API Docs:         http://localhost:8000/docs"
        print_status "    • Health Check:     http://localhost:8000/health"
    else
        print_error "🔧 Pizza API:          Not running"
    fi
    
    echo ""
    print_header "Features & Capabilities:"
    print_status "✅ Enhanced ChatBot with dual mode support (WebSocket + REST)"
    print_status "✅ Pizza Agent AutoGen with AutoGen framework integration"
    print_status "✅ Demo mode enabled (works without Azure OpenAI)"
    print_status "✅ Full pizza ordering flow with OAuth authentication"
    print_status "✅ Modern React frontend with enhanced UI/UX"
    
    echo ""
    print_header "Configuration:"
    print_status "• Chat Mode: $(grep VITE_CHAT_MODE pizza-shack/.env 2>/dev/null | cut -d'=' -f2 || echo 'websocket (default)')"
    print_status "• Agent URL: $(grep VITE_AGENT_URL pizza-shack/.env 2>/dev/null | cut -d'=' -f2 || echo 'http://localhost:8001 (default)')"
    print_status "• Demo Mode: $(grep DEMO_MODE pizza-agent-autogen/.env 2>/dev/null | cut -d'=' -f2 || echo 'true (recommended for testing)')"
    
    echo ""
    print_header "Service Logs:"
    print_status "📝 Pizza Shack:    tail -f logs/pizza-shack-frontend.log"
    print_status "📝 Riders App:     tail -f logs/pizza-shack-riders.log"
    print_status "📝 Agent AutoGen:  tail -f logs/pizza-agent-autogen.log"
    print_status "📝 Pizza API:      tail -f logs/pizza-api.log"
    
    echo ""
    print_header "Testing & Usage:"
    print_status "🧪 Test Chat API:  curl -X POST http://localhost:8001/chat -H 'Content-Type: application/json' -d '{\"message\": \"show me the menu\"}'"
    print_status "🧪 Test Menu API:  curl http://localhost:8000/api/menu"
    print_status "🌐 Open Browser:   http://localhost:5173/"
    
    echo ""
    print_header "Management:"
    print_status "🔄 Switch to REST mode:     Edit pizza-shack/.env, set VITE_CHAT_MODE=rest, restart"
    print_status "🔄 Enable Azure OpenAI:     Edit pizza-agent-autogen/.env, set DEMO_MODE=false, add credentials"
    print_status "🛑 Stop all services:       ./stop_pizza_shack.sh"
    print_status "📋 View this status again:  ./start_pizza_shack.sh --status"
}

# Function to check if script is run with --status flag
check_status_only() {
    if [[ "$1" == "--status" ]]; then
        echo "🍕 Pizza Shack Service Status Check"
        echo "===================================="
        show_status
        exit 0
    fi
}

# Main execution function
main() {
    # Check if only status is requested
    check_status_only "$1"
    
    print_status "Starting Pizza Shack Complete Service Stack..."
    
    # Create logs directory
    create_logs_dir
    
    # Clean up existing services
    cleanup_services
    
    # Start all services in order
    if start_pizza_api && start_pizza_agent_autogen && start_pizza_shack_riders && start_pizza_shack_frontend; then
        print_success "🎉 All services started successfully!"
        
        # Perform health checks
        health_checks
        
        # Show final status
        show_status
        
        echo ""
        print_success "🚀 Pizza Shack Complete Stack is Ready!"
        print_status "🌟 Your enhanced pizza ordering experience awaits at http://localhost:5173/"
        
    else
        print_error "❌ Failed to start one or more services"
        echo ""
        print_status "Check the logs for more information:"
        print_status "• Pizza API logs:     tail -f logs/pizza-api.log"
        print_status "• Agent logs:         tail -f logs/pizza-agent-autogen.log"
        print_status "• Riders logs:        tail -f logs/pizza-shack-riders.log"
        print_status "• Frontend logs:      tail -f logs/pizza-shack-frontend.log"
        exit 1
    fi
}

# Handle script interruption
trap 'print_warning "Script interrupted. Services may still be running."; show_status; exit 1' INT

# Run main function
main "$@"