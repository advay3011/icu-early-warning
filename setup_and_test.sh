#!/bin/bash

# ICU Early Warning System - Setup and Test Script
# Creates virtual environment, installs dependencies, and runs tests

set -e  # Exit on error

echo "================================================================================"
echo "ICU EARLY WARNING SYSTEM - SETUP & TEST"
echo "================================================================================"

# Step 1: Create virtual environment
echo ""
echo "[1/4] Creating Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Step 2: Activate virtual environment
echo ""
echo "[2/4] Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Step 3: Install dependencies
echo ""
echo "[3/4] Installing dependencies..."
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

# Step 4: Run quick test
echo ""
echo "[4/4] Running quick test..."
python -u test_quick.py

echo ""
echo "================================================================================"
echo "✅ SETUP COMPLETE"
echo "================================================================================"
echo ""
echo "Next steps:"
echo "1. Activate environment: source venv/bin/activate"
echo "2. Run full pipeline: python -u run_full_pipeline.py"
echo "3. Launch dashboard: streamlit run clinical_dashboard.py --server.port 8504"
echo ""
