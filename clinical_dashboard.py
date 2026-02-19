"""
ICU Sepsis Early Warning System - Clinical Dashboard
Clean, user-friendly interface for sepsis risk assessment
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_ingestion_v2 import DataIngestionModule
from model_training import ImbalanceAwareModelTrainer
from calibration_and_thresholds import CalibrationAndThresholdOptimizer
from explanation import ClinicalExplainer

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="ICU Sepsis Early Warning",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional appearance
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .risk-high {
        background-color: #ffe6e6;
        border-left: 4px solid #dc3545;
        padding: 1rem;
        border-radius: 0.25rem;
    }
    .risk-moderate {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        border-radius: 0.25rem;
    }
    .risk-low {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# LOAD MODELS FUNCTION
# ============================================================================

def load_models():
    """Load and train models."""
    # Load data
    possible_paths = [
        "icu-early-warning/Dataset.csv",
        "Dataset.csv",
        "../Dataset.csv",
    ]
    
    dataset_path = None
    for path in possible_paths:
        if os.path.exists(path):
            dataset_path = path
            break
    
    if dataset_path is None:
        st.error("Dataset.csv not found!")
        st.stop()
    
    # Ingest data
    ingestion = DataIngestionModule(dataset_path)
    df, report = ingestion.run_validation()
    
    # Identify target column
    target_col = None
    for col in df.columns:
        if 'sepsis' in col.lower() or 'target' in col.lower() or 'label' in col.lower():
            target_col = col
            break
    
    if target_col is None:
        st.error("Target column not found!")
        st.stop()
    
    # Train models
    trainer = ImbalanceAwareModelTrainer(df, target_col=target_col)
    trainer.run_training_pipeline()
    
    # Calibrate
    y_pred_proba = trainer.model_weighted.predict_proba(trainer.X_test)[:, 1]
    calibrator = CalibrationAndThresholdOptimizer(
        trainer.y_test.values,
        y_pred_proba,
        trainer.model_weighted
    )
    calibrator.evaluate_calibration()
    calibrator.apply_calibration()
    
    # Create explainer
    explainer = ClinicalExplainer(
        trainer.model_weighted,
        trainer.X_train,
        trainer.X_test,
        trainer.y_test,
        trainer.X_test.columns.tolist()
    )
    
    return trainer, calibrator, explainer, df

# ============================================================================
# HEADER
# ============================================================================

st.title("🏥 ICU Sepsis Early Warning System")
st.markdown("""
**Clinical Decision Support Tool**

