import streamlit as st
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Добавляем путь к родительской директории для импорта модулей
sys.path.append(str(Path(__file__).parent.parent.parent))

from web.utils.init_session import init_session_state
from web.components.chat import render_structured_response
from web.components.sidebar import render_sidebar

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

# Убираем функцию render_sidebar, так как теперь используем импортированную

def render_chat_interface():
    """Render chat interface"""
    
    # Header with current agent info
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        st.title("💬 AI Agent Chat")
    
    with col2:
        # Quick agent selector (закомментирован для избежания конфликтов с sidebar)
        # TODO: В будущем можно раскомментировать для быстрого доступа к смене агента
        # try:
        #     agents = st.session_state.api_client.get_agents()
        #     
        #     if agents:
        #         agent_options = {agent['id']: agent['name'] for agent in agents}
        #         current_index = 0
        #         if st.session_state.current_agent in agent_options:
        #             current_index = list(agent_options.keys()).index(st.session_state.current_agent)
        #         
        #         selected_agent = st.selectbox(
        #             "🤖 Quick Agent Select:",
        #             options=list(agent_options.keys()),
        #             format_func=lambda x: agent_options[x],
        #             index=current_index,
        #             key="quick_agent_select"
        #         )
        #         
        #         if selected_agent != st.session_state.current_agent:
        #             st.session_state.current_agent = selected_agent
        #             st.rerun()
        #     else:
        #         st.warning("⚠️ No agents found")
        #         
        # except Exception as e:
        #     st.error(f"❌ Error loading agents: {e}")
        
        # Показываем информацию о текущем агенте
        try:
            agents = st.session_state.api_client.get_agents()
            current_agent_info = next((agent for agent in agents if agent['id'] == st.session_state.current_agent), None)
            if current_agent_info:
                st.info(f"🤖 Текущий агент: **{current_agent_info['name']}**")
            else:
                st.warning("⚠️ Агент не найден")
        except Exception as e:
            st.error(f"❌ Ошибка загрузки агента: {e}")
    
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
                # Check if this is a temperature comparison
                if message.get("temperature_comparison"):
                    # Display temperature comparison
                    st.markdown("### 🌡️ Temperature Comparison")
                    comparison_data = message.get("comparison_data", [])
                    
                    if comparison_data:
                        cols = st.columns(3)
                        for i, (col, response_data) in enumerate(zip(cols, comparison_data)):
                            with col:
                                temp = response_data["temperature"]
                                response = response_data["response"]
                                
                                # Header for each temperature
                                if response_data["success"]:
                                    st.markdown(f"#### 🌡️ Temperature: {temp}")
                                else:
                                    st.markdown(f"#### ❌ Temperature: {temp}")
                                
                                # Display response content
                                response_content = response.get("message", response.get("response", "No response received"))
                                
                                # Show structured data if available
                                if response.get("parsed_data") and response.get("format_valid") and response_data["success"]:
                                    response_format = response.get("response_format")
                                    agent_id = message.get("metadata", {}).get("agent_id")
                                    render_structured_response(response["parsed_data"], response_format, agent_id)
                                else:
                                    st.markdown(response_content)
                                
                                # Show metadata
                                with st.expander("ℹ️ Details", expanded=False):
                                    if response_data["success"]:
                                        col1, col2 = st.columns(2)
                                        with col1:
                                            if response.get("model"):
                                                st.write(f"**Model:** {response['model']}")
                                            tokens = response.get("usage", {}).get("total_tokens") if response.get("usage") else response.get("tokens_used")
                                            if tokens:
                                                st.write(f"**Tokens:** {tokens}")
                                        with col2:
                                            if response.get("format_valid") is not None:
                                                status = "✅ Valid" if response["format_valid"] else "❌ Invalid"
                                                st.write(f"**Format:** {status}")
                                    else:
                                        st.error("Failed to get response")
                    else:
                        st.markdown(message["content"])
                # Показываем структурированные данные если есть
                elif "parsed_data" in message and message["parsed_data"] and message.get("format_valid"):
                    response_format = None
                    if "raw_response" in message and message["raw_response"].get("response_format"):
                        response_format = message["raw_response"]["response_format"]
                    agent_id = message.get("metadata", {}).get("agent_id")
                    render_structured_response(message["parsed_data"], response_format, agent_id)
                else:
                    st.markdown(message["content"])
                
                # Show additional info for assistant messages (skip for comparisons)
                if message.get("metadata") and not message.get("temperature_comparison"):
                    metadata = message["metadata"]
                    with st.expander("ℹ️ Message Information", expanded=False):
                        # Показываем базовую информацию
                        if metadata.get("agent_id"):
                            st.write(f"**Agent ID:** {metadata['agent_id']}")
                        if metadata.get("model"):
                            st.write(f"**Model:** {metadata['model']}")
                        if metadata.get("temperature") is not None:
                            st.write(f"**Temperature:** {metadata['temperature']}")
                        if metadata.get("max_tokens"):
                            st.write(f"**Max tokens:** {metadata['max_tokens']}")
                        if metadata.get("tokens_used"):
                            st.write(f"**Tokens used:** {metadata['tokens_used']}")
                        
                        # Показываем статус валидации формата если есть
                        if metadata.get("format_valid") is not None:
                            status_icon = "✅" if metadata["format_valid"] else "❌"
                            st.write(f"**Format valid:** {status_icon}")
                        
                        # Показываем информацию об ошибке если есть
                        if metadata.get("error"):
                            st.error("⚠️ Response contains error")
                        
                        # Показываем timestamp если есть
                        if metadata.get("timestamp"):
                            st.write(f"**Timestamp:** {metadata['timestamp']}")
                        
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
            if st.session_state.temperature_comparison_mode:
                # Temperature comparison mode
                render_temperature_comparison(prompt)
            else:
                # Normal single response mode
                render_single_response(prompt)

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

