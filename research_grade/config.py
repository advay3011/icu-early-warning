"""
Configuration and constants for ICU Sepsis Early Warning System
Research-grade clinical decision support tool
"""

# Model Configuration
MODEL_CONFIG = {
    'algorithm': 'Logistic Regression with class_weight=balanced',
    'test_size': 0.2,
    'random_state': 42,
    'cv_folds': 5,
    'stratified': True,
}

# Clinical Feature Definitions with Reference Ranges
CLINICAL_FEATURES = {
    'HR': {
        'label': 'Heart Rate',
        'unit': 'bpm',
        'normal_range': (60, 100),
        'critical_low': 40,
        'critical_high': 180,
        'clinical_significance': 'Tachycardia (>100) indicates sympathetic activation; common in sepsis'
    },
    'SBP': {
        'label': 'Systolic Blood Pressure',
        'unit': 'mmHg',
        'normal_range': (100, 140),
        'critical_low': 90,
        'critical_high': 220,
        'clinical_significance': 'Hypotension (<90) indicates shock; critical in sepsis protocols'
    },
    'DBP': {
        'label': 'Diastolic Blood Pressure',
        'unit': 'mmHg',
        'normal_range': (60, 90),
        'critical_low': 50,
        'critical_high': 140,
        'clinical_significance': 'Used to calculate MAP and pulse pressure'
    },
    'O2Sat': {
        'label': 'Oxygen Saturation',
        'unit': '%',
        'normal_range': (95, 100),
        'critical_low': 88,
        'critical_high': 100,
        'clinical_significance': 'Hypoxemia (<90%) indicates respiratory compromise'
    },
    'Temp': {
        'label': 'Temperature',
        'unit': '°C',
        'normal_range': (36.5, 37.5),
        'critical_low': 35.0,
        'critical_high': 42.0,
        'clinical_significance': 'Fever (>38°C) is SIRS criterion; hypothermia (<36°C) is poor prognostic sign'
    },
    'Resp': {
        'label': 'Respiratory Rate',
        'unit': 'breaths/min',
        'normal_range': (12, 20),
        'critical_low': 8,
        'critical_high': 50,
        'clinical_significance': 'Tachypnea (>20) is SIRS criterion; indicates metabolic stress'
    },
    'WBC': {
        'label': 'White Blood Cell Count',
        'unit': 'K/µL',
        'normal_range': (4.5, 11.0),
        'critical_low': 1.0,
        'critical_high': 30.0,
        'clinical_significance': 'Elevated WBC (>12) or low (<4) is SIRS criterion; indicates infection/immune response'
    },
    'Lactate': {
        'label': 'Lactate',
        'unit': 'mmol/L',
        'normal_range': (0.5, 2.0),
        'critical_low': 0.5,
        'critical_high': 10.0,
        'clinical_significance': 'Elevated lactate (>2) indicates tissue hypoperfusion; strong sepsis marker'
    },
}

# Derived Clinical Features (Feature Engineering)
DERIVED_FEATURES = {
    'shock_index': {
        'label': 'Shock Index',
        'formula': 'HR / SBP',
        'normal_range': (0.5, 0.9),
        'critical_threshold': 0.9,
        'clinical_significance': 'Shock Index >0.9 indicates hemodynamic instability; combines HR and perfusion pressure'
    },
    'pulse_pressure': {
        'label': 'Pulse Pressure',
        'formula': 'SBP - DBP',
        'normal_range': (40, 60),
        'critical_low': 30,
        'critical_high': 80,
        'clinical_significance': 'Low pulse pressure (<30) suggests reduced cardiac output; high (>60) suggests arterial stiffness'
    },
    'MAP': {
        'label': 'Mean Arterial Pressure',
        'formula': '(SBP + 2*DBP) / 3',
        'normal_range': (70, 100),
        'critical_threshold': 65,
        'clinical_significance': 'MAP <65 mmHg indicates inadequate tissue perfusion; critical threshold in sepsis management'
    },
    'SIRS_score': {
        'label': 'SIRS Score',
        'formula': 'Sum of: Temp >38°C, HR >90, RR >20, WBC >12 or <4',
        'range': (0, 4),
        'critical_threshold': 2,
        'clinical_significance': '≥2 SIRS criteria + suspected infection = sepsis definition'
    },
}

