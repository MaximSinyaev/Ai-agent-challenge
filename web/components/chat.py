import streamlit as st
from typing import List, Dict, Any
import time
import json

def render_raw_response_expander(raw_content: str, metadata: Dict[str, Any] = None):
    """Universal function to display raw model response in an expander"""
    with st.expander("🔍 Raw Model Response", expanded=False):
        st.markdown("**Original Response:**")
        st.code(raw_content, language="text")
        
        if metadata:
            st.markdown("**Response Metadata:**")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if "model" in metadata:
                    st.metric("Model", metadata["model"])
            
            with col2:
                if "usage" in metadata and metadata["usage"]:
                    total_tokens = metadata["usage"].get("total_tokens", 0)
                    st.metric("Tokens Used", total_tokens)
            
            with col3:
                if "finish_reason" in metadata:
                    st.metric("Finish Reason", metadata["finish_reason"])
            
            # Additional metadata in JSON format
            if len(metadata) > 3:
                st.markdown("**Full Metadata:**")
                st.json(metadata)

def render_structured_response(data: Any, response_format: dict = None, agent_id: str = None, raw_content: str = None, metadata: Dict[str, Any] = None):
    """Rendering structured response depending on its type"""
    # If response format is not JSON or not specified, show as is
    if not response_format or response_format.get('type') != 'json':
        if isinstance(data, dict):
            st.json(data)
        else:
            st.write(data)
        # Show raw response for non-JSON responses too
        if raw_content:
            render_raw_response_expander(raw_content, metadata)
        return
    
    if isinstance(data, dict):
        # If this is JSON object, show it nicely for special agents
        if "problem_analysis" in data and "solution_steps" in data:
            render_math_response(data, raw_content, metadata)
        elif "task_understanding" in data and "code" in data:
            render_code_response(data, raw_content, metadata)
        elif "data_summary" in data and "recommendations" in data:
            render_analysis_response(data, raw_content, metadata)
        elif "project_breakdown" in data and "tasks" in data:
            render_planning_response(data, raw_content, metadata)
        else:
            # General JSON rendering for unknown structures
            st.json(data)
            # Show raw response for unknown JSON structures
            if raw_content:
                render_raw_response_expander(raw_content, metadata)
    else:
        # If this is not dict, show as is
        st.write(data)
        # Show raw response for non-dict data
        if raw_content:
            render_raw_response_expander(raw_content, metadata)

def render_math_response(data: dict, raw_content: str = None, metadata: Dict[str, Any] = None):
    """Rendering mathematical assistant response"""
    st.markdown("## 📊 Mathematical Solution")
    
    # Problem analysis
    if "problem_analysis" in data:
        st.markdown("### 🔍 Problem Analysis")
        st.write(data["problem_analysis"])
    
    # Step-by-step solution
    if "solution_steps" in data:
        st.markdown("### 📝 Step-by-Step Solution")
        for i, step in enumerate(data["solution_steps"], 1):
            with st.container():
                st.markdown(f"**Step {step.get('step', i)}:** {step.get('description', '')}")
                if step.get('formula'):
                    st.latex(step['formula'])
                if step.get('calculation'):
                    st.code(step['calculation'])
    
    # Final answer
    if "final_answer" in data:
        st.markdown("### ✅ Final Answer")
        st.success(data["final_answer"])
    
    # Verification
    if "verification" in data:
        st.markdown("### 🔍 Verification")
        st.info(data["verification"])
    
    # Confidence
    if "confidence" in data:
        st.markdown("### 📈 Confidence")
        confidence = data["confidence"]
        st.progress(confidence)
        st.write(f"Confidence: {confidence:.0%}")
    
    # Show raw response if provided
    if raw_content:
        render_raw_response_expander(raw_content, metadata)