def render_single_response(prompt):
    """Render single response for normal mode"""
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
            print("Sending chat request:", request_data)
            response = st.session_state.api_client.send_chat_message(request_data=request_data)
            
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
            
            # Show immediate metadata info
            with st.expander("ℹ️ Response Info", expanded=False):
                col1, col2, col3 = st.columns(3)
                with col1:
                    if response.get("model"):
                        st.write(f"**Model:** {response['model']}")
                    if response.get("agent_id"):
                        st.write(f"**Agent:** {response['agent_id']}")
                with col2:
                    if response.get("temperature") is not None:
                        st.write(f"**Temperature:** {response['temperature']}")
                    tokens = response.get("usage", {}).get("total_tokens") if response.get("usage") else response.get("tokens_used")
                    if tokens:
                        st.write(f"**Tokens:** {tokens}")
                with col3:
                    if response.get("format_valid") is not None:
                        status = "✅ Valid" if response["format_valid"] else "❌ Invalid"
                        st.write(f"**Format:** {status}")
            
            # Force rerun to display metadata immediately
            st.rerun()
                
    except Exception as e:
        error_message = f"❌ Error getting response: {e}"
        message_placeholder.error(error_message)
        
        # Store error message with basic metadata
        error_assistant_message = {
            "role": "assistant",
            "content": error_message,
            "metadata": {
                "agent_id": st.session_state.current_agent,
                "temperature": st.session_state.temperature,
                "max_tokens": st.session_state.max_tokens,
                "error": True,
                "timestamp": None
            }
        }
        st.session_state.messages.append(error_assistant_message)
        st.rerun()

def render_temperature_comparison(prompt):
    """Render temperature comparison with three different temperatures"""
    temperatures = [0.0, 0.7, 1.2]
    
    st.markdown("### 🌡️ Temperature Comparison")
    st.markdown(f"**Prompt:** {prompt}")
    
    # Create progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    responses = []
    
    # Send requests for each temperature
    for i, temp in enumerate(temperatures):
        status_text.text(f"🤔 Getting response for temperature {temp}...")
        
        try:
            # Prepare request
            request_data = {
                "message": prompt,
                "agent_id": st.session_state.current_agent,
                "temperature": temp,
                "max_tokens": st.session_state.max_tokens
            }
            
            # Add custom model if selected
            if st.session_state.selected_model:
                request_data["model"] = st.session_state.selected_model
            
            # Send request to API
            response = st.session_state.api_client.send_chat_message(request_data=request_data)
            
            responses.append({
                "temperature": temp,
                "response": response,
                "success": True
            })
            
        except Exception as e:
            responses.append({
                "temperature": temp,
                "response": {"message": f"❌ Error: {e}"},
                "success": False
            })
        
        # Update progress
        progress_bar.progress((i + 1) / len(temperatures))
    
    progress_bar.empty()
    status_text.empty()
    
    # Display comparison results
    cols = st.columns(3)
    
    for i, (col, response_data) in enumerate(zip(cols, responses)):
        with col:
            temp = response_data["temperature"]
            response = response_data["response"]
            
            # Header for each temperature
            if response_data["success"]:
                st.markdown(f"#### 🌡️ Temperature: {temp}")
            else:
                st.markdown(f"#### ❌ Temperature: {temp}")
            
            # Display response content
            response_content = response.get("message", response.get("response", "No response received"))
            
            # Show structured data if available
            if response.get("parsed_data") and response.get("format_valid") and response_data["success"]:
                response_format = response.get("response_format")
                agent_id = st.session_state.current_agent
                render_structured_response(response["parsed_data"], response_format, agent_id)
            else:
                st.markdown(response_content)
            
            # Show metadata
            with st.expander("ℹ️ Details", expanded=False):
                if response_data["success"]:
                    col1, col2 = st.columns(2)
                    with col1:
                        if response.get("model"):
                            st.write(f"**Model:** {response['model']}")
                        tokens = response.get("usage", {}).get("total_tokens") if response.get("usage") else response.get("tokens_used")
                        if tokens:
                            st.write(f"**Tokens:** {tokens}")
                    with col2:
                        if response.get("format_valid") is not None:
                            status = "✅ Valid" if response["format_valid"] else "❌ Invalid"
                            st.write(f"**Format:** {status}")
                else:
                    st.error("Failed to get response")
    
    # Store comparison result in chat history
    comparison_content = f"🔄 Temperature comparison for: {prompt}"
    assistant_message = {
        "role": "assistant",
        "content": comparison_content,
        "temperature_comparison": True,
        "comparison_data": responses,
        "metadata": {
            "agent_id": st.session_state.current_agent,
            "max_tokens": st.session_state.max_tokens,
            "comparison_mode": True,
            "temperatures": temperatures
        }
    }
    st.session_state.messages.append(assistant_message)
    
    # Force rerun to display in chat history
    st.rerun()

# Main chat interface
render_chat_interface()