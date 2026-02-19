# ICU Early Warning Agent: Detailed Specification

## 1. Problem Definition

### Clinical Context
Sepsis is a life-threatening condition requiring rapid recognition and treatment. Early detection from continuous ICU monitoring can enable timely intervention.

### Prediction Task
**Binary classification at each patient-hour:**
- **Positive class (1)**: Patient will develop sepsis within the next 6 hours
- **Negative class (0)**: Patient will not develop sepsis within the next 6 hours
- **Prediction point**: Each hour of ICU stay (sliding window)
- **Lookahead window**: 6 hours

### Output Format
For each patient-hour prediction:
```python
{
    "patient_id": str,
    "hour": int,
    "risk_score": float,  # [0, 1]
    "risk_level": str,    # "low" | "medium" | "high"
    "top_features": List[Tuple[str, float]],  # [(feature_name, importance), ...]
    "explanation": str,   # Natural language summary
}
```

## 2. Input Features

### Vital Signs (if available)
- Heart Rate (HR) [bpm]
- Systolic Blood Pressure (SBP) [mmHg]
- Diastolic Blood Pressure (DBP) [mmHg]
- Mean Arterial Pressure (MAP) [mmHg]
- Respiratory Rate (RR) [breaths/min]
- Oxygen Saturation (SpO2) [%]
- Temperature (Temp) [°C]

### Laboratory Values (if available)
- White Blood Cell count (WBC) [K/uL]
- Lactate [mmol/L]
- Glucose [mg/dL]
- Creatinine [mg/dL]
- Platelets [K/uL]
- Hemoglobin [g/dL]

### Derived Features
- **Missingness indicators**: Binary flags for each missing value
- **Rolling statistics** (last 6h, 12h windows):
  - Mean, std dev, min, max, trend (linear slope)
  - Rate of change (delta per hour)
- **Composite scores**:
  - qSOFA-like indicators (if components available)
  - Lactate elevation flag

## 3. Module Interfaces

### 3.1 Data Ingestion Module
**File**: `src/data_ingestion.py`

```python
class DataIngestionModule:
    def load_raw_data(data_dir: str) -> Dict[str, pd.DataFrame]:
        """
        Load all patient files from directory.
        Returns: {patient_id: patient_dataframe}
        """
        pass
    
    def validate_schema(df: pd.DataFrame) -> bool:
        """Validate that dataframe has required columns."""
        pass
    
    def parse_timestamps(df: pd.DataFrame) -> pd.DataFrame:
        """Convert time column to datetime, ensure hourly alignment."""
        pass
    
    def align_labels(df: pd.DataFrame, label_file: str) -> pd.DataFrame:
        """Merge sepsis labels with vital signs."""
        pass
```

### 3.2 Feature Engineering Module
**File**: `src/feature_engineering.py`

```python
class FeatureEngineeringModule:
    def create_patient_hours(df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert patient time-series to patient-hour rows.
        Each row = one patient-hour with features + label.
        """
        pass
    
    def compute_rolling_stats(df: pd.DataFrame, windows=[6, 12]) -> pd.DataFrame:
        """
        For each vital/lab, compute rolling mean/std/min/max/trend.
        """
        pass
    
    def add_missingness_flags(df: pd.DataFrame) -> pd.DataFrame:
        """Add binary indicators for missing values."""
        pass
    
    def create_lookahead_label(df: pd.DataFrame, lookahead_hours=6) -> pd.DataFrame:
        """
        Create binary label: will sepsis occur in next 6 hours?
        Drop rows where label cannot be determined (end of record).
        """
        pass
    
    def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
        """Orchestrate all feature engineering steps."""
        pass
```

### 3.3 Baseline Model Module
**File**: `src/baseline_model.py`

```python
class BaselineModel:
    def __init__(self, model_type: str = "logistic_regression"):
        """
        model_type: "logistic_regression" | "gradient_boosting"
        """
        pass
    
    def fit(X_train: pd.DataFrame, y_train: pd.Series) -> None:
        """Train on training set."""
        pass
    
    def predict_proba(X: pd.DataFrame) -> np.ndarray:
        """Return probability of sepsis (shape: [n_samples, 2])."""
        pass
    
    def predict(X: pd.DataFrame, threshold: float = 0.5) -> np.ndarray:
        """Return binary predictions."""
        pass
    
    def get_feature_importance() -> pd.DataFrame:
        """Return feature importance scores."""
        pass
```

