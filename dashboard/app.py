"""
ADM Dashboard — Entry Point
=============================
Streamlit App principal. Inicializa DB, agents e sidebar.
Cada tab é renderizada por um módulo separado em dashboard/tabs/.
Navegação lateral estilo Dashdark X — sidebar vira o hub de navegação.

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

# ── Custom CSS (Dashdark Theme) ─────────────────────────────────────
# Usa path absoluto baseado no __file__ em vez de path relativo ao CWD.
# Isso evita que o CSS não seja encontrado se o Streamlit for iniciado de
# outro diretório.
from pathlib import Path as _Path
_CSS_PATH = _Path(__file__).resolve().parent / "static" / "cupertino.css"
_CSS_CONTENT = _CSS_PATH.read_text(encoding="utf-8")
st.markdown(f"<style>{_CSS_CONTENT}</style>", unsafe_allow_html=True)
# Marker invisível que prova que o CSS foi injetado nesta sessão.
# No DevTools, F12 → Elements → procure por <meta name="css-loaded">.
# Se você ver o conteúdo, o CSS injetou de fato.
_meta_lines = _CSS_CONTENT.count(chr(10)) + 1
_meta_has_sep = "Separadores" in _CSS_CONTENT
_meta_has_before = "background: var(--dx-separator)" in _CSS_CONTENT
_meta_content = f"lines={_meta_lines},has-separadores={_meta_has_sep},has-before={_meta_has_before}"
st.markdown(f'<meta name="css-loaded" content="{_meta_content}">', unsafe_allow_html=True)


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


# ── Navigation Config ───────────────────────────────────────────────
TAB_LABELS = [
    "🏠  Resumo",
    "💰  Financeiro",
    "📢  Central de Marketing",
    "🤝  Atendimento",
    "📦  Meus Anúncios",
    "🔍  Concorrência",
    "⚙️  Configurações",
]
TAB_KEYS = [
    "resumo", "financeiro", "marketing", "atendimento",
    "anuncios", "concorrencia", "configuracoes",
]

# Ensure active_tab is initialized (keep existing selection across reruns)
if "active_tab" not in st.session_state:
    st.session_state.active_tab = TAB_KEYS[0]


# ── Sidebar ─────────────────────────────────────────────────────────
def render_sidebar(user):
    """Render the sidebar with user profile and navigation."""
    with st.sidebar:
        # ── Brand / Logo ──
        st.markdown(
            '<div class="sidebar-brand">'
            '  <span class="brand-icon">🚀</span>'
            '  <span class="brand-name">ADM</span>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<div class="sidebar-subtitle">Shopee Growth Quest</div>',
            unsafe_allow_html=True,
        )

        st.divider()

        # ── User Profile ──
        st.markdown(
            f'<div class="user-profile">'
            f'  <div class="user-avatar">👤</div>'
            f'  <div class="user-info">'
            f'    <div class="user-name">{user.username}</div>'
            f'    <div class="user-level">Nível {user.level}</div>'
            f'  </div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # XP Bar
        xp_progress = (user.xp % 100) / 100 if user.xp else 0
        st.progress(min(xp_progress, 1.0), text=f"XP: {user.xp}")

        # Achievements
        st.markdown(
            '<div class="sidebar-achievements">'
            '  <span class="achievement-badge">🏆 Fundador</span>'
            '</div>',
            unsafe_allow_html=True,
        )

        st.divider()
        st.markdown("###  Navegação")

        # ── Navigation Radio ──
        current_idx = TAB_KEYS.index(st.session_state.active_tab)
        selected = st.radio(
            "nav",
            options=TAB_LABELS,
            index=current_idx,
            key="nav_radio",
            label_visibility="collapsed",
        )

        # Update active tab if changed
        new_idx = TAB_LABELS.index(selected)
        new_key = TAB_KEYS[new_idx]
        if new_key != st.session_state.active_tab:
            st.session_state.active_tab = new_key
            st.rerun()

        st.divider()

        # ── LLM Toggle (moved from header) ──
        llm_on = st.toggle(
            "🤖  IA Ativa",
            value=llm_client.enabled,
            help="Ativar ou desativar a conexão com a IA",
        )
        if llm_on != llm_client.enabled:
            llm_client.set_enabled(llm_on)
            st.rerun()

        # ── Bottom CTA ──
        st.markdown(
            '<div class="sidebar-footer">'
            '  <a href="#" class="sidebar-cta">ADM v1.0</a>'
            '</div>',
            unsafe_allow_html=True,
        )


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

    user = load_user()

    # ── Sidebar ──
    render_sidebar(user)

    # ── Main Header ──
    active_label = TAB_LABELS[TAB_KEYS.index(st.session_state.active_tab)]
    st.markdown(f"## {active_label}")
    st.markdown(
        '<p class="page-subtitle">'
        'Measure your advertising ROI and report website traffic.'
        '</p>',
        unsafe_allow_html=True,
    )

    # ── Content (render active tab) ──
    render_fn = TAB_RENDERERS.get(st.session_state.active_tab)
    if render_fn:
        render_fn(user, agents)
    else:
        st.error(f"Tab '{st.session_state.active_tab}' não encontrada.")


if __name__ == "__main__":
    main()
