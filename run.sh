#!/bin/bash
# Convenience script to run both backend and frontend

echo "🚀 Starting Sephira Orion..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found"
    echo "   Please run: python setup.py"
    exit 1
fi

# Check if data exists
if [ ! -f data/raw/all_indexes_beta.csv ]; then
    echo "❌ Sentiment data not found"
    echo "   Please copy all_indexes_beta.csv to data/raw/"
    exit 1
fi

# Check if processed data exists
if [ ! -f data/processed/metadata.json ]; then
    echo "⚠️  Processed data not found. Running data processing..."
    python -m backend.services.data_loader
fi

# Check if embeddings exist
if [ ! -d data/chroma ]; then
    echo "⚠️  Vector database not found. You may need to run:"
    echo "   python -m backend.services.embeddings"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "Starting backend on port 8000..."
uvicorn backend.api.main:app --reload --port 8000 &
BACKEND_PID=$!

echo "Waiting for backend to start..."
sleep 3

echo "Starting Next.js frontend on port 3000..."
cd frontend && npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Sephira Orion is running!"
echo ""
echo "📊 Frontend: http://localhost:3000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both services"
echo ""

# Handle termination
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
