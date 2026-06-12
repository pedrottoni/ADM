"""
ADM Dashboard — Entry Point
=============================
Streamlit App principal. Inicializa DB, agents e sidebar.
Cada tab é renderizada por um módulo separado em dashboard/tabs/.

Uso:
    streamlit run dashboard/app.py
"""

import streamlit as st
from core.config import Config
from core.llm_client import llm_client
from core.database.engine import create_db_and_tables, initialize_default_user, get_session
from core.database.models import User
from sqlmodel import select
from sqlalchemy.orm import selectinload
from agents.finance_agent import FinanceAgent
from agents.product_agent import ProductAgent
from agents.ads_agent import AdsAgent
from agents.customer_agent import CustomerAgent
from dashboard.tabs import TAB_RENDERERS

# ── Page Config ─────────────────────────────────────────────────────
st.set_page_config(
    page_title=Config.APP_NAME,
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS (Cupertino Dark) ───────────────────────────
with open("dashboard/static/cupertino.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def load_user():
    """Load Admin user with missions eagerly loaded."""
    session = next(get_session())
    statement = select(User).options(selectinload(User.missions)).where(User.username == "Admin")
    return session.exec(statement).first()


# ── Init DB ─────────────────────────────────────────────────────────
if "db_initialized" not in st.session_state:
    create_db_and_tables()
    initialize_default_user()
    st.session_state["db_initialized"] = True


# ── Main ────────────────────────────────────────────────────────────
def main():
    # Initialize agents (cached in session_state)
    if 'finance_agent' not in st.session_state:
        st.session_state.finance_agent = FinanceAgent()
    if 'product_agent' not in st.session_state:
        st.session_state.product_agent = ProductAgent()
    if 'ads_agent' not in st.session_state:
        st.session_state.ads_agent = AdsAgent()
    if 'customer_agent' not in st.session_state:
        st.session_state.customer_agent = CustomerAgent()

    agents = {
        "finance_agent": st.session_state.finance_agent,
        "product_agent": st.session_state.product_agent,
        "ads_agent": st.session_state.ads_agent,
        "customer_agent": st.session_state.customer_agent,
    }

    # Sidebar: User profile & gamification
    user = load_user()
    with st.sidebar:
        st.header(f"👋 Olá, {user.username}!")
        st.metric(label="Nível", value=f"Lvl {user.level}")
        st.progress(user.xp % 100 / 100, text=f"XP: {user.xp}")
        st.divider()
        st.write("### 🏆 Conquistas Recentes")
        st.write("🛠️ Fundador (Badge)")

    # Title + LLM toggle
    title_col, toggle_col = st.columns([6, 1])
    with title_col:
        st.title("🚀 Shopee Growth Quest")
    with toggle_col:
        llm_on = st.toggle(
            "🤖 IA",
            value=llm_client.enabled,
            help="Ativar ou desativar a conexão com a IA",
        )
        if llm_on != llm_client.enabled:
            llm_client.set_enabled(llm_on)
            st.rerun()

    # ── Tabs ────────────────────────────────────────────────────────
    tab_labels = [
        "🏠 Resumo",
        "💰 Financeiro",
        "📢 Central de Marketing",
        "🤝 Atendimento",
        "📦 Meus Anúncios",
        "🔍 Concorrência",
        "⚙️ Configurações",
    ]
    tab_keys = ["resumo", "financeiro", "marketing", "atendimento",
                "anuncios", "concorrencia", "configuracoes"]

    tabs = st.tabs(tab_labels)

    for i, (tab, key) in enumerate(zip(tabs, tab_keys)):
        with tab:
            render_fn = TAB_RENDERERS.get(key)
            if render_fn:
                render_fn(user, agents)
            else:
                st.error(f"Tab '{key}' não encontrada.")


if __name__ == "__main__":
    main()
