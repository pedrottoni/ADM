import streamlit as st
from core.llm_client import llm_client
from core.config import Config

def render_settings_page():

    if not llm_client.enabled:
        st.warning("🤖 A conexão com IA está **desativada**. Ative-a no botão 🤖 IA no topo da página para usar os recursos de IA.")
        st.divider()

    # 1. Select Provider
    provider = st.selectbox(
        "Provedor de IA",
        ["gemini", "openrouter", "nvidia"],
        index=["gemini", "openrouter", "nvidia"].index(llm_client.provider)
    )
    
    # Update global client if changed
    if provider != llm_client.provider:
        llm_client.update_settings(provider, None)
        Config.set_llm_settings(provider, llm_client.model_name)
        st.toast(f"Provedor alterado para {provider}!")

    # 2. Show masked key check and Edit Form
    key_map = {
        "gemini": Config.GOOGLE_API_KEY,
        "openrouter": Config.OPENROUTER_API_KEY,
        "nvidia": Config.NVIDIA_API_KEY
    }
    
    current_key = key_map.get(provider)
    
    col_k1, col_k2 = st.columns([4, 1])
    with col_k1:
        if current_key:
            masked_key = f"{current_key[:4]}...{current_key[-4:]}" if len(current_key) > 8 else "****"
            st.info(f"🔑 Chave API detectada: `{masked_key}`")
        else:
            st.error("❌ Chave API não encontrada no arquivo .env!")
            
    with col_k2:
        if st.button("✏️ Editar Chave", use_container_width=True):
            st.session_state[f"edit_key_{provider}"] = not st.session_state.get(f"edit_key_{provider}", False)

    # Key editing form
    if st.session_state.get(f"edit_key_{provider}", False):
        with st.container(border=True):
            new_key = st.text_input(f"Nova Chave API para {provider}", type="password", help="Cole a nova chave aqui.")
            
            c1, c2 = st.columns(2)
            if c1.button("Salvar Chave 💾", type="primary", use_container_width=True):
                if new_key:
                    success = Config.set_api_key(provider, new_key)
                    if success:
                        st.success("Chave salva com sucesso!")
                        # Force reload of LLM client so it grabs the new key
                        llm_client.setup_provider() 
                        st.session_state[f"edit_key_{provider}"] = False
                        st.rerun()
                    else:
                        st.error("Erro ao salvar a chave.")
                else:
                    st.warning("Insira uma chave válida.")
            
            if c2.button("Cancelar ❌", use_container_width=True):
                st.session_state[f"edit_key_{provider}"] = False
                st.rerun()

    # 3. Model Selection
    available_models = llm_client.get_available_models()
    current_model = llm_client.model_name or available_models[0] if available_models else None
    model_index = available_models.index(current_model) if current_model and current_model in available_models else 0
    selected_model = st.selectbox(
        "Modelo",
        available_models,
        index=model_index
    )

    # Update model if changed
    if selected_model and selected_model != llm_client.model_name:
        llm_client.update_settings(provider, selected_model)
        Config.set_llm_settings(provider, selected_model)

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

    # ── Admin / Dev Tools (moved from sidebar) ──
    st.divider()
    with st.expander("🛠️ Ferramentas de Admin / Dev"):
        st.caption("Use com cuidado — ações administrativas do sistema.")
        if st.button("🔄 Recarregar Módulos e Limpar Cache"):
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

            st.toast("Sistema recarregado com sucesso!", icon="✅")
            st.rerun()
