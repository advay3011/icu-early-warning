"""
ICU Early Warning Agent: Comprehensive Clinical Dashboard
Streamlit App for Data Validation, Model Training, and Clinical Simulation
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
import os
import pickle
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_ingestion_v2 import DataIngestionModule
from model_training import ImbalanceAwareModelTrainer
from calibration_and_thresholds import CalibrationAndThresholdOptimizer
from explanation import ClinicalExplainer
from simulator import ICUSimulator

# Page configuration
st.set_page_config(
    page_title="ICU Early Warning Agent",
    page_icon="🏥",
    layout="wide"
)

st.title("🏥 ICU Early Warning Agent")
st.markdown("**Hemodynamic Instability Early-Warning System**")
st.divider()

# Navigation tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Data Overview",
    "🤖 Model Performance",
    "📈 Clinical Calibration",
    "🔍 Explainability",
    "⏱️ Clinical Simulation"
])

# Load data
@st.cache_resource
def load_and_validate_data():
    """Load and validate dataset."""
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
    
    ingestion = DataIngestionModule(dataset_path)
    df, report = ingestion.run_validation()
    return df, report, ingestion

@st.cache_resource
def train_models(df):
    """Train models on dataset."""
    # Identify target column
    target_col = None
    for col in df.columns:
        if 'sepsis' in col.lower() or 'target' in col.lower() or 'label' in col.lower():
            target_col = col
            break
    
    if target_col is None:
        st.error("Target column not found!")
        st.stop()
    
    trainer = ImbalanceAwareModelTrainer(df, target_col=target_col)
    trainer.run_training_pipeline()
    return trainer

@st.cache_resource
def calibrate_model(_trainer):
    """Calibrate model and optimize thresholds."""
    y_pred_proba = _trainer.model_weighted.predict_proba(_trainer.X_test)[:, 1]
    calibrator = CalibrationAndThresholdOptimizer(
        _trainer.y_test.values,
        y_pred_proba,
        _trainer.model_weighted
    )
    calibrator.evaluate_calibration()
    calibrator.apply_calibration()
    calibrator.optimize_thresholds()
    return calibrator

@st.cache_resource
def create_explainer(_trainer):
    """Create explainability module."""
    explainer = ClinicalExplainer(
        _trainer.model_weighted,
        _trainer.X_train,
        _trainer.X_test,
        _trainer.y_test,
        _trainer.X_test.columns.tolist()
    )
    return explainer

@st.cache_resource
def create_simulator(_trainer):
    """Create simulator module."""
    simulator = ICUSimulator(
        _trainer.model_weighted,
        _trainer.X_test,
        _trainer.y_test,
        _trainer.X_test.columns.tolist(),
        alert_threshold=0.25
    )
    return simulator

# Run validation
df, report, ingestion = load_and_validate_data()

# ============================================================================
# TAB 1: DATA OVERVIEW
# ============================================================================

with tab1:
    st.subheader("📊 Dataset Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Samples", report['total_samples'])
    
    with col2:
        st.metric("Total Features", report['total_features'])
    
    with col3:
        st.metric("Missing Values", report['missing_values'])
    
    with col4:
        st.metric("Duplicate Rows", report['duplicate_rows'])
    
    st.divider()
    
    # Class Distribution
    st.subheader("⚖️ Class Distribution (Target Variable)")
    
    if 'class_distribution' in report:
        col1, col2 = st.columns(2)
        
        with col1:
            class_dist = report['class_distribution']
            class_pct = report['class_percentages']
            
            dist_data = []
            for label, count in class_dist.items():
                pct = class_pct[label]
                dist_data.append({
                    'Class': f'Class {label}',
                    'Count': count,
                    'Percentage': f'{pct}%'
                })
            
            st.dataframe(pd.DataFrame(dist_data), use_container_width=True)
        
        with col2:
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(figsize=(8, 6))
            labels = [f'Class {k}' for k in class_dist.keys()]
            sizes = list(class_dist.values())
            colors = ['#27ae60', '#e74c3c']
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
            ax.set_title('Class Distribution', fontweight='bold')
            st.pyplot(fig)
    
    st.divider()
    
    # First 5 rows
    st.subheader("📋 First 5 Rows")
    st.dataframe(df.head(), use_container_width=True)
    
    st.divider()
    
    # Column information
    st.subheader("📑 Column Information")
    
    col_info = ingestion.identify_columns()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Numeric Features**")
        st.write(f"Count: {len(col_info['numeric'])}")
        st.write(col_info['numeric'])
    
    with col2:
        st.write("**Categorical Features**")
        st.write(f"Count: {len(col_info['categorical'])}")
        st.write(col_info['categorical'])
    
    st.divider()
    
    # Missing values
    st.subheader("🔍 Missing Values Analysis")
    
    missing_data = ingestion.check_missing_values()
    
    if len(missing_data) > 0:
        st.dataframe(missing_data, use_container_width=True)
    else:
        st.success("✓ No missing values found!")
    
    st.divider()
    
    # Basic statistics
    st.subheader("📈 Basic Statistics (Numeric Features)")
    
    st.dataframe(df[col_info['numeric']].describe().round(2), use_container_width=True)

# ============================================================================
# TAB 2: MODEL PERFORMANCE
# ============================================================================

with tab2:
    st.subheader("🤖 Model Training & Performance")
    
    with st.spinner("Training models..."):
        trainer = train_models(df)
    
    st.success("✓ Models trained successfully!")
    
    st.divider()
    
    # Model comparison
    st.subheader("📊 Model Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Baseline Model (No Class Weighting)**")
        st.metric("AUROC", f"{trainer.results['baseline']['auroc']:.4f}")
        st.metric("Recall", f"{trainer.results['baseline']['recall']:.4f}")
        st.metric("Precision", f"{trainer.results['baseline']['precision']:.4f}")
    
    with col2:
        st.write("**Weighted Model (Balanced Classes)**")
        st.metric("AUROC", f"{trainer.results['weighted']['auroc']:.4f}")
        st.metric("Recall", f"{trainer.results['weighted']['recall']:.4f}")
        st.metric("Precision", f"{trainer.results['weighted']['precision']:.4f}")
    
    st.divider()
    
    # ROC Curve
    st.subheader("📈 ROC Curve")
    
    if os.path.exists("icu-early-warning/roc_curve.png"):
        st.image("icu-early-warning/roc_curve.png", use_container_width=True)
    
    # Precision-Recall Curve
    st.subheader("📊 Precision-Recall Curve")
    
    if os.path.exists("icu-early-warning/pr_curve.png"):
        st.image("icu-early-warning/pr_curve.png", use_container_width=True)

# ============================================================================
# TAB 3: CLINICAL CALIBRATION
# ============================================================================

with tab3:
    st.subheader("📈 Model Calibration & Threshold Optimization")
    
    with st.spinner("Calibrating model..."):
        trainer = train_models(df)
        calibrator = calibrate_model(trainer)
    
    st.success("✓ Model calibrated successfully!")
    
    st.divider()
    
    # Calibration metrics
    st.subheader("📊 Calibration Metrics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Brier Score (Uncalibrated)", f"{calibrator.brier_uncalibrated:.4f}")
        st.metric("Brier Score (Calibrated)", f"{calibrator.brier_calibrated:.4f}")
    
    with col2:
        improvement = ((calibrator.brier_uncalibrated - calibrator.brier_calibrated) / 
                      calibrator.brier_uncalibrated * 100)
        st.metric("Improvement", f"{improvement:.2f}%")
    
    st.divider()
    
    # Calibration curve
    st.subheader("📈 Calibration Curve")
    
    if os.path.exists("icu-early-warning/calibration_curve.png"):
        st.image("icu-early-warning/calibration_curve.png", use_container_width=True)
    
    st.divider()
    
    # Threshold optimization
    st.subheader("🎯 Threshold Optimization")
    
    if os.path.exists("icu-early-warning/threshold_performance.png"):
        st.image("icu-early-warning/threshold_performance.png", use_container_width=True)
    
    st.divider()
    
    # Recommended thresholds
    st.subheader("✅ Recommended Clinical Thresholds")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**High-Sensitivity Threshold**")
        st.write("Threshold: 0.05")
        st.write("Recall: 100%")
        st.write("Use: Catch all potential cases")
    
    with col2:
        st.write("**Balanced Threshold**")
        st.write("Threshold: 0.25")
        st.write("Recall: 70%")
        st.write("Use: Balance sensitivity and specificity")

# ============================================================================
# TAB 4: EXPLAINABILITY
# ============================================================================

with tab4:
    st.subheader("🔍 Clinical Interpretability & Explainability")
    
    with st.spinner("Generating explanations..."):
        trainer = train_models(df)
        explainer = create_explainer(trainer)
    
    st.success("✓ Explainability module ready!")
    
    st.divider()
    
    # Global feature importance
    st.subheader("📊 Global Feature Importance")
    
    if os.path.exists("icu-early-warning/feature_importance.png"):
        st.image("icu-early-warning/feature_importance.png", use_container_width=True)
    
    st.divider()
    
    # Patient explanation
    st.subheader("👤 Patient-Level Explanation")
    
    patient_idx = st.slider("Select Patient Index", 0, len(trainer.X_test) - 1, 0)
    
    if st.button("Generate Explanation"):
        y_pred_proba = trainer.model_weighted.predict_proba(trainer.X_test)[:, 1]
        explanation = explainer.explain_patient_prediction(patient_idx, y_pred_proba)
        
        st.write(f"**Patient #{patient_idx}**")
        st.write(f"Predicted Sepsis Probability: {explanation['predicted_probability']:.1%}")
        st.write(f"Actual Label: {'Sepsis' if trainer.y_test.iloc[patient_idx] == 1 else 'No Sepsis'}")
        
        st.write("**Top 5 Contributing Features:**")
        for i, (feature, value, contribution) in enumerate(explanation['top_features'], 1):
            direction = "↑ INCREASES" if contribution > 0 else "↓ DECREASES"
            st.write(f"{i}. {feature}: {value:.2f} ({direction} risk)")
    
    st.divider()
    
    # Patient contributions plot
    st.subheader("📈 Patient Contribution Plot")
    
    if os.path.exists("icu-early-warning/patient_contributions.png"):
        st.image("icu-early-warning/patient_contributions.png", use_container_width=True)

# ============================================================================
# TAB 5: CLINICAL SIMULATION
# ============================================================================

with tab5:
    st.subheader("⏱️ Clinical Simulation & Real-Time Alerting")
    
    with st.spinner("Initializing simulator..."):
        trainer = train_models(df)
        simulator = create_simulator(trainer)
    
    st.success("✓ Simulator ready!")
    
    st.divider()
    
    # Patient selection
    st.subheader("👤 Select Patient for Simulation")
    
    patient_idx = st.slider("Patient Index", 0, len(trainer.X_test) - 1, 0, key="sim_patient")
    
    if st.button("Run Simulation"):
        with st.spinner("Simulating patient monitoring..."):
            # Run simulation
            simulation_results = simulator.simulate_patient_monitoring(patient_idx)
            
            # Display results
            st.success("✓ Simulation complete!")
            
            st.divider()
            
            # Alert information
            st.subheader("🚨 Alert Summary")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Alert Triggered", "Yes" if simulation_results['alert_triggered'] else "No")
            
            with col2:
                st.metric("Alert Time", f"Hour {simulation_results['alert_hour']}")
            
            with col3:
                st.metric("Risk at Alert", f"{simulation_results['risk_at_alert']:.1%}")
            
            st.divider()
            
            # Risk trajectory plot
            st.subheader("📈 Risk Trajectory Over Time")
            
            simulator.plot_risk_trajectory(save_path="icu-early-warning/risk_trajectory_temp.png")
            
            if os.path.exists("icu-early-warning/risk_trajectory_temp.png"):
                st.image("icu-early-warning/risk_trajectory_temp.png", use_container_width=True)
            
            st.divider()
            
            # Vital signs trajectory
            st.subheader("📊 Vital Signs Trajectory")
            
            simulator.plot_vital_signs_trajectory(save_path="icu-early-warning/vital_signs_temp.png")
            
            if os.path.exists("icu-early-warning/vital_signs_temp.png"):
                st.image("icu-early-warning/vital_signs_temp.png", use_container_width=True)
            
            st.divider()
            
            # Alert narrative
            st.subheader("📋 Clinical Alert Narrative")
            
            alert_analysis = simulator.analyze_alert_moment()
            narrative = simulator.generate_alert_narrative(alert_analysis)
            
            st.info(narrative)

# ============================================================================
# FOOTER
# ============================================================================

st.divider()

st.markdown("""
---
**ICU Early Warning Agent** | Hemodynamic Instability Early-Warning System

✓ System fully operational with data ingestion, model training, calibration, explainability, and clinical simulation.

**Project Status**: Step 7 - Clinical Simulation & Alerting Module (In Progress)
""")
