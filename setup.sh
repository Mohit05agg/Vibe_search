#!/bin/bash
# Complete setup script for Vibe Search

echo "=========================================="
echo "Vibe Search - Complete Setup"
echo "=========================================="

# Check Python
echo "Checking Python..."
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.11+"
    exit 1
fi
echo "✅ Python found: $(python --version)"

# Check Node.js
echo "Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi
echo "✅ Node.js found: $(node --version)"

# Setup Python environment
echo ""
echo "Setting up Python environment..."
if [ ! -d ".venv" ]; then
    python -m venv .venv
fi
source .venv/bin/activate
pip install -r requirements.txt
echo "✅ Python dependencies installed"

# Setup frontend
echo ""
echo "Setting up frontend..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
fi
cd ..
echo "✅ Frontend dependencies installed"

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Setup database: python database/setup_database.py"
echo "2. Import products: python database/import_products.py"
echo "3. Generate embeddings: python embeddings/generate_clip_embeddings.py"
echo "4. Start backend: python run_server.py"
echo "5. Start frontend: cd frontend && npm run dev"

