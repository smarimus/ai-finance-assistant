# Goals planning tab for the Streamlit web interface
# Handle goal creation, tracking, and projection visualizations

import streamlit as st
from typing import Dict, Any, List, Optional
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import json
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Import goal planning components
from src.agents.goal_agent import GoalPlanningAgent
from src.utils.portfolio_calc import FinancialCalculator

def render_goals_tab(workflow, session_state: Dict[str, Any]):
    """
    Render the goals planning tab with real goal planning functionality
    
    Features:
    - Goal creation and definition
    - Progress tracking and visualization
    - Projection scenarios with interactive charts
    - Actionable recommendations and milestones
    """
    
    st.header("🎯 Financial Goals Planning")
    
    # Initialize goal agent from workflow if available
    if "goal_agent" not in session_state:
        if workflow and hasattr(workflow, 'agents') and 'goal_planning' in workflow.agents:
            session_state["goal_agent"] = workflow.agents['goal_planning']
            st.success("✅ **Goal Planning Active** - Real AI agent loaded!")
        else:
            # Fallback: Create real goal agent directly
            try:
                from langchain_openai import ChatOpenAI
                from src.agents.goal_agent import GoalPlanningAgent
                from src.utils.portfolio_calc import FinancialCalculator
                import os
                
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key and api_key != "your_openai_api_key_here":
                    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1, max_tokens=1000)
                    financial_calculator = FinancialCalculator()
                    session_state["goal_agent"] = GoalPlanningAgent(llm, financial_calculator)
                    st.success("✅ **Goal Planning Active** - Real AI agent created!")
                else:
                    st.error("❌ OpenAI API key required for goal planning functionality")
                    return
            except Exception as e:
                st.error(f"❌ Failed to initialize goal planning: {str(e)}")
                return
    
    # Initialize session state variables
    if "investment_goals" not in session_state:
        session_state["investment_goals"] = []
    
    if "user_profile" not in session_state:
        session_state["user_profile"] = {}
    
    if "financial_calculator" not in session_state:
        session_state["financial_calculator"] = FinancialCalculator()
    
    # Main content area
    render_user_profile_setup(session_state)
    
    st.divider()
    
    # Unified goal management interface
    render_unified_goal_interface(session_state)
    
    st.divider()
    
    # Goals overview and tracking
    if session_state.get("investment_goals"):
        render_existing_goals_section(session_state)
    else:
        st.info("📝 Create your first financial goal above to see detailed analysis and tracking.")

