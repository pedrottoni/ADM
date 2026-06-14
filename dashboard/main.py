"""
:material/warning: DEPRECATED: Use dashboard/app.py instead.

This file kept for backward compatibility.
Redirects to the new modular app.py entry point.
"""

import streamlit as st
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dashboard.app import main

st.warning(":material/warning: **main.py está depreciado.** O dashboard agora está em `dashboard/app.py` com tabs separadas em `dashboard/tabs/`.")

main()
