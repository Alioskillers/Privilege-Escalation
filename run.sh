#!/bin/bash

echo "🔐 Starting Access Control Security Simulator..."
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "⚠️  Virtual environment not found. Creating one..."
    python3 -m venv .venv
    .venv/bin/pip install streamlit numpy networkx matplotlib --quiet
    echo "✅ Dependencies installed"
fi

# Run the Streamlit app
echo "🚀 Launching Streamlit app..."
echo "   Open your browser at: http://localhost:8501"
echo ""

.venv/bin/streamlit run app.py