def render_user_profile_setup(session_state: Dict[str, Any]):
    """Enhanced user profile setup with better performance"""
    
    with st.expander("� User Profile Setup", expanded=not bool(session_state.get("user_profile"))):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Name", value=session_state.get("user_profile", {}).get("name", ""))
            age = st.number_input("Age", min_value=18, max_value=100, 
                                value=session_state.get("user_profile", {}).get("age", 30))
            annual_income = st.number_input("Annual Income ($)", min_value=0, step=1000,
                                          value=session_state.get("user_profile", {}).get("annual_income", 50000))
            monthly_expenses = st.number_input("Monthly Expenses ($)", min_value=0, step=100,
                                             value=session_state.get("user_profile", {}).get("monthly_expenses", 3000))
        
        with col2:
            current_savings = st.number_input("Current Savings ($)", min_value=0, step=500,
                                            value=session_state.get("user_profile", {}).get("current_savings", 5000))
            debt_amount = st.number_input("Total Debt ($)", min_value=0, step=500,
                                        value=session_state.get("user_profile", {}).get("debt_amount", 0))
            debt_payment = st.number_input("Monthly Debt Payment ($)", min_value=0, step=50,
                                         value=session_state.get("user_profile", {}).get("debt_payment", 0))
            risk_tolerance = st.selectbox("Risk Tolerance", 
                                        ["conservative", "moderate", "aggressive"],
                                        index=["conservative", "moderate", "aggressive"].index(
                                            session_state.get("user_profile", {}).get("risk_tolerance", "moderate")))
        
        retirement_age = st.slider("Target Retirement Age", 50, 80, 
                                 value=session_state.get("user_profile", {}).get("retirement_age", 65))
        
        if st.button("💾 Save Profile", type="primary", use_container_width=True):
            session_state["user_profile"] = {
                "name": name,
                "age": age,
                "annual_income": annual_income,
                "monthly_expenses": monthly_expenses,
                "current_savings": current_savings,
                "debt_amount": debt_amount,
                "debt_payment": debt_payment,
                "risk_tolerance": risk_tolerance,
                "retirement_age": retirement_age,
                "life_expectancy": 85
            }
            st.success("✅ Profile saved successfully!")
            st.rerun()
        
        # Quick profile templates
        st.markdown("**🚀 Quick Start Templates:**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("👨‍💼 Young Professional", use_container_width=True):
                session_state["user_profile"] = {
                    "name": "Young Professional",
                    "age": 25,
                    "annual_income": 65000,
                    "monthly_expenses": 3500,
                    "current_savings": 8000,
                    "debt_amount": 15000,
                    "debt_payment": 400,
                    "risk_tolerance": "moderate",
                    "retirement_age": 65,
                    "life_expectancy": 85
                }
                st.rerun()
        
        with col2:
            if st.button("👩‍💼 Mid-Career", use_container_width=True):
                session_state["user_profile"] = {
                    "name": "Mid-Career Professional",
                    "age": 40,
                    "annual_income": 95000,
                    "monthly_expenses": 6000,
                    "current_savings": 45000,
                    "debt_amount": 25000,
                    "debt_payment": 800,
                    "risk_tolerance": "moderate",
                    "retirement_age": 65,
                    "life_expectancy": 85
                }
                st.rerun()
        
        with col3:
            if st.button("👴 Pre-Retirement", use_container_width=True):
                session_state["user_profile"] = {
                    "name": "Pre-Retirement",
                    "age": 55,
                    "annual_income": 110000,
                    "monthly_expenses": 7000,
                    "current_savings": 350000,
                    "debt_amount": 45000,
                    "debt_payment": 1200,
                    "risk_tolerance": "conservative",
                    "retirement_age": 65,
                    "life_expectancy": 85
                }
                st.rerun()

def render_unified_goal_interface(session_state: Dict[str, Any]):
    """Unified goal creation and analysis interface with clear purpose separation"""
    
    # Tab-based interface for clarity
    tab1, tab2 = st.tabs(["➕ Create New Goal", "🧠 Goal Analysis & Advice"])
    
    with tab1:
        st.markdown("### Create and Plan Your Financial Goals")
        st.caption("Describe a financial goal and get AI-powered analysis with projections")
        
        # Check if there's existing analysis to display
        existing_analysis = session_state.get("last_goal_analysis")
        if existing_analysis:
            st.info("💡 Showing your most recent goal analysis. Create a new goal below to replace it.")
            with st.expander("🔍 Previous Analysis Results", expanded=True):
                st.markdown(f"**Goal:** {existing_analysis['goal_query']}")
                st.markdown("**Analysis:**")
                result = existing_analysis["result"]
                if isinstance(result, dict) and "agent_response" in result:
                    st.write(result["agent_response"])
                
                # Action buttons for the existing analysis
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("💾 Save This Goal", key="save_existing_analysis"):
                        logger.info("=== SAVE EXISTING ANALYSIS BUTTON CLICKED ===")
                        goal_data = extract_goal_from_analysis(
                            existing_analysis["goal_query"], 
                            existing_analysis["result"], 
                            session_state
                        )
                        if goal_data:
                            if "investment_goals" not in session_state:
                                session_state["investment_goals"] = []
                            session_state["investment_goals"].append(goal_data)
                            st.success("✅ Previous goal saved successfully!")
                            logger.info(f"Previous goal saved! Total goals: {len(session_state['investment_goals'])}")
                        else:
                            st.error("❌ Could not save previous goal")
                
                with col2:
                    if st.button("📈 View Projections", key="show_existing_projections"):
                        display_goal_projections(
                            existing_analysis["goal_query"], 
                            existing_analysis["analysis_state"], 
                            session_state
                        )
                
                with col3:
                    if st.button("🗑️ Clear Analysis", key="clear_existing_analysis"):
                        del session_state["last_goal_analysis"]
                        st.rerun()
        
        col1, col2 = st.columns([2, 1])
        
        # Check if a template was selected
        template_value = ""
        if "selected_template" in session_state:
            template_value = session_state["selected_template"]
            del session_state["selected_template"]  # Clear after use
        
        with col1:
            goal_query = st.text_area(
                "Describe Your Financial Goal",
                placeholder="Examples:\n• I want to retire at age 65 with $1M\n• Save $50,000 for a house down payment in 5 years\n• Build a $25,000 emergency fund\n• Save for my child's college education",
                height=100,
                key="new_goal_query"
                # Removed value parameter that might be causing issues
            )
        
        with col2:
            st.markdown("**Quick Goal Templates**")
            
            templates = [
                ("🏠 House Down Payment", "Save $60,000 for a house down payment in 5 years"),
                ("🎓 Education Fund", "Save for college education starting in 10 years"),
                ("🚨 Emergency Fund", "Build a 6-month emergency fund"),
                ("🏖️ Retirement", "Plan for retirement at age 65"),
                ("💰 Investment Goal", "Save $100,000 for investments in 10 years")
            ]
            
            for emoji_title, template_text in templates:
                if st.button(emoji_title, key=f"template_{emoji_title}"):
                    session_state["selected_template"] = template_text
                    st.rerun()
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Debug: Show what we received
            st.write("**Debug Info:**")
            st.write(f"- Text area value: '{goal_query}'")
            st.write(f"- Text area length: {len(goal_query) if goal_query else 0}")
            
            analyze_button = st.button("🎯 Analyze & Create Goal", key="analyze_new_goal", type="primary")
            
            if analyze_button:
                st.write(f"**Button clicked!**")
                if goal_query and len(goal_query.strip()) > 0:
                    st.write(f"✅ Processing goal: {goal_query}")
                    with st.spinner("Analyzing your goal and creating projections..."):
                        analyze_new_goal(goal_query.strip(), session_state)
                else:
                    st.error("❌ Please enter a goal description above before clicking Analyze & Create Goal")
                    st.write(f"Goal query was: '{goal_query}'")
            
        with col2:
            if st.button("💾 Quick Add", key="quick_add_goal"):
                if goal_query and len(goal_query.strip()) > 0:
                    quick_add_goal(goal_query.strip(), session_state)
                else:
                    st.error("❌ Please enter a goal description first")
    
    with tab2:
        st.markdown("### AI Financial Planning Advice")
        st.caption("Get personalized insights about your existing goals and financial strategy")
        
        col1, col2 = st.columns([3, 1])
        
        # Check if a quick analysis was selected
        quick_analysis_value = ""
        if "selected_quick_analysis" in session_state:
            quick_analysis_value = session_state["selected_quick_analysis"]
            del session_state["selected_quick_analysis"]  # Clear after use
        
        with col1:
            analysis_query = st.text_input(
                "Ask about your goals or financial planning",
                placeholder="e.g., 'How am I progressing towards retirement?' or 'Should I prioritize paying off debt or saving for a house?'",
                key="goal_analysis_query"
                # Removed value parameter that might be causing issues
            )
        
        with col2:
            analyze_button = st.button("🔍 Get Advice", key="analyze_goals", type="primary")
        
        # Debug info for advice section
        st.write("**Debug Info:**")
        st.write(f"- Analysis query: '{analysis_query}'")
        st.write(f"- Query length: {len(analysis_query) if analysis_query else 0}")
        
        # Handle analysis request
        if analyze_button:
            st.write("**Get Advice button clicked!**")
            if analysis_query and len(analysis_query.strip()) > 0:
                st.write(f"✅ Processing advice request: {analysis_query}")
                perform_goal_analysis(analysis_query.strip(), session_state)
            else:
                st.error("❌ Please enter a question above before clicking Get Advice")
                st.write(f"Analysis query was: '{analysis_query}'")

def render_goal_creation_section(session_state: Dict[str, Any]):
    """Render goal creation interface"""
    st.subheader("➕ Create New Goal")
    
    col1, col2 = st.columns([2, 1])
    
    # Check if a template was selected
    template_value = ""
    if "selected_template" in session_state:
        template_value = session_state["selected_template"]
        del session_state["selected_template"]  # Clear after use
    
    with col1:
        goal_query = st.text_area(
            "Describe Your Financial Goal",
            placeholder="Examples:\n• I want to retire at age 65 with $1M\n• Save $50,000 for a house down payment in 5 years\n• Build a $25,000 emergency fund\n• Save for my child's college education",
            height=100,
            key="new_goal_query",
            value=template_value
        )
    
    with col2:
        st.markdown("**Quick Goal Templates**")
        
        templates = [
            ("🏠 House Down Payment", "Save $60,000 for a house down payment in 5 years"),
            ("🎓 Education Fund", "Save for college education starting in 10 years"),
            ("🚨 Emergency Fund", "Build a 6-month emergency fund"),
            ("🏖️ Retirement", "Plan for retirement at age 65"),
            ("💰 Investment Goal", "Save $100,000 for investments in 10 years")
        ]
        
        for emoji_title, template_text in templates:
            if st.button(emoji_title, key=f"template_{emoji_title}"):
                session_state["selected_template"] = template_text
                st.rerun()
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.button("🎯 Analyze Goal", key="analyze_new_goal", type="primary") and goal_query:
            with st.spinner("Analyzing your goal and creating projections..."):
                analyze_new_goal(goal_query, session_state)
    
    with col2:
        if st.button("📋 Quick Add", key="quick_add_goal") and goal_query:
            quick_add_goal(goal_query, session_state)

def render_existing_goals_section(session_state: Dict[str, Any]):
    """Render existing goals management"""
    st.subheader("📋 Your Goals")
    
    goals = session_state.get("investment_goals", [])
    
    if not goals:
        st.info("🎯 No goals created yet. Create your first goal above to start planning for your financial future!")
        return
    
    # Goals overview metrics
    total_target = sum(goal.get("target_amount", 0) for goal in goals)
    total_current = sum(goal.get("current_balance", 0) for goal in goals)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Goals", len(goals))
    
    with col2:
        st.metric("Target Amount", f"${total_target:,.0f}")
    
    with col3:
        progress = (total_current / total_target * 100) if total_target > 0 else 0
        st.metric("Overall Progress", f"{progress:.1f}%")
    
    # Individual goal cards
    for i, goal in enumerate(goals):
        render_goal_card(goal, i, session_state)

def render_goal_card(goal: Dict[str, Any], index: int, session_state: Dict[str, Any]):
    """Render individual goal card"""
    goal_type = goal.get("goal_type", "investment")
    target_amount = goal.get("target_amount", 0)
    current_balance = goal.get("current_balance", 0)
    timeline_years = goal.get("timeline_years", 0)
    monthly_target = goal.get("monthly_target", 0)
    
    # Calculate progress
    progress = (current_balance / target_amount * 100) if target_amount > 0 else 0
    
    # Goal type emoji mapping
    goal_emojis = {
        'retirement': '🏖️',
        'emergency_fund': '🚨',
        'house': '🏠',
        'education': '🎓',
        'investment': '💰'
    }
    
    emoji = goal_emojis.get(goal_type, '🎯')
    
    with st.container():
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            st.markdown(f"**{emoji} {goal_type.title().replace('_', ' ')} Goal**")
            st.progress(progress / 100)
            st.caption(f"${current_balance:,.0f} / ${target_amount:,.0f} ({progress:.1f}%)")
        
        with col2:
            st.metric("Timeline", f"{timeline_years} years")
        
        with col3:
            st.metric("Monthly Target", f"${monthly_target:,.0f}")
        
        with col4:
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("📊", key=f"view_goal_{index}", help="View Details"):
                    session_state[f"show_goal_details_{index}"] = True
                    st.rerun()
            with col_b:
                if st.button("🗑️", key=f"delete_goal_{index}", help="Delete Goal"):
                    session_state["investment_goals"].pop(index)
                    st.rerun()
        
        # Show detailed view if requested
        if session_state.get(f"show_goal_details_{index}", False):
            with st.expander("📊 Goal Details", expanded=True):
                render_goal_details(goal, index, session_state)
                if st.button("✖️ Close Details", key=f"close_details_{index}"):
                    session_state[f"show_goal_details_{index}"] = False
                    st.rerun()

def render_goal_details(goal: Dict[str, Any], index: int, session_state: Dict[str, Any]):
    """Render detailed goal information and projections"""
    
    # Update current balance
    col1, col2 = st.columns(2)
    
    with col1:
        new_balance = st.number_input(
            "Update Current Balance ($)",
            min_value=0,
            value=goal.get("current_balance", 0),
            step=100,
            key=f"update_balance_{index}",
            format="%d"
        )
    
    with col2:
        if st.button("💾 Update Balance", key=f"save_balance_{index}"):
            session_state["investment_goals"][index]["current_balance"] = new_balance
            session_state["investment_goals"][index]["last_updated"] = datetime.now().isoformat()
            st.success("Balance updated!")
            st.rerun()
    
    # Show projections if available
    if goal.get("projections"):
        st.subheader("📈 Projection Chart")
        create_goal_projection_chart(goal)
    
    # Show milestones if available
    if goal.get("milestones"):
        st.subheader("🎯 Milestones")
        render_goal_milestones(goal, index, session_state)

def render_goal_milestones(goal: Dict[str, Any], index: int, session_state: Dict[str, Any]):
    """Render goal milestones tracking"""
    milestones = goal.get("milestones", [])
    current_balance = goal.get("current_balance", 0)
    
    for i, milestone in enumerate(milestones):
        target_balance = milestone["target_balance"]
        achieved = current_balance >= target_balance
        
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            icon = "✅" if achieved else "⏳"
            st.write(f"{icon} **{milestone['percent']}% Milestone**")
            st.caption(f"Target: ${target_balance:,.0f}")
        
        with col2:
            st.write(f"Year {milestone['target_year']}")
        
        with col3:
            if achieved and not milestone.get("achieved"):
                if st.button("🎉 Mark Achieved", key=f"achieve_{index}_{i}"):
                    session_state["investment_goals"][index]["milestones"][i]["achieved"] = True
                    session_state["investment_goals"][index]["milestones"][i]["achieved_date"] = datetime.now().isoformat()
                    st.balloons()
                    st.rerun()

def render_goal_analysis_section(session_state: Dict[str, Any]):
    """Render goal analysis and insights"""
    st.subheader("🧠 AI Goal Analysis")
    
    col1, col2 = st.columns([3, 1])
    
    # Check if a quick analysis was selected
    quick_analysis_value = ""
    if "selected_quick_analysis" in session_state:
        quick_analysis_value = session_state["selected_quick_analysis"]
        del session_state["selected_quick_analysis"]  # Clear after use
    
    with col1:
        analysis_query = st.text_input(
            "Ask about your goals or financial planning",
            placeholder="e.g., 'How am I progressing towards retirement?' or 'Should I prioritize paying off debt or saving for a house?'",
            key="goal_analysis_query",
            value=quick_analysis_value
        )
    
    with col2:
        analyze_button = st.button("🔍 Analyze", key="analyze_goals", type="primary")
    
    # Quick analysis buttons
    st.write("**Quick Analysis:**")
    quick_analyses = [
        "Review my retirement progress",
        "Prioritize my multiple goals",
        "Assess my savings rate",
        "Optimize my goal timelines",
        "Emergency fund strategy"
    ]
    
    cols = st.columns(len(quick_analyses))
    for i, analysis in enumerate(quick_analyses):
        with cols[i]:
            if st.button(analysis, key=f"quick_analysis_{i}"):
                session_state["selected_quick_analysis"] = analysis
                st.rerun()
    
    # Handle analysis request
    target_query = None
    if analyze_button and analysis_query:
        target_query = analysis_query
    
    if target_query:
        perform_goal_analysis(target_query, session_state)

def analyze_new_goal(goal_query: str, session_state: Dict[str, Any]):
    """Analyze a new goal using the real goal planning agent"""
    try:
        # Display analysis header
        st.subheader("🎯 Goal Analysis Results")
        
        # Prepare comprehensive state for goal agent
        analysis_state = {
            "user_query": goal_query,
            "portfolio_data": session_state.get("portfolio_data", {}),
            "investment_goals": session_state.get("investment_goals", []),
            "user_profile": session_state.get("user_profile", {}),
            "current_savings": session_state.get("user_profile", {}).get("current_savings", 0),
            "annual_income": session_state.get("user_profile", {}).get("annual_income", 0),
            "monthly_expenses": session_state.get("user_profile", {}).get("monthly_expenses", 0),
            "age": session_state.get("user_profile", {}).get("age", 30),
            "risk_tolerance": session_state.get("user_profile", {}).get("risk_tolerance", "moderate")
        }
        
        # Execute real goal analysis
        with st.spinner("🧠 AI analyzing your goal and creating projections..."):
            result = session_state["goal_agent"].execute(analysis_state)
        
        # Store analysis results in session state for persistence
        session_state["last_goal_analysis"] = {
            "goal_query": goal_query,
            "result": result,
            "analysis_state": analysis_state,
            "timestamp": datetime.now().isoformat()
        }
        
        # Display comprehensive results
        if isinstance(result, dict) and "agent_response" in result:
            st.markdown("### 📊 AI Goal Analysis")
            st.write(result["agent_response"])
            
            # Display sources if available
            if result.get("sources"):
                with st.expander("📚 Analysis Sources", expanded=False):
                    for source in result["sources"]:
                        st.write(f"• {source}")
            
            # Show confidence level
            if result.get("confidence"):
                confidence = result["confidence"]
                if confidence >= 0.8:
                    st.success(f"🎯 High Confidence Analysis ({confidence:.1%})")
                elif confidence >= 0.6:
                    st.info(f"📊 Good Analysis ({confidence:.1%})")
                else:
                    st.warning(f"⚠️ Preliminary Analysis ({confidence:.1%}) - Consider providing more details")
        else:
            # Handle simple string response
            st.write(result)
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 Save This Goal", key="save_analyzed_goal"):
                logger.info("=== SAVE GOAL BUTTON CLICKED ===")
                logger.info(f"goal_query: '{goal_query}'")
                logger.info(f"result available: {'result' in locals()}")
                logger.info(f"result type: {type(result) if 'result' in locals() else 'N/A'}")
                logger.info(f"session_state keys: {list(session_state.keys())}")
                
                st.write("**Save This Goal button clicked!**")
                st.write(f"**Debug - Available variables:**")
                st.write(f"- goal_query: '{goal_query}'")
                st.write(f"- result type: {type(result) if 'result' in locals() else 'result not found'}")
                st.write(f"- session_state keys: {list(session_state.keys())}")
                
                # Ensure investment_goals exists
                if "investment_goals" not in session_state:
                    session_state["investment_goals"] = []
                    logger.info("Initialized investment_goals in session_state")
                    st.write("**Debug - Initialized investment_goals**")
                
                # Extract goal information and save
                logger.info("Calling extract_goal_from_analysis...")
                goal_data = extract_goal_from_analysis(goal_query, result, session_state)
                logger.info(f"extract_goal_from_analysis returned: {goal_data}")
                
                st.write(f"**Debug - Goal data extracted:** {goal_data}")
                if goal_data:
                    session_state["investment_goals"].append(goal_data)
                    logger.info(f"Goal saved! Total goals: {len(session_state['investment_goals'])}")
                    st.success("✅ Goal saved successfully!")
                    st.write(f"**Total goals saved:** {len(session_state.get('investment_goals', []))}")
                    # Show the goal that was saved
                    with st.expander("View Saved Goal"):
                        st.json(goal_data)
                    # Don't rerun - keep the analysis visible
                    st.info("💡 Your goal has been saved! You can continue to view projections or create more goals.")
                else:
                    logger.error("Failed to extract goal data")
                    st.error("❌ Could not extract goal data")
                    st.write(f"**Debug - Failed extraction for goal_query:** '{goal_query}'")
                    st.write(f"**Debug - Result type:** {type(result) if result else 'None'}")
                    st.write(f"**Debug - Result content:** {result}")
        
        with col2:
            # Check button state and display projections immediately
            show_projections_clicked = st.button("📈 View Projections", key="show_projections")
            
            if show_projections_clicked:
                st.success("✅ Projections Loading...")
                st.info("📍 Scroll down to see your goal projections!")
                st.write("**View Projections button clicked!**")
                st.write(f"**Debug - goal_query:** '{goal_query}'")
                st.write(f"**Debug - analysis_state:** {analysis_state}")
            
            # Display projections immediately if button was clicked OR if previously shown
            if show_projections_clicked or session_state.get("show_projections", False):
                if show_projections_clicked:
                    # Store state for future renders
                    session_state["show_projections"] = True
                    session_state["projections_data"] = {
                        "goal_query": goal_query,
                        "analysis_state": analysis_state
                    }
                
                # Get data from current click or stored state
                if show_projections_clicked:
                    proj_goal_query = goal_query
                    proj_analysis_state = analysis_state
                else:
                    projections_data = session_state.get("projections_data", {})
                    proj_goal_query = projections_data.get("goal_query", "")
                    proj_analysis_state = projections_data.get("analysis_state", {})
                
                # Show the projections with a very visible header
                st.markdown("---")
                st.markdown("# 📈 GOAL PROJECTIONS")
                st.success("🎯 Projections are displayed below - scroll down if needed!")
                
                # Add a container to make it more visible
                with st.container():
                    st.markdown("### 📊 Financial Projections Analysis")
                    display_goal_projections(proj_goal_query, proj_analysis_state, session_state)
                
                st.markdown("---")
                # Add hide button
                if st.button("🙈 Hide Projections", key="hide_projections"):
                    session_state["show_projections"] = False
                    if "projections_data" in session_state:
                        del session_state["projections_data"]
        
        with col3:
            if st.button("🔄 Refine Goal", key="refine_goal"):
                st.info("💡 Use the text area above to modify your goal description and analyze again")
        
    except Exception as e:
        st.error(f"❌ Error analyzing goal: {str(e)}")
        st.info("Please try rephrasing your goal or check that your user profile is complete.")

def quick_add_goal(goal_query: str, session_state: Dict[str, Any]):
    """Quick add a basic goal without full analysis"""
    goal = {
        "goal_id": f"goal_{int(datetime.now().timestamp())}",
        "goal_type": "investment",
        "description": goal_query,
        "target_amount": 50000,  # Default
        "timeline_years": 5,     # Default
        "current_balance": 0,
        "monthly_target": 833,   # Default calculation
        "created_date": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat()
    }
    
    session_state["investment_goals"].append(goal)
    st.success("✅ Goal added! Use the analyze feature for detailed planning.")
    st.rerun()

def perform_goal_analysis(query: str, session_state: Dict[str, Any]):
    """Perform goal analysis using the real goal planning agent"""
    try:
        # Display analysis header
        st.subheader("🧠 AI Financial Planning Advice")
        
        # Prepare comprehensive state for goal agent
        analysis_state = {
            "user_query": query,
            "portfolio_data": session_state.get("portfolio_data", {}),
            "investment_goals": session_state.get("investment_goals", []),
            "user_profile": session_state.get("user_profile", {}),
            "current_savings": session_state.get("user_profile", {}).get("current_savings", 0),
            "annual_income": session_state.get("user_profile", {}).get("annual_income", 0),
            "monthly_expenses": session_state.get("user_profile", {}).get("monthly_expenses", 0),
            "age": session_state.get("user_profile", {}).get("age", 30),
            "risk_tolerance": session_state.get("user_profile", {}).get("risk_tolerance", "moderate"),
            "existing_goals_count": len(session_state.get("investment_goals", [])),
            "analysis_type": "advice"  # Indicates this is for advice, not goal creation
        }
        
        # Execute real goal analysis
        with st.spinner("🧠 AI analyzing your financial situation and goals..."):
            result = session_state["goal_agent"].execute(analysis_state)
        
        # Display comprehensive results
        if isinstance(result, dict) and "agent_response" in result:
            st.markdown("### 💡 Personalized Financial Advice")
            st.write(result["agent_response"])
            
            # Display sources if available
            if result.get("sources"):
                with st.expander("📚 Analysis Sources", expanded=False):
                    for source in result["sources"]:
                        st.write(f"• {source}")
            
            # Show confidence level
            if result.get("confidence"):
                confidence = result["confidence"]
                if confidence >= 0.8:
                    st.success(f"🎯 High Confidence Advice ({confidence:.1%})")
                elif confidence >= 0.6:
                    st.info(f"📊 Good Advice ({confidence:.1%})")
                else:
                    st.warning(f"⚠️ General Advice ({confidence:.1%}) - Consider completing your profile for better insights")
        else:
            # Handle simple string response
            st.write(result)
        
        # Additional action buttons for advice
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📋 Get Action Plan", key="get_action_plan"):
                st.info("💡 **Next Steps**: Based on this advice, consider creating specific goals using the 'Create New Goal' tab above.")
        
        with col2:
            if st.button("🎯 Create Goal", key="create_goal_from_advice"):
                st.info("💡 **Tip**: Switch to the 'Create New Goal' tab to turn this advice into a trackable goal.")
        
    except Exception as e:
        st.error(f"❌ Error getting financial advice: {str(e)}")
        st.info("Please try rephrasing your question or check that your user profile is complete.")

def extract_goal_from_analysis(goal_query: str, analysis_result: Dict[str, Any], session_state: Dict[str, Any]) -> Dict[str, Any]:
    """Extract goal data from analysis result to save as a trackable goal"""
    try:
        logger.info("=== EXTRACT_GOAL_FROM_ANALYSIS CALLED ===")
        logger.info(f"goal_query: '{goal_query}'")
        logger.info(f"analysis_result type: {type(analysis_result)}")
        logger.info(f"analysis_result: {analysis_result}")
        
        st.write(f"**DEBUG extract_goal_from_analysis called:**")
        st.write(f"- goal_query: '{goal_query}'")
        st.write(f"- analysis_result type: {type(analysis_result)}")
        st.write(f"- analysis_result keys: {list(analysis_result.keys()) if isinstance(analysis_result, dict) else 'Not a dict'}")
        
        # Create a structured goal from the analysis
        goal_data = {
            "id": f"goal_{int(datetime.now().timestamp())}",
            "name": goal_query[:50] + "..." if len(goal_query) > 50 else goal_query,
            "description": goal_query,
            "type": "custom",
            "target_amount": 50000,  # Default - could be extracted from analysis
            "target_date": (datetime.now() + timedelta(days=1825)).strftime("%Y-%m-%d"),  # 5 years default
            "current_amount": 0,
            "monthly_contribution": 800,  # Default - could be calculated
            "priority": "medium",
            "created_date": datetime.now().strftime("%Y-%m-%d"),
            "analysis_result": str(analysis_result.get("agent_response", ""))[:200] + "..." if analysis_result else "",
            "status": "active"
        }
        
        logger.info(f"goal_data created: {goal_data}")
        st.write(f"**DEBUG goal_data created:** {goal_data}")
        return goal_data
    except Exception as e:
        logger.error(f"Error in extract_goal_from_analysis: {str(e)}")
        logger.error(f"Exception details: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        st.error(f"Error extracting goal data: {str(e)}")
        st.write(f"**DEBUG Exception details:** {e}")
        import traceback
        st.write(f"**DEBUG Traceback:** {traceback.format_exc()}")
        return None

def display_goal_projections(goal_query: str, analysis_state: Dict[str, Any], session_state: Dict[str, Any]):
    """Display goal projections and scenarios"""
    st.subheader("📈 Goal Projections")
    
    # Use financial calculator for projections
    calc = session_state.get("financial_calculator")
    if not calc:
        from src.utils.portfolio_calc import FinancialCalculator
        calc = FinancialCalculator()
    
    # Sample projection scenarios
    scenarios = {
        "Conservative (4% return)": {"return_rate": 0.04, "monthly": 800},
        "Moderate (7% return)": {"return_rate": 0.07, "monthly": 700},
        "Aggressive (10% return)": {"return_rate": 0.10, "monthly": 600}
    }
    
    st.write("**Sample projections based on different scenarios:**")
    
    logger.info("=== DISPLAYING PROJECTIONS ===")
    
    for scenario_name, params in scenarios.items():
        logger.info(f"Processing scenario: {scenario_name}")
        logger.info(f"Params: {params}")
        
        try:
            # Calculate 5-year projection using future value of annuity
            monthly_payment = params["monthly"]
            annual_rate = params["return_rate"]
            monthly_rate = annual_rate / 12
            months = 5 * 12
            
            logger.info(f"Calculation inputs: monthly_payment={monthly_payment}, annual_rate={annual_rate}, months={months}")
            
            # Use future_value_annuity for regular monthly payments
            future_value = calc.future_value_annuity(
                payment=monthly_payment,
                rate=monthly_rate,
                periods=months
            )
            
            logger.info(f"Calculated future_value: {future_value}")
            
            # Debug output for user
            st.write(f"**Debug {scenario_name}:**")
            st.write(f"- Monthly payment: ${monthly_payment}")
            st.write(f"- Annual rate: {annual_rate * 100}%")
            st.write(f"- Future value: ${future_value:,.2f}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(scenario_name, f"${future_value:,.0f}")
            with col2:
                st.metric("Monthly Required", f"${params['monthly']:,.0f}")
            with col3:
                st.metric("Total Contributions", f"${params['monthly'] * 60:,.0f}")
                
        except Exception as e:
            logger.error(f"Error calculating projection for {scenario_name}: {str(e)}")
            logger.error(f"Exception details: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            st.error(f"❌ Could not calculate projection for {scenario_name}: {str(e)}")
            st.write(f"**Debug error details:** {e}")
    
    logger.info("=== PROJECTIONS COMPLETE ===")
    st.info("💡 **Note**: These are sample projections. Complete your profile for personalized calculations.")

def display_goal_scenarios(scenarios: Dict[str, Any]):
    """Display goal scenarios in a formatted way"""
    st.subheader("📊 Scenario Analysis")
    
    scenarios_data = scenarios.get("scenarios", {})
    
    if not scenarios_data:
        return
    
    # Create comparison table
    comparison_data = []
    for scenario_name, scenario in scenarios_data.items():
        if scenario_name == 'feasibility':
            continue
        
        comparison_data.append({
            "Scenario": scenario_name.title(),
            "Annual Return": f"{scenario['annual_return']:.1%}",
            "Monthly Savings": f"${scenario['monthly_savings_required']:,.0f}",
            "Final Balance": f"${scenario['final_balance']:,.0f}",
            "Goal Achieved": "✅" if scenario['goal_achieved'] else "❌"
        })
    
    df = pd.DataFrame(comparison_data)
    st.table(df)

def display_action_plan(action_plan: List[Dict[str, Any]]):
    """Display action plan in an organized way"""
    st.subheader("📋 Action Plan")
    
    for step in action_plan:
        with st.expander(f"{step['category']}: {step['title']}", expanded=True):
            st.write(step['description'])
            
            st.write("**Actions:**")
            for action in step['actions']:
                st.write(f"• {action}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Timeline:** {step['timeline']}")
            with col2:
                priority_colors = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}
                priority_color = priority_colors.get(step['priority'], '⚪')
                st.write(f"**Priority:** {priority_color} {step['priority'].title()}")

def display_goal_visualizations(viz_data: Dict[str, Any]):
    """Display goal visualization charts"""
    st.subheader("📈 Goal Projections")
    
    projection_charts = viz_data.get("projection_charts", {})
    
    if not projection_charts:
        return
    
    # Create projection chart
    fig = go.Figure()
    
    for scenario_name, data in projection_charts.items():
        fig.add_trace(go.Scatter(
            x=data['years'],
            y=data['balances'],
            mode='lines+markers',
            name=f"{scenario_name.title()} Scenario",
            line=dict(width=3)
        ))
        
        # Add contributions line
        fig.add_trace(go.Scatter(
            x=data['years'],
            y=data['contributions'],
            mode='lines',
            name=f"{scenario_name.title()} Contributions",
            line=dict(dash='dash', width=2),
            opacity=0.7
        ))
    
    fig.update_layout(
        title="Goal Projection Scenarios",
        xaxis_title="Years",
        yaxis_title="Amount ($)",
        height=500,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_goal_projection_chart(goal: Dict[str, Any]):
    """Create projection chart for individual goal"""
    projections = goal.get("projections", [])
    
    if not projections:
        st.warning("No projection data available for this goal.")
        return
    
    # Create chart
    fig = go.Figure()
    
    years = [p['year'] for p in projections]
    balances = [p['balance'] for p in projections]
    contributions = [p['cumulative_contributions'] for p in projections]
    
    fig.add_trace(go.Scatter(
        x=years,
        y=balances,
        mode='lines+markers',
        name='Projected Balance',
        line=dict(color='blue', width=3),
        fill='tonexty'
    ))
    
    fig.add_trace(go.Scatter(
        x=years,
        y=contributions,
        mode='lines',
        name='Total Contributions',
        line=dict(color='green', width=2, dash='dash')
    ))
    
    # Add target line
    target_amount = goal.get("target_amount", 0)
    if target_amount > 0:
        fig.add_hline(
            y=target_amount,
            line_dash="dot",
            line_color="red",
            annotation_text=f"Target: ${target_amount:,.0f}"
        )
    
    fig.update_layout(
        title=f"{goal.get('goal_type', 'Goal').title()} Projection",
        xaxis_title="Years",
        yaxis_title="Amount ($)",
        height=400,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def save_goal_from_analysis(result: Dict[str, Any], session_state: Dict[str, Any]):
    """Save goal from analysis results"""
    goal_details = result.get("goal_details", {})
    scenarios = result.get("goal_scenarios", {})
    tracking_data = result.get("tracking_data", {})
    
    # Create goal from analysis
    goal = {
        "goal_id": tracking_data.get("goal_id", f"goal_{int(datetime.now().timestamp())}"),
        "goal_type": goal_details.get("goal_type", "investment"),
        "description": goal_details.get("original_query", ""),
        "target_amount": scenarios.get("target_amount", 0),
        "timeline_years": scenarios.get("timeline_years", 0),
        "current_balance": scenarios.get("current_savings", 0),
        "monthly_target": tracking_data.get("monthly_target", 0),
        "projections": tracking_data.get("projections", []),
        "milestones": tracking_data.get("milestones", []),
        "scenarios": scenarios.get("scenarios", {}),
        "created_date": datetime.now().isoformat(),
        "last_updated": datetime.now().isoformat()
    }
    
    session_state["investment_goals"].append(goal)

def create_mock_goal_agent():
    """Create mock goal agent when real one isn't available"""
    class MockGoalAgent:
        def execute(self, state):
            query = state.get("user_query", "")
            
            response = f"""🎯 **Goal Planning Analysis for**: *{query[:50]}...*

📊 **Goal Planning Features Available:**
• Comprehensive goal analysis with multiple scenarios
• Retirement planning with detailed projections  
• Emergency fund and major purchase planning
• Actionable monthly savings targets
• Progress tracking with milestone checkpoints

**📈 Sample Goal Analysis:**
Based on your request, here's a preliminary analysis:

**Conservative Scenario (4% return)**:
• Monthly savings needed: $850
• Timeline: 5 years
• Total contributions: $51,000
• Final balance: $55,500

**Moderate Scenario (7% return)**:
• Monthly savings needed: $780
• Timeline: 5 years  
• Total contributions: $46,800
• Final balance: $55,200

**📋 Recommended Next Steps:**
1. Set up automatic monthly transfers
2. Choose appropriate investment allocation
3. Review progress quarterly
4. Adjust as life circumstances change

**💡 Key Insight**: Starting early and consistent contributions are the keys to reaching your financial goals.

**Note**: This is a simplified analysis. For detailed projections, please ensure your user profile is complete and try the analysis again.

**Disclaimer**: Projections are estimates only and actual results may vary."""
            
            return {
                "agent_response": response,
                "sources": ["Goal Planning Assistant", "Financial Planning Principles"],
                "confidence": 0.8,
                "next_agent": None,
                "agent_name": "goal_planning"
            }
    
    return MockGoalAgent()

# Quick goal creation helper functions
def quick_create_emergency_fund(session_state: Dict[str, Any]):
    """Create emergency fund goal with smart defaults"""
    if session_state.get("user_profile"):
        target = session_state["user_profile"]["monthly_expenses"] * 6
        monthly_contribution = min(target / 12, session_state["user_profile"]["annual_income"] / 12 * 0.1)
    else:
        target = 18000
        monthly_contribution = 500
    
    goal = {
        "id": f"emergency_{int(datetime.now().timestamp())}",
        "name": "Emergency Fund (6 months)",
        "type": "emergency_fund",
        "target_amount": target,
        "target_date": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
        "current_amount": 0,
        "monthly_contribution": monthly_contribution,
        "priority": "high",
        "created_date": datetime.now().strftime("%Y-%m-%d")
    }
    
    if "investment_goals" not in session_state:
        session_state["investment_goals"] = []
    
    session_state["investment_goals"].append(goal)
    st.success("✅ Emergency Fund goal created!")
    st.rerun()

def quick_create_house_goal(session_state: Dict[str, Any]):
    """Create house down payment goal"""
    goal = {
        "id": f"house_{int(datetime.now().timestamp())}",
        "name": "House Down Payment",
        "type": "major_purchase",
        "target_amount": 60000,
        "target_date": (datetime.now() + timedelta(days=1095)).strftime("%Y-%m-%d"),
        "current_amount": 0,
        "monthly_contribution": 1500,
        "priority": "high",
        "created_date": datetime.now().strftime("%Y-%m-%d")
    }
    
    if "investment_goals" not in session_state:
        session_state["investment_goals"] = []
    
    session_state["investment_goals"].append(goal)
    st.success("✅ House Down Payment goal created!")
    st.rerun()

def quick_create_retirement_goal(session_state: Dict[str, Any]):
    """Create retirement goal"""
    if session_state.get("user_profile"):
        years_to_retirement = max(1, session_state["user_profile"]["retirement_age"] - session_state["user_profile"]["age"])
        target = session_state["user_profile"]["annual_income"] * 12
    else:
        target = 1000000
        years_to_retirement = 30
    
    goal = {
        "id": f"retirement_{int(datetime.now().timestamp())}",
        "name": "Retirement Fund",
        "type": "retirement",
        "target_amount": target,
        "target_date": (datetime.now() + timedelta(days=years_to_retirement * 365)).strftime("%Y-%m-%d"),
        "current_amount": 0,
        "monthly_contribution": 1000,
        "priority": "medium",
        "created_date": datetime.now().strftime("%Y-%m-%d")
    }
    
    if "investment_goals" not in session_state:
        session_state["investment_goals"] = []
    
    session_state["investment_goals"].append(goal)
    st.success("✅ Retirement Fund goal created!")
    st.rerun()

def quick_create_college_goal(session_state: Dict[str, Any]):
    """Create college fund goal"""
    goal = {
        "id": f"college_{int(datetime.now().timestamp())}",
        "name": "College Fund",
        "type": "education",
        "target_amount": 100000,
        "target_date": (datetime.now() + timedelta(days=6570)).strftime("%Y-%m-%d"),  # 18 years
        "current_amount": 0,
        "monthly_contribution": 400,
        "priority": "medium",
        "created_date": datetime.now().strftime("%Y-%m-%d")
    }
    
    if "investment_goals" not in session_state:
        session_state["investment_goals"] = []
    
    session_state["investment_goals"].append(goal)
    st.success("✅ College Fund goal created!")
    st.rerun()

def quick_create_car_goal(session_state: Dict[str, Any]):
    """Create car purchase goal"""
    goal = {
        "id": f"car_{int(datetime.now().timestamp())}",
        "name": "Car Purchase",
        "type": "major_purchase",
        "target_amount": 25000,
        "target_date": (datetime.now() + timedelta(days=730)).strftime("%Y-%m-%d"),  # 2 years
        "current_amount": 0,
        "monthly_contribution": 800,
        "priority": "medium",
        "created_date": datetime.now().strftime("%Y-%m-%d")
    }
    
    if "investment_goals" not in session_state:
        session_state["investment_goals"] = []
    
    session_state["investment_goals"].append(goal)
    st.success("✅ Car Purchase goal created!")
    st.rerun()

def quick_create_vacation_goal(session_state: Dict[str, Any]):
    """Create vacation fund goal"""
    goal = {
        "id": f"vacation_{int(datetime.now().timestamp())}",
        "name": "Dream Vacation",
        "type": "major_purchase",
        "target_amount": 8000,
        "target_date": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
        "current_amount": 0,
        "monthly_contribution": 650,
        "priority": "low",
        "created_date": datetime.now().strftime("%Y-%m-%d")
    }
    
    if "investment_goals" not in session_state:
        session_state["investment_goals"] = []
    
    session_state["investment_goals"].append(goal)
    st.success("✅ Vacation Fund goal created!")
    st.rerun()