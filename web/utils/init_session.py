import streamlit as st
from web.utils.api_client import APIClient
from web.utils.config import WebConfig

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
        st.session_state.api_client = APIClient(config.backend_url, api_version="v1")
    
    if 'temperature' not in st.session_state:
        st.session_state.temperature = 0.7
    
    if 'max_tokens' not in st.session_state:
        st.session_state.max_tokens = 1000
    
    if 'selected_model' not in st.session_state:
        st.session_state.selected_model = None
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "chat"