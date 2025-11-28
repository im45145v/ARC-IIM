#!/bin/bash
# Start the Alumni Management System

echo "🎓 Starting Alumni Management System..."
echo ""

# Check if database is running
if ! docker-compose ps | grep -q "postgres.*Up"; then
    echo "⚠️  Database is not running. Starting it now..."
    docker-compose up -d
    echo "⏳ Waiting for database to be ready..."
    sleep 5
fi

echo "✅ Database is running"
echo ""

# Set PYTHONPATH to ensure imports work
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Start Streamlit
echo "🚀 Launching Streamlit app..."
echo ""
streamlit run alumni_system/frontend/app.py
