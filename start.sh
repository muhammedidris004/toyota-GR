#!/bin/bash

# GR Race Strategist AI - Start Script
# Starts both backend and frontend servers

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🏁 Starting GR Race Strategist AI...${NC}\n"

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Clean up any existing processes
echo -e "${YELLOW}Cleaning up existing processes...${NC}"
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
sleep 2

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Stopping servers...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    exit
}

trap cleanup SIGINT SIGTERM

# Check if backend venv exists, create if not
if [ ! -d "backend/venv" ]; then
    echo -e "${YELLOW}Creating backend virtual environment...${NC}"
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    echo -e "${YELLOW}Installing backend dependencies...${NC}"
    pip install -q -r requirements.txt
    cd ..
fi

# Check if frontend node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    cd frontend
    npm install
    cd ..
fi

# Clear Next.js cache
echo -e "${YELLOW}Clearing Next.js cache...${NC}"
rm -rf frontend/.next

# Start Backend
echo -e "${GREEN}Starting Backend (FastAPI) on http://localhost:8000${NC}"
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait for backend to be ready
echo -e "${YELLOW}Waiting for backend to start...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend is running${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}✗ Backend failed to start. Check backend.log${NC}"
        cat backend.log | tail -20
        exit 1
    fi
    sleep 1
done

# Start Frontend
echo -e "${GREEN}Starting Frontend (Next.js) on http://localhost:3000${NC}"
cd frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait for frontend to be ready (Next.js takes longer to compile)
echo -e "${YELLOW}Waiting for frontend to compile and start...${NC}"
echo -e "${YELLOW}(This may take 30-60 seconds on first run)${NC}"
for i in {1..90}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        # Check if it's actually serving HTML (not just connection)
        RESPONSE=$(curl -s http://localhost:3000)
        if echo "$RESPONSE" | grep -q "GR Race Strategist\|DOCTYPE html"; then
            echo -e "${GREEN}✓ Frontend is running${NC}"
            break
        fi
    fi
    if [ $i -eq 90 ]; then
        echo -e "${RED}✗ Frontend failed to start. Check frontend.log${NC}"
        echo -e "${YELLOW}Last 30 lines of frontend.log:${NC}"
        cat frontend.log | tail -30
        echo -e "\n${YELLOW}You can check the full log at: frontend.log${NC}"
        exit 1
    fi
    # Show progress every 10 seconds
    if [ $((i % 10)) -eq 0 ]; then
        echo -e "${YELLOW}Still waiting... (${i}s)${NC}"
    fi
    sleep 1
done

# Final check
echo -e "\n${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🚀 Servers are running!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "Frontend: ${GREEN}http://localhost:3000${NC}"
echo -e "Backend:  ${GREEN}http://localhost:8000${NC}"
echo -e "API Docs: ${GREEN}http://localhost:8000/docs${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Wait a bit more for everything to be fully ready
sleep 2

# Open browser
echo -e "\n${YELLOW}Opening browser...${NC}"
open http://localhost:3000 2>/dev/null || xdg-open http://localhost:3000 2>/dev/null || echo "Please open http://localhost:3000 in your browser"

echo -e "\n${YELLOW}Press Ctrl+C to stop both servers${NC}\n"

# Keep script running and show logs
echo -e "${BLUE}Monitoring servers (logs will appear below)...${NC}\n"
tail -f backend.log frontend.log 2>/dev/null || wait
