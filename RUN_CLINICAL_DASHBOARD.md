# How to Run the Clinical Dashboard

## Quick Start (3 Steps)

### Step 1: Open New Terminal
Open a **NEW** terminal window (don't use the frozen one)

### Step 2: Run These Commands
```bash
cd icu-early-warning
source venv/bin/activate
streamlit run clinical_dashboard.py --server.port 8504
```

### Step 3: Open Browser
Go to: `http://localhost:8504`

---

## That's It! 🎉

The dashboard will load and you can start entering patient vital signs.

---

## What You'll See

1. **Title**: "ICU Sepsis Early Warning System"
2. **Sidebar**: Sliders for vital signs
3. **Main Area**: Risk assessment results
4. **Button**: "Calculate Sepsis Risk"

---

## How to Use

1. **Enter vital signs** using sidebar sliders
2. **Select alert threshold** (Balanced recommended)
3. **Click "Calculate Sepsis Risk"**
4. **Review risk percentage and explanation**

---

## If Terminal Freezes Again

1. Open a NEW terminal window
2. Run the commands above
3. The new terminal should work fine

---

## Troubleshooting

**Port already in use?**
```bash
streamlit run clinical_dashboard.py --server.port 8505
```

**Module not found?**
```bash
pip install -r requirements.txt
```

**Dataset not found?**
Make sure Dataset.csv is in the icu-early-warning directory

---

**Ready to go!** 🚀
