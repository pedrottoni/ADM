"""
📊 Metric Card — Componente de métrica customizado
====================================================
Substitui st.metric() por HTML puro com st.html(),
dando controle total sobre o layout (inline value+delta)
sem depender do CSS-in-JS interno do Streamlit 1.56.

Uso:
    from dashboard.components.metric_card import metric_card
    metric_card("💰 Receita", "R$ 10.502,63")
    metric_card("📈 Lucro", "R$ 8.124,52", delta="77.4%")
    metric_card("📉 Margem", "R$ 5,00", delta="🔴 5.0%")
"""

import streamlit as st


def metric_card(label: str, value: str, delta: str | None = None) -> None:
    """Renderiza um card de métrica com value + delta lado a lado.

    Args:
        label: Rótulo do card (ex: "💰 Receita Total")
        value: Valor principal (ex: "R$ 10.502,63")
        delta: Percentual opcional (ex: "77.4%", "-5.2%").
               Se iniciar com 🟢🟡🔴 o emoji define arrow/cor.
    """
    delta_html = ""
    if delta is not None:
        stripped = delta.strip()

        # Detecta indicador por emoji 🟢🟡🔴 (3 estados)
        if "🔴" in stripped:
            is_positive = False
        elif "🟢" in stripped or "🟡" in stripped:
            is_positive = True
        else:
            # Fallback: limpa arrow symbol e verifica sinal
            for sym in ("↑", "↓", "▲", "▼"):
                stripped = stripped.replace(sym, "").strip()
            is_positive = not stripped.startswith("-")

        bg = "#166534" if is_positive else "#7f1d1d"
        color = "#86efac" if is_positive else "#fca5a5"
        arrow = "▲" if is_positive else "▼"
        delta_html = (
            f'<span class="mc-delta" style="'
            f"background:{bg};color:{color};"
            f"border-radius:100px;padding:2px 10px;"
            f"font-size:0.75rem;font-weight:600;"
            f"display:inline-flex;align-items:center;gap:3px;"
            f"white-space:nowrap;flex-shrink:0;"
            f'">{arrow} {stripped}</span>'
        )

    html = f"""<div class="metric-card" style="
        background:#1E293B;
        border:1px solid #334155;
        border-radius:8px;
        padding:1.25rem 1.5rem;
        box-shadow:0 1px 3px rgba(0,0,0,0.2);
        transition:all 0.2s ease;
    ">
        <div class="mc-label" style="
            color:#94A3B8;
            font-size:0.8rem;
            font-weight:500;
            margin-bottom:4px;
        ">{label}</div>
        <div class="mc-row" style="
            display:flex;
            flex-direction:row;
            flex-wrap:nowrap;
            align-items:baseline;
            gap:8px;
        ">
            <span class="mc-value" style="
                font-size:1.5rem;
                font-weight:600;
                color:#F8FAFC;
                letter-spacing:-0.02em;
                line-height:1.3;
                white-space:nowrap;
                overflow:hidden;
                text-overflow:ellipsis;
            ">{value}</span>
            {delta_html}
        </div>
    </div>"""

    st.html(html)