This system provides real-time sepsis risk assessment based on patient vital signs and laboratory values. 
Use this tool to identify high-risk patients requiring immediate clinical evaluation.
""")

st.divider()

# ============================================================================
# LOAD MODELS (ONCE PER SESSION)
# ============================================================================

if 'models_loaded' not in st.session_state:
    with st.spinner("Loading models... This may take 30-60 seconds on first run."):
        trainer, calibrator, explainer, df = load_models()
        st.session_state.trainer = trainer
        st.session_state.calibrator = calibrator
        st.session_state.explainer = explainer
        st.session_state.df = df
        st.session_state.models_loaded = True
else:
    trainer = st.session_state.trainer
    calibrator = st.session_state.calibrator
    explainer = st.session_state.explainer
    df = st.session_state.df

# ============================================================================
# SIDEBAR - USER INPUTS
# ============================================================================

st.sidebar.header("📋 Patient Vital Signs")
st.sidebar.markdown("Enter patient measurements:")

# Extract numeric columns for input
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

# Create input dictionary
patient_data = {}

# Key vital signs with clinical ranges
vital_signs = {
    'HR': {'label': 'Heart Rate (bpm)', 'min': 40, 'max': 180, 'default': 80, 'step': 1},
    'SBP': {'label': 'Systolic BP (mmHg)', 'min': 60, 'max': 220, 'default': 120, 'step': 1},
    'DBP': {'label': 'Diastolic BP (mmHg)', 'min': 30, 'max': 140, 'default': 80, 'step': 1},
    'O2Sat': {'label': 'Oxygen Saturation (%)', 'min': 70, 'max': 100, 'default': 95, 'step': 1},
    'Temp': {'label': 'Temperature (°C)', 'min': 35.0, 'max': 42.0, 'default': 37.0, 'step': 0.5},
    'Resp': {'label': 'Respiratory Rate (breaths/min)', 'min': 8, 'max': 50, 'default': 16, 'step': 1},
    'WBC': {'label': 'WBC (K/µL)', 'min': 1.0, 'max': 30.0, 'default': 7.0, 'step': 0.5},
    'Lactate': {'label': 'Lactate (mmol/L)', 'min': 0.5, 'max': 10.0, 'default': 1.5, 'step': 0.5},
}

# Create sliders for available vital signs
for feature, config in vital_signs.items():
    if feature in numeric_cols:
        patient_data[feature] = st.sidebar.slider(
            config['label'],
            min_value=config['min'],
            max_value=config['max'],
            value=config['default'],
            step=config['step']
        )

# Add other numeric features if available
st.sidebar.markdown("---")
st.sidebar.subheader("Additional Parameters")

# Add gender dropdown
if 'gender' in df.columns:
    patient_data['gender'] = st.sidebar.selectbox(
        "Gender",
        options=['Male', 'Female'],
        index=0
    )

for col in numeric_cols:
    if col not in patient_data and col not in ['SepsisLabel', 'sepsis', 'target', 'label', 'gender']:
        if col not in vital_signs:
            min_val = float(df[col].min())
            max_val = float(df[col].max())
            default_val = float(df[col].median())
            
            patient_data[col] = st.sidebar.slider(
                f"{col}",
                min_value=min_val,
                max_value=max_val,
                value=default_val,
                step=(max_val - min_val) / 100
            )

# Clinical threshold selection
st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Alert Threshold")
threshold_option = st.sidebar.radio(
    "Select sensitivity level:",
    options=["High Sensitivity (0.05)", "Balanced (0.25)", "High Specificity (0.50)"],
    help="High Sensitivity: Catch more cases but more false alarms\nBalanced: Recommended for most settings\nHigh Specificity: Fewer false alarms but may miss cases"
)

threshold_map = {
    "High Sensitivity (0.05)": 0.05,
    "Balanced (0.25)": 0.25,
    "High Specificity (0.50)": 0.50
}
selected_threshold = threshold_map[threshold_option]

# ============================================================================
# MAIN CONTENT - RISK ASSESSMENT
# ============================================================================

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Risk Assessment")
    
    # Calculate button
    if st.button("🔍 Calculate Sepsis Risk", use_container_width=True, type="primary"):
        
        # Prepare patient data for model
        patient_df = pd.DataFrame([patient_data])
        
        # Encode gender if present
        if 'gender' in patient_df.columns:
            patient_df['gender'] = (patient_df['gender'] == 'Male').astype(int)
        
        # Ensure all features from training are present
        for col in trainer.X_test.columns:
            if col not in patient_df.columns:
                patient_df[col] = 0  # Fill missing with 0
        
        # Reorder columns to match training
        patient_df = patient_df[trainer.X_test.columns]
        
        # Get prediction
        risk_probability = trainer.model_weighted.predict_proba(patient_df)[0, 1]
        
        # Determine risk level
        if risk_probability >= selected_threshold:
            alert_status = "🚨 ALERT"
            risk_level = "HIGH"
            risk_color = "risk-high"
            recommendation = "Immediate clinical evaluation recommended"
        elif risk_probability >= selected_threshold * 0.6:
            alert_status = "⚠️ WARNING"
            risk_level = "MODERATE"
            risk_color = "risk-moderate"
            recommendation = "Close monitoring and evaluation recommended"
        else:
            alert_status = "✅ LOW RISK"
            risk_level = "LOW"
            risk_color = "risk-low"
            recommendation = "Continue routine monitoring"
        
        # Display risk percentage
        st.markdown(f"""
        <div class="{risk_color}">
            <h2 style="margin: 0; text-align: center;">{alert_status}</h2>
            <h1 style="margin: 0.5rem 0; text-align: center; font-size: 3rem;">{risk_probability:.1%}</h1>
            <p style="margin: 0; text-align: center; font-size: 1.1rem;">Sepsis Risk Probability</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        **Threshold Used**: {selected_threshold:.2f}  
        **Risk Level**: {risk_level}  
        **Clinical Action**: {recommendation}
        """)
        
        st.divider()
        
        # ====================================================================
        # EXPLANATION
        # ====================================================================
        
        st.subheader("📊 Clinical Explanation")
        
        # Get feature contributions
        coefficients = trainer.model_weighted.coef_[0]
        contributions = patient_df.iloc[0].values * coefficients
        
        # Create contribution dataframe
        contrib_df = pd.DataFrame({
            'Feature': trainer.X_test.columns,
            'Value': patient_df.iloc[0].values,
            'Coefficient': coefficients,
            'Contribution': contributions,
            'Abs_Contribution': np.abs(contributions)
        })
        
        # Sort by absolute contribution
        contrib_df = contrib_df.sort_values('Abs_Contribution', ascending=False)
        top_3 = contrib_df.head(3)
        
        # Display top 3 contributing features
        st.markdown("**Top 3 Contributing Factors:**")
        
        for idx, (_, row) in enumerate(top_3.iterrows(), 1):
            feature = row['Feature']
            value = row['Value']
            contribution = row['Contribution']
            direction = "↑ Increases" if contribution > 0 else "↓ Decreases"
            
            col_a, col_b = st.columns([1, 3])
            with col_a:
                st.metric(f"#{idx}", f"{value:.2f}")
            with col_b:
                st.write(f"**{feature}** - {direction} risk")
        
        st.divider()
        
        # ====================================================================
        # CLINICAL NARRATIVE
        # ====================================================================
        
        st.subheader("📋 Clinical Summary")
        
        # Generate narrative
        risk_factors = []
        protective_factors = []
        
        for _, row in top_3.iterrows():
            if row['Contribution'] > 0:
                risk_factors.append(row['Feature'])
            else:
                protective_factors.append(row['Feature'])
        
        narrative = f"""
