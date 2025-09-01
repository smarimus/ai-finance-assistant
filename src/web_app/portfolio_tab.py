# Portfolio analysis tab for the Streamlit web interface
# Handle portfolio data input, analysis display, and visualization

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, Optional
import io

def render_portfolio_tab(workflow, session_state: Dict[str, Any]):
    """
    Render the portfolio analysis tab
    
    Features:
    - Portfolio data input (CSV upload, manual entry)
    - Portfolio analysis display
    - Interactive charts and visualizations
    - Recommendations and insights
    """
    
    st.header("📊 Portfolio Analysis")
    
    # Portfolio input section
    st.subheader("📋 Portfolio Data Input")
    
    # Create tabs for different input methods
    input_tab1, input_tab2, input_tab3 = st.tabs(["📁 CSV Upload", "✍️ Manual Entry", "📝 Text Format"])
    
    with input_tab1:
        handle_csv_upload(session_state)
    
    with input_tab2:
        handle_manual_entry(session_state)
    
    with input_tab3:
        handle_text_input(session_state)
    
    # Analysis and display section
    if session_state.get("portfolio_data"):
        display_portfolio_analysis(session_state, workflow)
    else:
        st.info("👆 Upload your portfolio data above to see analysis and recommendations.")
        
        # DEBUG: Show manual holdings if they exist
        if session_state.get("manual_holdings"):
            num_holdings = len(session_state["manual_holdings"])
            st.warning(f"🔧 DEBUG: Found {num_holdings} manual holdings but portfolio_data is not set. 🔧 Fix: Copy manual holdings to portfolio data ")
            
            # Show the holdings details
            with st.expander("🔍 View Manual Holdings"):
                for i, holding in enumerate(session_state["manual_holdings"]):
                    st.write(f"{i+1}. {holding.get('name', 'Unknown')} - ${holding.get('value', 0):,.2f}")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("✅ Copy Manual Holdings to Portfolio Data", key="debug_fix", type="primary"):
                    try:
                        # Copy manual holdings to portfolio_data
                        session_state["portfolio_data"] = {"holdings": session_state["manual_holdings"].copy()}
                        
                        # Clear manual_holdings to avoid duplication
                        # session_state["manual_holdings"] = []
                        
                        st.success(f"✅ Successfully copied {num_holdings} holdings to portfolio data!")
                        st.info("💡 Portfolio analysis will now be available below.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error copying holdings: {str(e)}")
            
            with col2:
                if st.button("🗑️ Clear Manual Holdings", key="clear_manual", type="secondary"):
                    session_state["manual_holdings"] = []
                    st.success("✅ Manual holdings cleared!")
                    st.rerun()
        
        # Show example format
        st.subheader("📋 Example Portfolio Data")
        example_data = pd.DataFrame([
            {"Name": "Apple Inc.", "Symbol": "AAPL", "Value": 25000, "Type": "Stock"},
            {"Name": "Vanguard S&P 500 ETF", "Symbol": "VOO", "Value": 30000, "Type": "ETF"},
            {"Name": "Total Bond Market", "Symbol": "BND", "Value": 15000, "Type": "Bond"},
            {"Name": "Cash", "Symbol": "CASH", "Value": 5000, "Type": "Cash"}
        ])
        st.dataframe(example_data, use_container_width=True)

