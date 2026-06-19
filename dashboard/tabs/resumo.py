"""
:material/home: Resumo — Tab de Resumo
"""

import streamlit as st
from core.config import Config
from core.database.engine import get_session


def render(user, agents):
    """Render the tab content."""
    finance_agent = agents["finance_agent"]
    product_agent = agents["product_agent"]
    ads_agent = agents["ads_agent"]
    customer_agent = agents["customer_agent"]

    # ── KPI Cards ──
    from dashboard.components.metric_card import metric_card

    stats = finance_agent.get_financial_stats(user.id)
    kpi_row1 = st.columns(4)
    with kpi_row1[0]:
        metric_card(":material/payments: Receita Total", f"R$ {stats['total_revenue']:,.2f}")
    with kpi_row1[1]:
        metric_card(":material/trending_down: Despesas", f"R$ {stats['total_expenses']:,.2f}")
    with kpi_row1[2]:
        delta_val = f"{stats['margin']:.1f}%" if stats['total_revenue'] > 0 else None
        metric_card(":material/trending_up: Lucro Líquido", f"R$ {stats['net_profit']:,.2f}", delta=delta_val)
    with kpi_row1[3]:
        metric_card(":material/analytics: Transações", str(stats['transaction_count']))

    st.divider()

    # ── Top Vendas + Top Produtos (card único) ──
    top_prods = finance_agent.get_top_products(user.id, limit=10)
    top_by_potes = finance_agent.get_top_products_by_potes(user.id, limit=10)

    # Build rank HTML
    def _rank_class(i):
        if i == 1:
            return "top-rank rank-gold"
        elif i == 2:
            return "top-rank rank-silver"
        elif i == 3:
            return "top-rank rank-bronze"
        return "top-rank"

    vendas_html = ""
    if top_prods:
        for i, p in enumerate(top_prods[:10], 1):
            title = p['product_title'][:28] + "..." if len(p['product_title']) > 28 else p['product_title']
            vendas_html += (
                f'<div class="top-item">'
                f'  <span class="{_rank_class(i)}">{i}</span>'
                f'  <span class="top-name">{title}</span>'
                f'  <span class="top-value">R$ {p["total_revenue"]:,.2f}</span>'
                f'</div>'
            )
    else:
        vendas_html = '<div class="top-empty">Nenhuma venda registrada ainda.</div>'

    produtos_html = ""
    if top_by_potes:
        for i, p in enumerate(top_by_potes[:10], 1):
            title = p['product_title'][:28] + "..." if len(p['product_title']) > 28 else p['product_title']
            produtos_html += (
                f'<div class="top-item">'
                f'  <span class="{_rank_class(i)}">{i}</span>'
                f'  <span class="top-name">{title}</span>'
                f'  <span class="top-value top-value-teal">{p["total_potes"]} un.</span>'
                f'</div>'
            )
    else:
        produtos_html = '<div class="top-empty">Nenhum produto vendido ainda.</div>'

    st.markdown(
        f'<div class="top-rankings-card">'
        f'  <div class="top-rankings-col">'
        f'    <div class="card-title"><span class="material-symbols-rounded">trending_up</span> Top Vendas</div>'
        f'    <div class="top-list">{vendas_html}</div>'
        f'  </div>'
        f'  <div class="top-rankings-col">'
        f'    <div class="card-title"><span class="material-symbols-rounded">inventory_2</span> Top Produtos</div>'
        f'    <div class="top-list">{produtos_html}</div>'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # ── Progresso + Alertas (2 colunas, abaixo) ──
    col_bot_left, col_bot_right = st.columns([1, 1])

    with col_bot_left:
        st.markdown('''<div class="progresso-card-marker"></div>''', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><span class="material-symbols-rounded">adjust</span> Progresso</div>', unsafe_allow_html=True)
        next_level_xp = user.level * 100
        progress = min(user.xp / next_level_xp, 1.0)
        completed = len([m for m in user.missions if m.is_completed]) if user.missions else 0
        pending_count = len([m for m in user.missions if not m.is_completed]) if user.missions else 0
        st.markdown(f'<div style="margin-bottom:8px"><div style="display:flex;justify-content:space-between;margin-bottom:4px"><span style="font-size:0.98rem;color:var(--dx-text-primary);font-weight:500">N\xedvel {user.level}</span><span style="font-size:0.85rem;color:var(--dx-text-secondary)">{user.xp}/{next_level_xp} XP</span></div><div style="background:rgba(100,116,139,0.15);border-radius:100px;height:8px;overflow:hidden"><div style="background:var(--dx-indigo);width:{progress*100:.1f}%;height:100%;border-radius:100px;transition:width 0.3s ease"></div></div></div><div style="display:flex;gap:1rem;font-size:0.85rem;color:var(--dx-text-secondary)"><span><span class="material-symbols-rounded" style="font-size:1rem;vertical-align:middle">task_alt</span> {completed} realizadas</span><span><span class="material-symbols-rounded" style="font-size:1rem;vertical-align:middle">pending</span> {pending_count} pendentes</span></div>', unsafe_allow_html=True)

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        # ── Missões Ativas ──
        st.markdown('<div class="card-title"><span class="material-symbols-rounded">edit_note</span> Miss\u00f5es Ativas</div>', unsafe_allow_html=True)
        if user.missions:
            pending = [m for m in user.missions if not m.is_completed]
            if pending:
                for m in pending[:3]:
                    st.info(f":material/edit_note: **{m.title}** — +{m.xp_reward} XP")
                    st.caption(m.description[:80] + "..." if len(m.description) > 80 else m.description)
            else:
                st.success("Todas as missões concluídas!", icon=":material/check_circle:")
        else:
            st.info("Nenhuma missão cadastrada. Comece registrando vendas!")

    with col_bot_right:
        st.markdown('''<div class="alertas-card-marker"></div>''', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><span class="material-symbols-rounded">warning</span> Alertas de Estoque</div>', unsafe_allow_html=True)
        low_stock_items = product_agent.get_low_stock_items(user.id)
        if low_stock_items:
            for item in low_stock_items:
                st.error(f"**{item.name}** — {item.stock} un (mín: {item.min_stock})")
        else:
            st.success("Todos os itens com estoque saudável.", icon=":material/check_circle:")

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # ── Ações Rápidas ──
    with st.container():
        st.markdown('''<div class="acoes-card-marker"></div>''', unsafe_allow_html=True)
        st.markdown('<div class="card-title"><span class="material-symbols-rounded">bolt</span> A\u00e7\u00f5es R\u00e1pidas</div>', unsafe_allow_html=True)
        qa1, qa2, qa3, qa4 = st.columns(4)
    with qa1:
        if st.button("➕ Nova Venda", use_container_width=True, type="primary"):
            st.toast("Vá para a aba :material/payments: Financeiro > Registrar Venda")
    with qa2:
        if st.button(":material/inventory_2: Novo Produto", use_container_width=True, type="secondary"):
            st.toast("Vá para a aba :material/inventory_2: Meus Anúncios > Adicionar Anúncio")
    with qa3:
        if st.button(":material/search: Concorrência", use_container_width=True, type="secondary"):
            st.toast("Vá para a aba :material/search: Concorrência")
    with qa4:
        if st.button(":material/file_download: Importar", use_container_width=True, type="secondary"):
            st.toast("Vá para a aba :material/inventory_2: Meus Anúncios > Importar")

