"""
Utility functions for clinical calculations and data processing
"""

import numpy as np
import pandas as pd
from config import CLINICAL_FEATURES, DERIVED_FEATURES, SOFA_COMPONENTS


def calculate_shock_index(hr, sbp):
    """
    Calculate Shock Index = HR / SBP
    
    Clinical significance: >0.9 indicates hemodynamic instability
    
    Args:
        hr: Heart rate (bpm)
        sbp: Systolic blood pressure (mmHg)
        
    Returns:
        float: Shock index value
    """
    if sbp <= 0:
        return np.nan
    return hr / sbp


def calculate_pulse_pressure(sbp, dbp):
    """
    Calculate Pulse Pressure = SBP - DBP
    
    Clinical significance: Normal 40-60 mmHg
    - Low (<30): Reduced cardiac output
    - High (>60): Arterial stiffness or hyperdynamic state
    
    Args:
        sbp: Systolic blood pressure (mmHg)
        dbp: Diastolic blood pressure (mmHg)
        
    Returns:
        float: Pulse pressure value
    """
    return sbp - dbp


def calculate_map(sbp, dbp):
    """
    Calculate Mean Arterial Pressure = (SBP + 2*DBP) / 3
    
    Clinical significance: <65 mmHg indicates inadequate tissue perfusion
    
    Args:
        sbp: Systolic blood pressure (mmHg)
        dbp: Diastolic blood pressure (mmHg)
        
    Returns:
        float: MAP value
    """
    return (sbp + 2 * dbp) / 3


def calculate_sirs_score(temp, hr, resp, wbc):
    """
    Calculate SIRS (Systemic Inflammatory Response Syndrome) Score
    
    Criteria (≥2 = SIRS):
    - Temperature >38°C or <36°C
    - Heart rate >90 bpm
    - Respiratory rate >20 breaths/min
    - WBC >12 K/µL or <4 K/µL
    
    Clinical significance: ≥2 SIRS + suspected infection = sepsis
    
    Args:
        temp: Temperature (°C)
        hr: Heart rate (bpm)
        resp: Respiratory rate (breaths/min)
        wbc: White blood cell count (K/µL)
        
    Returns:
        int: SIRS score (0-4)
    """
    score = 0
    if temp > 38 or temp < 36:
        score += 1
    if hr > 90:
        score += 1
    if resp > 20:
        score += 1
    if wbc > 12 or wbc < 4:
        score += 1
    return score


def calculate_qsofa_score(sbp, resp, altered_mental_status):
    """
    Calculate qSOFA (Quick SOFA) Score
    
    Criteria (≥2 = high risk):
    - Systolic BP ≤100 mmHg
    - Respiratory rate ≥22 breaths/min
    - Altered mental status
    
    Clinical significance: Predicts mortality in sepsis
    
    Args:
        sbp: Systolic blood pressure (mmHg)
        resp: Respiratory rate (breaths/min)
        altered_mental_status: Boolean, whether patient has altered mental status
        
    Returns:
        int: qSOFA score (0-3)
    """
    score = 0
    if sbp <= 100:
        score += 1
    if resp >= 22:
        score += 1
    if altered_mental_status:
        score += 1
    return score


def calculate_sofa_score(pao2_fio2, platelets, bilirubin, map_value, gcs, creatinine):
    """
    Calculate SOFA (Sequential Organ Failure Assessment) Score
    
    Comprehensive organ dysfunction assessment (0-24 scale)
    
    Args:
        pao2_fio2: PaO2/FiO2 ratio
        platelets: Platelet count (K/µL)
        bilirubin: Total bilirubin (mg/dL)
        map_value: Mean arterial pressure (mmHg)
        gcs: Glasgow Coma Scale (3-15)
        creatinine: Serum creatinine (mg/dL)
        
    Returns:
        dict: SOFA components and total score
    """
    sofa = {}
    
    # Respiratory
    if pao2_fio2 >= 400:
        sofa['respiratory'] = 0
    elif pao2_fio2 >= 300:
        sofa['respiratory'] = 1
    elif pao2_fio2 >= 200:
        sofa['respiratory'] = 2
    elif pao2_fio2 >= 100:
        sofa['respiratory'] = 3
    else:
        sofa['respiratory'] = 4
    
    # Coagulation
    if platelets > 150:
        sofa['coagulation'] = 0
    elif platelets > 100:
        sofa['coagulation'] = 1
    elif platelets > 50:
        sofa['coagulation'] = 2
    elif platelets > 20:
        sofa['coagulation'] = 3
    else:
        sofa['coagulation'] = 4
    
    # Liver
    if bilirubin < 1.2:
        sofa['liver'] = 0
    elif bilirubin < 2.0:
        sofa['liver'] = 1
    elif bilirubin < 6.0:
        sofa['liver'] = 2
    elif bilirubin < 12.0:
        sofa['liver'] = 3
    else:
        sofa['liver'] = 4
    
    # Cardiovascular
    if map_value >= 70:
        sofa['cardiovascular'] = 0
    elif map_value >= 60:
        sofa['cardiovascular'] = 1
    else:
        sofa['cardiovascular'] = 2  # Simplified; actual scoring includes vasopressors
    
    # CNS
    if gcs == 15:
        sofa['cns'] = 0
    elif gcs >= 13:
        sofa['cns'] = 1
    elif gcs >= 10:
        sofa['cns'] = 2
    elif gcs >= 6:
        sofa['cns'] = 3
    else:
        sofa['cns'] = 4
    
    # Renal
    if creatinine < 1.2:
        sofa['renal'] = 0
    elif creatinine < 2.0:
        sofa['renal'] = 1
    elif creatinine < 3.5:
        sofa['renal'] = 2
    elif creatinine < 5.0:
        sofa['renal'] = 3
    else:
        sofa['renal'] = 4
    
    sofa['total'] = sum(sofa.values())
    
    return sofa