def handle_csv_upload(session_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Handle CSV portfolio data upload"""
    
    st.write("Upload a CSV file with your portfolio holdings:")
    
    # Show expected format
    with st.expander("📋 Expected CSV Format"):
        st.write("""
        **Required columns:**
        - `Name`: Investment name (e.g., "Apple Inc.")
        - `Value`: Dollar amount invested (e.g., 25000)
        
        **Optional columns:**
        - `Symbol`: Ticker symbol (e.g., "AAPL")
        - `Type`: Asset type (Stock, Bond, ETF, Cash)
        - `Sector`: Sector classification
        
        **Example:**
        ```
        Name,Symbol,Value,Type
        Apple Inc.,AAPL,25000,Stock
        Vanguard S&P 500 ETF,VOO,30000,ETF
        Total Bond Market,BND,15000,Bond
        ```
        """)
    
    uploaded_file = st.file_uploader(
        "Choose CSV file", 
        type=['csv'],
        help="Upload a CSV file with your portfolio holdings"
    )
    
    if uploaded_file is not None:
        try:
            # Read the CSV
            df = pd.read_csv(uploaded_file)
            
            # Validate required columns
            df.columns = df.columns.str.strip().str.title()
            
            if 'Name' not in df.columns:
                st.error("❌ CSV must have a 'Name' column")
                return None
            
            if 'Value' not in df.columns:
                st.error("❌ CSV must have a 'Value' column")
                return None
            
            # Show preview
            st.write("**📋 Data Preview:**")
            st.dataframe(df, use_container_width=True)
            
            # Convert to portfolio format
            holdings = []
            for _, row in df.iterrows():
                holding = {
                    'name': str(row['Name']),
                    'value': float(row['Value'])
                }
                
                if 'Symbol' in df.columns and pd.notna(row['Symbol']):
                    holding['symbol'] = str(row['Symbol'])
                if 'Type' in df.columns and pd.notna(row['Type']):
                    holding['type'] = str(row['Type']).lower()
                if 'Sector' in df.columns and pd.notna(row['Sector']):
                    holding['sector'] = str(row['Sector']).lower()
            
                holdings.append(holding)
            
            if st.button("📊 Analyze Portfolio", key="csv_analyze"):
                # Save directly to session state instead of returning
                portfolio_data = {"holdings": holdings}
                session_state["portfolio_data"] = portfolio_data
                st.success("✅ Portfolio data saved successfully!")
                st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error reading CSV: {str(e)}")
    
    return None

def handle_manual_entry(session_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Handle manual portfolio data entry"""
    
    st.write("Enter your portfolio holdings manually:")
    
    # Initialize holdings in session state
    if "manual_holdings" not in session_state:
        session_state["manual_holdings"] = []
    
    # Add holding form
    with st.form("add_holding_form"):
        col1, col2, col3, col4 = st.columns([3, 1, 2, 1])
        
        with col1:
            name = st.text_input("Investment Name", placeholder="e.g., Apple Inc.")
        with col2:
            symbol = st.text_input("Symbol", placeholder="AAPL")
        with col3:
            value = st.number_input("Value ($)", min_value=0.0, format="%.2f")
        with col4:
            asset_type = st.selectbox("Type", ["Stock", "Bond", "ETF", "Mutual Fund", "Cash", "Other"])
        
        submitted = st.form_submit_button("➕ Add Holding")
        
        if submitted and name and value > 0:
            holding = {
                'name': name,
                'value': value,
                'type': asset_type.lower()
            }
            if symbol:
                holding['symbol'] = symbol.upper()
            
            # Add to manual holdings
            session_state["manual_holdings"].append(holding)
            
            # Immediately add to portfolio_data as well
            if "portfolio_data" not in session_state or session_state["portfolio_data"] is None:
                session_state["portfolio_data"] = {"holdings": []}
            
            # Ensure portfolio_data has holdings key
            if "holdings" not in session_state["portfolio_data"]:
                session_state["portfolio_data"]["holdings"] = []
            
            # Update portfolio_data with current manual holdings
            session_state["portfolio_data"]["holdings"] = session_state["manual_holdings"].copy()
            
            st.success(f"✅ Added {name} (${value:,.2f}) to portfolio!")
            st.rerun()
    
    # Display current holdings
    if session_state["manual_holdings"]:
        st.write("**📋 Current Holdings:**")
        
        holdings_df = pd.DataFrame(session_state["manual_holdings"])
        holdings_df['Value'] = holdings_df['value'].apply(lambda x: f"${x:,.2f}")
        
        # Add delete buttons
        for i, holding in enumerate(session_state["manual_holdings"]):
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"{holding['name']}: ${holding['value']:,.2f}")
            with col2:
                if st.button("🗑️", key=f"delete_{i}"):
                    # Remove from manual holdings
                    session_state["manual_holdings"].pop(i)
                    
                    # Update portfolio_data to stay in sync
                    if session_state["manual_holdings"]:
                        # Ensure portfolio_data exists and has proper structure
                        if "portfolio_data" not in session_state or session_state["portfolio_data"] is None:
                            session_state["portfolio_data"] = {"holdings": []}
                        session_state["portfolio_data"]["holdings"] = session_state["manual_holdings"].copy()
                    else:
                        # If no holdings left, clear portfolio_data
                        if "portfolio_data" in session_state:
                            del session_state["portfolio_data"]
                    
                    st.rerun()
        
        total_value = sum(h['value'] for h in session_state["manual_holdings"])
        st.write(f"**Total Portfolio Value: ${total_value:,.2f}**")
        
        # Show status
        st.success(f"✅ Portfolio with {len(session_state['manual_holdings'])} holdings is ready for analysis!")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.info("💡 Holdings are automatically saved and ready for analysis below.")
        with col2:
            if st.button("🗑️ Clear All", key="clear_all"):
                session_state["manual_holdings"] = []
                # Also clear portfolio_data
                if "portfolio_data" in session_state:
                    del session_state["portfolio_data"]
                st.rerun()
    
    # Show current session state for debugging
    if session_state.get("portfolio_data"):
        st.info(f"✅ Portfolio data is saved in session state with {len(session_state['portfolio_data']['holdings'])} holdings")
    else:
        st.warning("❌ No portfolio data found in session state")
    
    return None

