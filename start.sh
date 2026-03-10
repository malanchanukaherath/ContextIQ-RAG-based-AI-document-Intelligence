#!/bin/bash

echo "Starting RAG Application..."
echo ""

echo "[1/2] Starting Backend Server on port 8000..."
cd "$(dirname "$0")"
uv run uvicorn main:app --reload &
BACKEND_PID=$!
sleep 3

echo "[2/2] Starting Frontend Server on port 3000..."
cd frontend
npm start &
FRONTEND_PID=$!

echo ""
echo "================================"
echo "RAG Application Started!"
echo "================================"
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "================================"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
