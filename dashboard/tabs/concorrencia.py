"""
:material/search: Concorrência — Tab de Concorrencia
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

    from dashboard.components.competitor_view import render_competitor_page
    render_competitor_page(user.id)
