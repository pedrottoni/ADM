"""
⚙️ Configurações — Tab de Configuracoes
"""

import streamlit as st
from core.config import Config
from core.database.engine import get_session


def render(user, agents):
    """Render the tab content."""
    finance_agent = agents["finance_agent"]
    product_agent = agents["product_agent"]
    ads_agent = agents["ads_agent"]
    customer_agent = agents["customer_agent"]

    from dashboard.components.settings_view import render_settings_page
    render_settings_page()
