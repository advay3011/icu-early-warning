"""
Research-grade Streamlit UI for ICU Sepsis Early Warning System
Includes model card, ROC curves, calibration plots, and clinical literature
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from config import (
    CLINICAL_FEATURES, ALERT_THRESHOLDS, RESEARCH_DISCLAIMER,
    CLINICAL_REFERENCES, DATASET_INFO, UI_CONFIG
)
from utils import (
    calculate_shock_index, calculate_map, calculate_pulse_pressure,
    calculate_sirs_score, check_abnormal_values, get_clinical_recommendation,
    format_confidence_interval, generate_clinical_narrative
)


def setup_page():
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title=UI_CONFIG['page_title'],
        page_icon=UI_CONFIG['page_icon'],
        layout=UI_CONFIG['layout'],
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .risk-high {
        background-color: #ffe6e6;
        border-left: 4px solid #ff4444;
        padding: 1rem;
        border-radius: 0.25rem;
    }
    .risk-moderate {
        background-color: #fff3cd;
        border-left: 4px solid #ffaa00;
        padding: 1rem;
        border-radius: 0.25rem;
    }
    .risk-low {
        background-color: #d4edda;
        border-left: 4px solid #44aa44;
        padding: 1rem;
        border-radius: 0.25rem;
    }
    .research-disclaimer {
        background-color: #fff3cd;
        border: 2px solid #ffaa00;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)


def render_header():
    """Render page header with disclaimer."""
    st.title("🏥 ICU Sepsis Early Warning System")
    st.markdown("**Research-Grade Clinical Decision Support Tool**")
    
    st.markdown(f"""
    <div class="research-disclaimer">
    {RESEARCH_DISCLAIMER}
    </div>
    """, unsafe_allow_html=True)


def render_model_card_tab():
    """Render Model Card tab with comprehensive documentation."""
    st.header("📋 Model Card")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Model Architecture")
        st.write("""
        - **Algorithm:** Logistic Regression with class_weight='balanced'
        - **Calibration:** Isotonic Regression
        - **Validation:** 5-fold Stratified Cross-Validation
        - **Features:** 51 engineered clinical features
        """)
        
        st.subheader("Training Data")
        st.write(f"""
        - **Dataset:** {DATASET_INFO['name']}
        - **Size:** {DATASET_INFO['size']}
        - **Patients:** {DATASET_INFO['patients']}
        - **Sepsis Prevalence:** {DATASET_INFO['sepsis_prevalence']}
        - **Citation:** {DATASET_INFO['citation']}
        """)
    
    with col2:
        st.subheader("Performance Metrics")
        st.write("""
        - **AUROC:** 0.7337
        - **Recall:** 63.8% (catches most sepsis cases)
        - **Precision:** 5.1%
        - **F1 Score:** 0.097
        - **Brier Score:** 0.0195 (calibration)
        """)
        
        st.subheader("Intended Use")
        st.write("""
        - Research and educational purposes
        - Clinical decision support (not diagnostic)
        - Requires clinical validation before deployment
        - NOT FDA approved
        """)
    
    st.divider()
    
    st.subheader("Known Limitations")
    st.write("""
    1. **Not FDA Approved:** This is a research prototype
    2. **Class Imbalance:** 20% positive class may affect generalization
    3. **Limited Scope:** Trained on ICU data; may not generalize to other settings
    4. **Requires Validation:** Clinical validation needed before deployment
    5. **Missing Features:** No real-time streaming, EHR integration, or medication history
    6. **Precision-Recall Trade-off:** Higher recall means more false alarms
    """)
    
    st.subheader("Ethical Considerations")
    st.write("""
    - **Bias:** Model trained on specific ICU population; may not generalize
    - **Fairness:** Requires evaluation across demographic groups
    - **Transparency:** All predictions should be explainable
    - **Accountability:** Clinical team responsible for final decisions
    - **Safety:** False negatives (missed sepsis) are more dangerous than false positives
    """)


def render_clinical_inputs_tab():
    """Render tab for clinical input with reference ranges."""
    st.header("📊 Patient Assessment")
    
    st.markdown("""
    Enter patient vital signs below. **Red values** indicate critical abnormalities.
    """)
    
    patient_data = {}
    
    # Create input columns
    col1, col2, col3 = st.columns(3)
    
    features_list = list(CLINICAL_FEATURES.keys())
    
    for idx, feature in enumerate(features_list):
        config = CLINICAL_FEATURES[feature]
        col = [col1, col2, col3][idx % 3]
        
        with col:
            st.markdown(f"**{config['label']}** ({config['unit']})")
            st.caption(f"Normal: {config['normal_range'][0]}-{config['normal_range'][1]}")
            
            value = st.number_input(
                label=f"{feature}_input",
                label_visibility="collapsed",
                min_value=config['critical_low'],
                max_value=config['critical_high'],
                value=config['normal_range'][0],
                step=1 if config['unit'] in ['bpm', 'breaths/min', '%'] else 0.1,
            )
            
            patient_data[feature] = value
    
    # Gender dropdown
    st.markdown("**Gender**")
    patient_data['gender'] = st.selectbox(
        "Select gender",
        options=['Male', 'Female'],
        label_visibility="collapsed"
    )
    
    return patient_data


def render_risk_assessment_tab(model, patient_data):
    """Render risk assessment with predictions and confidence intervals."""
    st.header("🔍 Risk Assessment")
    
    # Threshold selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        threshold_option = st.radio(
            "Select Alert Threshold:",
            options=list(ALERT_THRESHOLDS.keys()),
            format_func=lambda x: ALERT_THRESHOLDS[x]['description'],
            horizontal=True,
        )
    
    threshold = ALERT_THRESHOLDS[threshold_option]['threshold']
    
    # Make prediction
    if st.button("Calculate Sepsis Risk", type="primary", use_container_width=True):
        
        # Prepare data
        patient_df = pd.DataFrame([patient_data])
        
        # Get prediction with confidence interval
        pred_result = model.predict_with_confidence(patient_df, confidence=0.95)
        risk_prob = pred_result['prediction'][0]
        ci_lower = pred_result['ci_lower'][0]
        ci_upper = pred_result['ci_upper'][0]
        
        # Display risk
        recommendation = get_clinical_recommendation(risk_prob, threshold)
        
        st.markdown(f"""
        <div class="risk-{recommendation['alert_level'].lower()}">
        <h2>{recommendation['icon']} {recommendation['alert_level']} RISK</h2>
        <h1 style="font-size: 3rem; margin: 0.5rem 0;">{risk_prob:.1%}</h1>
        <p style="font-size: 1.1rem;">Sepsis Risk Probability</p>
        <p>95% CI: {ci_lower:.1%}–{ci_upper:.1%}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"**Recommendation:** {recommendation['recommendation']}")
        
        st.subheader("Recommended Actions:")
        for action in recommendation['actions']:
            st.write(f"• {action}")
        
        # Abnormality check
        abnormalities = check_abnormal_values(patient_data)
        if abnormalities:
            st.warning("⚠️ Abnormal Vital Signs Detected:")
            for abn in abnormalities:
                st.write(f"- {abn['label']}: {abn['value']} ({abn['severity']})")


