# Data Schema: PhysioNet Challenge 2019 Sepsis Dataset

## Raw Data Format

### Patient Files
**Location**: `data/training_data/` (user-provided)

**Format**: Pipe-delimited text files, one per patient
**Filename**: `{patient_id}.psv` (e.g., `p000001.psv`)

**Columns** (in order):
```
Hour | HR | SBP | DBP | MAP | RR | SpO2 | Temp | WBC | Lactate | Glucose | Creatinine | Platelets | Hemoglobin
```

**Data Types**:
- Hour: Integer (0, 1, 2, ...)
- All measurements: Float (missing values represented as NaN or empty)

**Example**:
```
Hour|HR|SBP|DBP|MAP|RR|SpO2|Temp|WBC|Lactate|Glucose|Creatinine|Platelets|Hemoglobin
0|85.0|120.0|70.0|86.7|16.0|98.0|37.2|7.5|1.2|110.0|0.9|250.0|14.5
1|87.0|118.0|68.0|84.7|17.0|97.5|37.1||1.3|112.0|0.9|248.0|14.4
2|||||||||||||
3|88.0|119.0|69.0|85.7|16.5|98.2|37.3|7.6||111.0|0.9|251.0|14.6
```

### Labels File
**Location**: `data/training_data/` (user-provided)

**Filename**: `sepsis_labels.csv`

**Format**: CSV with headers

**Columns**:
```
patient_id,sepsis_label,sepsis_onset_hour
```

**Data Types**:
- patient_id: String (e.g., "p000001")
- sepsis_label: Integer (0 = no sepsis, 1 = sepsis)
- sepsis_onset_hour: Integer or NaN (hour when sepsis criteria met; NaN if no sepsis)

**Example**:
```
patient_id,sepsis_label,sepsis_onset_hour
p000001,1,24
p000002,0,
p000003,1,18
```

## Processed Data Format

### Patient-Hour Dataset
**Output**: `data/processed/patient_hours.csv`

**One row per patient-hour** with engineered features and label.

**Columns**:
```
patient_id | hour | label_sepsis_6h | 
HR | HR_mean_6h | HR_std_6h | HR_trend_6h | HR_missing |
SBP | SBP_mean_6h | SBP_std_6h | SBP_trend_6h | SBP_missing |
DBP | DBP_mean_6h | DBP_std_6h | DBP_trend_6h | DBP_missing |
MAP | MAP_mean_6h | MAP_std_6h | MAP_trend_6h | MAP_missing |
RR | RR_mean_6h | RR_std_6h | RR_trend_6h | RR_missing |
SpO2 | SpO2_mean_6h | SpO2_std_6h | SpO2_trend_6h | SpO2_missing |
Temp | Temp_mean_6h | Temp_std_6h | Temp_trend_6h | Temp_missing |
WBC | WBC_mean_6h | WBC_std_6h | WBC_trend_6h | WBC_missing |
Lactate | Lactate_mean_6h | Lactate_std_6h | Lactate_trend_6h | Lactate_missing |
Glucose | Glucose_mean_6h | Glucose_std_6h | Glucose_trend_6h | Glucose_missing |
Creatinine | Creatinine_mean_6h | Creatinine_std_6h | Creatinine_trend_6h | Creatinine_missing |
Platelets | Platelets_mean_6h | Platelets_std_6h | Platelets_trend_6h | Platelets_missing |
Hemoglobin | Hemoglobin_mean_6h | Hemoglobin_std_6h | Hemoglobin_trend_6h | Hemoglobin_missing |
n_missing_values
```

**Data Types**:
- patient_id: String
- hour: Integer
- label_sepsis_6h: Integer (0/1)
- All measurements: Float (NaN if not available)
- All _missing flags: Integer (0/1)
- n_missing_values: Integer (count of missing measurements at this hour)

**Example Row**:
```
patient_id=p000001, hour=5, label_sepsis_6h=0,
HR=87.0, HR_mean_6h=86.2, HR_std_6h=1.5, HR_trend_6h=0.3, HR_missing=0,
SBP=119.0, SBP_mean_6h=119.2, SBP_std_6h=0.8, SBP_trend_6h=-0.1, SBP_missing=0,
...
n_missing_values=2
```

## Feature Engineering Details

### Rolling Window Statistics
For each vital/lab measurement at hour `t`:
- **6-hour window**: Hours [t-5, t-4, ..., t]
- **12-hour window**: Hours [t-11, t-10, ..., t]
- **Statistics computed**:
  - Mean (average of available values)
  - Std dev (standard deviation of available values)
  - Min, Max (if needed)
  - Trend: Linear regression slope (hours vs. values)

### Missingness Handling
- **Missing indicator**: Binary flag (1 if value is NaN at hour t, 0 otherwise)
- **Rolling stats**: Computed only on available values (ignore NaN)
- **Rows with >50% missing**: Optionally excluded from training

### Label Creation (Lookahead)
For each patient-hour `t`:
- **label_sepsis_6h = 1** if sepsis_onset_hour ∈ [t+1, t+6]
- **label_sepsis_6h = 0** otherwise
- **Rows where t+6 > max_hour**: Excluded (cannot determine label)

## Data Splits

### Train/Val/Test Split
**Strategy**: Patient-level stratified split

- **Train**: 80% of patients (all their hours)
- **Validation**: 10% of patients (all their hours)
- **Test**: 10% of patients (all their hours)

**Stratification**: By sepsis label (ensure similar prevalence in each split)

**Example**:
- Total patients: 1000
- Sepsis patients: 200 (20%)
- Train: 800 patients (160 sepsis, 640 non-sepsis)
- Val: 100 patients (20 sepsis, 80 non-sepsis)
- Test: 100 patients (20 sepsis, 80 non-sepsis)

## Class Imbalance

**Prevalence**: ~20% sepsis cases (typical for ICU data)

**Handling**:
- **Training**: Apply SMOTE to balance classes
- **Validation/Test**: Keep original distribution (for realistic evaluation)

## Data Quality Checks

**Validation steps**:
1. Check for required columns
2. Verify Hour is sequential (0, 1, 2, ...)
3. Check for duplicate patient-hours
4. Verify label consistency (sepsis_onset_hour ≤ max_hour)
5. Flag patients with >80% missing data
6. Check for outliers (e.g., HR > 200 or < 20)

## File Organization

```
data/
├── training_data/
│   ├── p000001.psv
│   ├── p000002.psv
│   ├── ...
│   └── sepsis_labels.csv
├── processed/
│   ├── patient_hours.csv          # Full engineered dataset
│   ├── train_indices.pkl          # Patient IDs in train set
│   ├── val_indices.pkl            # Patient IDs in val set
│   └── test_indices.pkl           # Patient IDs in test set
└── splits/
    ├── X_train.csv
    ├── y_train.csv
    ├── X_val.csv
    ├── y_val.csv
    ├── X_test.csv
    └── y_test.csv
```
