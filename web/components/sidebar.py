import streamlit as st
from typing import List, Dict, Any

def render_sidebar():
    """Render sidebar with settings"""
    
    st.header("Settings")
    
    # Connection information
    with st.expander("Connection", expanded=False):
        try:
            health = st.session_state.api_client.health_check()
            st.success(f"Connected to: {health.get('service', 'Unknown')}")
            st.info(f"Version: {health.get('version', 'Unknown')}")
            if health.get('openrouter_configured'):
                st.success("OpenRouter configured")
            else:
                st.warning("OpenRouter not configured")
        except Exception as e:
            st.error(f"Connection error: {e}")
    
    # Agent selection
    st.subheader("Agent")
    
    try:
        agents = st.session_state.api_client.get_agents()
        st.session_state.agents_list = agents
        
        if agents:
            agent_options = {agent['id']: f"{agent['name']} ({agent['id']})" for agent in agents}
            selected_agent = st.selectbox(
                "Select agent:",
                options=list(agent_options.keys()),
                format_func=lambda x: agent_options[x],
                index=0 if st.session_state.current_agent not in agent_options else list(agent_options.keys()).index(st.session_state.current_agent)
            )
            st.session_state.current_agent = selected_agent
            
            # Selected agent information
            current_agent_info = next((agent for agent in agents if agent['id'] == selected_agent), None)
            if current_agent_info:
                with st.expander("Agent Information", expanded=False):
                    st.write(f"**Name:** {current_agent_info['name']}")
                    st.write(f"**Description:** {current_agent_info.get('description', 'No description')}")
                    st.write(f"**Model:** {current_agent_info.get('model', 'Default')}")
        else:
            st.warning("No agents found")
            
    except Exception as e:
        st.error(f"Error loading agents: {e}")
    
    # Model settings
    st.subheader("Model Parameters")
    
    # Temperature
    temperature = st.slider(
        "Temperature:",
        min_value=0.0,
        max_value=2.0,
        value=st.session_state.temperature,
        step=0.1,
        help="Controls randomness of responses. Lower = more predictable, higher = more creative"
    )
    st.session_state.temperature = temperature
    
    # Maximum tokens
    max_tokens = st.slider(
        "Max tokens:",
        min_value=50,
        max_value=4000,
        value=st.session_state.max_tokens,
        step=50,
        help="Maximum response length"
    )
    st.session_state.max_tokens = max_tokens
    
    # Выбор модели (опционально)
    with st.expander("🎯 Кастомная модель", expanded=False):
        try:
            models = st.session_state.api_client.get_models()
            if models:
                model_options = ["По умолчанию"] + [model.get('id', str(model)) for model in models[:20]]  # Ограничиваем количество
                selected_model_idx = st.selectbox(
                    "Модель:",
                    options=range(len(model_options)),
                    format_func=lambda x: model_options[x],
                    index=0
                )
                
                if selected_model_idx == 0:
                    st.session_state.selected_model = None
                else:
                    st.session_state.selected_model = model_options[selected_model_idx]
            else:
                st.info("Модели не загружены")
        except Exception as e:
            st.error(f"Ошибка загрузки моделей: {e}")
    
    # Действия
    st.subheader("🗑️ Действия")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Очистить чат", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    with col2:
        if st.button("🔄 Обновить", use_container_width=True):
            # Очищаем кеш
            st.cache_data.clear()
            st.rerun()
    
    # Информация о сессии
    with st.expander("📊 Статистика сессии", expanded=False):
        st.write(f"**Сообщений в чате:** {len(st.session_state.messages)}")
        st.write(f"**Текущая температура:** {st.session_state.temperature}")
        st.write(f"**Макс. токены:** {st.session_state.max_tokens}")
        if st.session_state.selected_model:
            st.write(f"**Выбранная модель:** {st.session_state.selected_model}")
        else:
            st.write("**Модель:** По умолчанию")