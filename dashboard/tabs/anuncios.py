"""
:material/inventory_2: Meus Anúncios — Tab de Anuncios
"""

import streamlit as st
import pandas as pd
import re
from core.config import Config
from core.database.engine import get_session
from dashboard.components.metric_card import metric_card


def render(user, agents):
    """Render the tab content."""
    finance_agent = agents["finance_agent"]
    product_agent = agents["product_agent"]
    ads_agent = agents["ads_agent"]
    customer_agent = agents["customer_agent"]

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
    from sqlmodel import select
    session_txn = next(get_session())
    income_transactions = session_txn.exec(
        select(Transaction).where(
            Transaction.user_id == user.id,
            Transaction.type == "INCOME"
        )
    ).all()

    # Mapa: product_id -> soma de receita e soma de quantidade vendida
    receita_por_produto = {}
    vendas_por_produto = {}
    for txn in income_transactions:
        if txn.product_id:
            receita_por_produto[txn.product_id] = receita_por_produto.get(txn.product_id, 0.0) + txn.amount
            vendas_por_produto[txn.product_id] = vendas_por_produto.get(txn.product_id, 0) + (txn.quantity or 1)


    if products:
        for p in products:
            base_name = re.sub(r' - \d+x$', '', p.title.strip()).strip()

            # Quantidade vendida agora vem das transações
            pkgs_sold = vendas_por_produto.get(p.id, 0)

            total_variantes_vendidas += pkgs_sold
            ad_potes_sold = 0
            ad_cogs = 0.0
            ad_stock_kits = 0
            unit_cogs = 0.0

            if hasattr(p, 'components') and p.components:
                # O estoque do kit é limitado pelo item físico com menor disponibilidade proporcional
                kit_capacity = []
                for comp in p.components:
                    inv_item = next((i for i in inventory_items if i.id == comp.inventory_item_id), None)
                    if inv_item:
                        qty_per_kit = comp.quantity or 1
                        item_units_sold = pkgs_sold * qty_per_kit
                        item_cogs = item_units_sold * (inv_item.supplier_price or 0.0)

                        ad_potes_sold += item_units_sold
                        ad_cogs += item_cogs
                        unit_cogs += qty_per_kit * (inv_item.supplier_price or 0.0)

                        # Calcular capacidade baseada no estoque físico atual
                        kit_capacity.append(inv_item.stock // qty_per_kit)

                        if comp.inventory_item_id in vendidos_por_item:
                            vendidos_por_item[comp.inventory_item_id] += item_units_sold

                ad_stock_kits = min(kit_capacity) if kit_capacity else 0
            else:
                # Fallback caso não tenha componentes mapeados
                ad_potes_sold = pkgs_sold
                ad_cogs = pkgs_sold * (p.supplier_price or 0.0)
                unit_cogs = p.supplier_price or 0.0
                ad_stock_kits = p.stock

            # Receita real deste produto (do financeiro)
            ad_receita = receita_por_produto.get(p.id, 0.0)
            ad_lucro = ad_receita - ad_cogs
            ad_margem = (ad_lucro / ad_receita * 100) if ad_receita > 0 else 0.0

            # Margem Estimada baseada no preço de tabela e custo unitário
            potential_profit = (p.price or 0.0) - unit_cogs
            potential_margin = (potential_profit / p.price * 100) if p.price and p.price > 0 else 0.0


            if base_name not in product_groups:
                product_groups[base_name] = {"units": 0, "cogs": 0.0, "receita": 0.0, "lucro": 0.0, "variations": []}

            product_groups[base_name]["units"] += ad_potes_sold
            product_groups[base_name]["cogs"] += ad_cogs
            product_groups[base_name]["receita"] += ad_receita
            product_groups[base_name]["lucro"] += ad_lucro
            product_groups[base_name]["variations"].append({
                "id": p.id, "title": p.title, "pkgs": pkgs_sold, "stock": ad_stock_kits, 
                "units": ad_potes_sold, "cogs": ad_cogs, "receita": ad_receita,
                "lucro": ad_lucro, "margem": ad_margem, "preco_tabela": p.price,
                "unit_cogs": unit_cogs, "potential_margin": potential_margin
            })

            total_potes_vendidos += ad_potes_sold
            total_cogs_vendas += ad_cogs
            total_receita_real += ad_receita

    sub_tab_vendas, sub_tab_estoque, sub_tab_calc = st.tabs([":material/analytics: Desempenho de Vendas", ":material/store: Estoque de Potes", ":material/calculate: Calculadora de Preços"])

    with sub_tab_vendas:
        st.subheader("Performance Comercial")

        if products:
            # KPIs com métricas avançadas
            total_lucro = total_receita_real - total_cogs_vendas
            total_margem = (total_lucro / total_receita_real * 100) if total_receita_real > 0 else 0.0
            ticket_medio = (total_receita_real / total_variantes_vendidas) if total_variantes_vendidas > 0 else 0.0
            roi = ((total_lucro / total_cogs_vendas) * 100) if total_cogs_vendas > 0 else 0.0
            valor_por_kit = (total_receita_real / total_variantes_vendidas) if total_variantes_vendidas > 0 else 0.0

            c1, c2, c3, c4, c5 = st.columns(5)
            with c1: metric_card("Kits Vendidos", f"{total_variantes_vendidas}")
            with c2: metric_card("Custo (COGS)", f"R$ {total_cogs_vendas:,.2f}")
            with c3: metric_card("Ticket Médio", f"R$ {ticket_medio:,.2f}")
            with c4: metric_card("Margem %", f"{total_margem:.1f}%",
                     delta=":material/check_circle:" if total_margem >= 20 else (":material/warning_amber:" if total_margem >= 10 else ":material/cancel:"))
            with c5: metric_card("ROI", f"{roi:.0f}%")

            # Métricas secundárias
            m1, m2 = st.columns(2)
            with m1: metric_card("Valor por Kit", f"R$ {valor_por_kit:,.2f}")

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
                    label = f":material/inventory_2: {base_name} **:green[Vendidos: {data['units']} un.]** &nbsp;|&nbsp; Receita: **R$ {data['receita']:,.2f}** &nbsp;|&nbsp; **:green[Margem: {grp_margem:.1f}%]**"
                else:
                    label = f":material/inventory_2: {base_name} **:green[Vendidos: {data['units']} un.]** &nbsp;|&nbsp; :red[Custo: R$ {data['cogs']:,.2f}]**"

                with st.expander(label):
                    for v in data["variations"]:
                        m = re.search(r'- (\d+)x$', v['title'])
                        n = m.group(1) if m else "1"
                        txt = f"{n} Frasco" if n == "1" else f"{n} Frascos"

                        # Preços e Margens
                        preco_tabela = v.get('preco_tabela', 0)
                        unit_cogs = v.get('unit_cogs', 0)
                        receita_v = v.get('receita', 0)
                        pkgs_v = v.get('pkgs', 0)

                        # Info de Venda Real
                        if pkgs_v > 0:
                            preco_medio_real = receita_v / pkgs_v
                            margem_v = v.get('margem', 0)
                            margem_color = '#4CAF50' if margem_v >= 20 else ('#FF9800' if margem_v >= 10 else '#F44336')

                            desconto_pct = ((preco_tabela - preco_medio_real) / preco_tabela * 100) if preco_tabela > 0 else 0
                            desc_html = f" <span style='color: #9E9E9E; font-size: 0.8em;'>(-{desconto_pct:.0f}%)</span>" if desconto_pct > 2 else ""

                            result_info = (
                                f"<span style='color: #4CAF50;'>{pkgs_v} vendidos</span> &nbsp;|&nbsp; "
                                f"Venda Média: <b>R$ {preco_medio_real:,.2f}</b>{desc_html} &nbsp;|&nbsp; "
                                f"<span style='color: {margem_color}; font-weight: bold;'>Margem Real: {margem_v:.1f}%</span>"
                            )
                        else:
                            # Info Estimada (Potencial)
                            p_margem = v.get('potential_margin', 0)
                            p_color = '#81C784' if p_margem >= 20 else ('#FFB74D' if p_margem >= 10 else '#E57373')
                            result_info = (
                                f"<span style='color: #9E9E9E;'>Sem vendas</span> &nbsp;|&nbsp; "
                                f"<span style='color: {p_color}; opacity: 0.8;'>Margem Est.: {p_margem:.1f}%</span>"
                            )

                        st.markdown(f"""
    <div style='display: flex; justify-content: space-between; border-bottom: 1px solid #ffffff1e; padding: 8px 0; flex-wrap: wrap; align-items: center;'>
    <div style='flex: 1; min-width: 150px;'>
    <span style='font-size: 0.9em; color: #9E9E9E;'>{v['title']}</span><br>
    <b>{txt}</b> &nbsp;|&nbsp; Tabela: <span style='color: #64B5F6;'>R$ {preco_tabela:,.2f}</span>
    </div>
    <div style='flex: 2; text-align: right; min-width: 250px;'>
    <span style='font-size: 0.85em;'>Estoque: <b>{v['stock']} kits</b></span><br>
    {result_info}
    </div>
    </div>
    """, unsafe_allow_html=True)


        else:
            st.info("Nenhum anúncio mapeado.")

    with sub_tab_estoque:
        st.markdown("#### :material/store: Inventário de Potes")

        # Filtro de período com calendário (dia 15 a 14 do mês seguinte)
        from datetime import datetime, timedelta
        today = datetime.now()

        # Período padrão: dia 15 do mês passado até dia 14 do mês atual
        if today.day >= 15:
            start_date_default = today.replace(day=15)
        else:
            if today.month == 1:
                start_date_default = today.replace(year=today.year-1, month=12, day=15)
            else:
                start_date_default = today.replace(month=today.month-1, day=15)
        end_date_default = today.replace(day=14)

        col_date1, col_date2 = st.columns(2)
        with col_date1:
            start_date = st.date_input(
                "Data Início",
                value=start_date_default,
                help="Período de pagamento fornecedor: dia 15"
            )
        with col_date2:
            end_date = st.date_input(
                "Data Fim",
                value=end_date_default
            )

        # Garantir que end_date seja datetime para comparação
        if isinstance(end_date, datetime):
            end_date = end_date + timedelta(days=1)  # Inclui o dia todo
        else:
            end_date = datetime.combine(end_date, datetime.max.time()) + timedelta(days=1)

        # Converter start_date para datetime se necessário
        if not isinstance(start_date, datetime):
            start_date = datetime.combine(start_date, datetime.min.time())

        # Filtrar transações do período
        period_transactions = [t for t in income_transactions 
                               if t.date and start_date <= t.date < end_date]

        # Calcular métricas do período
        period_potes_vendidos = 0
        period_cogs = 0.0

        for txn in period_transactions:
            if txn.product_id:
                product = next((p for p in products if p.id == txn.product_id), None)
                if product and hasattr(product, 'components') and product.components:
                    for comp in product.components:
                        inv_item = next((i for i in inventory_items if i.id == comp.inventory_item_id), None)
                        if inv_item:
                            potes = txn.quantity * (comp.quantity or 1)
                            period_potes_vendidos += potes
                            period_cogs += potes * (inv_item.supplier_price or 0.0)
                elif product:
                    period_potes_vendidos += txn.quantity
                    period_cogs += txn.quantity * (product.supplier_price or 0.0)

        if inventory_items:
            display_start = start_date.date() if isinstance(start_date, datetime) else start_date
            display_end = (end_date - timedelta(days=1)).date() if isinstance(end_date, datetime) else end_date
            c1, c2, c3, c4 = st.columns(4)
            with c1: metric_card("Potes Vendidos (Período)", f"{period_potes_vendidos} un.")
            with c2: metric_card("COGS (Período)", f"R$ {period_cogs:,.2f}")
            with c3: metric_card("Potes Vendidos (Total)", f"{total_potes_vendidos} un.")
            with c4: metric_card("COGS (Total)", f"R$ {total_cogs_vendas:,.2f}")

            # Calcular potes vendidos por item no período
            potes_por_item_periodo = {item.id: 0 for item in inventory_items}
            for txn in period_transactions:
                if txn.product_id:
                    product = next((p for p in products if p.id == txn.product_id), None)
                    if product and hasattr(product, 'components') and product.components:
                        for comp in product.components:
                            if comp.inventory_item_id in potes_por_item_periodo:
                                potes_por_item_periodo[comp.inventory_item_id] += txn.quantity * (comp.quantity or 1)
                    elif product:
                        potes_por_item_periodo[product.id if product.id in potes_por_item_periodo else 0] += txn.quantity

            df_inv = pd.DataFrame([{
                "ID": item.id,
                "Nome": item.name,
                "Estoque Atual": item.stock,
                "Estoque Mínimo": item.min_stock,
                "Custo": item.supplier_price,
                "Potes Vendidos (Mês)": potes_por_item_periodo.get(item.id, 0),
                "Potes Vendidos (Total)": vendidos_por_item.get(item.id, 0)
            } for item in inventory_items])

            st.info("O estoque é controlado centralmente pelo **Estoque de Potes Físicos**. Os anúncios virtuais (Shopee) apenas refletem essa disponibilidade.", icon=":material/lightbulb:")




            edited_inv = st.data_editor(
                df_inv,
                column_config={
                    "ID": None,
                    "Custo": st.column_config.NumberColumn(format="R$ %.2f"),
                    "Estoque Atual": st.column_config.NumberColumn(disabled=True),
                    "Potes Vendidos (Mês)": st.column_config.NumberColumn(disabled=True),
                    "Potes Vendidos (Total)": st.column_config.NumberColumn(disabled=True)
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

        with st.expander(":material/add: Novo Item Físico"):
            col_i1, col_i2, col_i3 = st.columns(3)
            ni_name = col_i1.text_input("Nome", key="ni_name_inp")
            ni_cost = col_i2.number_input("Custo", min_value=0.0, key="ni_cost_inp")
            ni_min = col_i3.number_input("Mínimo", min_value=0, value=5, step=1, key="ni_min_inp")
            if st.button("Adicionar Item"):
                from core.database.models import InventoryItem
                with Session(engine) as session:
                    session.add(InventoryItem(name=ni_name, supplier_price=ni_cost, stock=600, initial_stock=600, min_stock=ni_min, user_id=user.id))
                    session.commit()
                st.success("Adicionado!"); st.rerun()

    with sub_tab_calc:
        st.markdown("#### :material/calculate: Simulador de Precificação e Lucro")
        st.info("Utilize esta calculadora para planejar seus preços antes de publicar os anúncios, analisando todas as taxas da Shopee, impostos e custos de fornecedor.")

        col_in, col_out = st.columns([1, 1], gap="large")

        with col_in:
            st.markdown("### :material/file_download: Parâmetros do Anúncio")

            c_p1, c_p2 = st.columns(2)
            calc_cost = c_p1.number_input("Custo Fornecedor (unit.) R$", min_value=0.0, value=15.0, step=1.0, format="%.2f", help="Valor pago pelo item físico")
            calc_price = c_p2.number_input("Preço de Venda R$", min_value=0.0, value=35.0, step=1.0, format="%.2f", help="Valor total da venda (independente da quantidade)")

            c_q1, c_q2, c_q3 = st.columns(3)
            calc_qty = c_q1.number_input("Qtd no Pedido", min_value=1, value=1, step=1, help="Simula cliente comprando + de 1 unidade")
            calc_coupon_pct = c_q2.number_input("Cupom da Loja (%)", min_value=0.0, value=0.0, step=1.0, format="%.1f", help="Desconto percentual dado por você")
            calc_other_discount_pct = c_q3.number_input("Outros Desc. (%)", min_value=0.0, value=0.0, step=1.0, format="%.1f", help="Promoções como Leve mais por Menos")

            st.markdown("### :material/receipt_long: Taxas e Encargos")

            c_t1, c_t2 = st.columns(2)
            calc_shopee_pct = c_t1.selectbox("Tarifa Shopee (%)", options=[20.0, 14.0], format_func=lambda x: f"{x}% (Frete Grátis)" if x == 20 else f"{x}% (Padrão)", help="Comissão + Taxa de Transação (2%)")
            calc_shopee_fixed = c_t2.number_input("Taxa Fixa (por item) R$", min_value=0.0, value=4.0, step=0.5, format="%.2f", help="R$ 4,00 por item. Limitado a R$100 totais.")

            c_t3, c_t4 = st.columns(2)
            calc_ads_pct = c_t3.number_input("Recarga Automática Ads (%)", min_value=0.0, value=10.0, step=1.0, help="Porcentagem de ads do pedido")
            calc_simples_pct = c_t4.number_input("Simples Nacional (%)", min_value=0.0, value=4.0, step=0.5)

            calc_extra = st.number_input("Custos Extras (Embalagem, etc) R$", min_value=0.0, value=0.0, step=1.0, format="%.2f", help="Custo por pedido")

        with col_out:
            st.markdown("### :material/trending_up: Resultados e Saúde Financeira")

            gross_revenue = calc_price

            # Cálculo em cascata (Sequencial como a Shopee)
            # 1. Aplica o desconto de combo/outros primeiro
            calc_other_discount = gross_revenue * (calc_other_discount_pct / 100.0)
            revenue_after_other = gross_revenue - calc_other_discount

            # 2. Aplica o cupom da loja sobre o valor restante
            calc_coupon = revenue_after_other * (calc_coupon_pct / 100.0)

            total_descontos_loja = calc_other_discount + calc_coupon
            net_revenue_base = gross_revenue - total_descontos_loja

            if net_revenue_base < 0: net_revenue_base = 0.0

            comissao_shopee = net_revenue_base * (calc_shopee_pct / 100.0)
            taxa_fixa_shopee = calc_shopee_fixed * calc_qty
            if taxa_fixa_shopee > 100.0: taxa_fixa_shopee = 100.0

            custo_ads = net_revenue_base * (calc_ads_pct / 100.0)
            custo_imposto = net_revenue_base * (calc_simples_pct / 100.0)
            custo_fornecedor_total = calc_cost * calc_qty

            total_deductions = total_descontos_loja + comissao_shopee + taxa_fixa_shopee + custo_ads + custo_imposto + custo_fornecedor_total + calc_extra
            net_profit = gross_revenue - total_deductions

            profit_margin = (net_profit / gross_revenue * 100.0) if gross_revenue > 0 else 0.0
            roi = (net_profit / custo_fornecedor_total * 100.0) if custo_fornecedor_total > 0 else 0.0
            repasse_shopee = net_revenue_base - comissao_shopee - taxa_fixa_shopee - custo_ads

            margin_color = ":material/check_circle:" if profit_margin >= 20 else (":material/warning_amber:" if profit_margin >= 10 else ":material/cancel:")

            metric_card("Lucro Líquido Real", f"R$ {net_profit:,.2f}", delta=f"{margin_color} {profit_margin:.1f}%")

            m1, m2 = st.columns(2)
            with m1: metric_card("ROI", f"{roi:.0f}%")
            with m2: metric_card("Repasse da Shopee", f"R$ {repasse_shopee:,.2f}")

            st.divider()
            st.markdown("**Detalhamento Financeiro do Pedido:**")
            st.markdown(f"""
            <div style="font-family: monospace; font-size: 14px; background-color: #1e1e1e; color: #e0e0e0; padding: 15px; border-radius: 8px;">
                <div style="display: flex; justify-content: space-between;"><span>Subtotal dos Produtos ({calc_qty}x):</span> <span>R$ {gross_revenue:,.2f}</span></div>
                <div style="display: flex; justify-content: space-between; color: #ffab91;"><span>Cupons & descontos (Loja):</span> <span>- R$ {total_descontos_loja:,.2f}</span></div>
                <div style="display: flex; justify-content: space-between; font-weight: bold; border-top: 1px solid #424242; margin-top: 5px; padding-top: 5px;"><span>Base para Taxas Shopee:</span> <span>R$ {net_revenue_base:,.2f}</span></div>
                <br>
                <div style="display: flex; justify-content: space-between; color: #ffab91;"><span>Taxas e Encargos Shopee:</span> <span>- R$ {comissao_shopee + taxa_fixa_shopee + custo_ads:,.2f}</span></div>
                <div style="display: flex; justify-content: space-between; color: #ffab91; padding-left: 15px; font-size: 12px;"><span>↳ Tarifa Shopee ({calc_shopee_pct}%):</span> <span>- R$ {comissao_shopee:,.2f}</span></div>
                <div style="display: flex; justify-content: space-between; color: #ffab91; padding-left: 15px; font-size: 12px;"><span>↳ Taxa por item vendido ({calc_qty}x):</span> <span>- R$ {taxa_fixa_shopee:,.2f}</span></div>
                <div style="display: flex; justify-content: space-between; color: #ffab91; padding-left: 15px; font-size: 12px;"><span>↳ Recarga Automática Ads ({calc_ads_pct}%):</span> <span>- R$ {custo_ads:,.2f}</span></div>
                <br>
                <div style="display: flex; justify-content: space-between; color: #ffab91;"><span>Simples Nacional ({calc_simples_pct}%):</span> <span>- R$ {custo_imposto:,.2f}</span></div>
                <div style="display: flex; justify-content: space-between; color: #ffab91;"><span>Custos Extras:</span> <span>- R$ {calc_extra:,.2f}</span></div>
                <div style="display: flex; justify-content: space-between; color: #64b5f6;"><span>Custo Fornecedor ({calc_qty}x):</span> <span>- R$ {custo_fornecedor_total:,.2f}</span></div>
                <div style="display: flex; justify-content: space-between; font-weight: bold; border-top: 1px solid #424242; margin-top: 5px; padding-top: 5px; font-size: 16px;">
                    <span>Lucro Líquido Real:</span> 
                    <span style="color: {'#81c784' if net_profit > 0 else '#e57373'}">R$ {net_profit:,.2f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)


    st.divider()
    with st.expander(":material/description: Editor de Anúncios Shopee (SKUs Virtuais)"):
        if products:
            df_prods = pd.DataFrame([{"ID": p.id, "Título": p.title, "Preço": p.price} for p in products])
            edit_ads = st.data_editor(df_prods, column_config={"ID": None}, hide_index=True, use_container_width=True, key="ads_ed")
            if st.button("Salvar Anúncios"):
                for _, row in edit_ads.iterrows():
                    product_agent.update_product(int(row["ID"]), {"title": row["Título"], "price": float(row["Preço"])})
                st.success("Anúncios salvos!"); st.rerun()

        else:
            st.info("Nenhum anúncio para editar.")

        with st.expander(":material/add: Novo SKU Virtual (Manual)"):
            col_nv1, col_nv2 = st.columns([2, 1])
            nv_title = col_nv1.text_input("Título do Anúncio", key="nv_title_inp")
            nv_price = col_nv2.number_input("Preço de Venda", min_value=0.0, key="nv_price_inp")
            if st.button("Adicionar SKU Virtual"):
                product_agent.save_product({
                    "title": nv_title, "price": nv_price, "description": "Manual", "stock": 0
                }, user.id)
                st.success("SKU Virtual adicionado!"); st.rerun()


    st.divider()

    # 2. ADICIONAR ANÚNCIO (The core engine)
    with st.container(border=True):
        st.markdown("#### :material/add: Adicionar Novo Anúncio com IA")

        method = st.radio("Método de Criação:", ["Manual (Texto)", "Imagem (Vision + IA Search)"], horizontal=True)

        if method == "Manual (Texto)":
            col_m1, col_m2 = st.columns([1, 1])
            with col_m1:
                p_name = st.text_input("Nome do Produto", placeholder="Ex: Creatina Monohidratada Pura", key="manual_name")
                p_ing = st.text_input("Ingredientes/Detalhes", placeholder="Ex: 300g, 100% Pura", key="manual_ing")
            with col_m2:
                p_ben = st.text_area("Principais Benefícios", placeholder="Ex: Aumento de força...", key="manual_ben")

            if st.button("Gerar Anúncio", icon=":material/auto_awesome:", type="primary", key="btn_manual"):
                if p_name and p_ben:
                    with st.spinner("Analisando e criando copy..."):
                        listing = product_agent.generate_listing(p_name, p_ben, p_ing)
                        st.session_state.last_generated_res = listing
                else:
                    st.warning("Preencha o Nome e os Benefícios.")

        else: # Image Method
            st.info("Passo 1: Envie uma foto e a IA identificará o produto. Passo 2: Você revisa e geramos o anúncio com busca web.", icon=":material/lightbulb:")
            img_file = st.file_uploader("Upload da Imagem do Produto", type=["jpg", "jpeg", "png"])

            if img_file:
                st.image(img_file, width=200)
                if st.button("Passo 1: Extrair Informações", icon=":material/photo_camera:", type="primary"):
                    with st.spinner("Lendo rótulo..."):
                        img_bytes = img_file.getvalue()
                        info = product_agent.extract_product_info(img_bytes)
                        st.session_state.extracted_info = info
                        if 'last_generated_res' in st.session_state: del st.session_state.last_generated_res

            if 'extracted_info' in st.session_state:
                st.divider()
                st.markdown("### :material/edit_note: Informações Detectadas")
                st.caption("Ajuste os dados abaixo se necessário antes da pesquisa web.")
                edited_info = st.text_area("Dados do Produto", value=st.session_state.extracted_info, height=150)

                if st.button("Passo 2: Gerar Anúncio Completo (com Busca Web)", icon=":material/search:", type="primary"):
                    with st.spinner("Pesquisando na internet e criando copy..."):
                        listing = product_agent.generate_from_extracted_info(edited_info)
                        st.session_state.last_generated_res = listing
                        # Keep extracted_info so they can refine and regenerate if needed, 
                        # but usually we might want to clear it after saving.

        # Review and Save Area (Shared for both methods)
        if 'last_generated_res' in st.session_state:
            res = st.session_state.last_generated_res
            st.divider()
            st.markdown("### :material/search: Revisão e Ajustes Finais")

            edit_title = st.text_input("Título SEO", value=res['title'])
            edit_keys = st.text_area("Keywords (Tags)", value=res.get('keywords', ''))
            edit_desc = st.text_area("Descrição", value=res['description'], height=300)

            col1, col2 = st.columns(2)
            p_price = col1.number_input("Preço de Venda (R$)", min_value=0.0, step=1.0, value=0.0, key="price_input")
            p_stock = col2.number_input("Estoque Inicial", min_value=0, step=1, value=100, key="stock_input")

            if st.button("Confirmar e Salvar no Catálogo", icon=":material/save:", type="primary", width="stretch"):
                final_data = {
                    "title": edit_title,
                    "description": edit_desc,
                    "keywords": edit_keys,
                    "price": p_price,
                    "stock": p_stock
                }
                save_res = product_agent.save_product(final_data, user.id)
                if save_res["success"]:
                    st.success(f"Produto '{edit_title}' salvo com sucesso!")
                    del st.session_state.last_generated_res
                    st.rerun()
                else:
                    st.error(f"Erro ao salvar: {save_res['message']}")

    # --- NEW: BUNDLE / KIT COMPOSITION UI ---
    st.divider()
    with st.expander(":material/build: Configurar Composição de Kits (Vincular Itens Físicos)"):
        st.caption("Associe anúncios da Shopee (SKUs Virtuais) aos produtos que você tem na prateleira.")

        # 1. Select Product
        if products:
            prod_names = {p.title: p.id for p in products}
            selected_p_title = st.selectbox("Selecione o Anúncio (SKU Virtual)", ["-- Escolha um --"] + list(prod_names.keys()), key="bundle_prod_select")

            if selected_p_title != "-- Escolha um --":
                p_id = prod_names[selected_p_title]

                # 2. Show Current Components
                components = product_agent.get_product_components(p_id)
                inventory_items_list = product_agent.get_all_inventory_items(user.id)
                inv_map = {item.id: item.name for item in inventory_items_list}

                if components:
                    st.write("**Componentes Atuais:**")
                    for comp in components:
                        c_col1, c_col2, c_col3 = st.columns([3, 1, 1])
                        item_name = inv_map.get(comp.inventory_item_id, "Item Desconhecido")
                        c_col1.write(f":material/fiber_manual_record: {comp.quantity}x {item_name}")
                        if c_col3.button("Remover", key=f"del_comp_{comp.id}"):
                            res = product_agent.delete_product_component(comp.id)
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
                            add_res = product_agent.add_product_component(p_id, inv_id, comp_qty)
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
        with st.expander(":material/file_download: Importar da Shopee (CSV)"):
            st.caption("Suba o arquivo CSV exportado da Shopee para cadastrar em massa.")
            up_file = st.file_uploader("Selecione o CSV", type=["csv"], key="import_csv")
            if up_file:
                if st.button("Processar Importação", icon=":material/file_download:", key="btn_import"):
                    with st.spinner("Importando produtos..."):
                        imp_res = product_agent.process_csv_import(up_file, user.id)
                        if imp_res["success"]:
                            st.success(f"Sucesso! {imp_res['count']} produtos importados.")
                            st.rerun()
                        else:
                            st.error(imp_res["message"])

    with col_ie2:
        with st.expander(":material/file_upload: Exportar para Shopee (CSV)"):
            st.caption("Selecione os produtos do catálogo para gerar o arquivo de upload.")
            products_to_export = product_agent.get_all_products(user.id)

            if products_to_export:
                df_exp = pd.DataFrame([{
                    "Sel": False,
                    "ID": p.id,
                    "Título": p.title
                } for p in products_to_export])

                edited_exp = st.data_editor(df_exp, hide_index=True, width="stretch", key="export_editor")
                selected_ids = edited_exp[edited_exp["Sel"] == True]["ID"].tolist()

                if st.button("Gerar CSV", icon=":material/file_upload:", key="btn_export"):
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

                        csv_data = product_agent.generate_mass_upload_csv(export_data)
                        st.download_button("Clique para Download", data=csv_data, file_name="upload_shopee.csv", mime="text/csv")
                    else:
                        st.warning("Selecione itens.")
            else:
                st.info("Catálogo vazio.")
