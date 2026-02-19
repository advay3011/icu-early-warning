"""
ICU Sepsis Early Warning System - Research Grade
A rigorous, clinically-informed ML system for sepsis risk prediction

Version: 2.0
Status: Research Prototype
License: MIT
"""

__version__ = "2.0"
__author__ = "Research Team"
__status__ = "Research Prototype"

from .model import ResearchGradeModel
from .config import (
    MODEL_CONFIG,
    CLINICAL_FEATURES,
    DERIVED_FEATURES,
    ALERT_THRESHOLDS,
    SOFA_COMPONENTS,
    CLINICAL_REFERENCES,
    DATASET_INFO,
)
from .utils import (
    calculate_shock_index,
    calculate_map,
    calculate_pulse_pressure,
    calculate_sirs_score,
    calculate_qsofa_score,
    calculate_sofa_score,
    check_abnormal_values,
    get_clinical_recommendation,
)

__all__ = [
    'ResearchGradeModel',
    'MODEL_CONFIG',
    'CLINICAL_FEATURES',
    'DERIVED_FEATURES',
    'ALERT_THRESHOLDS',
    'SOFA_COMPONENTS',
    'CLINICAL_REFERENCES',
    'DATASET_INFO',
    'calculate_shock_index',
    'calculate_map',
    'calculate_pulse_pressure',
    'calculate_sirs_score',
    'calculate_qsofa_score',
    'calculate_sofa_score',
    'check_abnormal_values',
    'get_clinical_recommendation',
]