def render_code_response(data: dict, raw_content: str = None, metadata: Dict[str, Any] = None):
    """Rendering programming assistant response"""
    st.markdown("## 💻 Programming Solution")
    
    # Task understanding
    if "task_understanding" in data:
        st.markdown("### 🎯 Task Understanding")
        st.write(data["task_understanding"])
    
    # Approach
    if "approach" in data:
        st.markdown("### 🛠️ Solution Approach")
        st.write(data["approach"])
    
    # Code
    if "code" in data:
        code_data = data["code"]
        st.markdown("### 📝 Solution Code")
        
        if code_data.get("language") and code_data.get("content"):
            st.code(code_data["content"], language=code_data["language"])
        
        if code_data.get("explanation"):
            st.markdown("**Explanation:**")
            st.write(code_data["explanation"])
    
    # Test cases
    if "test_cases" in data:
        st.markdown("### 🧪 Test Cases")
        for i, test in enumerate(data["test_cases"], 1):
            with st.container():
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Test {i} - Input:**")
                    st.code(test.get("input", ""), language="text")
                with col2:
                    st.markdown(f"**Expected Output:**")
                    st.code(test.get("expected_output", ""), language="text")
    
    # Complexity
    if "complexity" in data:
        st.markdown("### ⏱️ Complexity")
        complexity = data["complexity"]
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Time Complexity", complexity.get("time", "N/A"))
        with col2:
            st.metric("Space Complexity", complexity.get("space", "N/A"))
    
    # Improvements
    if "improvements" in data:
        st.markdown("### 💡 Improvement Suggestions")
        for improvement in data["improvements"]:
            st.write(f"• {improvement}")
    
    # Show raw response if provided
    if raw_content:
        render_raw_response_expander(raw_content, metadata)

def render_analysis_response(data: dict, raw_content: str = None, metadata: Dict[str, Any] = None):
    """Rendering analytical assistant response"""
    st.markdown("## 📊 Data Analysis")
    
    # Brief description
    if "data_summary" in data:
        st.markdown("### 📄 Data Description")
        st.write(data["data_summary"])
    
    # Key insights
    if "key_insights" in data:
        st.markdown("### 🔍 Key Insights")
        for insight in data["key_insights"]:
            st.write(f"• {insight}")
    
    # Metrics
    if "metrics" in data:
        st.markdown("### 📈 Metrics")
        metrics = data["metrics"]
        
        if metrics:
            cols = st.columns(min(len(metrics), 3))
            for i, (key, metric_data) in enumerate(metrics.items()):
                with cols[i % 3]:
                    value = metric_data.get("value", "N/A")
                    trend = metric_data.get("trend", "stable")
                    trend_icon = {"up": "↗️", "down": "↘️", "stable": "➡️"}.get(trend, "")
                    st.metric(key, f"{value} {trend_icon}")
    
    # Recommendations
    if "recommendations" in data:
        st.markdown("### 💡 Recommendations")
        for rec in data["recommendations"]:
            priority = rec.get("priority", "medium")
            priority_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(priority, "⚪")
            st.write(f"{priority_color} **{rec.get('action', '')}** (Priority: {priority})")
    
    # Confidence
    if "confidence_level" in data:
        st.markdown("### 📊 Analysis Confidence")
        confidence = data["confidence_level"]
        st.progress(confidence)
        st.write(f"Confidence Level: {confidence:.0%}")
    
    # Limitations
    if "limitations" in data:
        st.markdown("### ⚠️ Analysis Limitations")
        for limitation in data["limitations"]:
            st.warning(f"• {limitation}")
    
    # Show raw response if provided
    if raw_content:
        render_raw_response_expander(raw_content, metadata)