**Patient Risk Assessment Summary**

The model predicts a **{risk_probability:.1%}** probability of sepsis for this patient.

**Key Findings:**
"""
        
        if risk_factors:
            narrative += f"\n- Risk-increasing factors: {', '.join(risk_factors)}"
        if protective_factors:
            narrative += f"\n- Protective factors: {', '.join(protective_factors)}"
        
        narrative += f"""

**Clinical Recommendation:**
Based on this assessment, {recommendation.lower()}

**Important Notes:**
- This tool is a clinical decision support system, not a diagnostic tool
- All recommendations should be integrated with comprehensive clinical assessment
- Consider clinical context, patient history, and other diagnostic criteria
- Sepsis diagnosis requires clinical evaluation per SIRS, qSOFA, or SOFA criteria
"""
        
        st.info(narrative)
        
        st.divider()
        
        # ====================================================================
        # DISCLAIMER
        # ====================================================================
        
        st.markdown("""
        <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 0.5rem; margin-top: 2rem;">
            <p style="margin: 0; font-size: 0.9rem; color: #666;">
                <strong>⚕️ Clinical Disclaimer:</strong> This system is a research tool for clinical decision support only. 
                It should not replace clinical judgment or established diagnostic criteria. All clinical decisions should be made 
                by qualified healthcare professionals based on comprehensive patient assessment.
            </p>
        </div>
        """, unsafe_allow_html=True)

with col2:
    st.subheader("ℹ️ Quick Reference")
    
    st.markdown("""
    **Risk Levels:**
    - 🟢 **Low**: <25%
    - 🟡 **Moderate**: 25-50%
    - 🔴 **High**: >50%
    
    **Key Indicators:**
    - Shock Index (HR/SBP)
    - Blood Pressure
    - Lactate
    - Temperature
    - WBC
    
    **When to Alert:**
    - Risk ≥ threshold
    - Rapid deterioration
    - Multiple abnormalities
    """)

# ============================================================================
# FOOTER
# ============================================================================

st.divider()

st.markdown("""
---
**ICU Sepsis Early Warning System** | Clinical Decision Support Tool

Version 1.0 | Last Updated: February 19, 2026

For questions or feedback, contact your clinical informatics team.
""")
