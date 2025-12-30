import streamlit as st
from core.llm_client import llm_client
from core.config import Config

def render_settings_page():
    st.header("⚙️ Configurações de IA")
    
    # 1. Select Provider
    provider = st.selectbox(
        "Provedor de IA",
        ["gemini", "openrouter", "nvidia"],
        index=["gemini", "openrouter", "nvidia"].index(llm_client.provider)
    )
    
    # Update global client if changed
    if provider != llm_client.provider:
        llm_client.update_settings(provider, None)
        st.toast(f"Provedor alterado para {provider}!")

    # 2. Show masked key check
    key_map = {
        "gemini": Config.GOOGLE_API_KEY,
        "openrouter": Config.OPENROUTER_API_KEY,
        "nvidia": Config.NVIDIA_API_KEY
    }
    
    current_key = key_map.get(provider)
    if current_key:
        masked_key = f"{current_key[:4]}...{current_key[-4:]}" if len(current_key) > 8 else "****"
        st.info(f"🔑 Chave API detectada: `{masked_key}`")
    else:
        st.error("❌ Chave API não encontrada no arquivo .env!")

    # 3. Model Selection
    available_models = llm_client.get_available_models()
    selected_model = st.selectbox(
        "Modelo", 
        available_models,
        index=0 if available_models else None
    )
    
    # Update model if changed
    if selected_model and selected_model != llm_client.model_name:
        llm_client.update_settings(provider, selected_model)

    # 4. Connectivity Test
    st.divider()
    st.subheader("Verificação de Conectividade")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.caption(f"Testando conexão com **{provider}** usando modelo **{selected_model}**")
    
    with col2:
        if st.button("🔄 Verificar Conexão"):
            with st.spinner("Conectando aos servidores..."):
                response = llm_client.check_connection()
                if response:
                    st.success("✅ Conectado com sucesso!")
                    st.balloons()
                else:
                    st.error("❌ Falha na conexão. Verifique sua chave ou internet.")

    # Show live response for verification
    if st.session_state.get("last_test_response"):
        with st.expander("Ver detalhes da resposta"):
            st.code(st.session_state.last_test_response)
