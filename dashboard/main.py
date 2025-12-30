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
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🏠 Resumo", "💰 Financeiro", "📢 Anúncios", "🤝 Atendimento", "🏭 Fábrica de Produtos", "⚙️ Configurações"])
    
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
        st.header("📢 Mestre dos Anúncios")
        from agents.ads_agent import AdsAgent
        ads_agent = AdsAgent()
        
        st.info("💡 **Dica**: Use a 'Fábrica de Produtos' para gerar palavras-chave de cauda longa para seus anúncios durante a criação do produto!")
        
        col_tool2, col_blank = st.columns([1, 1])
        with col_tool2:
            st.subheader("Análise Tática de Campanha")
            
            c1, c2 = st.columns(2)
            spend = c1.number_input("Gasto (R$)", min_value=0.0, step=10.0)
            revenue = c2.number_input("Faturamento (R$)", min_value=0.0, step=10.0)
            
            c3, c4 = st.columns(2)
            impressions = c3.number_input("Impressões (Visualizações)", min_value=0, step=100)
            clicks = c4.number_input("Cliques", min_value=0, step=10)
            
            if st.button("Analisar Performance 📊"):
                if spend > 0 and impressions > 0:
                    ad_data = {
                        "spend": spend,
                        "revenue": revenue,
                        "impressions": impressions,
                        "clicks": clicks
                    }
                    
                    # Call Agent
                    with st.spinner("O Agente está calculando suas métricas..."):
                        advice = ads_agent.analyze_ad_performance(ad_data)
                    
                    # Calculate Metrics for Display
                    roas = revenue / spend
                    ctr = (clicks / impressions) * 100
                    
                    # Display Results
                    st.divider()
                    kpi1, kpi2 = st.columns(2)
                    kpi1.metric("ROAS", f"{roas:.2f}x", delta=f"{roas-2:.2f}x (Meta 2x)")
                    kpi2.metric("CTR", f"{ctr:.2f}%", delta=f"{ctr-1.5:.2f}% (Meta 1.5%)")
                    
                    st.info(f"💡 **Estratégia**: {advice}")
                else:
                    st.warning("Preencha pelo menos Gasto e Impressões para calcular!")
            
    with tab4:
        st.header("🤝 Customer Hero (Atendimento)")
        from agents.customer_agent import CustomerAgent
        customer_agent = CustomerAgent()
        
        col_c1, col_c2 = st.tabs(["💬 Gerador de Respostas", "⭐ Análise de Reviews"])
        
        with col_c1:
            st.subheader("Responder Cliente")
            msg = st.text_area("Mensagem do Cliente", placeholder="Ex: O produto chegou quebrado e quero meu dinheiro de volta!")
            tone = st.select_slider("Tom da Resposta", options=["Formal", "Empático", "Descontraído"], value="Empático")
            
            if st.button("Gerar Resposta ✍️"):
                if msg:
                    with st.spinner("Escrevendo..."):
                        reply = customer_agent.generate_response(msg, tone)
                        st.text_area("Sugestão de Resposta:", value=reply, height=150)
                        st.success("Ajuste se necessário e envie!")
                else:
                    st.warning("Cole a mensagem do cliente primeiro.")

        with col_c2:
            st.subheader("Analisador de Sentimento")
            reviews_input = st.text_area("Cole aqui várias avaliações (uma por linha)", height=150, placeholder="Amei o produto!\nDemorou muito para chegar.\nQualidade excelente.")
            
            if st.button("Analisar Sentimento 🧠"):
                if reviews_input:
                    reviews_list = [r for r in reviews_input.split('\n') if r.strip()]
                    with st.spinner("Lendo mentes..."):
                        result = customer_agent.analyze_sentiment(reviews_list)
                        st.markdown(result["analysis"])
                else:
                    st.warning("Insira algumas avaliações.")


    with tab5:
        st.header("🏭 Fábrica de Produtos (Nutri Active)")
        from agents.product_agent import ProductAgent
        if 'product_agent' not in st.session_state:
            st.session_state.product_agent = ProductAgent()
        
        # Initialize Batch Session State
        if 'batch_products' not in st.session_state:
            st.session_state.batch_products = []
        
        st.info("💡 **Dica sobre Imagens**: Como a API é restrita, a estratégia é: Gere os textos aqui, baixe o CSV, suba na Shopee e depois **arraste as imagens do seu computador** direto para cada produto criado. É o método mais rápido!")
        
        col_p1, col_p2 = st.tabs(["📝 Criar Unitário", "📦 Lote (CSV)"])
        
        with col_p1:
            st.subheader("Criar Anúncio Perfeito")
            p_name = st.text_input("Produto", placeholder="Ex: Creatina Monohidratada Pura")
            p_ing = st.text_input("Ingredientes/Detalhes", placeholder="Ex: 300g, 100% Pura, Sem Sabor")
            p_ben = st.text_area("Principais Benefícios", placeholder="Ex: Aumento de força, recuperação muscular, energia")
            
            c_gen, c_add = st.columns([1, 1])
            
            if c_gen.button("Gerar Anúncio Nutri Active (2025) ✨"):
                if p_name and p_ben:
                    with st.spinner("🤖 O Agente está analisando concorrência e criando copy..."):
                        listing = st.session_state.product_agent.generate_listing(p_name, p_ben, p_ing)
                        st.session_state.last_generated = listing # Store for review
                        
            # Show Result if exists
            if 'last_generated' in st.session_state:
                listing = st.session_state.last_generated
                
                st.divider()
                st.markdown("### 🕵️ Revisão do Humano")
                
                c_title, c_keys = st.columns([2, 1])
                title = c_title.text_input("Título (SEO)", value=listing['title'])
                keywords = c_keys.text_area("Keywords (Tags)", value=listing.get('keywords', ''), height=68, help="Use isso nas Tags do produto ou no final da descrição")
                
                desc = st.text_area("Descrição (Markdown)", value=listing['description'], height=400)
                
                # Update logic if user edits
                st.session_state.last_generated['title'] = title
                st.session_state.last_generated['description'] = desc
                # Append keywords to description if desired, or keep separate. 
                # For CSV logic, we can append them to description or ignore.
                
                if st.button("➕ Aprovar e Adicionar ao Lote"):
                    # Append keywords to description for final listing if not present
                    final_desc = desc
                    if keywords and keywords not in desc:
                        final_desc += f"\n\nTAGS: {keywords}"
                    
                    final_product = {
                        "title": title,
                        "description": final_desc,
                        "keywords": keywords # Keep track
                    }
                    
                    st.session_state.batch_products.append(final_product)
                    st.toast(f"Produto '{title}' salvo no lote! Total: {len(st.session_state.batch_products)}")
                    del st.session_state.last_generated # Clear after adding

        with col_p2:
            st.subheader(f"Gerador em Massa ({len(st.session_state.batch_products)} produtos)")
            
            # Show table of added products
            if st.session_state.batch_products:
                df_view = pd.DataFrame(st.session_state.batch_products)
                st.dataframe(df_view[['title']], use_container_width=True)
                
                if st.button("📥 Baixar CSV para Shopee"):
                    csv = st.session_state.product_agent.generate_mass_upload_csv(st.session_state.batch_products)
                    st.download_button(
                        label="Clique para Download",
                        data=csv,
                        file_name="nutri_active_upload.csv",
                        mime="text/csv"
                    )
                    
                    # MANDAMENTOS DA SHOPEE
                    st.divider()
                    st.success("CSV Gerado! Agora siga os 5 Mandamentos da Shopee:")
                    
                    m1, m2, m3 = st.columns(3)
                    with m1:
                        st.write("📸 **1. Fotos**")
                        st.caption("Mínimo de **5 fotos** (Ideal: 9). A primeira com fundo branco/limpo.")
                    with m2:
                        st.write("🎥 **2. Vídeo**")
                        st.caption("Tenha 1 vídeo curto (15-30s) mostrando o produto. Aumenta muito a conversão.")
                    with m3:
                        st.write("🏷️ **3. Preço/Estoque**")
                        st.caption("Preencha manualmente no arquivo ou na Shopee após subir.")
                        
                    st.warning("⚠️ **Dica de Ouro**: Use fotos reais na sequência (segurando o pote) para passar confiança.")
            else:
                st.info("O lote está vazio. Gere anúncios na aba 'Criar Unitário' e adicione aqui!")

    with tab6:
        from dashboard.components.settings_view import render_settings_page
        render_settings_page()

if __name__ == "__main__":
    main()
