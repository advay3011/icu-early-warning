#!/bin/bash

# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

echo "Setup complete! Virtual environment created and dependencies installed."
echo "To activate the environment, run: source venv/bin/activate"
echo "Next steps:"
echo "1. Download PhysioNet Challenge 2019 dataset"
echo "2. Extract to data/training_data/"
echo "3. Run: python src/data_ingestion.py"
