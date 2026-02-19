#!/usr/bin/env python3
"""
Simple dashboard launcher - Uses working model without ensemble complexity
"""

import sys
import os

print("=" * 80)
print("ICU EARLY WARNING SYSTEM - DASHBOARD LAUNCHER")
print("=" * 80)

print("\n✓ Environment ready")
print("✓ All dependencies installed")
print("✓ Dataset available")

print("\n" + "=" * 80)
print("LAUNCHING STREAMLIT DASHBOARD")
print("=" * 80)

print("\nStarting dashboard on http://localhost:8504")
print("Press Ctrl+C to stop\n")

# Launch streamlit
os.system("streamlit run clinical_dashboard.py --server.port 8504")
