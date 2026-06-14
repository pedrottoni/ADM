"""
:material/analytics: Metric Card — Componente de métrica customizado
====================================================
Substitui st.metric() por HTML puro com st.html(),
dando controle total sobre o layout (inline value+delta)
sem depender do CSS-in-JS interno do Streamlit 1.56.

Uso:
    from dashboard.components.metric_card import metric_card
    metric_card(":material/payments: Receita", "R$ 10.502,63")
    metric_card(":material/trending_up: Lucro", "R$ 8.124,52", delta="77.4%")
    metric_card(":material/trending_down: Margem", "R$ 5,00", delta=":material/cancel: 5.0%")
"""

import re
import streamlit as st


def _material_to_html(text: str) -> str:
    """Convert :material/icon_name: to <span class="material-symbols-rounded">icon_name</span>."""
    return re.sub(r':material/(\w+):', r'<span class="material-symbols-rounded">\1</span>', text)


def metric_card(label: str, value: str, delta: str | None = None) -> None:
    """Renderiza um card de métrica com value + delta lado a lado.

    Args:
        label: Rótulo do card (ex: ":material/payments: Receita Total")
        value: Valor principal (ex: "R$ 10.502,63")
        delta: Percentual opcional (ex: "77.4%", "-5.2%").
               Se conter :material/check_circle: → positive (green).
               Se conter :material/warning_amber: → neutral (green).
               Se conter :material/cancel: → negative (red).
    """
    label_html = _material_to_html(label)

    delta_html = ""
    if delta is not None:
        stripped = delta.strip()

        # Detecta indicador por :material/ icon (3 estados)
        if ":material/cancel:" in stripped:
            is_positive = False
        elif ":material/check_circle:" in stripped or ":material/warning_amber:" in stripped:
            is_positive = True
        else:
            # Fallback: limpa arrow symbol e verifica sinal
            for sym in ("↑", "↓", "▲", "▼"):
                stripped = stripped.replace(sym, "").strip()
            is_positive = not stripped.startswith("-")

        # Remove :material/ shortcodes from displayed text
        stripped = re.sub(r':material/\w+:', '', stripped).strip()

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
        ">{label_html}</div>
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
