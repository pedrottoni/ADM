"""
🏠 Resumo — Tab de Resumo
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
    stats = finance_agent.get_financial_stats(user.id)
    kpi_row1 = st.columns(4)
    kpi_row1[0].metric("💰 Receita Total", f"R$ {stats['total_revenue']:,.2f}")
    kpi_row1[1].metric("📉 Despesas", f"R$ {stats['total_expenses']:,.2f}")
    kpi_row1[2].metric("📈 Lucro Líquido", f"R$ {stats['net_profit']:,.2f}",
                       delta=f"{stats['margin']:.1f}%" if stats['total_revenue'] > 0 else None)
    kpi_row1[3].metric("📊 Transações", str(stats['transaction_count']))

    st.divider()

    # ── Top Vendas + Top Produtos (2 colunas, topo) ──
    col_top_left, col_top_right = st.columns([1, 1])

    with col_top_left:
        st.subheader("🏆 Top Vendas")
        top_prods = finance_agent.get_top_products(user.id, limit=10)
        if top_prods:
            for i, p in enumerate(top_prods, 1):
                title = p['product_title'][:35] + "..." if len(p['product_title']) > 35 else p['product_title']
                st.markdown(f"**{i}.** {title} — *R$ {p['total_revenue']:,.2f}*")
        else:
            st.info("Nenhuma venda registrada ainda.")

    with col_top_right:
        st.subheader("🏆 Top Produtos")
        top_by_potes = finance_agent.get_top_products_by_potes(user.id, limit=10)
        if top_by_potes:
            for i, p in enumerate(top_by_potes, 1):
                title = p['product_title'][:35] + "..." if len(p['product_title']) > 35 else p['product_title']
                st.markdown(f"**{i}.** {title} — **:green[Vendidos: {p['total_potes']} un.]**")
        else:
            st.info("Nenhum produto vendido ainda.")

    st.divider()

    # ── Progresso + Alertas (2 colunas, abaixo) ──
    col_bot_left, col_bot_right = st.columns([1, 1])

    with col_bot_left:
        st.subheader("🎯 Progresso")
        next_level_xp = user.level * 100
        progress = min(user.xp / next_level_xp, 1.0)
        st.progress(progress, text=f"Nível {user.level} — {user.xp}/{next_level_xp} XP")
        st.caption(f"Total de missões completadas: {len([m for m in user.missions if m.is_completed]) if user.missions else 0}")

        st.divider()

        # ── Missões Ativas ──
        st.markdown("**Missões Ativas**")
        if user.missions:
            pending = [m for m in user.missions if not m.is_completed]
            if pending:
                for m in pending[:3]:
                    st.info(f"📝 **{m.title}** — +{m.xp_reward} XP")
                    st.caption(m.description[:80] + "..." if len(m.description) > 80 else m.description)
            else:
                st.success("✅ Todas as missões concluídas!")
        else:
            st.info("Nenhuma missão cadastrada. Comece registrando vendas!")

    with col_bot_right:
        st.subheader("⚠️ Alertas de Estoque")
        low_stock_items = product_agent.get_low_stock_items(user.id)
        if low_stock_items:
            for item in low_stock_items:
                st.error(f"**{item.name}** — {item.stock} un (mín: {item.min_stock})")
        else:
            st.success("✅ Todos os itens com estoque saudável.")

    st.divider()

    # ── Ações Rápidas ──
    st.subheader("⚡ Ações Rápidas")
    qa1, qa2, qa3, qa4 = st.columns(4)
    with qa1:
        if st.button("💰 Nova Venda", use_container_width=True, type="primary"):
            st.switch_page("dashboard/main.py")  # fallback: will just scroll to tab2
            # Streamlit doesn't support programmatic tab switching;
            # We redirect to the same page (a re-run) and show a toast
            st.toast("Vá para a aba 💰 Financeiro > Registrar Venda")
    with qa2:
        if st.button("📦 Novo Produto", use_container_width=True):
            st.toast("Vá para a aba 📦 Meus Anúncios > Adicionar Anúncio")
    with qa3:
        if st.button("🔍 Ver Concorrência", use_container_width=True):
            st.toast("Vá para a aba 🔍 Concorrência")
    with qa4:
        if st.button("📥 Importar CSV", use_container_width=True):
            st.toast("Vá para a aba 📦 Meus Anúncios > Importar")
