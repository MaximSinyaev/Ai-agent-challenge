import streamlit as st
import json
from typing import Dict, Any

def render_settings_page():
    """Application settings page"""
    
    st.set_page_config(
        page_title="Settings - AI Agent Interface", 
        page_icon="⚙️",
        layout="wide"
    )
    
    st.title("Settings")
    st.markdown("---")
    
    # API client initialization
    try:
        from web.utils.api_client import APIClient
        from web.utils.config import WebConfig
        
        config = WebConfig()
        api_client = APIClient(config.backend_url)
        
    except Exception as e:
        st.error(f"❌ Initialization error: {e}")
        st.stop()
    
    # Settings tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Connection", "Interface", "AI Models", "Data"])
    
    # Connection settings
    with tab1:
        st.header("Connection Settings")
        
        # Current settings
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Current settings")
            st.code(f"""
Backend URL: {config.backend_url}
Local backend: {config.is_backend_local}
Cache timeout: {config.cache_ttl_agents}s (agents)
Cache timeout: {config.cache_ttl_models}s (models)
            """)
        
        with col2:
            st.subheader("🔍 Connection check")
            
            if st.button("🔄 Check connection", width="content"):
                with st.spinner("Checking connection..."):
                    try:
                        health = api_client.health_check()
                        st.success("✅ Connection successful!")
                        st.json(health)
                    except Exception as e:
                        st.error(f"❌ Connection error: {e}")
        
        # Backend URL change
        st.markdown("---")
        st.subheader("🔧 Change Backend URL")
        
        new_backend_url = st.text_input(
            "Backend URL:",
            value=config.backend_url,
            help="Backend server URL (e.g.: http://localhost:8000)"
        )
        
        if st.button("💾 Save URL"):
            # In a real application, we would save to settings here
            st.success("✅ URL saved (restart application to apply)")
    
    # Interface settings
    with tab2:
        st.header("🎛️ Interface settings")
        
        # Theme (placeholder)
        st.subheader("🎨 Appearance")
        theme = st.selectbox(
            "Theme:",
            ["Auto", "Light", "Dark"],
            help="Appearance theme (managed by Streamlit)"
        )
        
        # Chat settings
        st.subheader("💬 Chat settings")
        
        col1, col2 = st.columns(2)
        
        with col1:
            max_history = st.number_input(
                "Max messages in history:",
                min_value=10,
                max_value=200,
                value=config.max_history_length,
                help="Maximum number of messages to store"
            )
        
        with col2:
            auto_scroll = st.checkbox(
                "Auto-scroll chat",
                value=True,
                help="Automatically scroll to new messages"
            )
        
        # Experimental features
        st.subheader("🧪 Experimental features")
        
        col1, col2 = st.columns(2)
        
        with col1:
            enable_voice = st.checkbox(
                "Voice input",
                value=False,
                disabled=True,
                help="Feature in development"
            )
        
        with col2:
            enable_images = st.checkbox(
                "Image support", 
                value=False,
                disabled=True,
                help="Feature in development"
            )
    
    # AI models settings
    with tab3:
        st.header("🤖 AI Models Settings")
        
        # Default parameters
        st.subheader("🎯 Default Parameters")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            default_temperature = st.slider(
                "Default temperature:",
                min_value=0.0,
                max_value=2.0,
                value=config.default_temperature,
                step=0.1
            )
        
        with col2:
            default_max_tokens = st.number_input(
                "Default max tokens:",
                min_value=50,
                max_value=4000,
                value=config.default_max_tokens
            )
        
        with col3:
            timeout = st.number_input(
                "Request timeout (sec):",
                min_value=5,
                max_value=120,
                value=30
            )
        
        # Available models
        st.subheader("📋 Available Models")
        
        try:
            models = api_client.get_models()
            if models:
                st.success(f"✅ {len(models)} models available")
                
                # Show first few models
                for model in models[:5]:
                    with st.expander(f"🤖 {model.get('name', model.get('id'))}", expanded=False):
                        st.json(model)
                
                if len(models) > 5:
                    st.info(f"... and {len(models) - 5} more models. Full list available on 'Models' page")
            else:
                st.warning("⚠️ Models not found")
        except Exception as e:
            st.error(f"❌ Error loading models: {e}")
    
    # Data management
    with tab4:
        st.header("📊 Data Management")
        
        # Statistics
        st.subheader("📈 Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Count messages in current session
            message_count = len(st.session_state.get('messages', []))
            st.metric("Messages in session", message_count)
        
        with col2:
            # Count agents
            try:
                agents = api_client.get_agents()
                agent_count = len(agents) if agents else 0
            except:
                agent_count = 0
            st.metric("Total agents", agent_count)
        
        with col3:
            st.metric("Cache size", "N/A")
        
        with col4:
            st.metric("Uptime", "N/A")
        
        # Data cleanup
        st.subheader("🗑️ Data Cleanup")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear chat history", type="secondary", width="content"):
                if 'messages' in st.session_state:
                    st.session_state.messages = []
                st.success("✅ Chat history cleared")
                st.rerun()
        
        with col2:
            if st.button("🔄 Clear cache", type="secondary", width="content"):
                st.cache_data.clear()
                st.success("✅ Cache cleared")
                st.rerun()
        
        # Data export
        st.subheader("📥 Data Export")
        
        export_data = {
            "session_messages": st.session_state.get('messages', []),
            "current_agent": st.session_state.get('current_agent', 'default'),
            "settings": {
                "temperature": st.session_state.get('temperature', 0.7),
                "max_tokens": st.session_state.get('max_tokens', 1000)
            }
        }
        
        st.download_button(
            "💾 Download session data (JSON)",
            data=json.dumps(export_data, indent=2, ensure_ascii=False),
            file_name=f"session_export_{int(st.session_state.get('session_start', 0))}.json",
            mime="application/json",
            width="content"
        )

if __name__ == "__main__":
    render_settings_page()