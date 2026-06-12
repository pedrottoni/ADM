"""
🤝 Atendimento — Tab de Atendimento
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

    st.header("🤝 Customer Hero (Atendimento)")

    col_c1, col_c2 = st.tabs(["💬 Gerador de Respostas", "⭐ Análise de Reviews"])

    with col_c1:
        st.subheader("Responder Cliente")
        msg = st.text_area("Mensagem do Cliente", placeholder="Ex: O produto chegou quebrado e quero meu dinheiro de volta!", height=120)
        tone = st.select_slider("Tom da Resposta", options=["Formal", "Empático", "Descontraído"], value="Empático")

        if st.button("Gerar Resposta ✍️"):
            if msg:
                with st.spinner("Escrevendo..."):
                    reply = customer_agent.generate_response(msg, tone)
                    st.session_state.generated_reply = reply
            else:
                st.warning("Cole a mensagem do cliente primeiro.")

        # Show response with copy button if generated
        if "generated_reply" in st.session_state and st.session_state.generated_reply:
            reply = st.session_state.generated_reply
            st.text_area("Sugestão de Resposta:", value=reply, height=150, key="reply_area")
            rcol1, rcol2 = st.columns([1, 4])
            with rcol1:
                if st.button("📋 Copiar Resposta", key="copy_reply"):
                    st.toast("Copiado! (Ctrl+C no campo acima)", icon="📋")
            with rcol2:
                if st.button("✏️ Refinar", key="refine_reply"):
                    st.session_state.generated_reply = customer_agent.generate_response(
                        f"{msg}\n\n[Minha resposta anterior foi: '{reply}'. Refine-a para ficar ainda melhor.]",
                        tone
                    )
                    st.rerun()
            st.success("Ajuste se necessário e envie para o cliente!")

    with col_c2:
        st.subheader("Analisador de Sentimento")
        st.caption("Cole avaliações de clientes (texto livre, separando cada avaliação por linha ou parágrafo).")
        reviews_input = st.text_area("Avaliações dos Clientes", height=150,
            placeholder="Ex: Amei o produto! Chegou super rápido.\nDemorou muito para chegar, mas veio bem embalado.\nQualidade excelente, recomendo!",
            help="Cole as avaliações livres. Separe cada uma por linha ou parágrafo.")

        if st.button("Analisar Sentimento 🧠"):
            if reviews_input:
                # Split by newlines, filter empties — works for both one-per-line and free text
                reviews_list = [r.strip() for r in reviews_input.replace('\r\n', '\n').split('\n') if r.strip()]
                if len(reviews_list) == 1 and reviews_list[0] == reviews_input.strip():
                    # Single block of text with no line breaks — treat as one review
                    pass
                with st.spinner("Lendo mentes..."):
                    result = customer_agent.analyze_sentiment(reviews_list)
                    st.session_state.sentiment_result = result["analysis"]
            else:
                st.warning("Insira algumas avaliações.")

        # Show result with copy button
        if "sentiment_result" in st.session_state and st.session_state.sentiment_result:
            analysis_html = f"""
            <div style="background-color: #1e1e1e; color: #e0e0e0; padding: 15px; border-radius: 8px; font-family: monospace; font-size: 14px; white-space: pre-wrap;">
            {st.session_state.sentiment_result}
            </div>
            """
            st.markdown("**Resultado da Análise:**")
            st.markdown(analysis_html, unsafe_allow_html=True)
            if st.button("📋 Copiar Análise", key="copy_sentiment"):
                st.toast("Análise copiada! (Ctrl+C no campo acima)", icon="📋")

