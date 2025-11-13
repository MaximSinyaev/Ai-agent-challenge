import streamlit as st
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Добавляем путь к родительской директории для импорта модулей
sys.path.append(str(Path(__file__).parent.parent.parent))

from web.utils.init_session import init_session_state
from web.components.chat import render_structured_response

# Page configuration
st.set_page_config(
    page_title="🤖 AI Agent Interface",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


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

def render_sidebar():
    """Render sidebar with navigation and settings"""
    
    st.header("🎛️ Control Panel")
    
    # Connection information
    with st.expander("🔗 Connection", expanded=False):
        try:
            health = st.session_state.api_client.health_check()
            st.success(f"✅ Connected to: {health.get('service', 'Unknown')}")
            st.info(f"📝 Version: {health.get('version', 'Unknown')}")
            if health.get('openrouter_configured'):
                st.success("🌐 OpenRouter configured")
            else:
                st.warning("⚠️ OpenRouter not configured")
        except Exception as e:
            st.error(f"❌ Connection error: {e}")
    
    # Agent selection
    st.subheader("🤖 Current Agent")
    
    try:
        agents = st.session_state.api_client.get_agents()
        st.session_state.agents_list = agents
        
        if agents:
            agent_options = {agent['id']: f"{agent['name']}" for agent in agents}
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
                with st.expander("ℹ️ Agent Information", expanded=False):
                    st.write(f"**Name:** {current_agent_info['name']}")
                    st.write(f"**Description:** {current_agent_info.get('description', 'No description')}")
                    st.write(f"**Model:** {current_agent_info.get('model', 'Default')}")
        else:
            st.warning("⚠️ No agents found")
            
    except Exception as e:
        st.error(f"❌ Error loading agents: {e}")
    
    # Model settings
    st.subheader("🎛️ Model Parameters")
    
    # Temperature
    temperature = st.slider(
        "🌡️ Temperature:",
        min_value=0.0,
        max_value=2.0,
        value=st.session_state.temperature,
        step=0.1,
        help="Controls response creativity. Lower = more predictable, higher = more creative"
    )
    st.session_state.temperature = temperature
    
    # Maximum tokens
    max_tokens = st.slider(
        "📝 Max tokens:",
        min_value=50,
        max_value=4000,
        value=st.session_state.max_tokens,
        step=50,
        help="Maximum response length"
    )
    st.session_state.max_tokens = max_tokens
    
    # Model selection (optional)
    with st.expander("🎯 Custom Model", expanded=False):
        try:
            models = st.session_state.api_client.get_models()
            if models:
                model_options = ["Default"] + [model.get('id', str(model)) for model in models[:20]]  # Limit count
                selected_model_idx = st.selectbox(
                    "Model:",
                    options=range(len(model_options)),
                    format_func=lambda x: model_options[x],
                    index=0
                )
                
                if selected_model_idx == 0:
                    st.session_state.selected_model = None
                else:
                    st.session_state.selected_model = model_options[selected_model_idx]
            else:
                st.info("Models not loaded")
        except Exception as e:
            st.error(f"Error loading models: {e}")
    
    # Actions
    st.subheader("⚡ Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🧹 Clear Chat", width="content", help="Delete all messages from current chat"):
            st.session_state.messages = []
            st.rerun()
    
    with col2:
        if st.button("🔄 Refresh Data", width="content", help="Refresh agents and models list"):
            # Clear cache
            st.cache_data.clear()
            st.rerun()
    
    # Session information
    with st.expander("📊 Session Statistics", expanded=False):
        st.write(f"**Messages in chat:** {len(st.session_state.messages)}")
        st.write(f"**Current temperature:** {st.session_state.temperature}")
        st.write(f"**Max tokens:** {st.session_state.max_tokens}")
        if st.session_state.selected_model:
            st.write(f"**Selected model:** {st.session_state.selected_model}")
        else:
            st.write("**Model:** Default")

def render_chat_interface():
    """Render chat interface"""
    
    # Header with current agent info
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        st.title("💬 AI Agent Chat")
    
    with col2:
        # Quick agent selector
        try:
            agents = st.session_state.api_client.get_agents()
            
            if agents:
                agent_options = {agent['id']: agent['name'] for agent in agents}
                current_index = 0
                if st.session_state.current_agent in agent_options:
                    current_index = list(agent_options.keys()).index(st.session_state.current_agent)
                
                selected_agent = st.selectbox(
                    "🤖 Quick Agent Select:",
                    options=list(agent_options.keys()),
                    format_func=lambda x: agent_options[x],
                    index=current_index,
                    key="quick_agent_select"
                )
                
                if selected_agent != st.session_state.current_agent:
                    st.session_state.current_agent = selected_agent
                    st.rerun()
            else:
                st.warning("⚠️ No agents found")
                
        except Exception as e:
            st.error(f"❌ Error loading agents: {e}")
    
    with col3:
        # Quick stats
        st.metric("Messages", len(st.session_state.messages))
        if st.session_state.temperature:
            st.metric("Temperature", f"{st.session_state.temperature:.1f}")
    
    # Chat messages
    st.subheader("📨 Message History")
    
    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.markdown(message["content"])
        else:
            with st.chat_message("assistant"):
                # Показываем структурированные данные если есть
                if "parsed_data" in message and message["parsed_data"] and message.get("format_valid"):
                    response_format = None
                    if "raw_response" in message and message["raw_response"].get("response_format"):
                        response_format = message["raw_response"]["response_format"]
                    agent_id = message.get("metadata", {}).get("agent_id")
                    render_structured_response(message["parsed_data"], response_format, agent_id)
                else:
                    st.markdown(message["content"])
                
                # Show additional info for assistant messages
                if message.get("metadata"):
                    metadata = message["metadata"]
                    with st.expander("ℹ️ Message Information", expanded=False):
                        if metadata.get("model"):
                            st.write(f"**Model:** {metadata['model']}")
                        if metadata.get("agent_id"):
                            st.write(f"**Agent ID:** {metadata['agent_id']}")
                        if metadata.get("temperature"):
                            st.write(f"**Temperature:** {metadata['temperature']}")
                        if metadata.get("tokens_used"):
                            st.write(f"**Tokens used:** {metadata['tokens_used']}")
                        if metadata.get("format_valid"):
                            st.write(f"**Format valid:** {'✅' if metadata['format_valid'] else '❌'}")
                        
                        # Показываем сырые данные если есть структурированные
                        if "parsed_data" in message and message["parsed_data"]:
                            with st.expander("🔍 Структурированные данные", expanded=False):
                                st.json(message["parsed_data"])
    
    # Chat input
    if prompt := st.chat_input("Enter your message..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            try:
                with st.spinner("🤔 Agent is thinking..."):
                    # Prepare request
                    request_data = {
                        "message": prompt,
                        "agent_id": st.session_state.current_agent,
                        "temperature": st.session_state.temperature,
                        "max_tokens": st.session_state.max_tokens
                    }
                    
                    # Add custom model if selected
                    if st.session_state.selected_model:
                        request_data["model"] = st.session_state.selected_model
                    
                    # Send request to API
                    response = st.session_state.api_client.send_chat_message(request_data)
                    
                    # Display response
                    response_content = response.get("message", response.get("response", "No response received"))
                    
                    # Показываем структурированные данные если есть
                    if response.get("parsed_data") and response.get("format_valid"):
                        response_format = response.get("response_format")
                        agent_id = st.session_state.current_agent
                        render_structured_response(response["parsed_data"], response_format, agent_id)
                    else:
                        message_placeholder.markdown(response_content)
                    
                    # Store assistant response with metadata
                    assistant_message = {
                        "role": "assistant",
                        "content": response_content,
                        "raw_response": response,  # Сохраняем полный ответ API
                        "parsed_data": response.get("parsed_data"),
                        "format_valid": response.get("format_valid"),
                        "metadata": {
                            "model": response.get("model"),
                            "agent_id": response.get("agent_id"),
                            "temperature": response.get("temperature"),
                            "tokens_used": response.get("usage", {}).get("total_tokens") if response.get("usage") else response.get("tokens_used"),
                            "format_valid": response.get("format_valid"),
                            "timestamp": response.get("timestamp")
                        }
                    }
                    st.session_state.messages.append(assistant_message)
                    
                    # Show success/warning based on format validity
                    if response.get("format_valid") is False:
                        st.warning("⚠️ Agent response does not match expected format")
                        
            except Exception as e:
                error_message = f"❌ Error getting response: {e}"
                message_placeholder.error(error_message)
                st.session_state.messages.append({"role": "assistant", "content": error_message})

# Initialize session state
init_session_state()

# Check backend connection
try:
    health = st.session_state.api_client.health_check()
    if not health.get('status') == 'healthy':
        st.error("🚨 Backend unavailable. Make sure the server is running on port 8000")
        st.stop()
except Exception as e:
    st.error(f"🚨 Cannot connect to backend: {e}")
    st.markdown("""
    ### 🔧 Connection Issues?
    
    1. **Make sure the backend server is running:**
       ```bash
       ./run_server.sh
       ```
    
    2. **Check that the server is available on port 8000:**
       ```bash
       curl http://localhost:8000/health
       ```
    
    3. **Restart the server if needed**
    """)
    st.stop()

# Sidebar
with st.sidebar:
    render_sidebar()

# Main chat interface
render_chat_interface()