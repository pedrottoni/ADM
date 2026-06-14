"""
:material/payments: Financeiro — Tab de Financeiro
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from core.config import Config
from core.database.engine import get_session


def render(user, agents):
    """Render the tab content."""
    finance_agent = agents["finance_agent"]
    product_agent = agents["product_agent"]
    ads_agent = agents["ads_agent"]
    customer_agent = agents["customer_agent"]

    # Carregar Estatísticas e Produtos
    analysis = finance_agent.analyze_health(user.id)
    stats = analysis["stats"]
    all_transactions = [{"ID": t.id, "Data": t.date, "Desc": t.description, "Valor": t.amount, "Tipo": t.type, "Categoria": t.category} for t in stats["raw_data"]]
    df_all = pd.DataFrame(all_transactions)

    # Carregar produtos para os dropdowns e calcular COGS
    from agents.product_agent import ProductAgent
    if 'pa_fin' not in st.session_state: st.session_state.pa_fin = ProductAgent()
    products_list = st.session_state.pa_fin.get_all_products(user.id)

    # Calcular COGS (Custo dos Produtos Vendidos) a partir das transações de venda
    from core.database.models import Transaction, Product, InventoryItem, ProductComponent
    from sqlmodel import select
    from dashboard.components.metric_card import metric_card
    session_cogs = next(get_session())
    income_txns = session_cogs.exec(
        select(Transaction).where(
            Transaction.user_id == user.id,
            Transaction.type == "INCOME"
        )
    ).all()

    total_cogs = 0.0
    for txn in income_txns:
        if txn.product_id and txn.quantity:
            product = session_cogs.get(Product, txn.product_id)
            if product:
                if hasattr(product, 'components') and product.components:
                    # Produto é um kit - calcular custo baseado nos componentes físicos
                    for comp in product.components:
                        inv_item = session_cogs.get(InventoryItem, comp.inventory_item_id)
                        if inv_item:
                            unidades = txn.quantity * (comp.quantity or 1)
                            total_cogs += unidades * (inv_item.supplier_price or 0.0)
                else:
                    # Produto simples - usar supplier_price do próprio produto
                    total_cogs += txn.quantity * (product.supplier_price or 0.0)

    # Recalcular lucro real com COGS
    fat_bruto = stats['total_revenue']
    saidas = stats['total_expenses']
    lucro_real = fat_bruto - saidas - total_cogs
    margem_real = (lucro_real / fat_bruto * 100) if fat_bruto > 0 else 0

    sub_tab_dash, sub_tab_venda, sub_tab_gasto, sub_tab_upload = st.tabs([
        ":material/analytics: Resumo Geral", ":material/payments: Registrar Venda", ":material/receipt_long: Despesas", ":material/folder_open: Importar Dados"
    ])

    with sub_tab_dash:
    # ── KPIs Principais (fora do card) ──
        k1, k2, k3, k4 = st.columns(4)
        with k1: metric_card("Fat. Bruto", f"R$ {fat_bruto:,.2f}")
        with k2: metric_card("Saídas (Custos/Ads)", f"R$ {saidas:,.2f}")
        with k3: metric_card("COGS", f"R$ {total_cogs:,.2f}")
        with k4: metric_card("Lucro Real", f"R$ {lucro_real:,.2f}",
                            delta=f"{margem_real:.1f}%")
        if not df_all.empty:
            df_tmp = df_all.copy()
            df_tmp['Date'] = pd.to_datetime(df_tmp['Data'])
            # ── Period type (lido do session_state, definido pelo radio dentro do card) ──
            period_type = st.session_state.get('finance_period_type', 'Anual')
            # ── Period grouping ──
            if period_type == "Personalizado":
                # (legacy branch — kept for safety, but option no longer in radio)
                p_start = st.session_state.get('fin_start', pd.Timestamp.now().date())
                p_end = st.session_state.get('fin_end', pd.Timestamp.now().date())
                mask = (df_tmp['Date'] >= pd.Timestamp(p_start)) & (df_tmp['Date'] <= pd.Timestamp(p_end))
                df_tmp = df_tmp[mask]
                period_group = df_tmp['Date'].dt.strftime('%d-%m-%Y')
            elif period_type == "Anual":
                period_group = df_tmp['Date'].dt.strftime('%Y')
            elif period_type == "Semanal":
                period_group = df_tmp['Date'].dt.strftime('%Y-W%V')
            elif period_type == "Diário":
                period_group = df_tmp['Date'].dt.strftime('%d-%m-%Y')
            else:
                period_group = df_tmp['Date'].dt.strftime('%Y-%m')
            if not df_tmp.empty:
                df_tmp['Período'] = period_group
                chart_data = df_tmp.groupby(['Período', 'Tipo'])['Valor'].sum().reset_index()
                income_total = chart_data[chart_data['Tipo'] == 'INCOME']['Valor'].sum()
                expense_total = chart_data[chart_data['Tipo'] == 'EXPENSE']['Valor'].sum()
                net_total = income_total - expense_total
                net_margem = (net_total / income_total * 100) if income_total > 0 else 0
                # ================================================================
                # BIG CARD — Evolução Financeira (wraps everything)
                # ================================================================
                big_card = st.columns(1)[0]
                with big_card:
                    st.markdown(
                        '<div class="evolution-card-marker" style="display:none"></div>',
                        unsafe_allow_html=True,
                    )
                    # ── Main content: Evolução (growing vertically = Lucro + Cat somados) | Direita empilhada ──
                    col_evol, col_side = st.columns([2, 1], gap="medium")
                    # ── Sub-bloco 1: Evolução Financeira (header + legenda + radio + gráfico) ──
                    with col_evol:
                        # O sub_evol é um st.container() que cria um wrapper DOM persistente.
                        # Tudo que vier dentro do `with sub_evol:` vira filho real desse container.
                        # O CSS .sub-block-evolution estiliza esse .stContainer via :has() / .st-emotion-cache
                        sub_evol = st.container()
                        with sub_evol:
                            st.markdown(f"""
                            <div class="chart-card-header">
                                <div class="chart-card-header-left">
                                    <span class="chart-card-title"><span class="material-symbols-rounded">trending_up</span> Evolução Financeira</span>
                                    <div class="chart-card-value-row">
                                        <span class="chart-card-value" style="font-size:1.5rem">R$ {income_total:,.2f}</span>
                                        <span class="chart-card-delta">▲ {net_margem:.1f}%</span>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            st.markdown(
                                '<div class="scrollable-chart-marker" style="display:none"></div>',
                                unsafe_allow_html=True,
                            )
                            # ── Sub-header: Legend + Period filter (dentro do sub-bloco) ──
                            leg_col, per_col = st.columns([1.2, 1], gap="small", vertical_alignment="center")
                            with leg_col:
                                st.markdown(f"""
                                <div class="chart-card-legend" style="margin:0">
                                    <span class="chart-card-legend-item">
                                        <span class="chart-card-legend-dot" style="background:#818CF8"></span> Receitas
                                    </span>
                                    <span class="chart-card-legend-item">
                                        <span class="chart-card-legend-dot" style="background:#F87171"></span> Despesas
                                    </span>
                                </div>
                                """, unsafe_allow_html=True)
                            with per_col:
                                period_type = st.radio(
                                    "Agrupar por",
                                    options=["Anual", "Mensal", "Semanal", "Diário"],
                                    horizontal=True,
                                    index=0,
                                    key="finance_period_type",
                                    label_visibility="collapsed",
                                )
                            # ── Gráfico de barras ──
                            chart_display = chart_data.copy()
                            chart_display['Tipo'] = chart_display['Tipo'].replace({'EXPENSE': 'Despesas', 'INCOME': 'Receitas'})

                            n_periods = len(chart_display['Período'].unique())

                            fig = px.bar(chart_display, x='Período', y='Valor', color='Tipo',
                                         color_discrete_map={"Despesas": "#F87171", "Receitas": "#818CF8"},
                                         barmode='relative', height=480)
                            fig.update_layout(
                                margin=dict(l=0, r=0, t=0, b=0),
                                showlegend=False,
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)',
                                font=dict(color='#94A3B8', size=11),
                                hovermode='x unified',
                                autosize=True,
                            )
                            fig.update_xaxes(type='category', tickangle=0, gridcolor='#334155',
                                             title_text='', showticklabels=True,
                                             rangeslider=dict(visible=True, thickness=0.035))
                            fig.update_yaxes(gridcolor='#334155', title_text='', showticklabels=True)
                            event = st.plotly_chart(fig, on_select="rerun", use_container_width=True)
                    # ── Right: Side Cards ──
                    with col_side:
                        # ── Sub-bloco 2: Lucro Líquido ──
                        # st.container() cria um wrapper DOM persistente que engloba
                        # todos os elementos dentro do `with`. SEM key para evitar
                        # bug do Streamlit onde plotly_chart "escapa" do container com key.
                        sub_lucro = st.container()
                        with sub_lucro:
                            income_by_period = chart_data[chart_data['Tipo'] == 'INCOME'][['Período', 'Valor']].rename(columns={'Valor': 'Income'})
                            expense_by_period = chart_data[chart_data['Tipo'] == 'EXPENSE'][['Período', 'Valor']].rename(columns={'Valor': 'Expense'})
                            net_df = income_by_period.merge(expense_by_period, on='Período', how='outer').fillna(0)
                            net_df['Lucro'] = net_df['Income'] - net_df['Expense']
                            net_df['Período'] = pd.Categorical(net_df['Período'], categories=net_df['Período'].unique(), ordered=True)
                            net_df = net_df.sort_values('Período').reset_index(drop=True)
                            total_net = net_df['Lucro'].sum()
                            net_pos = total_net >= 0
                            net_pct = abs(total_net / income_total * 100) if income_total > 0 else 0
                            st.markdown(f"""
                            <div class="chart-card-header">
                                <div class="chart-card-header-left">
                                    <div style="display:flex;justify-content:space-between;align-items:flex-start;width:100%">
                                        <div>
                                            <div class="chart-card-title"><span class="material-symbols-rounded">bar_chart</span> Lucro Líquido</div>
                                            <div class="chart-card-value-row">
                                                <span class="chart-card-value" style="font-size:1.25rem">R$ {total_net:,.2f}</span>
                                                <span class="chart-card-delta" style="background:{'#166534' if net_pos else '#7f1d1d'};color:{'#86efac' if net_pos else '#fca5a5'}">
                                                    {'▲' if net_pos else '▼'} {net_pct:.1f}%
                                                </span>
                                            </div>
                                        </div>
                                        <span style="color:#94A3B8;font-size:0.75rem">por período</span>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            fig_net = px.bar(net_df, x='Período', y='Lucro',
                                             color_discrete_sequence=['#818CF8'], height=180)
                            fig_net.update_layout(
                                margin=dict(l=0, r=0, t=0, b=0),
                                showlegend=False,
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)',
                                font=dict(color='#94A3B8', size=9),
                                autosize=True,
                            )
                            fig_net.update_xaxes(tickangle=0, gridcolor='#334155', showticklabels=False,
                                                 title_text='')
                            fig_net.update_yaxes(gridcolor='#334155', showticklabels=True, title_text='')
                            st.plotly_chart(fig_net, use_container_width=True)
                        # ── Sub-bloco 3: Despesas por Categoria ──
                        sub_cat = st.container()
                        with sub_cat:
                            expense_df = df_tmp[df_tmp['Tipo'] == 'EXPENSE']
                            if not expense_df.empty:
                                cat_expense = expense_df.groupby('Categoria')['Valor'].sum().reset_index().sort_values('Valor', ascending=False)
                                total_exp = cat_expense['Valor'].sum()
                                st.markdown(f"""
                                <div class="chart-card-header">
                                    <div class="chart-card-header-left">
                                        <div style="display:flex;justify-content:space-between;align-items:flex-start;width:100%">
                                            <div>
                                                <div class="chart-card-title"><span class="material-symbols-rounded">receipt_long</span> Despesas por Categoria</div>
                                                <div class="chart-card-value-row">
                                                    <span class="chart-card-value" style="font-size:1.25rem">R$ {total_exp:,.2f}</span>
                                                </div>
                                            </div>
                                            <span style="color:#94A3B8;font-size:0.75rem">{len(cat_expense)} categorias</span>
                                        </div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                                fig_cat = px.pie(
                                    cat_expense, names='Categoria', values='Valor',
                                    color_discrete_sequence=px.colors.qualitative.Set3,
                                    hole=0.55, height=200,
                                )
                                fig_cat.update_layout(
                                    margin=dict(l=0, r=0, t=0, b=0),
                                    paper_bgcolor='rgba(0,0,0,0)',
                                    font=dict(color='#94A3B8', size=9),
                                    showlegend=True,
                                    legend=dict(orientation='v', yanchor='middle', y=0.5,
                                                xanchor='left', x=1.02,
                                                font=dict(size=10), bgcolor='rgba(0,0,0,0)'),
                                    autosize=True,
                                )
                                st.plotly_chart(fig_cat, use_container_width=True)
                            else:
                                st.markdown('<p style="color:#94A3B8;text-align:center;padding:1.5rem 0">Nenhuma despesa registrada</p>', unsafe_allow_html=True)
                    # ── Period Selector was moved into the header (head_per column above) ──
                    # ── Detail on click ──
                    sel_points = None
                    if event is not None:
                        raw_sel = event.get("selection", {}) if isinstance(event, dict) else getattr(event, "selection", None) or {}
                        sel_points = raw_sel.get("points", []) if isinstance(raw_sel, dict) else getattr(raw_sel, "points", [])
                    if sel_points:
                        periodo_clicado = sel_points[0].get("x") if isinstance(sel_points[0], dict) else getattr(sel_points[0], "x", None)
                        detail = df_tmp[df_tmp['Período'] == periodo_clicado]
                        if not detail.empty:
                            st.markdown("---")
                            st.markdown(f'<span class="chart-card-title"><span class="material-symbols-rounded">content_paste</span> Detalhamento: {periodo_clicado}</span>', unsafe_allow_html=True)
                            det_fat = detail[detail['Tipo'] == 'INCOME']['Valor'].sum()
                            det_sai = detail[detail['Tipo'] == 'EXPENSE']['Valor'].sum()
                            det_income_ids = set(detail[detail['Tipo'] == 'INCOME']['ID'].tolist())
                            det_cogs = 0.0
                            for txn in income_txns:
                                if txn.id in det_income_ids and txn.product_id and txn.quantity:
                                    product = session_cogs.get(Product, txn.product_id)
                                    if product:
                                        if hasattr(product, 'components') and product.components:
                                            for comp in product.components:
                                                inv_item = session_cogs.get(InventoryItem, comp.inventory_item_id)
                                                if inv_item:
                                                    det_cogs += txn.quantity * (comp.quantity or 1) * (inv_item.supplier_price or 0.0)
                                        else:
                                            det_cogs += txn.quantity * (product.supplier_price or 0.0)
                            det_lucro = det_fat - det_sai - det_cogs
                            det_margem = (det_lucro / det_fat * 100) if det_fat > 0 else 0
                            kd1, kd2, kd3, kd4 = st.columns(4)
                            with kd1: metric_card("Fat. Bruto", f"R$ {det_fat:,.2f}")
                            with kd2: metric_card("Saídas", f"R$ {det_sai:,.2f}")
                            with kd3: metric_card("COGS", f"R$ {det_cogs:,.2f}")
                            with kd4: metric_card("Lucro Real", f"R$ {det_lucro:,.2f}",
                                                  delta=f"{det_margem:.1f}%")
                            income_detail = detail[detail['Tipo'] == 'INCOME']
                            if not income_detail.empty:
                                with st.expander(":material/inventory_2: Produtos Vendidos", expanded=True):
                                    period_start = income_detail['Date'].min().to_pydatetime()
                                    period_end = income_detail['Date'].max().to_pydatetime()
                                    col_tv, col_tp = st.columns(2)
                                    with col_tv:
                                        st.markdown("**:material/emoji_events: Top Vendas**")
                                        top_prods = finance_agent.get_top_products(
                                            user.id, limit=10,
                                            start_date=period_start, end_date=period_end
                                        )
                                        if top_prods:
                                            for i, p in enumerate(top_prods, 1):
                                                title = p['product_title'][:35] + "..." if len(p['product_title']) > 35 else p['product_title']
                                                st.markdown(f"**{i}.** {title} — *R$ {p['total_revenue']:,.2f}*")
                                        else:
                                            st.info("Nenhuma venda no período.")
                                    with col_tp:
                                        st.markdown("**:material/emoji_events: Top Produtos**")
                                        top_potes = finance_agent.get_top_products_by_potes(
                                            user.id, limit=10,
                                            start_date=period_start, end_date=period_end
                                        )
                                        if top_potes:
                                            for i, p in enumerate(top_potes, 1):
                                                title = p['product_title'][:35] + "..." if len(p['product_title']) > 35 else p['product_title']
                                                st.markdown(f"**{i}.** {title} — **:green[Vendidos: {p['total_potes']} un.]**")
                                        else:
                                            st.info("Nenhum produto no período.")
                            with st.expander(":material/description: Todas as Transações", expanded=False):
                                st.dataframe(
                                    detail[['Data', 'Desc', 'Valor', 'Tipo', 'Categoria']].sort_values('Data'),
                                    hide_index=True, use_container_width=True
                                )
        else:
            st.info("Nenhuma transação financeira encontrada.")
        with st.expander(":material/edit_note: Gerenciar Histórico de Transações"):
            all_transactions_with_id = [{"ID": t.id, "Data": t.date, "Desc": t.description, "Valor": t.amount, "Tipo": t.type, "Categoria": t.category} for t in stats["raw_data"]]
            df_edit = pd.DataFrame(all_transactions_with_id).sort_values(by="Data", ascending=False)
            edited_df = st.data_editor(
                df_edit,
                column_config={
                    "ID": st.column_config.NumberColumn(disabled=True),
                    "Data": st.column_config.DateColumn("Data"),
                    "Valor": st.column_config.NumberColumn("Valor", format="R$ %.2f"),
                    "Tipo": st.column_config.SelectboxColumn("Tipo", options=["INCOME", "EXPENSE"]),
                    "Categoria": st.column_config.SelectboxColumn("Categoria", options=["Sale", "Ads", "Custo Produto", "Assinatura", "Outros"]),
                },
                hide_index=True, num_rows="dynamic", key="transaction_editor", use_container_width=True
            )
            if st.button("Salvar Alterações", type="primary"):
                original_ids = set(df_edit["ID"])
                edited_ids = set(edited_df["ID"].dropna())
                for txn_id in (original_ids - edited_ids): finance_agent.delete_transaction(int(txn_id))
                for index, row in edited_df.iterrows():
                    txn_id = row.get("ID")
                    if pd.notna(txn_id):
                        original_row = df_edit[df_edit["ID"] == txn_id].iloc[0]
                        updates = {}
                        if row["Desc"] != original_row["Desc"]: updates["description"] = row["Desc"]
                        if row["Valor"] != original_row["Valor"]: updates["amount"] = float(row["Valor"])
                        if row["Tipo"] != original_row["Tipo"]: updates["type"] = row["Tipo"]
                        if row["Categoria"] != original_row["Categoria"]: updates["category"] = row["Categoria"]
                        if pd.to_datetime(row["Data"]) != pd.to_datetime(original_row["Data"]): updates["date"] = pd.to_datetime(row["Data"])
                        if updates: finance_agent.update_transaction(int(txn_id), updates)
                st.success("Financeiro atualizado com sucesso!"); st.rerun()
        st.divider()
        if st.button("Gerar Insights de Negócio (IA)", icon=":material/auto_awesome:", use_container_width=True):
            context_insights = {
                "fat_bruto": fat_bruto,
                "saidas": saidas,
                "cogs": total_cogs,
                "lucro_real": lucro_real,
                "margem_real": margem_real
            }
            with st.spinner("Analisando padrões financeiros..."):
                report = finance_agent.generate_deep_analysis(user.id, context_insights)
                st.markdown(report)
            with st.expander(":material/warning: Zona de Perigo"):
                st.warning("Estas ações NÃO podem ser desfeitas.")
                col_z1, col_z2 = st.columns(2)
                with col_z1:
                    with st.popover(":material/delete: Zerar Vendas/Histórico", use_container_width=True):
                        st.error("Tem certeza? Todo o histórico financeiro será perdido.")
                        if st.button("Sim, zerar tudo", type="primary", key="confirm_clear_tx"):
                            res = finance_agent.clear_all_transactions(user.id)
                            if res["success"]: st.toast(res["message"]); st.rerun()
                with col_z2:
                    with st.popover(":material/refresh: Resetar Estoque (600 un.)", use_container_width=True):
                        st.error("Tem certeza? Todo o estoque será resetado para 600 unidades.")
                        if st.button("Sim, resetar", type="primary", key="confirm_reset_stock"):
                            res = finance_agent.reset_inventory(user.id)
                            if res["success"]: st.toast(res["message"]); st.rerun()
    with sub_tab_venda:
        st.markdown("#### :material/payments: Registrar Venda Manual")
        st.info("Utilize este formulário para registrar vendas que não foram importadas automaticamente. O estoque será abatido proporcionalmente.")
        # Produtos disponíveis
        if products_list:
            product_names = [p.title for p in products_list]
            product_map = {p.title: p for p in products_list}
            with st.form("income_form_new"):
                v_p_choice = st.selectbox("Selecione o Anúncio", product_names)
                v_p_obj = product_map[v_p_choice]
                st.caption(f"Valor de Tabela: R$ {v_p_obj.price:.2f}")
                vc1, vc2 = st.columns(2)
                v_val = vc1.number_input(
                    "Valor Total Recebido (R$)",
                    min_value=0.0,
                    value=0.0,
                    step=0.01,
                    format="%.2f",
                    help="Valor total recebido por todas as unidades vendidas."
                )
                v_qty = vc2.number_input("Quantidade Vendida", min_value=1, step=1, value=1)
                v_date = st.date_input("Data da Venda")
                if st.form_submit_button("Confirmar Venda e Abater Estoque", type="primary"):
                    res = finance_agent.add_transaction(
                        date=v_date, description=v_p_choice, amount=v_val,
                        category="Sale", type="INCOME", user_id=user.id,
                        product_id=v_p_obj.id, quantity=v_qty
                    )
                    if res["success"]:
                        st.success(f"Venda de {v_qty}x '{v_p_choice}' registrada! Estoque abatido.")
                        st.rerun()
                    else: st.error(res["message"])
        else:
            st.warning("Nenhum anúncio encontrado. Cadastre seus anúncios na aba 'Gestão de Anúncios'.")
    with sub_tab_gasto:
        st.markdown("#### :material/receipt_long: Registro de Despesas")
        with st.form("expense_form_new"):
            d_date = st.date_input("Data da Despesa")
            d_desc = st.text_input("Descrição", placeholder="Ex: Google Ads, Aluguel, Embalagens")
            dc1, dc2 = st.columns(2)
            d_val = dc1.number_input("Valor (R$)", min_value=0.01, step=10.0)
            d_cat = dc2.selectbox("Categoria", ["Ads", "Custo Produto", "Assinatura", "Outros"])
            if st.form_submit_button("Salvar Despesa", type="primary"):
                res = finance_agent.add_transaction(
                    date=d_date, description=d_desc, amount=d_val,
                    category=d_cat, type="EXPENSE", user_id=user.id
                )
                if res["success"]:
                    st.success("Gasto registrado com sucesso!"); st.rerun()
                else: st.error(res["message"])
    with sub_tab_upload:
        st.markdown("#### :material/folder_open: Importar Planilha de Vendas")
        st.markdown("Suba o arquivo XML/XLSX da Shopee ou um CSV próprio. Nossa IA irá processar os dados e vincular aos anúncios.")
        uploaded_file = st.file_uploader("Arraste o arquivo aqui", type=["csv", "xlsx"], key="income_upload_new")
        if uploaded_file and "upload_preview" not in st.session_state:
            if st.button("Processar com IA", type="primary"):
                with st.spinner("Interpretando dados da planilha..."):
                    result = finance_agent.process_upload(uploaded_file, user.id)
                    if result["success"]:
                        st.session_state["upload_preview"] = result["data"]
                        st.rerun()
                    else: st.error(result["message"])
        if "upload_preview" in st.session_state:
            st.info("Revise as transações identificadas pela IA antes de salvar.")
            df_preview = pd.DataFrame(st.session_state["upload_preview"])
            edited_preview = st.data_editor(df_preview, use_container_width=True, hide_index=True)
            cp1, cp2 = st.columns(2)
            if cp1.button("Confirmar Tudo e Abater Estoques", type="primary", use_container_width=True):
                confirmed_data = edited_preview.to_dict(orient="records")
                confirm_result = finance_agent.confirm_upload(confirmed_data, user.id)
                if confirm_result["success"]:
                    st.success(f"Sucesso! {confirm_result['matched_count']} vendas vinculadas e processadas."); del st.session_state["upload_preview"]
                    if confirm_result["unmatched"]: st.session_state["unmatched_products"] = confirm_result["unmatched"]
                    st.rerun()
            if cp2.button("Descartar", use_container_width=True):
                del st.session_state["upload_preview"]; st.rerun()
    # Resolução de Itens não Encontrados (Persistent ao final da aba Financeiro)
    if "unmatched_products" in st.session_state and st.session_state["unmatched_products"]:
        st.divider()
        st.markdown("#### :material/warning: Vendas não Vinculadas")
        st.caption("Os itens abaixo foram registrados no financeiro, mas não encontramos anúncios correspondentes para abater o estoque.")
        unmatched = st.session_state["unmatched_products"]
        for idx, item in enumerate(unmatched):
            with st.container(border=True):
                col_u1, col_u2 = st.columns([3, 1])
                col_u1.write(f"**{item['description']}** | R$ {item['amount']:.2f} (Qtd: {item.get('quantity', 1)})")
                if col_u2.button("Ignorar", key=f"ign_{idx}", use_container_width=True):
                    st.session_state["unmatched_products"].pop(idx); st.rerun()
        if not st.session_state["unmatched_products"]:
            del st.session_state["unmatched_products"]
            st.rerun()
