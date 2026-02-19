# Installing Dependencies for Improved Model

## Required Packages

The improved model needs a few additional packages:

- `xgboost` - XGBoost classifier
- `imbalanced-learn` - SMOTE for handling imbalance

## Installation Steps

### Step 1: Activate Virtual Environment
```bash
cd icu-early-warning
source venv/bin/activate
```

### Step 2: Install XGBoost
```bash
pip install xgboost
```

### Step 3: Install Imbalanced-Learn
```bash
pip install imbalanced-learn
```

### Step 4: Verify Installation
```bash
python -c "import xgboost; import imblearn; print('✓ All packages installed')"
```

## All at Once

Or install everything at once:
```bash
pip install xgboost imbalanced-learn
```

## Verify Requirements

Check that all dependencies are installed:
```bash
pip list | grep -E "xgboost|imbalanced-learn|scikit-learn|pandas|numpy"
```

You should see:
- xgboost
- imbalanced-learn
- scikit-learn
- pandas
- numpy

## If Installation Fails

### Issue: "pip: command not found"
**Solution**: Make sure virtual environment is activated
```bash
source venv/bin/activate
```

### Issue: "Permission denied"
**Solution**: Use `--user` flag
```bash
pip install --user xgboost imbalanced-learn
```

### Issue: "No module named pip"
**Solution**: Use python -m pip
```bash
python -m pip install xgboost imbalanced-learn
```

## Update Requirements File

To save these dependencies:
```bash
pip freeze > requirements.txt
```

This updates `requirements.txt` with all installed packages.

## Ready to Test?

Once installed, run:
```bash
python -u src/improved_model.py
```

Expected output: Model training progress + performance metrics
Expected time: 2-5 minutes
