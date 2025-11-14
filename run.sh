#!/bin/bash
# PROJECT LUMEN - Quick Start Script

echo "🔆 PROJECT LUMEN - Starting System..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/.installed" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    touch venv/.installed
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env with your configuration (especially OPENAI_API_KEY)"
    echo ""
fi

# Start backend
echo "🚀 Starting FastAPI backend..."
cd backend
python main.py &
BACKEND_PID=$!

echo ""
echo "✅ Backend started (PID: $BACKEND_PID)"
echo "📡 API: http://localhost:8000"
echo "📚 Docs: http://localhost:8000/docs"
echo ""

# Wait for backend to start
sleep 3

# Start frontend
echo "🎨 Starting frontend server..."
cd ../frontend
python -m http.server 3000 &
FRONTEND_PID=$!

echo ""
echo "✅ Frontend started (PID: $FRONTEND_PID)"
echo "🌐 UI: http://localhost:3000"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "PROJECT LUMEN is running!"
echo "Press Ctrl+C to stop all services"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Wait for Ctrl+C
trap "echo ''; echo '🛑 Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait
