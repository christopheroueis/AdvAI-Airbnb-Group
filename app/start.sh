#!/bin/bash

# Startup script for LA Airbnb Forecasting Platform
# This script starts both backend and frontend servers

echo "🚀 Starting LA Airbnb Forecasting Platform..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Start backend in background
echo -e "${BLUE}Starting Backend API...${NC}"
cd "$(dirname "$0")/airbnb-forecasting-backend"

# Activate virtual environment and start uvicorn
source venv/bin/activate 2>/dev/null || python3 -m venv venv && source venv/bin/activate
pip install -q -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo -e "${GREEN}✓ Backend started on http://localhost:8000${NC}"
echo "  API Docs: http://localhost:8000/docs"

# Wait for backend to start
sleep 3

# Start frontend
echo -e "${BLUE}Starting Frontend...${NC}"
cd ../airbnb-forecasting-frontend
npm install --silent
npm run dev &
FRONTEND_PID=$!

echo -e "${GREEN}✓ Frontend started on http://localhost:5173${NC}"

echo ""
echo "=============================================="
echo "🎉 Platform is ready!"
echo "=============================================="
echo ""
echo "📊 Dashboard:  http://localhost:5173"
echo "🔮 Backend API: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"
echo "=============================================="

# Wait for user to stop
wait