def render_planning_response(data: dict, raw_content: str = None, metadata: Dict[str, Any] = None):
    """Rendering task planner response"""
    st.markdown("## 📋 Project Plan")
    
    # Project breakdown
    if "project_breakdown" in data:
        st.markdown("### 🎯 Project Breakdown")
        st.write(data["project_breakdown"])
    
    # Tasks
    if "tasks" in data:
        st.markdown("### 📝 Tasks")
        tasks = data["tasks"]
        
        for task in tasks:
            priority_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task.get("priority", "medium"), "⚪")
            
            with st.container():
                st.markdown(f"{priority_color} **Task {task.get('id', '')}: {task.get('title', '')}**")
                st.write(task.get("description", ""))
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"⏱️ **Time:** {task.get('estimated_time', 'Not specified')}")
                with col2:
                    if task.get("skills_required"):
                        st.write(f"🛠️ **Skills:** {', '.join(task['skills_required'])}")
                
                st.divider()
    
    # Timeline
    if "timeline" in data:
        st.markdown("### ⏰ Timeline")
        timeline = data["timeline"]
        
        st.metric("Total Time", timeline.get("total_estimated_time", "Not specified"))
        
        if timeline.get("milestones"):
            st.markdown("**Milestones:**")
            for milestone in timeline["milestones"]:
                st.write(f"📅 {milestone.get('date', '')}: {milestone.get('goal', '')}")
    
    # Resources
    if "resources_needed" in data:
        st.markdown("### 🛠️ Required Resources")
        for resource in data["resources_needed"]:
            st.write(f"• {resource}")
    
    # Risks
    if "risks" in data:
        st.markdown("### ⚠️ Risks and Mitigation")
        for risk in data["risks"]:
            st.warning(f"**Risk:** {risk.get('risk', '')}")
            st.info(f"**Mitigation:** {risk.get('mitigation', '')}")
    
    # Show raw response if provided
    if raw_content:
        render_raw_response_expander(raw_content, metadata)

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
                # Show structured data if available
                if "parsed_data" in message and message["parsed_data"] and message.get("format_valid"):
                    response_format = None
                    if "raw_response" in message and message["raw_response"].get("response_format"):
                        response_format = message["raw_response"]["response_format"]
                    agent_id = message.get("metadata", {}).get("agent_id")
                    raw_content = message["content"]
                    metadata = message.get("metadata", {})
                    render_structured_response(message["parsed_data"], response_format, agent_id, raw_content, metadata)
                else:
                    st.write(message["content"])
                
                # Show metadata and raw response
                if "raw_response" in message or "metadata" in message:
                    with st.expander("🔍 Response Details", expanded=False):
                        # Main metrics
                        if "metadata" in message:
                            metadata = message["metadata"]
                            col1, col2, col3, col4 = st.columns(4)
                            
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
                                
                            with col4:
                                if message.get("format_valid") is not None:
                                    status = "✅ Valid" if message["format_valid"] else "❌ Invalid"
                                    st.metric("Format", status)
                        
                        # Tabs for different data types
                        if "raw_response" in message:
                            tab1, tab2, tab3 = st.tabs(["📄 Raw Response", "📋 Structured Data", "⚙️ Full API Response"])
                            
                            with tab1:
                                st.markdown("**Original response text:**")
                                st.code(message["content"], language="text")
                            
                            with tab2:
                                if message.get("parsed_data"):
                                    st.markdown("**Parsed data:**")
                                    st.json(message["parsed_data"])
                                else:
                                    st.info("No structured data")
                            
                            with tab3:
                                st.markdown("**Full API response:**")
                                st.json(message["raw_response"])
    
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
                    
                    # Show structured data if available
                    if response.get("parsed_data") and response.get("format_valid"):
                        response_format = response.get("response_format")
                        agent_id = st.session_state.current_agent
                        metadata = {
                            "model": response.get("model"),
                            "usage": response.get("usage"),
                            "finish_reason": response.get("finish_reason")
                        }
                        render_structured_response(response["parsed_data"], response_format, agent_id, response_text, metadata)
                    else:
                        st.write(response_text)
                    
                    # Add assistant response to session state
                    assistant_message = {
                        "role": "assistant",
                        "content": response_text,
                        "timestamp": time.time(),
                        "raw_response": response,  # Save full API response
                        "parsed_data": response.get("parsed_data"),
                        "format_valid": response.get("format_valid"),
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
    """Render chat export functionality"""
    if st.session_state.messages:
        st.subheader("📥 Chat Export")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 Download as JSON", width="content"):
                import json
                chat_data = {
                    "messages": st.session_state.messages,
                    "exported_at": time.time(),
                    "agent_id": st.session_state.current_agent
                }
                
                st.download_button(
                    label="📄 Download JSON file",
                    data=json.dumps(chat_data, indent=2, ensure_ascii=False),
                    file_name=f"chat_export_{int(time.time())}.json",
                    mime="application/json"
                )
        
        with col2:
            if st.button("📋 Copy as text", width="content"):
                text_export = []
                for msg in st.session_state.messages:
                    role = "User" if msg["role"] == "user" else "Assistant"
                    text_export.append(f"{role}: {msg['content']}")
                
                text_content = "\n\n".join(text_export)
                st.text_area("Chat export:", value=text_content, height=200)