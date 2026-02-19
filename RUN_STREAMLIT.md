# Running the ICU Early Warning Dashboard

## Quick Start

### 1. Activate Virtual Environment

```bash
cd icu-early-warning
source venv/bin/activate
```

### 2. Run the Streamlit App

```bash
streamlit run app.py
```

The dashboard will open in your browser at `http://localhost:8501`

---

## Dashboard Overview

The comprehensive dashboard includes 5 main tabs:

### Tab 1: 📊 Data Overview
- Dataset statistics (samples, features, missing values)
- Class distribution visualization
- Column information (numeric vs categorical)
- Missing values analysis
- Basic statistics for numeric features

**Use Case**: Understand data quality and characteristics

### Tab 2: 🤖 Model Performance
- Baseline model metrics (no class weighting)
- Weighted model metrics (balanced classes)
- ROC curve visualization
- Precision-Recall curve visualization

**Use Case**: Compare model performance and understand trade-offs

### Tab 3: 📈 Clinical Calibration
- Calibration metrics (Brier score before/after)
- Calibration curve visualization
- Threshold optimization analysis
- Recommended clinical thresholds

**Use Case**: Understand probability calibration and select appropriate alert thresholds

### Tab 4: 🔍 Explainability
- Global feature importance plot
- Patient-level prediction explanations
- Interactive patient selection
- Patient contribution visualization

**Use Case**: Understand which features drive predictions and explain individual cases

### Tab 5: ⏱️ Clinical Simulation
- Patient selection for simulation
- Risk trajectory over time
- Vital signs trajectory
- Alert narrative and analysis

**Use Case**: Simulate real ICU monitoring and see how alerts would trigger

---

## Features

### Caching for Performance
- Data loading is cached to avoid reloading
- Model training is cached to avoid retraining
- Calibration is cached to avoid recalibration

### Interactive Elements
- Patient selection sliders
- Simulation buttons
- Dynamic explanation generation

### Visualizations
- Class distribution pie chart
- ROC curves
- Precision-Recall curves
- Calibration curves
- Threshold performance plots
- Risk trajectories
- Vital signs trajectories
- Feature importance plots
- Patient contribution plots

---

## Troubleshooting

### Issue: "Dataset.csv not found"
**Solution**: Ensure you're running from the `icu-early-warning` directory or update the path in the app.

### Issue: "Module not found" errors
**Solution**: Make sure the virtual environment is activated and all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: Streamlit not responding
**Solution**: 
1. Stop the app (Ctrl+C)
2. Clear cache: `streamlit cache clear`
3. Restart: `streamlit run app.py`

### Issue: Slow performance
**Solution**: 
- The app uses caching to speed up repeated operations
- First run will be slower as it trains models
- Subsequent runs will use cached results
- To force retraining, use Streamlit's "Rerun" button or clear cache

---

## Advanced Usage

### Running on a Specific Port
```bash
streamlit run app.py --server.port 8502
```

### Running in Headless Mode (for servers)
```bash
streamlit run app.py --server.headless true
```

### Disabling Caching (for debugging)
Comment out `@st.cache_resource` decorators in the code

---

## Performance Notes

- **Data Loading**: ~2-5 seconds (cached after first run)
- **Model Training**: ~10-30 seconds (cached after first run)
- **Calibration**: ~5-10 seconds (cached after first run)
- **Simulation**: ~2-5 seconds per patient

Total first run: ~30-60 seconds
Subsequent runs: <5 seconds (all cached)

---

## Next Steps

1. **Batch Simulation**: Add capability to simulate multiple patients
2. **Export Reports**: Generate PDF clinical reports
3. **Real-time Monitoring**: Connect to live EHR data
4. **Performance Tracking**: Monitor metrics over time
5. **Clinical Validation**: Pilot with real clinicians

---

## Project Status

```
✅ Step 1: Data Ingestion & Validation          COMPLETE
✅ Step 2: Clinical Feature Engineering         COMPLETE
✅ Step 3: Imbalance-Aware Model Training       COMPLETE
✅ Step 4: Model Calibration & Thresholds       COMPLETE
✅ Step 5: Clinical Interpretability            COMPLETE
✅ Step 6: Clinical Simulation & Alerting       COMPLETE
⏳ Step 7: Dashboard Integration                IN PROGRESS
```

---

**Last Updated**: February 19, 2026
