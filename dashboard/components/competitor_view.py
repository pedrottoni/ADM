import streamlit as st
import pandas as pd
from core.competitor_service import competitor_service, MARKETPLACES, MARKETPLACE_LABELS
from agents.product_agent import ProductAgent


def render_competitor_page(user_id: int):

    product_agent = ProductAgent()
    products = product_agent.get_all_products(user_id)

    if not products:
        st.warning("Nenhum produto cadastrado. Cadastre produtos na aba 'Meus Anúncios' primeiro.")
        return

    product_options = {f"{p.title} — R${p.price:.2f}": p.id for p in products}

    col_sel, col_search = st.columns([3, 1])
    with col_sel:
        selected_name = st.selectbox("Selecione seu produto", list(product_options.keys()), index=0)
        selected_product_id = product_options[selected_name]
        product_obj = next((p for p in products if p.id == selected_product_id), None)
        default_keyword = product_obj.title if product_obj else ""

    search_keyword = st.text_input("Termo de busca nos marketplaces", value=default_keyword, help="Edite livremente para buscar com outro nome nas lojas concorrentes")

    with col_search:
        st.markdown("<br>", unsafe_allow_html=True)
        search_clicked = st.button("🔎 Buscar Preços", type="primary", use_container_width=True)

    marketplaces_sel = st.multiselect(
        "Marketplaces para monitorar",
        MARKETPLACES,
        default=["shopee", "mercadolivre", "amazon"],
        format_func=lambda x: MARKETPLACE_LABELS.get(x, x),
    )

    if search_clicked:
        if not search_keyword.strip():
            st.warning("Insira um termo de busca.")
        elif not marketplaces_sel:
            st.warning("Selecione pelo menos um marketplace.")
        else:
            with st.spinner("Buscando preços nos marketplaces... Isso pode levar alguns minutos."):
                status_placeholder = st.empty()
                for mp in marketplaces_sel:
                    status_placeholder.info(f"🔍 Buscando em {MARKETPLACE_LABELS.get(mp, mp)}...")
                results = competitor_service.search_competitors(selected_product_id, marketplaces_sel, keyword=search_keyword.strip())
                status_placeholder.empty()
                if results:
                    st.success(f"✅ {len(results)} resultados encontrados!")
                else:
                    st.warning("Nenhum resultado encontrado. Tente termos de busca diferentes ou verifique as sessões de login.")
                st.rerun()

    existing_data = competitor_service.get_comparison_data(selected_product_id)

    if existing_data:
        badge = competitor_service.get_competitiveness_badge(selected_product_id)
        badge_colors = {"green": "🟢", "orange": "🟠", "red": "🔴", "gray": "⚪"}
        st.markdown(f"### {badge_colors.get(badge['color'], '⚪')} {badge['label']}")

        st.divider()
        st.subheader("📊 Tabela Comparativa")

        product_obj = next((p for p in products if p.id == selected_product_id), None)
        our_price = product_obj.price if product_obj else 0

        col_our1, col_our2, col_our3 = st.columns(3)
        with col_our1:
            st.metric("Nosso Preço", f"R${our_price:.2f}")
        with col_our2:
            confirmed_data = [d for d in existing_data if d["is_confirmed_match"]]
            ref_data = confirmed_data if confirmed_data else existing_data
            comp_prices = [d["competitor_price"] for d in ref_data if d["competitor_price"] > 0]
            st.metric("Média Concorrentes", f"R${sum(comp_prices)/len(comp_prices):.2f}" if comp_prices else "—")
        with col_our3:
            st.metric("Total Encontrados", f"{len(existing_data)}")

        table_data = []
        for d in existing_data:
            mp_label = MARKETPLACE_LABELS.get(d["marketplace"], d["marketplace"])
            diff_sign = "+" if d["price_diff"] >= 0 else ""
            conf_icon = "✅" if d["is_confirmed_match"] else ("🔍" if d.get("confidence_score") in ["alto", "médio"] else "❓")

            table_data.append({
                "MP": mp_label,
                "Título": d["competitor_title"][:50] + ("..." if len(d["competitor_title"]) > 50 else ""),
                "Preço": f"R${d['competitor_price']:.2f}",
                "Nosso": f"R${d['our_price_at_time']:.2f}",
                "Diferença": f"{diff_sign}{d['price_diff_pct']:.1f}%",
                "Vendedor": d.get("competitor_seller", ""),
                "Frete": "Gratis" if d.get("shipping_cost") == 0.0 else ("R$" + f"{d['shipping_cost']:.2f}" if d.get("shipping_cost") else "—"),
                "Match": conf_icon,
                "Confiança": d.get("confidence_score", "—"),
            })

        if table_data:
            df = pd.DataFrame(table_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

        st.divider()
        st.subheader("✅ Confirmar Matches")

        unconfirmed = [d for d in existing_data if not d["is_confirmed_match"]]
        if unconfirmed:
            for d in unconfirmed[:10]:
                mp_label = MARKETPLACE_LABELS.get(d["marketplace"], d["marketplace"])
                with st.container(border=True):
                    col_info, col_actions = st.columns([4, 1])
                    with col_info:
                        st.markdown(f"**{mp_label}** — {d['competitor_title']}")
                        st.caption(f"Preço: R${d['competitor_price']:.2f} | Confiança IA: {d.get('confidence_score', '—')} | Vendedor: {d.get('competitor_seller', '—')}")
                    with col_actions:
                        c1, c2 = st.columns(2)
                        if c1.button("✅", key=f"confirm_{d['id']}"):
                            competitor_service.confirm_match(d["id"], True)
                            st.toast("Match confirmado!")
                            st.rerun()
                        if c2.button("❌", key=f"reject_{d['id']}"):
                            competitor_service.confirm_match(d["id"], False)
                            st.toast("Match rejeitado!")
                            st.rerun()
        else:
            st.info("Todos os matches foram confirmados/rejeitados.")

        st.divider()
        col_clear1, col_clear2 = st.columns([1, 4])
        with col_clear1:
            with st.popover("🗑️ Limpar Dados", use_container_width=True):
                st.error("Tem certeza? Os dados de concorrência deste produto serão apagados.")
                if st.button("Sim, limpar tudo", type="primary", key="confirm_clear_comp"):
                    competitor_service.clear_listings(selected_product_id)
                    st.toast("Dados limpos!")
                    st.rerun()
        with col_clear2:
            st.caption("Última verificação: " + (existing_data[0]["last_checked_at"].strftime("%d/%m/%Y %H:%M") if existing_data else "—"))

    else:
        st.info("Nenhum dado de concorrência ainda. Selecione um produto e clique **Buscar Preços** para começar.")
