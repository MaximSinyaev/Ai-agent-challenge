#!/bin/bash

# Script to run Streamlit web interface

echo "Starting AI Agent Web Interface..."
echo ""

# Check if backend is running
echo "Checking backend availability..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ Backend is available"
else
    echo "✗ Backend is not available. Please start the backend server first:"
    echo "   cd .. && ./run_server.sh"
    echo ""
    read -p "Continue without backend? (y/N): " continue_without_backend
    if [[ ! "$continue_without_backend" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Navigate to web directory
cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "../.venv" ]; then
    source ../.venv/bin/activate
    echo "✓ Virtual environment activated"
fi

# Install dependencies if not present
if ! python -c "import streamlit" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Load environment variables
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

echo ""
echo "Web interface: http://localhost:8501"
echo "Backend API: http://localhost:8000"
echo "API docs: http://localhost:8000/docs"
echo ""

# Run Streamlit
streamlit run app.py --server.port 8501 --server.address 0.0.0.0