def check_abnormal_values(patient_data):
    """
    Check for abnormal vital signs and flag them.
    
    Args:
        patient_data: dict with vital signs
        
    Returns:
        dict: Abnormality flags and severity
    """
    abnormalities = []
    
    for feature, value in patient_data.items():
        if feature not in CLINICAL_FEATURES:
            continue
        
        config = CLINICAL_FEATURES[feature]
        normal_range = config['normal_range']
        critical_low = config['critical_low']
        critical_high = config['critical_high']
        
        if value < critical_low or value > critical_high:
            abnormalities.append({
                'feature': feature,
                'label': config['label'],
                'value': value,
                'severity': 'CRITICAL',
                'normal_range': normal_range,
            })
        elif value < normal_range[0] or value > normal_range[1]:
            abnormalities.append({
                'feature': feature,
                'label': config['label'],
                'value': value,
                'severity': 'ABNORMAL',
                'normal_range': normal_range,
            })
    
    return abnormalities


def format_confidence_interval(point_estimate, ci_lower, ci_upper, confidence=0.95):
    """
    Format confidence interval for display.
    
    Args:
        point_estimate: Point estimate (e.g., risk probability)
        ci_lower: Lower bound of CI
        ci_upper: Upper bound of CI
        confidence: Confidence level (default 0.95)
        
    Returns:
        str: Formatted CI string
    """
    return f"{point_estimate:.1%} (95% CI: {ci_lower:.1%}–{ci_upper:.1%})"


def get_clinical_recommendation(risk_probability, threshold):
    """
    Generate clinical recommendation based on risk and threshold.
    
    Args:
        risk_probability: Model's predicted risk (0-1)
        threshold: Alert threshold
        
    Returns:
        dict: Recommendation with action items
    """
    if risk_probability >= threshold:
        return {
            'alert_level': 'HIGH',
            'icon': '🚨',
            'color': '#ff4444',
            'recommendation': 'Elevated risk markers detected — recommend immediate clinical assessment',
            'actions': [
                'Obtain blood cultures',
                'Initiate broad-spectrum antibiotics',
                'Assess for organ dysfunction',
                'Consider ICU transfer if not already admitted',
            ],
        }
    elif risk_probability >= threshold * 0.6:
        return {
            'alert_level': 'MODERATE',
            'icon': '⚠️',
            'color': '#ffaa00',
            'recommendation': 'Moderate risk markers detected — recommend close monitoring and evaluation',
            'actions': [
                'Increase monitoring frequency',
                'Repeat vital signs and labs',
                'Assess clinical trajectory',
                'Prepare for escalation if deterioration',
            ],
        }
    else:
        return {
            'alert_level': 'LOW',
            'icon': '✅',
            'color': '#44aa44',
            'recommendation': 'Low risk markers — continue routine monitoring',
            'actions': [
                'Continue standard ICU monitoring',
                'Reassess periodically',
                'Document clinical assessment',
            ],
        }


def create_patient_timeline(patient_history):
    """
    Create timeline of risk scores over time.
    
    Args:
        patient_history: List of dicts with timestamps and predictions
        
    Returns:
        pd.DataFrame: Timeline data
    """
    timeline_df = pd.DataFrame(patient_history)
    timeline_df['timestamp'] = pd.to_datetime(timeline_df['timestamp'])
    timeline_df = timeline_df.sort_values('timestamp')
    
    return timeline_df


def generate_clinical_narrative(patient_data, risk_probability, top_features):
    """
    Generate clinician-friendly narrative explanation.
    
    Args:
        patient_data: Patient vital signs
        risk_probability: Model's risk prediction
        top_features: Top 3 contributing features
        
    Returns:
        str: Clinical narrative
    """
    narrative = f"""
**Clinical Assessment Summary**

**Risk Assessment:** {risk_probability:.1%} sepsis probability

**Key Clinical Findings:**
"""
    
    for i, (feature, contribution) in enumerate(top_features, 1):
        direction = "↑ increases" if contribution > 0 else "↓ decreases"
        narrative += f"\n{i}. {feature} {direction} risk"
    
    narrative += """

**Clinical Interpretation:**
This assessment integrates multiple hemodynamic and inflammatory markers to estimate sepsis risk.
Elevated lactate and hemodynamic instability are particularly concerning.

**Recommended Actions:**
- Obtain blood cultures if not already done
- Assess for source of infection
- Monitor organ function closely
- Consider antimicrobial therapy per institutional protocols

**Important Notes:**
- This is a decision support tool, not a diagnostic tool
- Clinical judgment should always take precedence
- Requires integration with comprehensive clinical assessment
"""
    
    return narrative