def handle_text_input(session_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Handle text format portfolio input"""
    
    st.write("Enter your portfolio in text format:")
    
    # Show format examples
    with st.expander("📋 Supported Formats"):
        st.write("""
        **Format examples:**
        ```
        Apple Stock: $25,000
        MSFT - $15,000
        Vanguard S&P 500 ETF $30,000
        Bond Fund: 10000
        Cash $5,000
        ```
        
        **Tips:**
        - One investment per line
        - Use $ symbol or just numbers
        - Commas in numbers are okay
        """)
    
    text_input = st.text_area(
        "Portfolio Holdings",
        height=200,
        placeholder="Apple Stock: $25,000\nMicrosoft: $15,000\nBond Fund: $10,000"
    )
    
    if text_input and st.button("📊 Analyze Portfolio", key="text_analyze"):
        try:
            holdings = parse_text_input(text_input)
            if holdings:
                # Save directly to session state instead of returning
                portfolio_data = {"holdings": holdings}
                session_state["portfolio_data"] = portfolio_data
                st.success("✅ Portfolio data saved successfully!")
                st.rerun()
            else:
                st.error("❌ Could not parse any holdings from the text")
        except Exception as e:
            st.error(f"❌ Error parsing text: {str(e)}")
    
    return None

def parse_text_input(text: str) -> list:
    """Parse portfolio holdings from text input"""
    import re
    
    holdings = []
    lines = text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        # Extract value using regex
        value_match = re.search(r'[\$]?([0-9,]+(?:\.[0-9]{2})?)', line)
        if value_match:
            value = float(value_match.group(1).replace(',', ''))
            name = line[:value_match.start()].strip(' :-$')
            
            if name and value > 0:
                holdings.append({
                    'name': name,
                    'value': value
                })
    
    return holdings

def display_portfolio_analysis(session_state: Dict[str, Any], workflow):
    """Display portfolio analysis results with visualizations"""
    
    st.subheader("📈 Portfolio Analysis Results")
    
    portfolio_data = session_state["portfolio_data"]
    
    # Get analysis from portfolio agent
    if workflow and hasattr(workflow, 'portfolio_agent'):
        try:
            # Create state for agent
            agent_state = {
                "user_query": "analyze my portfolio",
                "portfolio_data": portfolio_data
            }
            
            # Get analysis
            result = workflow.portfolio_agent.execute(agent_state)
            
            # Display analysis
            display_analysis_results(result, portfolio_data)
            
        except Exception as e:
            st.error(f"❌ Error during analysis: {str(e)}")
            # Fallback to basic display
            display_basic_portfolio_info(portfolio_data)
    else:
        # Fallback to basic display
        display_basic_portfolio_info(portfolio_data)

def display_analysis_results(result: Dict[str, Any], portfolio_data: Dict[str, Any]):
    """Display comprehensive analysis results"""
    
    # Agent response
    if result.get("response"):
        st.write("**🤖 AI Analysis:**")
        st.write(result["response"])
    
    # Portfolio metrics
    metrics = result.get("portfolio_metrics", {})
    
    # Key metrics cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Value",
            f"${metrics.get('total_value', 0):,.2f}"
        )
    
    with col2:
        st.metric(
            "Holdings",
            metrics.get('num_holdings', 0)
        )
    
    with col3:
        div_score = metrics.get('diversification_score', 0)
        st.metric(
            "Diversification",
            f"{div_score}/100",
            delta=f"{div_score - 70}" if div_score != 70 else None
        )
    
    with col4:
        risk_level = metrics.get('risk_score', {}).get('level', 'Unknown')
        st.metric(
            "Risk Level",
            risk_level.title()
        )
    
    # Visualizations
    viz_data = result.get("visualization_data", {})
    
    # Asset allocation charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Holdings Allocation")
        create_allocation_pie_chart(viz_data.get("allocation_pie", {}))
    
    with col2:
        st.subheader("🏗️ Asset Class Allocation")
        create_asset_class_pie_chart(viz_data.get("asset_class_pie", {}))
    
    # Recommendations
    recommendations = result.get("recommendations", [])
    if recommendations:
        st.subheader("💡 Recommendations")
        
        for i, rec in enumerate(recommendations, 1):
            priority_color = {
                "high": "🔴",
                "medium": "🟡", 
                "low": "🟢"
            }.get(rec.get("priority", "medium"), "🔵")
            
            with st.expander(f"{priority_color} {rec['title']} (Priority: {rec.get('priority', 'medium').title()})"):
                st.write(f"**Description:** {rec['description']}")
                st.write(f"**Action:** {rec['action']}")
                if rec.get('target'):
                    st.write(f"**Target:** {rec['target']}")
    
    # Detailed metrics table
    if viz_data.get("metrics_table"):
        st.subheader("📋 Detailed Metrics")
        metrics_df = pd.DataFrame(viz_data["metrics_table"])
        st.dataframe(metrics_df, use_container_width=True, hide_index=True)

def display_basic_portfolio_info(portfolio_data: Dict[str, Any]):
    """Display basic portfolio information when agent analysis is not available"""
    
    holdings = portfolio_data.get("holdings", [])
    
    if not holdings:
        st.warning("No holdings found in portfolio data")
        return
    
    # Basic calculations
    total_value = sum(h.get('value', 0) for h in holdings)
    
    st.metric("Total Portfolio Value", f"${total_value:,.2f}")
    st.metric("Number of Holdings", len(holdings))
    
    # Holdings table
    st.subheader("📋 Portfolio Holdings")
    
    holdings_df = pd.DataFrame(holdings)
    holdings_df['percent'] = (holdings_df['value'] / total_value * 100).round(2)
    holdings_df['value_formatted'] = holdings_df['value'].apply(lambda x: f"${x:,.2f}")
    holdings_df['percent_formatted'] = holdings_df['percent'].apply(lambda x: f"{x}%")
    
    display_df = holdings_df[['name', 'value_formatted', 'percent_formatted']].copy()
    display_df.columns = ['Name', 'Value', 'Allocation %']
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)

def create_allocation_pie_chart(data: Dict[str, Any]):
    """Create pie chart for portfolio allocation"""
    
    if not data.get("labels") or not data.get("values"):
        st.write("No allocation data available")
        return
    
    fig = go.Figure(data=[go.Pie(
        labels=data["labels"],
        values=data["values"],
        hole=0.3,
        textinfo='label+percent',
        textposition='auto'
    )])
    
    fig.update_layout(
        title="Portfolio Holdings Distribution",
        showlegend=True,
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_asset_class_pie_chart(data: Dict[str, Any]):
    """Create pie chart for asset class allocation"""
    
    if not data.get("labels") or not data.get("values"):
        st.write("No asset class data available")
        return
    
    colors = {
        'stocks': '#FF6B6B',
        'bonds': '#4ECDC4', 
        'cash': '#45B7D1',
        'alternatives': '#96CEB4'
    }
    
    chart_colors = [colors.get(label.lower(), '#FECA57') for label in data["labels"]]
    
    fig = go.Figure(data=[go.Pie(
        labels=[label.title() for label in data["labels"]],
        values=data["values"],
        hole=0.3,
        textinfo='label+percent',
        textposition='auto',
        marker_colors=chart_colors
    )])
    
    fig.update_layout(
        title="Asset Class Distribution",
        showlegend=True,
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)