def render_model_performance_tab(model):
    """Render model performance metrics and curves."""
    st.header("📈 Model Performance")
    
    tab1, tab2, tab3, tab4 = st.tabs(["ROC Curve", "Calibration", "Threshold Analysis", "Cross-Validation"])
    
    with tab1:
        st.subheader("ROC Curve")
        if model.roc_data:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=model.roc_data['fpr'],
                y=model.roc_data['tpr'],
                mode='lines',
                name=f"ROC (AUC = {model.roc_data['auc']:.4f})",
                line=dict(color='#1f77b4', width=2),
            ))
            fig.add_trace(go.Scatter(
                x=[0, 1], y=[0, 1],
                mode='lines',
                name='Random Classifier',
                line=dict(color='gray', dash='dash'),
            ))
            fig.update_layout(
                xaxis_title='False Positive Rate',
                yaxis_title='True Positive Rate',
                hovermode='closest',
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Calibration Curve")
        if model.calibration_data:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=model.calibration_data['prob_pred'],
                y=model.calibration_data['prob_true'],
                mode='markers+lines',
                name='Calibration',
                marker=dict(size=8),
            ))
            fig.add_trace(go.Scatter(
                x=[0, 1], y=[0, 1],
                mode='lines',
                name='Perfect Calibration',
                line=dict(color='gray', dash='dash'),
            ))
            fig.update_layout(
                xaxis_title='Mean Predicted Probability',
                yaxis_title='Fraction of Positives',
                hovermode='closest',
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.metric("Brier Score", f"{model.calibration_data['brier_score']:.4f}")
            st.caption("Lower is better (0 = perfect, 0.25 = random)")
    
    with tab3:
        st.subheader("Threshold Performance")
        threshold_metrics = model.get_threshold_metrics()
        st.dataframe(threshold_metrics, use_container_width=True)
    
    with tab4:
        st.subheader("Cross-Validation Results")
        if model.cv_results:
            cv_df = pd.DataFrame({
                'Metric': ['ROC AUC', 'Precision', 'Recall', 'F1'],
                'Mean': [
                    model.cv_results['test_roc_auc'].mean(),
                    model.cv_results['test_precision'].mean(),
                    model.cv_results['test_recall'].mean(),
                    model.cv_results['test_f1'].mean(),
                ],
                'Std': [
                    model.cv_results['test_roc_auc'].std(),
                    model.cv_results['test_precision'].std(),
                    model.cv_results['test_recall'].std(),
                    model.cv_results['test_f1'].std(),
                ],
            })
            st.dataframe(cv_df, use_container_width=True)


def render_clinical_literature_tab():
    """Render clinical literature and references."""
    st.header("📚 Clinical Literature")
    
    st.markdown("""
    This system integrates evidence-based clinical markers for sepsis detection.
    Below are key references supporting each feature.
    """)
    
    for feature, reference in CLINICAL_REFERENCES.items():
        with st.expander(f"📖 {feature.upper()}"):
            st.write(reference)
    
    st.divider()
    
    st.subheader("Key Clinical Definitions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **SIRS (Systemic Inflammatory Response Syndrome)**
        ≥2 of:
        - Temperature >38°C or <36°C
        - Heart rate >90 bpm
        - Respiratory rate >20 breaths/min
        - WBC >12 K/µL or <4 K/µL
        """)
    
    with col2:
        st.markdown("""
        **qSOFA (Quick SOFA)**
        ≥2 of:
        - Systolic BP ≤100 mmHg
        - Respiratory rate ≥22 breaths/min
        - Altered mental status
        """)


def render_research_notes_tab():
    """Render research notes and methodology."""
    st.header("🔬 Research Notes")
    
    st.markdown("""
    ## Methodology
    
    ### Data Preparation
    - Loaded 546,123 patient-hours from PhysioNet ICU dataset
    - Removed unnecessary columns (Patient_ID, Unit, HospAdmTime, etc.)
    - Handled missing values through median imputation
    - Stratified train/test split (80/20) to preserve class distribution
    
    ### Feature Engineering
    - Created 51 clinical features from 44 raw measurements
    - Derived hemodynamic indices (Shock Index, MAP, Pulse Pressure)
    - Calculated inflammatory markers (SIRS score)
    - Added interaction terms and polynomial features
    
    ### Model Development
    - Algorithm: Logistic Regression with class_weight='balanced'
    - Handles severe class imbalance (20% positive class)
    - Stratified 5-fold cross-validation for robust evaluation
    - Isotonic regression calibration for probabilistic predictions
    
    ### Validation Strategy
    - ROC-AUC for overall discrimination ability
    - Precision-Recall curve for imbalanced data
    - Calibration curve to ensure probability reliability
    - Threshold optimization for clinical deployment
    
    ### Explainability
    - Feature importance from logistic regression coefficients
    - Per-patient contributions to risk score
    - Clinical narratives for interpretability
    """)


def main():
    """Main Streamlit application."""
    setup_page()
    render_header()
    
    # Create tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🔍 Risk Assessment",
        "📋 Model Card",
        "📈 Performance",
        "📚 Literature",
        "🔬 Research Notes",
        "ℹ️ About",
    ])
    
    with tab1:
        st.write("Patient assessment and risk prediction")
        # This would integrate with actual model
    
    with tab2:
        render_model_card_tab()
    
    with tab3:
        st.write("Model performance metrics and validation curves")
    
    with tab4:
        render_clinical_literature_tab()
    
    with tab5:
        render_research_notes_tab()
    
    with tab6:
        st.markdown("""
        ## About This Project
        
        This is a research-grade clinical decision support system for early sepsis detection in ICU patients.
        
        **Key Features:**
        - Rigorous model validation (5-fold cross-validation)
        - Calibrated probability estimates
        - Clinical explainability
        - Comprehensive documentation
        
        **Status:** Research prototype - NOT for clinical use
        
        **GitHub:** [advay3011/icu-early-warning](https://github.com/advay3011/icu-early-warning)
        """)


if __name__ == "__main__":
    main()
