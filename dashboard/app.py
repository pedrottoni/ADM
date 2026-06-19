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
from core.tasks.engine import TaskEngine
from dashboard.tabs import TAB_RENDERERS

# ── Page Config ─────────────────────────────────────────────────────
st.set_page_config(
    page_title=Config.APP_NAME,
    page_icon=":material/rocket:",
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
# Força header transparente — o CSS-in-JS do Emotion injeta background
# depois do nosso <style>, então usamos JS para limpar inline style.
st.markdown(
    '<script>'
    'const h=document.querySelector(\'header[data-testid="stHeader"]\');'
    'if(h){h.style.background="transparent";h.style.backgroundColor="transparent"}'
    '</script>',
    unsafe_allow_html=True,
)
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
# O sidebar usa st.button em loop com icon=":material/x:" (nativo
# Streamlit 1.58+). Estava num st.radio antes, mas os labels do radio
# não suportam Material icons; botões dão controle total.

TAB_LABELS = [
    "Resumo",
    "Financeiro",
    "Central de Marketing",
    "Atendimento",
    "Meus Anúncios",
    "Concorrência",
    "Tarefas",
    "Configurações",
]
TAB_KEYS = [
    "resumo", "financeiro", "marketing", "atendimento",
    "anuncios", "concorrencia", "tarefas", "configuracoes",
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
            '  <span class="brand-name">Shopee Growth Quest</span>'
            '</div>',
            unsafe_allow_html=True,
        )

        st.divider()

        st.markdown("###  Navegação")

        # ── Navigation (st.button com icon=:material/: nativo, 1.58+) ──
        _NAV_ICONS = {
            "resumo":        ":material/home:",
            "financeiro":    ":material/payments:",
            "marketing":     ":material/campaign:",
            "atendimento":   ":material/support_agent:",
            "anuncios":      ":material/inventory_2:",
            "concorrencia":  ":material/search:",
            "tarefas":       ":material/assignment:",
            "configuracoes": ":material/settings:",
        }
        with st.container(key="nav_container"):
            st.markdown('<div class="nav-block-marker"></div>', unsafe_allow_html=True)
            for _key in TAB_KEYS:
                _active = st.session_state.active_tab == _key
                _label = TAB_LABELS[TAB_KEYS.index(_key)]
                if st.button(
                    _label,
                    key=f"nav_{_key}",
                    icon=_NAV_ICONS.get(_key, ":material/help:"),
                    use_container_width=True,
                    type="primary" if _active else "secondary",
                ) and not _active:
                    st.session_state.active_tab = _key
                    st.rerun()
        selected = TAB_LABELS[TAB_KEYS.index(st.session_state.active_tab)]

        new_idx = TAB_LABELS.index(selected)
        new_key = TAB_KEYS[new_idx]
        if new_key != st.session_state.active_tab:
            st.session_state.active_tab = new_key
            st.rerun()

        # ── Divider before profile ──
        st.divider()

        # ── User Profile ──
        st.markdown(
            f'<div class="user-profile">'
            f'  <div class="user-avatar"><span class="material-symbols-rounded">person</span></div>'
            f'  <div class="user-info">'
            f'    <div class="user-name">{user.username}</div>'
            f'    <div class="user-level">Nível {user.level}</div>'
            f'  </div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Show pending task count in sidebar
        _session = next(get_session())
        _pending_count = TaskEngine.count_pending(_session, user.id)
        _session.close()

        if _pending_count > 0:
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:8px;'
                f'    padding:8px 12px;margin:8px 0;border-radius:12px;'
                f'    background:rgba(129,140,248,0.1);'
                f'    border:1px solid rgba(129,140,248,0.2);">'
                f'  <span class="material-symbols-rounded" style="color:#818CF8;font-size:20px;">assignment</span>'
                f'  <div>'
                f'    <div style="font-size:13px;font-weight:600;line-height:1.3;">{_pending_count} tarefa{"s" if _pending_count != 1 else ""} pendente{"s" if _pending_count != 1 else ""}</div>'
                f'    <div style="font-size:11px;color:var(--dx-muted);">Clique na aba Tarefas</div>'
                f'  </div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                "<div style='padding:8px 12px;margin:8px 0;border-radius:12px;"
                "background:rgba(34,197,94,0.08);border:1px solid rgba(34,197,94,0.2);"
                "font-size:13px;color:var(--dx-fg);'"
                ">:material/check_circle: Tudo em dia</div>",
                unsafe_allow_html=True,
            )

        # Remove XP/level — replaced by task count above
        # Level shown inline in the profile line
        st.caption(f"Nível {user.level} | {user.xp} XP")

        # ── IA Toggle ──
        st.divider()
        llm_on = st.toggle(
            "🤖 IA Ativa",
            value=llm_client.enabled,
            help="Ativar ou desativar a assistente de IA",
            label_visibility="visible",
        )
        if llm_on != llm_client.enabled:
            llm_client.set_enabled(llm_on)
            st.rerun()

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

    # ── Main Header ──────────────────────────────────────────────────
    # Header da tab ativa. Streamlit renderiza Material Symbols nativos
    # em st.markdown via shortcode (formato :material/snake_case:),
    # nativo no 1.58+.
    _ICON_FOR_KEY = {
        "resumo":        "home",
        "financeiro":    "payments",
        "marketing":     "campaign",
        "atendimento":   "support_agent",
        "anuncios":      "inventory_2",
        "concorrencia":  "search",
        "tarefas":       "assignment",
        "configuracoes": "settings",
    }
    active_label = TAB_LABELS[TAB_KEYS.index(st.session_state.active_tab)]
    _hdr_icon = _ICON_FOR_KEY.get(st.session_state.active_tab, "help")

    # Header row — title full width
    st.markdown(f"## :material/{_hdr_icon}: {active_label}")
    st.markdown(
        '<p class="page-subtitle">'
        'Monitore suas operações Shopee em tempo real.'
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
