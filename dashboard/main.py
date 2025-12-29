import streamlit as st
import pandas as pd
from core.config import Config
from core.database.engine import create_db_and_tables, get_session, initialize_default_user
from core.database.models import User
from sqlmodel import select
from agents.finance_agent import FinanceAgent

# Page Config
st.set_page_config(
    page_title=Config.APP_NAME,
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize DB on first run
if "db_initialized" not in st.session_state:
    create_db_and_tables()
    initialize_default_user()
    st.session_state["db_initialized"] = True

def load_user_data():
    """Load the main user (Admin) for display."""
    session = next(get_session())
    statement = select(User).where(User.username == "Admin")
    return session.exec(statement).first()

def main():
    # Sidebar: Gamification Profile
    user = load_user_data()
    
    with st.sidebar:
        st.header(f"👋 Olá, {user.username}!")
        st.metric(label="Nível", value=f"Lvl {user.level}")
        st.progress(user.xp % 100 / 100, text=f"XP: {user.xp}")
        st.divider()
        st.write("### 🏆 Conquistas Recentes")
        st.write("🛠️ Fundador (Badge)")
    
    # Main Content
    st.title("🚀 Shopee Growth Quest")
    
    tab1, tab2, tab3 = st.tabs(["🏠 Resumo", "💰 Financeiro", "📢 Anúncios"])
    
    with tab1:
        st.header("Missões do Dia")
        col1, col2 = st.columns(2)
        with col1:
            st.info("📝 **Missão 1**: Registre suas vendas de ontem.")
            if st.button("Completar (+10 XP)"):
                # Mock completion logic (will be real later)
                st.toast("XP Adicionado! (Simulação)")
        with col2:
            st.warning("⚠️ **Alerta**: Estoque do Produto X está baixo.")

    with tab2:
        st.header("Guardião Financeiro")
        finance_agent = FinanceAgent()
        
        # Mock Data Input for MVP
        st.subheader("📊 Analisar Vendas")
        uploaded_file = st.file_uploader("Suba seu relatório de vendas (CSV/Excel)", type=["csv", "xlsx"])
        
        if uploaded_file:
            # Placeholder for file processing
            st.success("Arquivo recebido! (Processamento em breve)")
            
        # Demo Button
        if st.button("Executar Análise Demo"):
            mock_data = [{'date': '2023-10-01', 'amount': 150.0}, {'date': '2023-10-02', 'amount': 200.0}]
            result = finance_agent.run(mock_data)
            st.code(result["stats"])
            st.success(f"🤖 **Conselho do Guardião**: {result['advice']}")

    with tab3:
        st.write("🚧 **Agente de Ads**: Em construção...")

if __name__ == "__main__":
    main()