### 3.4 Evaluation Module
**File**: `src/evaluation.py`

```python
class EvaluationModule:
    def compute_auroc(y_true: np.ndarray, y_pred_proba: np.ndarray) -> float:
        """Area under ROC curve."""
        pass
    
    def compute_auprc(y_true: np.ndarray, y_pred_proba: np.ndarray) -> float:
        """Area under Precision-Recall curve."""
        pass
    
    def compute_sensitivity_at_fpr(y_true, y_pred_proba, fpr_threshold=0.1) -> float:
        """Sensitivity at fixed false positive rate."""
        pass
    
    def compute_median_hours_early(y_true, y_pred_proba, patient_hours_df, threshold=0.5) -> float:
        """
        Among true positives, median hours before sepsis onset 
        that model crosses alert threshold.
        """
        pass
    
    def compute_calibration(y_true, y_pred_proba) -> Dict:
        """Brier score, calibration curve."""
        pass
    
    def evaluate_full(y_true, y_pred_proba, patient_hours_df) -> Dict:
        """Compute all metrics."""
        pass
```

### 3.5 Explanation Module
**File**: `src/explanation.py`

```python
class ExplanationModule:
    def __init__(self, model, X_train: pd.DataFrame):
        """Initialize with trained model and training data."""
        pass
    
    def get_feature_importance() -> pd.DataFrame:
        """Global feature importance (from model or SHAP)."""
        pass
    
    def explain_prediction(X_sample: pd.Series, top_k: int = 5) -> Dict:
        """
        Per-prediction explanation.
        Returns: {
            "top_features": [(name, contribution), ...],
            "summary": "Natural language explanation"
        }
        """
        pass
```

### 3.6 Simulator Module
**File**: `src/simulator.py`

```python
class PatientSimulator:
    def __init__(self, model, patient_df: pd.DataFrame):
        """Initialize with trained model and patient data."""
        pass
    
    def replay_timeline(alert_threshold: float = 0.5) -> List[Dict]:
        """
        Replay patient hour-by-hour, returning risk scores.
        Returns list of {hour, risk_score, risk_level, alert, explanation}
        """
        pass
    
    def plot_timeline() -> None:
        """Visualize risk score over time with sepsis onset marker."""
        pass
```

## 4. Data Schema

See `DATA_SCHEMA.md` for detailed format.

**Summary:**
- Raw data: Pipe-delimited files, one per patient
- Columns: Time, HR, SBP, DBP, MAP, RR, SpO2, Temp, WBC, Lactate, Glucose, Creatinine, Platelets, Hemoglobin
- Labels: Separate file with patient_id, sepsis_label (0/1), sepsis_onset_hour (if applicable)
- Processing: Convert to patient-hour rows with engineered features

## 5. Evaluation Plan

See `EVALUATION_PLAN.md` for full details.

**Summary:**
- **Split strategy**: Patient-level stratified split (80/10/10 train/val/test)
- **Class imbalance**: SMOTE on training set only
- **Metrics**: AUROC, AUPRC, sensitivity@FPR, median hours early, calibration
- **Baseline**: Logistic regression with standard features
- **Upgrade path**: Gradient boosting, feature selection, hyperparameter tuning

## 6. Implementation Roadmap

### Phase 1: Data & Baseline (Week 1)
- [ ] Implement data ingestion module
- [ ] Implement feature engineering module
- [ ] Create patient-hour dataset
- [ ] Implement baseline logistic regression
- [ ] Implement evaluation metrics

### Phase 2: Explanation & Simulation (Week 2)
- [ ] Implement explanation module (feature importance)
- [ ] Implement patient simulator
- [ ] Generate baseline results

### Phase 3: Model Improvements (Week 3)
- [ ] Hyperparameter tuning
- [ ] Feature selection
- [ ] Gradient boosting model
- [ ] Calibration improvements

### Phase 4: Validation & Documentation (Week 4)
- [ ] Cross-validation
- [ ] External validation (if data available)
- [ ] Final report generation
- [ ] Clinical interpretation

## 7. Success Criteria

- **AUROC ≥ 0.80** on test set
- **AUPRC ≥ 0.60** (accounting for class imbalance)
- **Median hours early ≥ 3** hours (true positives detected 3+ hours before onset)
- **Sensitivity ≥ 0.70** at FPR ≤ 0.10
- **Calibration**: Brier score < 0.15
- **Interpretability**: Top 5 features clearly identifiable per prediction
