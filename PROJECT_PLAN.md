# ICU Early Warning Agent: Project Plan & Milestones

## Executive Summary

Building a research-grade biomedical AI system to predict sepsis onset 6 hours early from ICU time-series data. The system will provide interpretable risk scores, feature importance, and clinical actionability.

**Timeline**: 4 weeks | **Team**: 1 engineer | **Data**: PhysioNet Challenge 2019

## Phase 1: Data & Baseline (Week 1)

### Objectives
- Load and validate PhysioNet dataset
- Create patient-hour engineered dataset
- Train baseline logistic regression
- Establish evaluation metrics

### Deliverables
- ✓ Data ingestion module (load, validate, align labels)
- ✓ Feature engineering module (rolling stats, missingness, lookahead labels)
- ✓ Patient-hour dataset (CSV with ~100k rows)
- ✓ Baseline model (logistic regression)
- ✓ Evaluation module (AUROC, AUPRC, sensitivity@FPR, median hours early)
- ✓ Baseline results report

### Success Criteria
- AUROC ≥ 0.75 on test set
- AUPRC ≥ 0.50
- No data leakage (patient-level splits)
- All metrics computed correctly

### Milestones
- Day 1-2: Data ingestion & validation
- Day 3-4: Feature engineering
- Day 5: Baseline model training
- Day 6-7: Evaluation & reporting

---

## Phase 2: Explanation & Simulation (Week 2)

### Objectives
- Implement feature importance (SHAP or sklearn)
- Build patient timeline simulator
- Generate per-prediction explanations
- Create visualization dashboard

### Deliverables
- ✓ Explanation module (global + per-prediction)
- ✓ Patient simulator (hour-by-hour replay)
- ✓ Timeline visualization (risk score over time)
- ✓ Example patient reports

### Success Criteria
- Top 5 features are clinically interpretable
- Simulator correctly replays patient timeline
- Visualizations are clear and actionable

### Milestones
- Day 1-2: Feature importance implementation
- Day 3-4: Patient simulator
- Day 5-6: Visualization & reporting
- Day 7: Example patient case studies

---

## Phase 3: Model Improvements (Week 3)

### Objectives
- Hyperparameter tuning
- Feature selection
- Gradient boosting model
- Calibration improvements

### Deliverables
- ✓ Hyperparameter tuning results
- ✓ Feature selection analysis
- ✓ Gradient boosting model (XGBoost/LightGBM)
- ✓ Calibration improvements
- ✓ Comparison report (baseline vs. improved)

### Success Criteria
- AUROC ≥ 0.80 on test set
- AUPRC ≥ 0.60
- Median hours early ≥ 3 hours
- Improved calibration (Brier score < 0.15)

### Milestones
- Day 1-2: Hyperparameter tuning
- Day 3-4: Feature selection
- Day 5-6: Gradient boosting
- Day 7: Calibration & comparison

---

## Phase 4: Validation & Documentation (Week 4)

### Objectives
- Cross-validation
- Final test set evaluation
- Clinical interpretation
- Final documentation

### Deliverables
- ✓ 5-fold cross-validation results
- ✓ Final test set metrics with confidence intervals
- ✓ Clinical interpretation report
- ✓ Final documentation & README
- ✓ Reproducible code & notebooks

### Success Criteria
- All success criteria met (see EVALUATION_PLAN.md)
- Code is clean, documented, and reproducible
- Results are clinically interpretable

### Milestones
- Day 1-2: Cross-validation
- Day 3-4: Final test evaluation
- Day 5-6: Clinical interpretation
- Day 7: Final documentation

---

## Key Decisions & Rationale

### 1. Patient-Level Splits
**Decision**: Split by patient (not by hour)
**Rationale**: Prevents data leakage; realistic evaluation

### 2. 6-Hour Lookahead
**Decision**: Predict sepsis 6 hours before onset
**Rationale**: Clinically actionable lead time for intervention

### 3. Logistic Regression Baseline
**Decision**: Start with logistic regression
**Rationale**: Interpretable, fast, good baseline; upgrade to GB later

### 4. SMOTE for Class Imbalance
**Decision**: Apply SMOTE on training set only
**Rationale**: Realistic evaluation on imbalanced test set

### 5. Multiple Evaluation Metrics
**Decision**: Report AUROC, AUPRC, sensitivity@FPR, median hours early
**Rationale**: Comprehensive assessment; AUPRC better for imbalanced data

---

## Data Requirements

### Input
- PhysioNet Challenge 2019 Sepsis Dataset
- ~1000 patients with time-series vitals/labs
- Pipe-delimited .psv files + sepsis_labels.csv

### Output
- Patient-hour dataset (~100k rows)
- Train/val/test splits (80/10/10 by patient)
- Model artifacts (trained model, scaler, feature names)
- Evaluation results & visualizations

---

## Module Dependencies

```
data_ingestion.py
    ↓
feature_engineering.py
    ↓
baseline_model.py ← evaluation.py
    ↓
explanation.py
    ↓
simulator.py
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Data quality issues | Implement comprehensive validation checks |
| Class imbalance | Use SMOTE + multiple metrics (AUPRC) |
| Overfitting | Patient-level splits + cross-validation |
| Poor interpretability | Use logistic regression baseline + SHAP |
| Slow training | Start with small feature set, optimize later |

---

## Success Metrics (Final)

| Metric | Target | Status |
|--------|--------|--------|
| AUROC | ≥ 0.80 | TBD |
| AUPRC | ≥ 0.60 | TBD |
| Sensitivity@FPR=0.10 | ≥ 0.70 | TBD |
| Median Hours Early | ≥ 3 hours | TBD |
| Brier Score | < 0.15 | TBD |
| Interpretability | Top 5 features clinically relevant | TBD |

---

## References

- PhysioNet Challenge 2019: https://physionet.org/content/challenge-2019/
- Sepsis-3 Consensus: https://jamanetwork.com/journals/jama/fullarticle/2492881
- SHAP Documentation: https://shap.readthedocs.io/
- Scikit-learn: https://scikit-learn.org/