# Alert Thresholds (Calibrated)
ALERT_THRESHOLDS = {
    'high_sensitivity': {
        'threshold': 0.05,
        'description': 'High Sensitivity (100% recall)',
        'use_case': 'High-risk patients, research settings',
        'expected_recall': 1.0,
        'expected_precision': 0.05,
    },
    'balanced': {
        'threshold': 0.25,
        'description': 'Balanced (Recommended)',
        'use_case': 'Standard ICU monitoring',
        'expected_recall': 0.70,
        'expected_precision': 0.40,
    },
    'high_specificity': {
        'threshold': 0.50,
        'description': 'High Specificity (Fewer false alarms)',
        'use_case': 'Resource-constrained settings',
        'expected_recall': 0.40,
        'expected_precision': 0.70,
    },
}

# SOFA Score Components (Parallel Reference Standard)
SOFA_COMPONENTS = {
    'respiration': {
        'label': 'Respiratory (PaO2/FiO2)',
        'normal': (>400, 0),
        'mild': (300-399, 1),
        'moderate': (200-299, 2),
        'severe': (100-199, 3),
        'critical': (<100, 4),
    },
    'coagulation': {
        'label': 'Coagulation (Platelets)',
        'normal': (>150, 0),
        'mild': (100-150, 1),
        'moderate': (50-99, 2),
        'severe': (20-49, 3),
        'critical': (<20, 4),
    },
    'liver': {
        'label': 'Liver (Bilirubin)',
        'normal': (<1.2, 0),
        'mild': (1.2-1.9, 1),
        'moderate': (2.0-5.9, 2),
        'severe': (6.0-11.9, 3),
        'critical': (>12.0, 4),
    },
    'cardiovascular': {
        'label': 'Cardiovascular (MAP/Vasopressors)',
        'normal': ('MAP ≥70', 0),
        'mild': ('MAP <70', 1),
        'moderate': ('Dopamine ≤5 or dobutamine', 2),
        'severe': ('Dopamine >5 or epinephrine ≤0.1', 3),
        'critical': ('Epinephrine >0.1 or norepinephrine', 4),
    },
    'cns': {
        'label': 'CNS (Glasgow Coma Scale)',
        'normal': (15, 0),
        'mild': (13-14, 1),
        'moderate': (10-12, 2),
        'severe': (6-9, 3),
        'critical': (<6, 4),
    },
    'renal': {
        'label': 'Renal (Creatinine/Urine Output)',
        'normal': ('<1.2', 0),
        'mild': ('1.2-1.9', 1),
        'moderate': ('2.0-3.4', 2),
        'severe': ('3.5-4.9', 3),
        'critical': ('>5.0', 4),
    },
}

# Clinical Literature References
CLINICAL_REFERENCES = {
    'shock_index': 'Cannon CM, et al. Shock Index predicts mortality in critically ill patients. Crit Care Med. 2009.',
    'lactate': 'Puskarich MA, et al. Prognostic value of blood lactate, pH, and base deficit in patients with sepsis. Am J Emerg Med. 2007.',
    'SIRS': 'Bone RC, et al. Definitions for sepsis and organ failure and guidelines for the use of innovative therapies in sepsis. Chest. 1992.',
    'MAP': 'Rivers E, et al. Early goal-directed therapy in the treatment of severe sepsis and septic shock. N Engl J Med. 2001.',
    'qSOFA': 'Singer M, et al. The Third International Consensus Definitions for Sepsis and Septic Shock (Sepsis-3). JAMA. 2016.',
}

# Dataset Information
DATASET_INFO = {
    'name': 'PhysioNet ICU Dataset',
    'size': '546,123 patient-hours',
    'patients': '~40,000',
    'sepsis_prevalence': '20%',
    'features': 44,
    'engineered_features': 51,
    'total_features': 95,
    'citation': 'PhysioNet Computing in Cardiology Challenge 2019',
    'url': 'https://physionet.org/content/challenge-2019/',
}

# Model Performance Targets
PERFORMANCE_TARGETS = {
    'auroc': 0.75,
    'recall': 0.70,
    'precision': 0.40,
    'f1': 0.15,
    'calibration_brier': 0.02,
}

# UI Configuration
UI_CONFIG = {
    'page_title': 'ICU Sepsis Early Warning System',
    'page_icon': '🏥',
    'layout': 'wide',
    'theme': 'light',
}

# Research Disclaimer
RESEARCH_DISCLAIMER = """
⚠️ **RESEARCH USE ONLY**

This system is a research prototype and NOT approved for clinical use.
- Not FDA approved
- Not validated for clinical decision-making
- Should NOT replace clinical judgment
- Intended for research and educational purposes only
- Requires clinical validation before deployment

For clinical use, consult qualified healthcare professionals.
"""
