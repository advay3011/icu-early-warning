# Dashboard Quick Fix Guide

## Issue Fixed

The dashboard had import errors due to incorrect class names. All issues have been resolved.

## What Was Fixed

### 1. Import Errors
- ❌ `ModelTrainer` → ✅ `ImbalanceAwareModelTrainer`
- ❌ `CalibrationModule` → ✅ `CalibrationAndThresholdOptimizer`

### 2. Function Signatures Updated
- `train_models()` now uses `ImbalanceAwareModelTrainer.run_training_pipeline()`
- `calibrate_model()` now uses correct calibrator initialization with `y_test.values` and `y_pred_proba`
- `create_simulator()` now passes `feature_names` and `alert_threshold` parameters

### 3. Attribute References Updated
- Model metrics now access `trainer.results['baseline']` and `trainer.results['weighted']`
- Calibration metrics now access `calibrator.brier_uncalibrated` and `calibrator.brier_calibrated`

## Running the Dashboard

### Step 1: Activate Virtual Environment
```bash
cd icu-early-warning
source venv/bin/activate
```

### Step 2: Run Streamlit
```bash
streamlit run app.py
```

### Step 3: Open Browser
Navigate to: `http://localhost:8501`

## Dashboard Tabs

1. **📊 Data Overview** - Dataset statistics and quality
2. **🤖 Model Performance** - Model metrics and curves
3. **📈 Clinical Calibration** - Calibration and thresholds
4. **🔍 Explainability** - Feature importance and explanations
5. **⏱️ Clinical Simulation** - Patient monitoring simulation

## Performance

- **First Run**: 30-60 seconds (all modules load and train)
- **Subsequent Runs**: <5 seconds (all cached)

## Troubleshooting

### Issue: Still getting import errors
**Solution**: Make sure you're in the `icu-early-warning` directory and the virtual environment is activated

### Issue: Module not found
**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: Slow performance
**Solution**: This is normal on first run. Subsequent runs will be fast due to caching.

### Issue: Streamlit not responding
**Solution**: Stop (Ctrl+C), clear cache, and restart
```bash
streamlit cache clear
streamlit run app.py
```

## All Fixed! ✅

The dashboard is now ready to use. All import errors have been resolved and the system is fully functional.
