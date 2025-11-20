import streamlit as st
from typing import List, Dict, Any
import time
import json


def render_structured_response(data: Any, response_format: dict = None, metadata: Dict[str, Any] = None):
    """Rendering structured response depending on its type"""
    # If response format is not JSON or not specified, show as is
    if not response_format or response_format.get('type') != 'json':
        if isinstance(data, dict):
            st.json(data)
        else:
            st.write(data)
        # Show raw response for non-JSON responses too
        return
    
    if isinstance(data, dict):
        # Special handling for orchestration steps
        if "orchestration_steps" in data:
            render_orchestration_response(data, metadata)
        # If this is JSON object, show it nicely for special agents
        elif "problem_analysis" in data and "solution_steps" in data:
            render_math_response(data, metadata)
        elif "task_understanding" in data and "code" in data:
            render_code_response(data, metadata)
        elif "data_summary" in data and "recommendations" in data:
            render_analysis_response(data, metadata)
        elif "project_breakdown" in data and "tasks" in data:
            render_planning_response(data, metadata)
        elif "status" in data and "message" in data:
            render_technical_spec_response(data, metadata)
        else:
            # General JSON rendering for unknown structures
            st.json(data)
    else:
        # If this is not dict, show as is
        st.write(data)

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


def render_technical_spec_response(data: dict, raw_content: str = None, metadata: Dict[str, Any] = None):
    """Rendering technical specification planner response"""
    status = data.get("status", "collecting")
    
    if status == "collecting":
        st.markdown("## 🔄 Gathering Requirements")
        st.info(data.get("message", "Collecting information..."))
        st.markdown("💡 **The assistant is still gathering requirements. Continue the conversation to provide more details.**")
    elif status == "complete":
        st.markdown("## 📋 Technical Specification")
        st.success(data.get("message", "Technical specification generated."))
        
        final_spec = data.get("final_spec", {})
        
        # Title
        if "title" in final_spec:
            st.markdown(f"### 📄 {final_spec['title']}")
        
        # Overview
        if "overview" in final_spec:
            st.markdown("### 🎯 Overview")
            st.write(final_spec["overview"])
        
        # Functional Requirements
        if "functional_requirements" in final_spec:
            st.markdown("### ✅ Functional Requirements")
            for req in final_spec["functional_requirements"]:
                st.write(f"• {req}")
        
        # Non-Functional Requirements
        if "non_functional_requirements" in final_spec:
            st.markdown("### ⚙️ Non-Functional Requirements")
            for req in final_spec["non_functional_requirements"]:
                st.write(f"• {req}")
        
        # Constraints
        if "constraints" in final_spec:
            st.markdown("### 🚧 Constraints")
            for constraint in final_spec["constraints"]:
                st.write(f"• {constraint}")
        
        # Deliverables
        if "deliverables" in final_spec:
            st.markdown("### 📦 Deliverables")
            for deliverable in final_spec["deliverables"]:
                st.write(f"• {deliverable}")
        
        # Timeline
        if "timeline" in final_spec:
            st.markdown("### ⏰ Timeline")
            st.metric("Estimated Timeline", final_spec["timeline"])
        
        # Risks
        if "risks" in final_spec:
            st.markdown("### ⚠️ Risks")
            for risk in final_spec["risks"]:
                st.warning(f"• {risk}")
    else:
        st.error("Unknown response status")


def render_orchestration_response(data: dict, metadata: Dict[str, Any] = None):
    """Rendering subagent orchestration response"""
    st.markdown("## 🔄 Subagent Orchestration Results")

    # Show orchestration steps
    if "orchestration_steps" in data:
        st.markdown("### 📋 Orchestration Steps")

        for step in data["orchestration_steps"]:
            step_num = step.get("step", "?")
            agent_name = step.get("agent", "Unknown")

            with st.expander(f"Step {step_num}: {agent_name}", expanded=True):
                step_output = step.get("output", {})

                if agent_name == "task_solver":
                    st.markdown("#### 🎯 Task Solver Output")
                    if "task_type" in step_output:
                        st.write(f"**Task Type:** {step_output['task_type']}")
                    if "solution" in step_output:
                        st.write(f"**Solution:** {step_output['solution']}")
                    if "key_data" in step_output:
                        st.info(f"**Key Data:** {step_output['key_data']}")
                    if "confidence" in step_output:
                        st.write(f"**Confidence:** {step_output['confidence']:.2f}")
                    if "processing_hints" in step_output:
                        st.write("**Processing Hints:**")
                        for hint in step_output["processing_hints"]:
                            st.write(f"• {hint}")

                elif agent_name == "result_processor":
                    st.markdown("#### ✅ Result Processor Output")
                    if "validation_status" in step_output:
                        status = step_output["validation_status"]
                        status_icon = {
                            "valid": "✅",
                            "invalid": "❌",
                            "needs_revision": "⚠️"
                        }.get(status, "❓")
                        st.write(f"**Validation Status:** {status_icon} {status}")

                    if "refined_result" in step_output:
                        st.success(f"**Refined Result:** {step_output['refined_result']}")

                    if "improvements_made" in step_output:
                        st.write("**Improvements Made:**")
                        for improvement in step_output["improvements_made"]:
                            st.write(f"• {improvement}")

                    if "final_assessment" in step_output:
                        st.info(f"**Final Assessment:** {step_output['final_assessment']}")

                    if "quality_score" in step_output:
                        quality = step_output["quality_score"]
                        st.progress(quality)
                        st.write(f"**Quality Score:** {quality:.2f}")

    # Show final result
    if "message" in data:
        st.markdown("### 🎉 Final Result")
        try:
            # Try to parse the message as JSON for better display
            final_data = json.loads(data["message"])
            if isinstance(final_data, dict):
                # Render based on the structure of the final result
                if "validation_status" in final_data and "refined_result" in final_data:
                    # This is the result processor output
                    render_result_processor_final(final_data)
                else:
                    st.json(final_data)
            else:
                st.write(data["message"])
        except json.JSONDecodeError:
            st.write(data["message"])

    # Show usage information
    if "usage" in data:
        st.markdown("### 📊 Usage Statistics")
        usage = data["usage"]

        if "task_solver" in usage:
            with st.expander("Task Solver Usage", expanded=False):
                ts_usage = usage["task_solver"]
                if ts_usage:
                    st.write(f"**Tokens:** {ts_usage.get('total_tokens', 'N/A')}")

        if "result_processor" in usage:
            with st.expander("Result Processor Usage", expanded=False):
                rp_usage = usage["result_processor"]
                if rp_usage:
                    st.write(f"**Tokens:** {rp_usage.get('total_tokens', 'N/A')}")


def render_result_processor_final(data: dict):
    """Render the final result from result processor"""
    col1, col2 = st.columns(2)

    with col1:
        status = data.get("validation_status", "unknown")
        status_icon = {
            "valid": "✅",
            "invalid": "❌",
            "needs_revision": "⚠️"
        }.get(status, "❓")
        st.metric("Validation Status", f"{status_icon} {status}")

    with col2:
        quality = data.get("quality_score", 0)
        st.metric("Quality Score", f"{quality:.2f}")

    if "refined_result" in data:
        st.markdown("#### ✨ Refined Result")
        st.success(data["refined_result"])

    if "final_assessment" in data:
        st.markdown("#### 📋 Final Assessment")
        st.info(data["final_assessment"])

    if "improvements_made" in data and data["improvements_made"]:
        st.markdown("#### 🔧 Improvements Made")
        for improvement in data["improvements_made"]:
            st.write(f"• {improvement}")
