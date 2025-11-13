import streamlit as st
from typing import List, Dict, Any
import time

def render_chat_interface():
    """Render chat interface using Streamlit's built-in chat components"""
    
    st.header("Chat with AI Agent")
    
    # Display chat messages from history
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant"):
                st.write(message["content"])
                
                # Show metadata for assistant responses
                if "metadata" in message:
                    with st.expander("Response Details", expanded=False):
                        metadata = message["metadata"]
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Model", metadata.get("model", "N/A"))
                        
                        with col2:
                            if "usage" in metadata and metadata["usage"]:
                                total_tokens = metadata["usage"].get("total_tokens", 0)
                                st.metric("Tokens", total_tokens)
                            else:
                                st.metric("Tokens", "N/A")
                        
                        with col3:
                            st.metric("Agent", metadata.get("agent_id", "default"))
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to session state
        st.session_state.messages.append({
            "role": "user", 
            "content": prompt,
            "timestamp": time.time()
        })
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Generating response..."):
                try:
                    # Send request to API
                    response = st.session_state.api_client.send_chat_message(
                        message=prompt,
                        agent_id=st.session_state.current_agent,
                        temperature=st.session_state.temperature,
                        max_tokens=st.session_state.max_tokens,
                        model=st.session_state.selected_model
                    )
                    
                    # Display response
                    response_text = response.get("message", "Sorry, an error occurred.")
                    st.write(response_text)
                    
                    # Add assistant response to session state
                    assistant_message = {
                        "role": "assistant",
                        "content": response_text,
                        "timestamp": time.time(),
                        "metadata": {
                            "model": response.get("model"),
                            "usage": response.get("usage"),
                            "agent_id": st.session_state.current_agent,
                            "finish_reason": response.get("finish_reason")
                        }
                    }
                    
                    st.session_state.messages.append(assistant_message)
                    
                    # Limit message history
                    max_history = 50
                    if len(st.session_state.messages) > max_history:
                        st.session_state.messages = st.session_state.messages[-max_history:]
                    
                except Exception as e:
                    error_message = f"Error sending message: {e}"
                    st.error(error_message)
                    
                    # Add error message to history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_message,
                        "timestamp": time.time()
                    })

def render_chat_export():
    """Рендер функции экспорта чата"""
    if st.session_state.messages:
        st.subheader("📥 Экспорт чата")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 Скачать как JSON", use_container_width=True):
                import json
                chat_data = {
                    "messages": st.session_state.messages,
                    "exported_at": time.time(),
                    "agent_id": st.session_state.current_agent
                }
                
                st.download_button(
                    label="📄 Загрузить JSON файл",
                    data=json.dumps(chat_data, indent=2, ensure_ascii=False),
                    file_name=f"chat_export_{int(time.time())}.json",
                    mime="application/json"
                )
        
        with col2:
            if st.button("📋 Скопировать как текст", use_container_width=True):
                text_export = []
                for msg in st.session_state.messages:
                    role = "Пользователь" if msg["role"] == "user" else "Ассистент"
                    text_export.append(f"{role}: {msg['content']}")
                
                text_content = "\n\n".join(text_export)
                st.text_area("Экспорт чата:", value=text_content, height=200)