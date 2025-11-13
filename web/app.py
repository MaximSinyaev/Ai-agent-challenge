import streamlit as st
import sys
import os
from pathlib import Path
import asyncio
from typing import Dict, List, Optional

# Добавляем путь к родительской директории для импорта модулей backend
sys.path.append(str(Path(__file__).parent.parent))

from web.utils.api_client import APIClient
from web.utils.config import WebConfig
from web.components.chat import render_chat_interface
from web.components.sidebar import render_sidebar
from web.components.agent_manager import render_agent_manager

# Page configuration
st.set_page_config(
    page_title="AI Agent Interface",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Инициализация состояния сессии
def init_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'current_agent' not in st.session_state:
        st.session_state.current_agent = "default"
    
    if 'agents_list' not in st.session_state:
        st.session_state.agents_list = []
    
    if 'api_client' not in st.session_state:
        config = WebConfig()
        st.session_state.api_client = APIClient(config.backend_url)
    
    if 'temperature' not in st.session_state:
        st.session_state.temperature = 0.7
    
    if 'max_tokens' not in st.session_state:
        st.session_state.max_tokens = 1000
    
    if 'selected_model' not in st.session_state:
        st.session_state.selected_model = None

@st.cache_data(ttl=60)
def load_agents():
    """Load agents list with caching"""
    try:
        return st.session_state.api_client.get_agents()
    except Exception as e:
        st.error(f"Error loading agents: {e}")
        return []

@st.cache_data(ttl=300)
def load_models():
    """Load available models with caching"""
    try:
        return st.session_state.api_client.get_models()
    except Exception as e:
        st.error(f"Error loading models: {e}")
        return []

def main():
    """Main application function"""
    init_session_state()
    
    # Application header
    st.title("AI Agent Interface")
    st.markdown("---")
    
    # Check backend connection
    try:
        health = st.session_state.api_client.health_check()
        if not health.get('status') == 'healthy':
            st.error("Backend unavailable. Make sure the server is running on port 8000")
            st.stop()
    except Exception as e:
        st.error(f"Cannot connect to backend: {e}")
        st.stop()
    
    # Sidebar
    with st.sidebar:
        render_sidebar()
    
    # Main content
    tab1, tab2, tab3 = st.tabs(["Chat", "Agent Management", "Statistics"])
    
    with tab1:
        render_chat_interface()
    
    with tab2:
        render_agent_manager()
    
    with tab3:
        st.header("Usage Statistics")
        st.info("Statistics will be added in future versions")
        
        # Statistics placeholder
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Messages", len(st.session_state.messages))
        with col2:
            st.metric("Active Agents", len(st.session_state.agents_list))
        with col3:
            st.metric("Current Agent", st.session_state.current_agent)

if __name__ == "__main__":
    main()