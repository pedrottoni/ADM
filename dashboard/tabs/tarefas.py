"""
:material/assignment: Tarefas — Tab de Tarefas Práticas
"""

import streamlit as st
from core.database.engine import get_session
from core.tasks.engine import TaskEngine
from dashboard.components.metric_card import metric_card


def render(user, agents):
    """Render the tab with pending and completed tasks."""
    session = next(get_session())
    TaskEngine.scan_and_generate(session, user.id)
    pending = TaskEngine.get_pending(session, user.id)
    completed = TaskEngine.get_completed(session, user.id)

    st.markdown(
        '<p class="page-subtitle">'
        "Tarefas práticas geradas automaticamente com base nos seus dados. "
        "Conclua cada uma para manter a operação em dia."
        "</p>",
        unsafe_allow_html=True,
    )

    # Stats row - usando metric_card
    col1, col2, col3 = st.columns(3)
    with col1:
        metric_card(":material/pending_actions: Pendentes", str(len(pending)))
    with col2:
        metric_card(":material/check_circle: Concluídas", str(len(completed)))
    with col3:
        if pending:
            urgent = sum(1 for t in pending if t.priority <= 2)
            metric_card(":material/priority_high: Prioritárias", str(urgent))

    if not pending:
        st.success(
            ":material/celebration: Nenhuma tarefa pendente! Sua operação está em dia.",
        )

    # Category icon map
    ICONS = {
        "vendas": ":material/payments:",
        "estoque": ":material/inventory:",
        "concorrencia": ":material/search:",
        "relatorio": ":material/analytics:",
        "marketing": ":material/campaign:",
        "anuncio": ":material/inventory_2:",
    }
    URGENCY = {1: ":material/priority_high: Urgente", 2: ":material/star: Importante", 3: ":material/checkbox_blank_circle: Normal", 4: ":material/expand_more: Baixa", 5: ":material/more_horiz: Opcional"}

    for task in pending:
        icon = ICONS.get(task.category, ":material/task:")
        prio = URGENCY.get(task.priority, ":material/checkbox_blank_circle: Normal")
        cat_label = task.category.capitalize() if task.category else "Geral"

        with st.container(border=True):
            cols = st.columns([6, 1])
            with cols[0]:
                st.markdown(f"### {icon} {task.title}")
                st.caption(f"{cat_label} · {prio}")
                st.markdown(f"<div style='margin-top:6px;'>{task.description}</div>", unsafe_allow_html=True)
            with cols[1]:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Concluir", key=f"task_done_{task.id}", type="primary", use_container_width=True):
                    TaskEngine.complete(session, task.id)
                    st.toast(":material/check: Tarefa concluída!")
                    st.rerun()

    if completed:
        st.divider()
        with st.expander(f":material/history: Últimas tarefas concluídas ({len(completed)})"):
            for task in completed:
                done_time = task.completed_at.strftime("%d/%m/%Y %H:%M") if task.completed_at else ""
                st.markdown(f"- ~~{task.title}~~ `{done_time}`", unsafe_allow_html=True)

    session.close()
