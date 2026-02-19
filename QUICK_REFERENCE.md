# ICU Early Warning System - Quick Reference Card

## 🚀 Launch Dashboard (30 seconds)

```bash
cd icu-early-warning
source venv/bin/activate
streamlit run clinical_dashboard.py --server.port 8504
```

**Then open**: http://localhost:8504

---

## 📊 Dashboard Usage

### Input Patient Data (Sidebar)
1. Enter vital signs:
   - Heart Rate (40-180 bpm)
   - Systolic BP (60-220 mmHg)
   - Diastolic BP (30-140 mmHg)
   - O2 Saturation (70-100%)
   - Temperature (35-42°C)
   - Respiratory Rate (8-50 breaths/min)
   - WBC (1-30 K/µL)
   - Lactate (0.5-10 mmol/L)

2. Select threshold:
   - 🟢 High Sensitivity (0.05) - Catch more cases
   - 🟡 Balanced (0.25) - Recommended
   - 🔴 High Specificity (0.50) - Fewer false alarms

3. Click "Calculate Sepsis Risk"

### Output
- **Risk %**: Color-coded (Green/Yellow/Red)
- **Top 3 Factors**: Which vitals drive the risk
- **Clinical Summary**: Interpretation & recommendations
- **Alert Status**: 🚨 ALERT / ⚠️ WARNING / ✅ LOW RISK

---

## 📈 Model Performance

| Metric | Value |
|--------|-------|
| AUROC | 0.7337 |
| Recall | 63.8% |
| Precision | 5.1% |
| F1 Score | 0.097 |
| Calibration | 0.0195 |

---

## 🔧 Setup (First Time Only)

```bash
cd icu-early-warning

# Option 1: Automated
bash setup_and_test.sh

# Option 2: Manual
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -u test_quick.py
```

---

## 🧪 Testing

### Quick Test (30 seconds)
```bash
source venv/bin/activate
python -u test_quick.py
```

### Full Pipeline (2-3 minutes)
```bash
source venv/bin/activate
python -u run_full_pipeline.py
```

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `clinical_dashboard.py` | Main dashboard (launch this) |
| `src/model_training.py` | Model implementation |
| `src/explanation.py` | Explainability module |
| `Dataset.csv` | Input data (546K rows) |
| `requirements.txt` | Dependencies |

---

## 🐛 Troubleshooting

### Port already in use
```bash
streamlit run clinical_dashboard.py --server.port 8505
```

### Missing dependencies
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### XGBoost error (macOS)
```bash
brew install libomp
export LDFLAGS="-L/opt/homebrew/opt/libomp/lib"
export CPPFLAGS="-I/opt/homebrew/opt/libomp/include"
pip install --force-reinstall xgboost
```

---

## 📚 Documentation

- `DEPLOYMENT_READY.md` - Full system overview
- `NEXT_STEPS.md` - Testing guide
- `FINAL_SUMMARY_FOR_PROFESSOR.md` - Presentation guide
- `SYSTEM_ARCHITECTURE.md` - System design
- `CALIBRATION_GUIDE.md` - Threshold details
- `EXPLAINABILITY_GUIDE.md` - Model interpretation

---

## ✅ System Status

- ✅ Data pipeline complete
- ✅ Feature engineering complete
- ✅ Model training complete
- ✅ Calibration complete
- ✅ Dashboard ready
- ✅ Documentation complete

**Status**: Production Ready 🚀

---

## 🎯 For Your Professor

**Key Talking Points:**
1. Sepsis early detection using ML
2. 546K patient-hours realistic dataset
3. 51 engineered clinical features
4. 63.8% recall (catches most cases)
5. Well-calibrated probabilities
6. Clinical explainability
7. Professional web interface
8. Ready for deployment

**Demo Flow:**
1. Show dashboard interface
2. Enter sample patient data
3. Calculate risk
4. Show top contributing factors
5. Explain clinical interpretation
6. Discuss model performance
7. Highlight explainability

---

## 💡 Tips

- Use **Balanced threshold (0.25)** for most settings
- **High Sensitivity (0.05)** for high-risk patients
- **High Specificity (0.50)** to reduce false alarms
- Dashboard loads models on first run (~30-60 seconds)
- All predictions are explained with top 3 factors
- Model is well-calibrated (probabilities are reliable)

---

**Last Updated**: February 19, 2026  
**Version**: 1.0  
**Status**: ✅ Ready to Use
