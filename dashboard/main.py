import streamlit as st
import pandas as pd
import re
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

# Custom CSS to make Primary Button Green (Success Color)
st.markdown("""
<style>
div.stButton > button:first-child[kind="primary"] {
    background-color: #4CAF50;
    border-color: #4CAF50;
    color: white;
}
div.stButton > button:first-child[kind="primary"]:hover {
    background-color: #45a049;
    border-color: #45a049;
}
</style>
""", unsafe_allow_html=True)

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
        
        st.divider()
        # Dev Tools
        with st.expander("🛠️ Admin Tools"):
            if st.button("🔄 Recarregar Sistema"):
                import importlib
                import sys
                import agents.finance_agent
                import agents.product_agent
                import agents.ads_agent
                
                # Force reload of agent modules
                importlib.reload(sys.modules['agents.finance_agent'])
                importlib.reload(sys.modules['agents.product_agent'])
                if 'agents.ads_agent' in sys.modules:
                    importlib.reload(sys.modules['agents.ads_agent'])
                
                # Clear Streamlit Cache
                st.cache_data.clear()
                st.cache_resource.clear()
                
                st.toast("Sistema recarregado com Sucesso!", icon="✅")
                st.rerun()
    
    # Main Content
    st.title("🚀 Shopee Growth Quest")
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🏠 Resumo", "💰 Financeiro", "📢 Central de Marketing", "🤝 Atendimento", "📦 Meus Anúncios", "⚙️ Configurações"])
    
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
        
        
        # Real Analysis - Always Run (Top Priority)
        with st.container():
            analysis = finance_agent.analyze_health(user.id)
            stats = analysis["stats"]
            
            # KPIs
            k1, k2, k3 = st.columns(3)
            k1.metric("Faturamento", f"R$ {stats['total_revenue']:.2f}")
            k2.metric("Custos", f"R$ {stats['total_expenses']:.2f}")
            k3.metric("Lucro Líquido", f"R$ {stats['net_profit']:.2f}", delta=f"{stats['margin']:.1f}% Margem")
            
            # Prepare Data
            all_transactions = [{"Data": t.date, "Desc": t.description, "Valor": t.amount, "Tipo": t.type} for t in stats["raw_data"]]
            df_all = pd.DataFrame(all_transactions)
            
            if not df_all.empty:
                # 1. Chart: Monthly Comparison (Revenue vs Expenses)
                st.subheader("📉 Comparativo Financeiro")
                df_all['Mês'] = pd.to_datetime(df_all['Data']).dt.strftime('%Y-%m') # Sortable format
                
                # Group by Month and Type
                chart_data = df_all.groupby(['Mês', 'Tipo'])['Valor'].sum().unstack().fillna(0)
                
                # Colors: INCOME=Green, EXPENSE=Red
                st.bar_chart(chart_data, color=["#ff4b4b", "#4bceac"] if 'EXPENSE' in chart_data.columns else ["#4bceac"])

                # 2. Last 10 Transactions (Always Open)
                st.subheader("⏱️ Últimas 10 Transações")
                # Sort by Date Descending
                df_sorted = df_all.sort_values(by="Data", ascending=False)
                st.dataframe(
                    df_sorted.head(10).style.format({"Valor": "R$ {:.2f}"}), 
                    width="stretch",
                    hide_index=True
                )

                # 3. Full History & Management (Closed Dropdown)
                with st.expander("📝 Gerenciar Histórico (Editar/Excluir)"):
                    # We need the ID to update/delete
                    all_transactions_with_id = [{"ID": t.id, "Data": t.date, "Desc": t.description, "Valor": t.amount, "Tipo": t.type, "Categoria": t.category} for t in stats["raw_data"]]
                    df_edit = pd.DataFrame(all_transactions_with_id)
                    
                    # Sort by Date Descending for display
                    df_edit = df_edit.sort_values(by="Data", ascending=False)
                    
                    # Editable Dataframe
                    edited_df = st.data_editor(
                        df_edit,
                        column_config={
                            "ID": st.column_config.NumberColumn(disabled=True),
                            "Data": st.column_config.DateColumn("Data"),
                            "Valor": st.column_config.NumberColumn("Valor", format="R$ %.2f"),
                            "Tipo": st.column_config.SelectboxColumn("Tipo", options=["INCOME", "EXPENSE"]),
                            "Categoria": st.column_config.SelectboxColumn("Categoria", options=["Sale", "Ads", "Custo Produto", "Assinatura", "Outros"]),
                        },
                        hide_index=True,
                        num_rows="dynamic", # Allows adding/deleting rows
                        key="transaction_editor",
                        width="stretch"
                    )
                    
                    # Control Buttons
                    b1, b2, b3, b4 = st.columns(4)
                    
                    # 1. Save
                    if b1.button("Salvar 💾", type="primary", width="stretch"):
                        # Identify Changes
                        # 1. Deletions (Rows present in original but missing in edited)
                        original_ids = set(df_edit["ID"])
                        edited_ids = set(edited_df["ID"].dropna()) # dropna for new rows which might have NaN ID
                        
                        ids_to_delete = original_ids - edited_ids
                        
                        changes_log = []
                        
                        # Process Deletions
                        for txn_id in ids_to_delete:
                            res = finance_agent.delete_transaction(int(txn_id))
                            if res["success"]:
                                changes_log.append(f"❌ ID {txn_id}: Deletado")
                        
                        # Process Updates (Rows with same ID but different content)
                        # We iterate over edited_df where ID exists
                        for index, row in edited_df.iterrows():
                            txn_id = row.get("ID")
                            
                            if pd.notna(txn_id):
                                # Check if changed
                                original_row = df_edit[df_edit["ID"] == txn_id].iloc[0]
                                
                                # Compare fields
                                updates = {}
                                if row["Desc"] != original_row["Desc"]: updates["description"] = row["Desc"]
                                if row["Valor"] != original_row["Valor"]: updates["amount"] = float(row["Valor"])
                                if row["Tipo"] != original_row["Tipo"]: updates["type"] = row["Tipo"]
                                if row["Categoria"] != original_row["Categoria"]: updates["category"] = row["Categoria"]
                                # Date comparison (careful with types)
                                if pd.to_datetime(row["Data"]) != pd.to_datetime(original_row["Data"]): updates["date"] = pd.to_datetime(row["Data"])

                                if updates:
                                    res = finance_agent.update_transaction(int(txn_id), updates)
                                    if res["success"]:
                                        changes_log.append(f"✏️ ID {txn_id}: Atualizado")

                        if changes_log:
                            st.success(f"Alterações salvas:\n" + "\n".join(changes_log))
                            st.rerun()
                        else:
                            st.info("Nenhuma alteração detectada.")

                    # 2. Undo
                    if b2.button("Desfazer ↩️", width="stretch"):
                        st.toast("Dica: Use **Ctrl+Z** (ou Cmd+Z) dentro da tabela para desfazer!", icon="💡")

                    # 3. Redo
                    if b3.button("Refazer ↪️", width="stretch"):
                        st.toast("Dica: Use **Ctrl+Shift+Z** dentro da tabela para refazer!", icon="💡")
                    
                    # 4. Restore (Discard Changes)
                    if b4.button("Restaurar 🔄", width="stretch"):
                        st.rerun()

                # Deep Analysis Button
                st.divider()
                if st.button("🧠 Análise Profunda do Guardião", width="stretch"):
                    with st.spinner("O Guardião está analisando cada centavo do seu cofre..."):
                        report = finance_agent.generate_deep_analysis(user.id)
                        
                        with st.expander("📄 Relatório Estratégico do CFO", expanded=True):
                            st.markdown(report)
            
        st.divider()

        col_in, col_out = st.columns(2)
        
        # Income Section (Upload)
        with col_in:
            st.subheader("📥 Receitas (Upload)")
            st.caption("Relatório Shopee")
            uploaded_file = st.file_uploader("Arquivo", type=["csv", "xlsx"], label_visibility="collapsed")
            
            if uploaded_file:
                if st.button("Processar Arquivo 📥"):
                    with st.spinner("Lendo..."):
                        result = finance_agent.process_upload(uploaded_file, user.id)
                        if result["success"]:
                            st.success("Sucesso!")
                            st.rerun()
                        else:
                            st.error(result["message"])

        # Expense Section (Manual)
        with col_out:
            st.subheader("💸 Despesas (Manual)")
            with st.form("expense_form"):
                d_date = st.date_input("Data")
                d_desc = st.text_input("Descrição", placeholder="Ex: Assinatura, Google Ads")
                d_val = st.number_input("Valor (R$)", min_value=0.01, step=10.0)
                d_cat = st.selectbox("Categoria", ["Ads", "Custo Produto", "Assinatura", "Outros"])
                
                if st.form_submit_button("Registrar Gasto 📤"):
                    res = finance_agent.add_transaction(
                        date=d_date,
                        description=d_desc,
                        amount=d_val,
                        category=d_cat,
                        type="EXPENSE",
                        user_id=user.id
                    )
                    if res["success"]:
                        st.success("Registrado!")
                        st.rerun()
                    else:
                        st.error(res["message"])

    with tab3:
        st.header("📢 Central de Marketing")
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
        st.header("📦 Gestão de Anúncios")
        from agents.product_agent import ProductAgent
        if 'product_agent' not in st.session_state:
            st.session_state.product_agent = ProductAgent()
        
        # Carregar dados (Anúncios Shopee e Itens de Inventário Físico)
        products = st.session_state.product_agent.get_all_products(user.id)
        inventory_items = st.session_state.product_agent.get_all_inventory_items(user.id)
        
        # -- LÓGICA DE AGREGAÇÃO UNIFICADA --
        total_potes_vendidos = 0
        total_cogs_vendas = 0.0
        total_variantes_vendidas = 0
        product_groups = {}
        vendidos_por_item = {item.id: 0 for item in inventory_items} if inventory_items else {}

        if products:
            for p in products:
                base_name = re.sub(r' - \d+x$', '', p.title.strip()).strip()
                pkgs_sold = (p.initial_stock or 100) - p.stock
                if pkgs_sold < 0: pkgs_sold = 0
                
                total_variantes_vendidas += pkgs_sold
                ad_potes_sold = 0
                ad_cogs = 0.0
                
                if hasattr(p, 'components') and p.components:
                    for comp in p.components:
                        inv_item = next((i for i in inventory_items if i.id == comp.inventory_item_id), None)
                        qty = comp.quantity or 1
                        item_units = pkgs_sold * qty
                        item_cogs = item_units * (inv_item.supplier_price if inv_item else 0.0)
                        ad_potes_sold += item_units
                        ad_cogs += item_cogs
                        if comp.inventory_item_id in vendidos_por_item:
                            vendidos_por_item[comp.inventory_item_id] += item_units
                else:
                    ad_potes_sold = pkgs_sold
                    ad_cogs = pkgs_sold * (p.supplier_price or 0.0)

                if base_name not in product_groups:
                    product_groups[base_name] = {"units": 0, "cogs": 0.0, "variations": []}
                
                product_groups[base_name]["units"] += ad_potes_sold
                product_groups[base_name]["cogs"] += ad_cogs
                product_groups[base_name]["variations"].append({
                    "id": p.id, "title": p.title, "pkgs": pkgs_sold, "stock": p.stock, "units": ad_potes_sold, "cogs": ad_cogs
                })
                total_potes_vendidos += ad_potes_sold
                total_cogs_vendas += ad_cogs

        sub_tab_vendas, sub_tab_estoque = st.tabs(["📊 Desempenho de Vendas", "🏬 Estoque de Potes (Físico)"])

        with sub_tab_vendas:
            st.subheader("📈 Performance Comercial")
            
            if products:
                c1, c2 = st.columns(2)
                c1.metric("Produtos (Bases)", len(product_groups))
                c2.metric("Variações Vendidas", f"{total_variantes_vendidas} kits")
                
                st.divider()
                
                st.markdown("""
                <style>
                [data-testid="stExpander"] summary div[data-testid="stMarkdownContainer"] { width: 100% !important; }
                [data-testid="stExpander"] summary p { display: flex !important; justify-content: space-between !important; width: 100% !important; align-items: center !important; }
                </style>
                """, unsafe_allow_html=True)

                for base_name, data in product_groups.items():
                    label = f"📦 {base_name} **:green[Vendidos: {data['units']} un.] &nbsp;|&nbsp; :red[Custo: R$ {data['cogs']:,.2f}]**"
                    with st.expander(label):
                        for v in data["variations"]:
                            m = re.search(r'- (\d+)x$', v['title'])
                            n = m.group(1) if m else "1"
                            txt = f"{n} Frasco" if n == "1" else f"{n} Frascos"
                            st.markdown(f"""
                                <div style='display: flex; justify-content: space-between; border-bottom: 1px solid #ffffff1e; padding: 5px 0;'>
                                    <span>Variação: <b>{txt}</b></span>
                                    <span>
                                        <span style='color: #4CAF50;'>{v['pkgs']} kits</span> &nbsp;|&nbsp; Stock Shopee: {v['stock']} &nbsp;|&nbsp; <span style='color: #F44336;'>Custo: R$ {v['cogs']:,.2f}</span>
                                    </span>
                                </div>
                            """, unsafe_allow_html=True)
            else:
                st.info("Nenhum anúncio mapeado.")
                
        with sub_tab_estoque:
            st.subheader("🏬 Inventário de Potes Físicos")
            if inventory_items:
                c1, c2 = st.columns(2)
                c1.metric("Potes Vendidos (Real)", f"{total_potes_vendidos} un.", help="Soma física de todos os potes de todos os kits")
                c2.metric("COGS (Custo de Venda)", f"R$ {total_cogs_vendas:,.2f}", delta="-Saída", delta_color="inverse")
                
                df_inv = pd.DataFrame([{
                    "ID": item.id,
                    "Nome": item.name,
                    "Custo": item.supplier_price,
                    "Potes Vendidos": vendidos_por_item.get(item.id, 0)
                } for item in inventory_items])

                st.info("💡 O estoque é controlado automaticamente pelo 'E. Shopee' nos SKUs Virtuais abaixo.")

 
                
                edited_inv = st.data_editor(
                    df_inv,
                    column_config={
                        "ID": None,
                        "Custo": st.column_config.NumberColumn(format="R$ %.2f"),
                        "Potes Vendidos": st.column_config.NumberColumn(disabled=True)
                    },
                    hide_index=True, use_container_width=True, key="inv_ed"
                )

                if st.button("Salvar Alterações de Custo"):
                    for _, row in edited_inv.iterrows():
                        st.session_state.product_agent.update_inventory_item(int(row["ID"]), {
                            "name": row["Nome"], 
                            "supplier_price": float(row["Custo"])
                        })
                    st.success("Costos atualizados!")
                    st.rerun()
            
            with st.expander("➕ Novo Item Físico"):
                col_i1, col_i2 = st.columns(2)
                ni_name = col_i1.text_input("Nome", key="ni_name_inp")
                ni_cost = col_i2.number_input("Custo", min_value=0.0, key="ni_cost_inp")
                if st.button("Adicionar Item"):
                    from core.database.models import InventoryItem
                    session = next(get_session()); session.add(InventoryItem(name=ni_name, supplier_price=ni_cost, stock=0, initial_stock=0, user_id=user.id)); session.commit()
                    st.success("Adicionado!"); st.rerun()

        st.divider()
        with st.expander("📑 Editor de Anúncios Shopee (SKUs Virtuais)"):
            if products:
                df_prods = pd.DataFrame([{"ID": p.id, "Título": p.title, "Preço": p.price, "E. Shopee": p.stock} for p in products])
                edit_ads = st.data_editor(df_prods, column_config={"ID": None}, hide_index=True, use_container_width=True, key="ads_ed")
                if st.button("Salvar Anúncios"):
                    for _, row in edit_ads.iterrows():
                        st.session_state.product_agent.update_product(int(row["ID"]), {"title": row["Título"], "price": float(row["Preço"]), "stock": int(row["E. Shopee"])})
                    st.success("Anúncios salvos!"); st.rerun()
            else:
                st.info("Nenhum anúncio para editar.")
            
            with st.expander("➕ Novo SKU Virtual (Manual)"):
                col_nv1, col_nv2, col_nv3 = st.columns([2, 1, 1])
                nv_title = col_nv1.text_input("Título do Anúncio", key="nv_title_inp")
                nv_price = col_nv2.number_input("Preço de Venda", min_value=0.0, key="nv_price_inp")
                nv_stock = col_nv3.number_input("E. Shopee", min_value=0, step=1, key="nv_stock_inp")
                if st.button("Adicionar SKU Virtual"):
                    st.session_state.product_agent.save_product({
                        "title": nv_title, "price": nv_price, "stock": int(nv_stock), "description": "Manual"
                    }, user.id)
                    st.success("SKU Virtual adicionado!"); st.rerun()
                    
        st.divider()

        # 2. ADICIONAR ANÚNCIO (The core engine)
        with st.container(border=True):
            st.subheader("➕ Adicionar Novo Anúncio com IA")
            
            method = st.radio("Método de Criação:", ["Manual (Texto)", "Imagem (Vision + IA Search) 📸"], horizontal=True)
            
            if method == "Manual (Texto)":
                col_m1, col_m2 = st.columns([1, 1])
                with col_m1:
                    p_name = st.text_input("Nome do Produto", placeholder="Ex: Creatina Monohidratada Pura", key="manual_name")
                    p_ing = st.text_input("Ingredientes/Detalhes", placeholder="Ex: 300g, 100% Pura", key="manual_ing")
                with col_m2:
                    p_ben = st.text_area("Principais Benefícios", placeholder="Ex: Aumento de força...", key="manual_ben")
                
                if st.button("Gerar Anúncio ✨", type="primary", key="btn_manual"):
                    if p_name and p_ben:
                        with st.spinner("🤖 Analisando e criando copy..."):
                            listing = st.session_state.product_agent.generate_listing(p_name, p_ben, p_ing)
                            st.session_state.last_generated_res = listing
                    else:
                        st.warning("Preencha o Nome e os Benefícios.")
            
            else: # Image Method
                st.info("💡 Passo 1: Envie uma foto e a IA identificará o produto. Passo 2: Você revisa e geramos o anúncio com busca web.")
                img_file = st.file_uploader("Upload da Imagem do Produto", type=["jpg", "jpeg", "png"])
                
                if img_file:
                    st.image(img_file, width=200)
                    if st.button("Passo 1: Extrair Informações 📸", type="primary"):
                        with st.spinner("Lendo rótulo..."):
                            img_bytes = img_file.getvalue()
                            info = st.session_state.product_agent.extract_product_info(img_bytes)
                            st.session_state.extracted_info = info
                            if 'last_generated_res' in st.session_state: del st.session_state.last_generated_res

                if 'extracted_info' in st.session_state:
                    st.divider()
                    st.markdown("### 📝 Informações Detectadas")
                    st.caption("Ajuste os dados abaixo se necessário antes da pesquisa web.")
                    edited_info = st.text_area("Dados do Produto", value=st.session_state.extracted_info, height=150)
                    
                    if st.button("Passo 2: Gerar Anúncio Completo (com Busca Web) 🔍", type="primary"):
                        with st.spinner("Pesquisando na internet e criando copy..."):
                            listing = st.session_state.product_agent.generate_from_extracted_info(edited_info)
                            st.session_state.last_generated_res = listing
                            # Keep extracted_info so they can refine and regenerate if needed, 
                            # but usually we might want to clear it after saving.
            
            # Review and Save Area (Shared for both methods)
            if 'last_generated_res' in st.session_state:
                res = st.session_state.last_generated_res
                st.divider()
                st.markdown("### 🕵️ Revisão e Ajustes Finais")
                
                edit_title = st.text_input("Título SEO", value=res['title'])
                edit_keys = st.text_area("Keywords (Tags)", value=res.get('keywords', ''))
                edit_desc = st.text_area("Descrição", value=res['description'], height=300)
                
                col1, col2 = st.columns(2)
                p_price = col1.number_input("Preço de Venda (R$)", min_value=0.0, step=1.0, value=0.0, key="price_input")
                p_stock = col2.number_input("Estoque Inicial", min_value=0, step=1, value=100, key="stock_input")
                
                if st.button("💾 Confirmar e Salvar no Catálogo", type="primary", width="stretch"):
                    final_data = {
                        "title": edit_title,
                        "description": edit_desc,
                        "keywords": edit_keys,
                        "price": p_price,
                        "stock": p_stock
                    }
                    save_res = st.session_state.product_agent.save_product(final_data, user.id)
                    if save_res["success"]:
                        st.success(f"Produto '{edit_title}' salvo com sucesso!")
                        del st.session_state.last_generated_res
                        st.rerun()
                    else:
                        st.error(f"Erro ao salvar: {save_res['message']}")

        st.divider()

        # 3. IMPORTAR & EXPORTAR (In Expanders to keep page clean)
        col_ie1, col_ie2 = st.columns(2)
        
        with col_ie1:
            with st.expander("📥 Importar da Shopee (CSV)"):
                st.caption("Suba o arquivo CSV exportado da Shopee para cadastrar em massa.")
                up_file = st.file_uploader("Selecione o CSV", type=["csv"], key="import_csv")
                if up_file:
                    if st.button("Processar Importação 📥", key="btn_import"):
                        with st.spinner("Importando produtos..."):
                            imp_res = st.session_state.product_agent.process_csv_import(up_file, user.id)
                            if imp_res["success"]:
                                st.success(f"Sucesso! {imp_res['count']} produtos importados.")
                                st.rerun()
                            else:
                                st.error(imp_res["message"])

        with col_ie2:
            with st.expander("📤 Exportar para Shopee (CSV)"):
                st.caption("Selecione os produtos do catálogo para gerar o arquivo de upload.")
                products_to_export = st.session_state.product_agent.get_all_products(user.id)
                
                if products_to_export:
                    df_exp = pd.DataFrame([{
                        "Sel": False,
                        "ID": p.id,
                        "Título": p.title
                    } for p in products_to_export])
                    
                    edited_exp = st.data_editor(df_exp, hide_index=True, width="stretch", key="export_editor")
                    selected_ids = edited_exp[edited_exp["Sel"] == True]["ID"].tolist()
                    
                    if st.button("Gerar CSV 📤", key="btn_export"):
                        if selected_ids:
                            selected_prods = [p for p in products_to_export if p.id in selected_ids]
                            export_data = []
                            for sp in selected_prods:
                                desc_with_keys = sp.description
                                if sp.keywords: desc_with_keys += f"\n\nTAGS: {sp.keywords}"
                                    
                                export_data.append({
                                    "title": sp.title,
                                    "description": desc_with_keys,
                                    "price": sp.price,
                                    "stock": sp.stock,
                                    "sku": sp.sku or "",
                                    "weight": 0.5
                                })
                            
                            csv_data = st.session_state.product_agent.generate_mass_upload_csv(export_data)
                            st.download_button("Clique para Download", data=csv_data, file_name="upload_shopee.csv", mime="text/csv")
                        else:
                            st.warning("Selecione itens.")
                else:
                    st.info("Catálogo vazio.")


    with tab6:
        from dashboard.components.settings_view import render_settings_page
        render_settings_page()

if __name__ == "__main__":
    main()
