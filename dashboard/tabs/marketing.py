"""
:material/campaign: Central de Marketing — Tab de Marketing
"""

import streamlit as st
from core.config import Config
from core.database.engine import get_session


def render(user, agents):
    """Render the tab content."""
    from dashboard.components.metric_card import metric_card
    finance_agent = agents["finance_agent"]
    product_agent = agents["product_agent"]
    ads_agent = agents["ads_agent"]
    customer_agent = agents["customer_agent"]

    st.info("**Dica**: Use a 'Fábrica de Produtos' para gerar palavras-chave de cauda longa para seus anúncios durante a criação do produto!", icon=":material/lightbulb:")

    col_tool2, col_tool3 = st.columns([1, 1])
    with col_tool2:
        st.subheader("Análise Tática de Campanha")

        c1, c2 = st.columns(2)
        spend = c1.number_input("Gasto (R$)", min_value=0.0, step=10.0)
        revenue = c2.number_input("Faturamento (R$)", min_value=0.0, step=10.0)

        c3, c4 = st.columns(2)
        impressions = c3.number_input("Impressões (Visualizações)", min_value=0, step=100)
        clicks = c4.number_input("Cliques", min_value=0, step=10)

        if st.button("Analisar Performance", icon=":material/analytics:"):
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
                with kpi1: metric_card("ROAS", f"{roas:.2f}x", delta=f"+{roas-2:.2f}x" if roas >= 2 else f"{roas-2:.2f}x")
                with kpi2: metric_card("CTR", f"{ctr:.2f}%", delta=f"+{ctr-1.5:.2f}%" if ctr >= 1.5 else f"{ctr-1.5:.2f}%")

                st.info(f"**Estratégia**: {advice}", icon=":material/lightbulb:")
            else:
                st.warning("Preencha pelo menos Gasto e Impressões para calcular!")

    with col_tool3:
        st.markdown("#### :material/palette: Gerador de Prompts (IA)")
        st.caption("Gere comandos para criar fotos ultra-realistas no Midjourney/DALL-E.")

        # Select product
        products_list = product_agent.get_all_products(user.id)
        if products_list:
            prod_names_mkt = {p.title: p for p in products_list}
            sel_p_title = st.selectbox("Escolha o Produto", ["-- Selecione --"] + list(prod_names_mkt.keys()), key="mkt_prod_select")

            if st.button("Gerar Prompts de Imagem", icon=":material/auto_awesome:"):
                if sel_p_title != "-- Selecione --":
                    selected_p = prod_names_mkt[sel_p_title]
                    with st.spinner("O Diretor de Arte está criando os prompts..."):
                        prompts = product_agent.generate_image_prompt(selected_p.title, selected_p.description)
                        st.write("---")
                        st.markdown(prompts)
                        st.info("**Dica**: Copie o prompt em inglês e cole no Midjourney ou Leonardo.ai!", icon=":material/lightbulb:")
                else:
                    st.warning("Selecione um produto.")
        else:
            st.info("Cadastre produtos na 'Fábrica' para gerar prompts.")
