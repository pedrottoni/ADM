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
    # Initialize Agents
    from agents.finance_agent import FinanceAgent
    from agents.product_agent import ProductAgent
    from agents.ads_agent import AdsAgent
    from agents.customer_agent import CustomerAgent

    if 'finance_agent' not in st.session_state: st.session_state.finance_agent = FinanceAgent()
    if 'product_agent' not in st.session_state: st.session_state.product_agent = ProductAgent()
    if 'ads_agent' not in st.session_state: st.session_state.ads_agent = AdsAgent()
    if 'customer_agent' not in st.session_state: st.session_state.customer_agent = CustomerAgent()

    finance_agent = st.session_state.finance_agent
    product_agent = st.session_state.product_agent
    ads_agent = st.session_state.ads_agent
    customer_agent = st.session_state.customer_agent

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
            low_stock_items = product_agent.get_low_stock_items(user.id)
            if low_stock_items:
                for item in low_stock_items:
                    st.error(f"⚠️ **Alerta**: Estoque de '{item.name}' está baixo ({item.stock} un | Mín: {item.min_stock})")
            else:
                st.success("✅ Todos os itens do inventário estão com estoque saudável.")

    with tab2:
        st.header("Guardiao Financeiro")
        
        
        # Real Analysis - Always Run (Top Priority)
        with st.container():
            analysis = finance_agent.analyze_health(user.id)
            stats = analysis["stats"]
            
            # KPIs
            k1, k2, k3 = st.columns(3)
            k1.metric("Faturamento", f"R$ {stats['total_revenue']:.2f}")
            k2.metric("Custos", f"R$ {stats['total_expenses']:.2f}")
            k3.metric("Lucro Liquido", f"R$ {stats['net_profit']:.2f}", delta=f"{stats['margin']:.1f}% Margem")
            
            # Prepare Data
            all_transactions = [{"Data": t.date, "Desc": t.description, "Valor": t.amount, "Tipo": t.type} for t in stats["raw_data"]]
            df_all = pd.DataFrame(all_transactions)
            
            if not df_all.empty:
                # 1. Chart: Monthly Comparison (Revenue vs Expenses)
                st.subheader("Comparativo Financeiro")
                df_all['Mes'] = pd.to_datetime(df_all['Data']).dt.strftime('%Y-%m') # Sortable format
                
                # Group by Month and Type
                chart_data = df_all.groupby(['Mes', 'Tipo'])['Valor'].sum().unstack().fillna(0)
                
                # Colors: dynamically match columns present
                color_map = {"EXPENSE": "#ff4b4b", "INCOME": "#4bceac"}
                chart_colors = [color_map[col] for col in chart_data.columns if col in color_map]
                if chart_colors:
                    st.bar_chart(chart_data, color=chart_colors)
                else:
                    st.bar_chart(chart_data)

                # 2. Last 10 Transactions (Always Open)
                st.subheader("Ultimas 10 Transacoes")
                # Sort by Date Descending
                df_sorted = df_all.sort_values(by="Data", ascending=False)
                st.dataframe(
                    df_sorted.head(10).style.format({"Valor": "R$ {:.2f}"}), 
                    width="stretch",
                    hide_index=True
                )

                # 3. Full History & Management (Closed Dropdown)
                with st.expander("Gerenciar Historico (Editar/Excluir)"):
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
                    if b1.button("Salvar", type="primary", width="stretch"):
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
                                changes_log.append(f"ID {txn_id}: Deletado")
                        
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
                                        changes_log.append(f"ID {txn_id}: Atualizado")

                        if changes_log:
                            st.success(f"Alteracoes salvas:\n" + "\n".join(changes_log))
                            st.rerun()
                        else:
                            st.info("Nenhuma alteracao detectada.")

                    # 2. Undo
                    if b2.button("Desfazer", width="stretch"):
                        st.toast("Dica: Use **Ctrl+Z** (ou Cmd+Z) dentro da tabela para desfazer!")

                    # 3. Redo
                    if b3.button("Refazer", width="stretch"):
                        st.toast("Dica: Use **Ctrl+Shift+Z** dentro da tabela para refazer!")
                    
                    # 4. Restore (Discard Changes)
                    if b4.button("Restaurar", width="stretch"):
                        st.rerun()

                # Deep Analysis Button
                st.divider()
                if st.button("Analise Profunda do Guardiao", width="stretch"):
                    with st.spinner("O Guardiao esta analisando cada centavo do seu cofre..."):
                        report = finance_agent.generate_deep_analysis(user.id)
                        
                        with st.expander("Relatorio Estrategico do CFO", expanded=True):
                            st.markdown(report)
            
        st.divider()

        # =====================================================
        # INCOME & EXPENSE FORMS (Redesigned)
        # =====================================================
        col_in, col_mid, col_out = st.columns(3)
        
        # --- COLUMN 1: Upload CSV/XLSX (LLM-Powered, 2-Phase) ---
        with col_in:
            st.subheader("Receitas (Upload)")
            st.caption("Relatorio Shopee ou CSV de vendas")
            uploaded_file = st.file_uploader("Arquivo", type=["csv", "xlsx"], label_visibility="collapsed", key="income_upload")
            
            if uploaded_file:
                if st.button("Processar com IA", type="primary", key="btn_process_upload"):
                    with st.spinner("A IA esta interpretando seu arquivo..."):
                        result = finance_agent.process_upload(uploaded_file, user.id)
                        if result["success"]:
                            st.session_state["upload_preview"] = result["data"]
                            st.session_state["upload_message"] = result["message"]
                            st.rerun()
                        else:
                            st.error(result["message"])
                            if "raw_response" in result:
                                with st.expander("Resposta bruta da IA"):
                                    st.text(result["raw_response"])
            
            # Show preview if exists
            if "upload_preview" in st.session_state and st.session_state["upload_preview"]:
                preview_data = st.session_state["upload_preview"]
                st.info(st.session_state.get("upload_message", ""))
                
                df_preview = pd.DataFrame(preview_data)
                edited_preview = st.data_editor(
                    df_preview,
                    column_config={
                        "date": st.column_config.DateColumn("Data"),
                        "product": st.column_config.TextColumn("Produto"),
                        "amount": st.column_config.NumberColumn("Valor", format="R$ %.2f"),
                        "quantity": st.column_config.NumberColumn("Qtd"),
                        "status": st.column_config.TextColumn("Status"),
                    },
                    hide_index=True,
                    num_rows="dynamic",
                    key="upload_preview_editor",
                    use_container_width=True
                )
                
                cp1, cp2 = st.columns(2)
                if cp1.button("Confirmar e Salvar", type="primary", key="btn_confirm_upload", use_container_width=True):
                    # Convert edited dataframe back to list of dicts
                    confirmed_data = edited_preview.to_dict(orient="records")
                    with st.spinner("Salvando transacoes e atualizando estoques..."):
                        confirm_result = finance_agent.confirm_upload(confirmed_data, user.id)
                        if confirm_result["success"]:
                            msg_parts = [f"Total: {confirm_result['total']}"]
                            msg_parts.append(f"Vinculados: {confirm_result['matched_count']}")
                            if confirm_result['duplicated_count'] > 0:
                                msg_parts.append(f"Duplicados (ignorados): {confirm_result['duplicated_count']}")
                            if confirm_result['unmatched_count'] > 0:
                                msg_parts.append(f"Nao encontrados: {confirm_result['unmatched_count']}")
                            
                            st.success(" | ".join(msg_parts))
                            
                            # Store unmatched for resolution
                            if confirm_result["unmatched"]:
                                st.session_state["unmatched_products"] = confirm_result["unmatched"]
                            
                            # Clear preview
                            del st.session_state["upload_preview"]
                            if "upload_message" in st.session_state:
                                del st.session_state["upload_message"]
                            st.rerun()
                        else:
                            st.error(confirm_result["message"])
                
                if cp2.button("Descartar", key="btn_discard_upload", use_container_width=True):
                    del st.session_state["upload_preview"]
                    if "upload_message" in st.session_state:
                        del st.session_state["upload_message"]
                    st.rerun()
        
        # --- COLUMN 2: Manual Income Form (NEW) ---
        with col_mid:
            st.subheader("Receitas (Manual)")
            
            # Load products for selectbox
            from agents.product_agent import ProductAgent
            if 'product_agent_fin' not in st.session_state:
                st.session_state.product_agent_fin = ProductAgent()
            
            products_list = st.session_state.product_agent_fin.get_all_products(user.id)
            product_names = ["-- Selecione --"] + [p.title for p in products_list] + ["Outro (digitar)"]
            product_map = {p.title: p.id for p in products_list}
            
            with st.form("income_form"):
                i_date = st.date_input("Data", key="inc_date")
                i_product_choice = st.selectbox("Produto", product_names, key="inc_product")
                i_desc_manual = st.text_input("Descricao (se 'Outro')", placeholder="Nome do produto", key="inc_desc")
                
                ic1, ic2 = st.columns(2)
                i_val = ic1.number_input("Valor (R$)", min_value=0.01, step=10.0, key="inc_val")
                i_qty = ic2.number_input("Quantidade", min_value=1, step=1, value=1, key="inc_qty")
                
                if st.form_submit_button("Registrar Venda"):
                    # Determine product_id and description
                    selected_product_id = None
                    description = i_desc_manual
                    
                    if i_product_choice != "-- Selecione --" and i_product_choice != "Outro (digitar)":
                        selected_product_id = product_map.get(i_product_choice)
                        description = i_product_choice
                    elif i_product_choice == "-- Selecione --":
                        st.warning("Selecione um produto ou escolha 'Outro'.")
                        st.stop()
                    
                    if not description:
                        st.warning("Preencha a descricao do produto.")
                        st.stop()
                    
                    res = finance_agent.add_transaction(
                        date=i_date,
                        description=description,
                        amount=i_val,
                        category="Sale",
                        type="INCOME",
                        user_id=user.id,
                        product_id=selected_product_id,
                        quantity=i_qty
                    )
                    if res["success"]:
                        if res.get("stock_updated"):
                            st.success(f"Venda registrada! Estoque atualizado.")
                        else:
                            st.success("Venda registrada (sem produto vinculado ao estoque).")
                        st.rerun()
                    else:
                        st.error(res["message"])

        # --- COLUMN 3: Expense Form (Existing) ---
        with col_out:
            st.subheader("Despesas (Manual)")
            with st.form("expense_form"):
                d_date = st.date_input("Data")
                d_desc = st.text_input("Descricao", placeholder="Ex: Assinatura, Google Ads")
                d_val = st.number_input("Valor (R$)", min_value=0.01, step=10.0)
                d_cat = st.selectbox("Categoria", ["Ads", "Custo Produto", "Assinatura", "Outros"])
                
                if st.form_submit_button("Registrar Gasto"):
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

        # =====================================================
        # UNMATCHED PRODUCTS RESOLUTION PANEL
        # =====================================================
        if "unmatched_products" in st.session_state and st.session_state["unmatched_products"]:
            st.divider()
            st.subheader("Produtos Nao Encontrados")
            st.caption("Estas vendas foram salvas no financeiro, mas nao foram vinculadas a nenhum produto. Escolha o que fazer:")
            
            unmatched = st.session_state["unmatched_products"]
            items_to_remove = []
            
            for idx, item in enumerate(unmatched):
                with st.container(border=True):
                    uc1, uc2, uc3, uc4 = st.columns([3, 1, 1, 1])
                    uc1.markdown(f"**{item['description']}** - R$ {item['amount']:.2f} (Qtd: {item.get('quantity', 1)})")
                    
                    if uc2.button("Ignorar", key=f"ignore_{idx}", use_container_width=True):
                        items_to_remove.append(idx)
                    
                    if uc3.button("+ SKU", key=f"add_sku_{idx}", use_container_width=True):
                        # Create a new Product (SKU Virtual)
                        from agents.product_agent import ProductAgent
                        pa = ProductAgent()
                        save_res = pa.save_product({
                            "title": item["description"],
                            "description": "Criado automaticamente via venda nao mapeada",
                            "price": float(item["amount"]),
                            "stock": max(100 - int(item.get("quantity", 1)), 0),
                            "initial_stock": 100
                        }, user.id)
                        if save_res["success"]:
                            st.success(f"SKU '{item['description']}' criado!")
                            items_to_remove.append(idx)
                        else:
                            st.error(f"Erro: {save_res.get('message', 'Desconhecido')}")

                    if uc4.button("+ Inventario", key=f"add_inv_{idx}", use_container_width=True):
                        # Create a new InventoryItem
                        from core.database.models import InventoryItem
                        session = next(get_session())
                        new_item = InventoryItem(
                            name=item["description"], 
                            supplier_price=0.0, 
                            stock=0, 
                            initial_stock=0, 
                            user_id=user.id
                        )
                        session.add(new_item)
                        session.commit()
                        st.success(f"Item '{item['description']}' adicionado ao inventario!")
                        items_to_remove.append(idx)
            
            # Remove resolved items
            if items_to_remove:
                remaining = [item for i, item in enumerate(unmatched) if i not in items_to_remove]
                if remaining:
                    st.session_state["unmatched_products"] = remaining
                else:
                    del st.session_state["unmatched_products"]
                st.rerun()


    with tab3:
        st.header("📢 Central de Marketing")
        
        st.info("💡 **Dica**: Use a 'Fábrica de Produtos' para gerar palavras-chave de cauda longa para seus anúncios durante a criação do produto!")
        
        col_tool2, col_tool3 = st.columns([1, 1])
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

        with col_tool3:
            st.subheader("🎨 Gerador de Prompts (IA)")
            st.caption("Gere comandos para criar fotos ultra-realistas no Midjourney/DALL-E.")
            
            # Select product
            products_list = product_agent.get_all_products(user.id)
            if products_list:
                prod_names_mkt = {p.title: p for p in products_list}
                sel_p_title = st.selectbox("Escolha o Produto", ["-- Selecione --"] + list(prod_names_mkt.keys()), key="mkt_prod_select")
                
                if st.button("Gerar Prompts de Imagem ✨"):
                    if sel_p_title != "-- Selecione --":
                        selected_p = prod_names_mkt[sel_p_title]
                        with st.spinner("O Diretor de Arte está criando os prompts..."):
                            prompts = product_agent.generate_image_prompt(selected_p.title, selected_p.description)
                            st.write("---")
                            st.markdown(prompts)
                            st.info("💡 **Dica**: Copie o prompt em inglês e cole no Midjourney ou Leonardo.ai!")
                    else:
                        st.warning("Selecione um produto.")
            else:
                st.info("Cadastre produtos na 'Fábrica' para gerar prompts.")

    with tab4:
        st.header("🤝 Customer Hero (Atendimento)")
        
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
        
        # Carregar dados (Anúncios Shopee e Itens de Inventário Físico)
        products = product_agent.get_all_products(user.id)
        inventory_items = product_agent.get_all_inventory_items(user.id)
        
        # -- LÓGICA DE AGREGAÇÃO UNIFICADA --
        total_potes_vendidos = 0
        total_cogs_vendas = 0.0
        total_variantes_vendidas = 0
        total_receita_real = 0.0  # Receita real (valor recebido após taxas/cupons)
        product_groups = {}
        vendidos_por_item = {item.id: 0 for item in inventory_items} if inventory_items else {}

        # Carregar receitas (INCOME) vinculadas a produtos para calcular receita real
        from core.database.models import Transaction
        session_txn = next(get_session())
        income_transactions = session_txn.exec(
            select(Transaction).where(
                Transaction.user_id == user.id,
                Transaction.type == "INCOME"
            )
        ).all()
        
        # Mapa: product_id -> soma de receita real recebida
        receita_por_produto = {}
        for txn in income_transactions:
            if txn.product_id:
                receita_por_produto[txn.product_id] = receita_por_produto.get(txn.product_id, 0.0) + txn.amount

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

                # Receita real deste produto (do financeiro)
                ad_receita = receita_por_produto.get(p.id, 0.0)
                ad_lucro = ad_receita - ad_cogs
                ad_margem = (ad_lucro / ad_receita * 100) if ad_receita > 0 else 0.0

                if base_name not in product_groups:
                    product_groups[base_name] = {"units": 0, "cogs": 0.0, "receita": 0.0, "lucro": 0.0, "variations": []}
                
                product_groups[base_name]["units"] += ad_potes_sold
                product_groups[base_name]["cogs"] += ad_cogs
                product_groups[base_name]["receita"] += ad_receita
                product_groups[base_name]["lucro"] += ad_lucro
                product_groups[base_name]["variations"].append({
                    "id": p.id, "title": p.title, "pkgs": pkgs_sold, "stock": p.stock, 
                    "units": ad_potes_sold, "cogs": ad_cogs, "receita": ad_receita,
                    "lucro": ad_lucro, "margem": ad_margem, "preco_tabela": p.price
                })
                total_potes_vendidos += ad_potes_sold
                total_cogs_vendas += ad_cogs
                total_receita_real += ad_receita

        sub_tab_vendas, sub_tab_estoque = st.tabs(["📊 Desempenho de Vendas", "🏬 Estoque de Potes (Físico)"])

        with sub_tab_vendas:
            st.subheader("Performance Comercial")
            
            if products:
                # KPIs com margem de lucro
                total_lucro = total_receita_real - total_cogs_vendas
                total_margem = (total_lucro / total_receita_real * 100) if total_receita_real > 0 else 0.0
                
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Kits Vendidos", f"{total_variantes_vendidas}")
                c2.metric("Receita Real", f"R$ {total_receita_real:,.2f}", help="Valor efetivamente recebido (com cupons, taxas, etc)")
                c3.metric("Custo (COGS)", f"R$ {total_cogs_vendas:,.2f}", help="Custo do fornecedor")
                
                lucro_delta = f"{total_margem:.1f}% margem"
                c4.metric("Lucro Real", f"R$ {total_lucro:,.2f}", delta=lucro_delta, 
                         delta_color="normal" if total_lucro >= 0 else "inverse")
                
                st.divider()
                
                st.markdown("""
                <style>
                [data-testid="stExpander"] summary div[data-testid="stMarkdownContainer"] { width: 100% !important; }
                [data-testid="stExpander"] summary p { display: flex !important; justify-content: space-between !important; width: 100% !important; align-items: center !important; }
                </style>
                """, unsafe_allow_html=True)

                for base_name, data in product_groups.items():
                    grp_margem = (data['lucro'] / data['receita'] * 100) if data['receita'] > 0 else 0.0
                    margem_color = "green" if grp_margem >= 20 else ("orange" if grp_margem >= 10 else "red")
                    
                    if data['receita'] > 0:
                        label = f"📦 {base_name} **:green[Vendidos: {data['units']} un.] &nbsp;|&nbsp; Receita: R$ {data['receita']:,.2f} &nbsp;|&nbsp; :{margem_color}[Margem: {grp_margem:.1f}%]**"
                    else:
                        label = f"📦 {base_name} **:green[Vendidos: {data['units']} un.] &nbsp;|&nbsp; :red[Custo: R$ {data['cogs']:,.2f}]**"
                    
                    with st.expander(label):
                        for v in data["variations"]:
                            m = re.search(r'- (\d+)x$', v['title'])
                            n = m.group(1) if m else "1"
                            txt = f"{n} Frasco" if n == "1" else f"{n} Frascos"
                            
                            # Calcular variação de preço: tabela vs real
                            preco_tabela = v.get('preco_tabela', 0)
                            receita_v = v.get('receita', 0)
                            pkgs_v = v.get('pkgs', 0)
                            preco_medio_real = (receita_v / pkgs_v) if pkgs_v > 0 else 0
                            desconto_pct = ((preco_tabela - preco_medio_real) / preco_tabela * 100) if preco_tabela > 0 and preco_medio_real > 0 else 0
                            
                            margem_v = v.get('margem', 0)
                            margem_v_color = '#4CAF50' if margem_v >= 20 else ('#FF9800' if margem_v >= 10 else '#F44336')
                            
                            # Linha de info com receita real e margem
                            receita_info = ""
                            if receita_v > 0:
                                receita_info = f"""&nbsp;|&nbsp; Receita: <b>R$ {receita_v:,.2f}</b>
                                    &nbsp;|&nbsp; <span style='color: {margem_v_color};'>Margem: {margem_v:.1f}%</span>"""
                                if desconto_pct > 0:
                                    receita_info += f""" &nbsp;|&nbsp; <span style='color: #9E9E9E;'>Desc: -{desconto_pct:.0f}%</span>"""
                            
                            st.markdown(f"""
                                <div style='display: flex; justify-content: space-between; border-bottom: 1px solid #ffffff1e; padding: 5px 0; flex-wrap: wrap;'>
                                    <span>Variação: <b>{txt}</b></span>
                                    <span>
                                        <span style='color: #4CAF50;'>{v['pkgs']} kits</span> &nbsp;|&nbsp; Stock: {v['stock']} &nbsp;|&nbsp; <span style='color: #F44336;'>Custo: R$ {v['cogs']:,.2f}</span>
                                        {receita_info}
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
                    "Estoque Atual": item.stock,
                    "Estoque Mínimo": item.min_stock,
                    "Custo": item.supplier_price,
                    "Potes Vendidos": vendidos_por_item.get(item.id, 0)
                } for item in inventory_items])

                st.info("💡 O estoque é controlado automaticamente pelo 'E. Shopee' nos SKUs Virtuais abaixo.")

 
                
                edited_inv = st.data_editor(
                    df_inv,
                    column_config={
                        "ID": None,
                        "Custo": st.column_config.NumberColumn(format="R$ %.2f"),
                        "Estoque Atual": st.column_config.NumberColumn(disabled=True),
                        "Potes Vendidos": st.column_config.NumberColumn(disabled=True)
                    },
                    hide_index=True, use_container_width=True, key="inv_ed"
                )

                if st.button("Salvar Alterações de Estoque"):
                    for _, row in edited_inv.iterrows():
                        product_agent.update_inventory_item(int(row["ID"]), {
                            "name": row["Nome"], 
                            "supplier_price": float(row["Custo"]),
                            "min_stock": int(row["Estoque Mínimo"])
                        })
                    st.success("Estoque e custos atualizados!")
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

        # --- NEW: BUNDLE / KIT COMPOSITION UI ---
        st.divider()
        with st.expander("🛠️ Configurar Composição de Kits (Vincular Itens Físicos)"):
            st.caption("Associe anúncios da Shopee (SKUs Virtuais) aos produtos que você tem na prateleira.")
            
            # 1. Select Product
            if products:
                prod_names = {p.title: p.id for p in products}
                selected_p_title = st.selectbox("Selecione o Anúncio (SKU Virtual)", ["-- Escolha um --"] + list(prod_names.keys()), key="bundle_prod_select")
                
                if selected_p_title != "-- Escolha um --":
                    p_id = prod_names[selected_p_title]
                    
                    # 2. Show Current Components
                    components = st.session_state.product_agent.get_product_components(p_id)
                    inventory_items_list = st.session_state.product_agent.get_all_inventory_items(user.id)
                    inv_map = {item.id: item.name for item in inventory_items_list}
                    
                    if components:
                        st.write("**Componentes Atuais:**")
                        for comp in components:
                            c_col1, c_col2, c_col3 = st.columns([3, 1, 1])
                            item_name = inv_map.get(comp.inventory_item_id, "Item Desconhecido")
                            c_col1.write(f"🔹 {comp.quantity}x {item_name}")
                            if c_col3.button("Remover", key=f"del_comp_{comp.id}"):
                                res = st.session_state.product_agent.delete_product_component(comp.id)
                                if res["success"]:
                                    st.toast("Componente removido!")
                                    st.rerun()
                    else:
                        st.info("Este anúncio ainda não possui itens físicos vinculados.")
                    
                    st.divider()
                    # 3. Add New Component
                    st.write("**Adicionar Item ao Kit:**")
                    if inventory_items_list:
                        inv_names = {item.name: item.id for item in inventory_items_list}
                        sel_inv_name = st.selectbox("Item Físico", ["-- Selecione --"] + list(inv_names.keys()), key="sel_inv_comp")
                        comp_qty = st.number_input("Quantidade no Kit", min_value=1, value=1, step=1, key="comp_qty_input")
                        
                        if st.button("Vincular ao Anúncio", type="primary"):
                            if sel_inv_name != "-- Selecione --":
                                inv_id = inv_names[sel_inv_name]
                                add_res = st.session_state.product_agent.add_product_component(p_id, inv_id, comp_qty)
                                if add_res["success"]:
                                    st.success("Vinculado com sucesso!")
                                    st.rerun()
                                else:
                                    st.error(f"Erro: {add_res['message']}")
                            else:
                                st.warning("Selecione um item físico.")
                    else:
                        st.warning("Você ainda não tem itens no Inventário Físico. Cadastre-os acima.")
            else:
                st.info("Nenhum anúncio cadastrado para configurar.")

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
