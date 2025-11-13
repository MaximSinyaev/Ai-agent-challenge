import streamlit as st
import sys
from pathlib import Path

# Добавляем путь к родительской директории для импорта модулей backend
sys.path.append(str(Path(__file__).parent.parent))

# Page configuration
st.set_page_config(
    page_title="🤖 AI Agent Interface",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application function - перенаправляет на страницы навигации"""
    
    st.title("🤖 AI Agent Interface")
    
    st.markdown("""
    ## 👋 Welcome to the AI Agent Interface!
    
    Use the navigation on the left to switch between sections:
    
    - **🏠 Chat** - Communicate with AI agents
    - **🤖 Agents** - Manage agents (create, delete, configure)
    - **📊 Statistics** - Usage statistics
    - **🔧 Models** - Model management
    - **⚙️ Settings** - System configuration
    
    ### 🚀 Quick Start
    
    1. Go to the **🏠 Chat** section to start chatting
    2. Use the **🤖 Agents** section to create your own agents
    3. Configure parameters in the sidebar
    
    ---
    *AI Agent Challenge Project - Intelligent agents for solving various tasks*
    """)
    
    # Проверка соединения с backend
    try:
        from web.utils.api_client import APIClient
        from web.utils.config import WebConfig
        
        config = WebConfig()
        api_client = APIClient(config.backend_url, api_version="v1")
        health = api_client.health_check()
        
        if health.get('status') == 'healthy':
            st.success(f"✅ Backend connected: {health.get('service', 'Unknown')} v{health.get('version', 'Unknown')}")
            
            if health.get('openrouter_configured'):
                st.success("🌐 OpenRouter configured and ready")
            else:
                st.warning("⚠️ OpenRouter not configured - some features may be unavailable")
        else:
            st.error("🚨 Backend unavailable")
            
    except Exception as e:
        st.error(f"🚨 Backend connection error: {e}")
        
        st.markdown("""
        ### 🔧 Troubleshooting
        
        If backend is unavailable:
        
        1. Make sure the server is running:
           ```bash
           ./run_server.sh
           ```
        
        2. Check server availability:
           ```bash
           curl http://localhost:8000/health
           ```
        
        3. Make sure port 8000 is not blocked
        """)

if __name__ == "__main__":
    main()