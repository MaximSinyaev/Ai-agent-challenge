import streamlit as st

def render_sidebar():
    """Render sidebar with navigation and settings"""
    
    st.header("🎛️ Control Panel")
    # NOTE: Navigation in the top block (App / Models / Settings / Statistics). Removing duplication here.
    
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
            
            # Automatically apply agent settings when switching
            if st.session_state.current_agent != selected_agent:
                st.session_state.current_agent = selected_agent
                # Apply new agent settings
                new_agent_info = next((agent for agent in agents if agent['id'] == selected_agent), None)
                if new_agent_info:
                    if 'temperature' in new_agent_info:
                        st.session_state.temperature = new_agent_info['temperature']
                    if 'max_tokens' in new_agent_info:
                        st.session_state.max_tokens = new_agent_info['max_tokens']
            
            # Selected agent information
            current_agent_info = next((agent for agent in agents if agent['id'] == selected_agent), None)
            if current_agent_info:
                with st.expander("ℹ️ Agent Information", expanded=False):
                    st.write(f"**Name:** {current_agent_info['name']}")
                    st.write(f"**Description:** {current_agent_info.get('description', 'No description')}")
                    st.write(f"**Model:** {current_agent_info.get('model', 'Default')}")
                    
                    # Show agent parameters
                    if 'temperature' in current_agent_info:
                        st.write(f"**Agent Temperature:** {current_agent_info['temperature']}")
                    if 'max_tokens' in current_agent_info:
                        st.write(f"**Agent Max Tokens:** {current_agent_info['max_tokens']}")
                    
                    # Button to apply agent settings
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("📥 Apply Agent Settings", help="Apply temperature and tokens from agent settings"):
                            if 'temperature' in current_agent_info:
                                st.session_state.temperature = current_agent_info['temperature']
                            if 'max_tokens' in current_agent_info:
                                st.session_state.max_tokens = current_agent_info['max_tokens']
                            st.rerun()
        else:
            st.warning("⚠️ Agents not found")
            
    except Exception as e:
        st.error(f"❌ Error loading agents: {e}")
    
    # Agent management (show only if agents page is selected)
    if st.session_state.current_page == "agents":
        st.divider()
        render_agent_management()
    
    # Model settings
    st.subheader("🎛️ Model Parameters")
    
    # Temperature comparison mode
    temperature_comparison = st.checkbox(
        "🔄 Compare Temperatures",
        value=st.session_state.temperature_comparison_mode,
        help="Send the same message with different temperatures (0, 0.7, 1.2) for comparison"
    )
    st.session_state.temperature_comparison_mode = temperature_comparison
    
    # Temperature
    temperature = st.slider(
        "🌡️ Temperature:",
        min_value=0.0,
        max_value=2.0,
        value=st.session_state.temperature,
        step=0.1,
        help="Controls response creativity. Lower = more predictable, higher = more creative",
        disabled=temperature_comparison  # Disable when comparison mode is on
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
    
    # Custom model selection (optional)
    with st.expander("🎯 Custom Model", expanded=False):
        try:
            models = st.session_state.api_client.get_models()
            if models:
                model_options = ["Default"] + [model.get('id', str(model)) for model in models[:20]]  # Limit quantity
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
        if st.button("🔄 Refresh Data", width="content", help="Refresh agents and modules list"):
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

def render_agent_management():
    """Render compact agent management in sidebar"""
    
    st.subheader("🛠️ Agent Management")
    
    # Management tabs
    tab1, tab2 = st.tabs(["➕ Create", "🗑️ Delete"])
    
    with tab1:
        render_create_agent_compact()
    
    with tab2:
        render_delete_agent_compact()

def render_create_agent_compact():
    """Compact form for creating agent"""
    
    with st.form("create_agent_compact"):
        st.markdown("**New Agent**")
        
        name = st.text_input("Name*:", placeholder="Python Expert")
        description = st.text_area("Description:", placeholder="Brief description", height=60)
        system_prompt = st.text_area("System Prompt*:", 
                                   placeholder="You are an experienced developer...", 
                                   height=100)
        
        col1, col2 = st.columns(2)
        with col1:
            temperature = st.slider("Temperature:", 0.0, 2.0, 0.7, 0.1)
        with col2:
            max_tokens = st.number_input("Tokens:", 50, 4000, 1000, 50)
        
        submit = st.form_submit_button("🚀 Create", width="content")
        
        if submit and name.strip() and system_prompt.strip():
            try:
                config = {
                    "name": name.strip(),
                    "description": description.strip() or None,
                    "system_prompt": system_prompt.strip(),
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
                
                with st.spinner("Creating..."):
                    response = st.session_state.api_client.create_agent(config)
                
                st.success(f"✅ Agent '{name}' created!")
                st.cache_data.clear()
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Error: {e}")
        elif submit:
            st.error("❌ Fill in required fields")

def render_delete_agent_compact():
    """Compact form for deleting agent"""
    
    try:
        agents = st.session_state.api_client.get_agents()
        deletable_agents = [agent for agent in agents if agent['id'] != 'default']
        
        if deletable_agents:
            agent_options = {agent['id']: f"{agent['name']}" for agent in deletable_agents}
            
            selected_agent_id = st.selectbox(
                "Agent to delete:",
                options=list(agent_options.keys()),
                format_func=lambda x: f"🗑️ {agent_options[x]}"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                confirm = st.text_input("Enter ID:", placeholder=selected_agent_id)
            
            with col2:
                st.write("")  # Spacing
                if st.button("🗑️ Delete", 
                           disabled=(confirm != selected_agent_id),
                           width="content"):
                    try:
                        st.session_state.api_client.delete_agent(selected_agent_id)
                        
                        if st.session_state.current_agent == selected_agent_id:
                            st.session_state.current_agent = "default"
                        
                        st.success("✅ Agent deleted!")
                        st.cache_data.clear()
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
        else:
            st.info("📭 No agents to delete")
            
    except Exception as e:
        st.error(f"❌ Error: {e}")