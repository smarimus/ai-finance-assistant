# Market analysis tab for the Streamlit web interface
# Display real-time market data, charts, and market insights

import streamlit as st
from typing import Dict, Any, List, Optional
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import time

# Import our market data components
from src.data.market_data import MarketDataProvider, MarketQuote
from src.agents.market_agent import MarketAnalysisAgent

def render_market_tab(workflow, session_state: Dict[str, Any]):
    """
    Render the market analysis tab
    
    Features:
    - Market overview dashboard
    - Stock quote lookup
    - Market trend analysis
    - Interactive charts
    """
    
    st.header("📈 Market Analysis Dashboard")
    
    # Initialize market components if not exists
    if "market_provider" not in session_state:
        session_state["market_provider"] = MarketDataProvider()
    
    if "market_agent" not in session_state:
        # Don't create market agent until explicitly requested
        session_state["market_agent"] = None
    
    # Add loading notice to prevent immediate API calls
    st.info("📊 **Market Data**: Click 'Load Market Data' below to fetch real-time information")
    
    # Add manual trigger for market data loading
    if st.button("🔄 Load Market Data", type="primary"):
        # Load workflow only when market data is explicitly requested
        with st.spinner("Loading market analysis workflow..."):
            if "workflow" not in st.session_state or st.session_state.workflow is None:
                from src.core.workflow_v2 import create_simple_workflow
                try:
                    st.session_state.workflow = create_simple_workflow()
                    st.session_state.workflow_available = True
                except Exception as e:
                    st.error(f"Failed to load workflow: {e}")
                    st.session_state.workflow = None
                    st.session_state.workflow_available = False
            
            # Create market agent if workflow is available
            if st.session_state.workflow and hasattr(st.session_state.workflow, 'agents') and 'market_analysis' in st.session_state.workflow.agents:
                session_state["market_agent"] = st.session_state.workflow.agents['market_analysis']
            else:
                # Create a simple mock market agent
                class MockMarketAgent:
                    def execute(self, state):
                        return {
                            "agent_response": "Market analysis temporarily unavailable in demo mode.",
                            "sources": ["Demo Mode"],
                            "confidence": 0.5
                        }
                session_state["market_agent"] = MockMarketAgent()
        
        session_state["market_data_loaded"] = True
        st.rerun()
    
    # Only render market data if explicitly requested
    if session_state.get("market_data_loaded", False):
        render_market_overview(session_state)
        
        st.divider()
        
        render_stock_lookup(session_state)
        
        st.divider()
        
        render_market_analysis(session_state)
        
        st.divider()
        
        # Watchlist - only load when market data is active
        render_watchlist(session_state)
    else:
        st.markdown("""
        ### 🚀 Market Analysis Features Available:
        - **Real-time Quotes**: Get current stock prices and market data
        - **Market Overview**: See major indices (SPY, QQQ, DIA, IWM)
        - **Stock Lookup**: Search and analyze individual stocks
        - **AI Analysis**: Get intelligent market insights and explanations
        - **Interactive Charts**: Visualize market trends and data
        - **Watchlist**: Personal stock tracking with real-time updates
        
        **Click 'Load Market Data' above to access live market information.**
        
        *Note: This prevents unnecessary API calls when browsing other tabs.*
        """)
    

def render_market_overview(session_state: Dict[str, Any]):
    """Render the market overview dashboard"""
    st.subheader("📊 Market Overview")
    
    # Auto-refresh controls
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        auto_refresh = st.checkbox("Auto-refresh (30 seconds)", key="auto_refresh_market")
    
    with col2:
        if st.button("🔄 Refresh Now", key="manual_refresh"):
            session_state["market_provider"].clear_cache()
    
    with col3:
        data_source = "Live" if not session_state["market_provider"].mock_mode else "Demo"
        st.metric("Data Source", data_source)
    
    # Auto-refresh logic
    if auto_refresh:
        if "last_market_refresh" not in session_state:
            session_state["last_market_refresh"] = time.time()
        
        if time.time() - session_state["last_market_refresh"] > 30:
            session_state["market_provider"].clear_cache()
            session_state["last_market_refresh"] = time.time()
            st.rerun()
    
    # Get market overview data
    with st.spinner("Loading market data..."):
        overview_data = session_state["market_provider"].get_market_overview()
    
    if not overview_data:
        st.error("Unable to load market data. Please check your connection.")
        return
    
    # Display market indices in columns
    cols = st.columns(len(overview_data))
    
    index_names = {
        "SPY": "S&P 500",
        "QQQ": "NASDAQ-100", 
        "DIA": "Dow Jones",
        "IWM": "Russell 2000"
    }
    
    for i, (symbol, quote) in enumerate(overview_data.items()):
        with cols[i]:
            index_name = index_names.get(symbol, symbol)
            
            # Color based on performance
            delta_color = "normal" if quote.change >= 0 else "inverse"
            
            st.metric(
                label=f"{index_name} ({symbol})",
                value=f"${quote.price:.2f}",
                delta=f"{quote.change:+.2f} ({quote.change_percent:+.2f}%)",
                delta_color=delta_color
            )
    
    # Market sentiment analysis
    st.subheader("🎯 Market Sentiment")
    
    positive_moves = sum(1 for quote in overview_data.values() if quote.change >= 0)
    total_indices = len(overview_data)
    
    sentiment_score = positive_moves / total_indices
    
    if sentiment_score >= 0.75:
        sentiment = "🟢 Strong Bullish"
        sentiment_color = "green"
    elif sentiment_score >= 0.5:
        sentiment = "🟡 Moderate Bullish"
        sentiment_color = "orange"
    elif sentiment_score >= 0.25:
        sentiment = "🟡 Moderate Bearish"
        sentiment_color = "orange"
    else:
        sentiment = "🔴 Strong Bearish"
        sentiment_color = "red"
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Market Sentiment", sentiment)
    
    with col2:
        st.metric("Positive Indices", f"{positive_moves}/{total_indices}")
    
    # Create market overview chart
    create_market_overview_chart(overview_data)

def render_stock_lookup(session_state: Dict[str, Any]):
    """Render the stock lookup section"""
    st.subheader("🔍 Stock Quote Lookup")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        symbol_input = st.text_input(
            "Enter Stock Symbol",
            placeholder="e.g., AAPL, MSFT, GOOGL",
            key="stock_symbol_input"
        ).upper().strip()
    
    with col2:
        lookup_button = st.button("Get Quote", key="lookup_quote", type="primary")
    
    # Popular stocks for quick access
    st.write("**Quick Access:**")
    quick_symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "NFLX"]
    
    cols = st.columns(len(quick_symbols))
    for i, symbol in enumerate(quick_symbols):
        with cols[i]:
            if st.button(symbol, key=f"quick_{symbol}"):
                session_state["selected_stock"] = symbol
                st.rerun()
    
    # Handle symbol lookup
    target_symbol = None
    if lookup_button and symbol_input:
        target_symbol = symbol_input
    elif session_state.get("selected_stock"):
        target_symbol = session_state["selected_stock"]
        session_state["selected_stock"] = None  # Clear after use
    
    if target_symbol:
        display_stock_quote(target_symbol, session_state)

def render_watchlist(session_state: Dict[str, Any]):
    """Render watchlist section for tracking favorite stocks"""
    st.subheader("👁️ My Watchlist")
    
    # Initialize watchlist if not exists
    if "watchlist" not in session_state:
        session_state["watchlist"] = ["AAPL", "MSFT", "GOOGL"]  # Default watchlist
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        new_symbol = st.text_input(
            "Add to Watchlist",
            placeholder="Enter symbol to add",
            key="watchlist_input"
        ).upper().strip()
    
    with col2:
        if st.button("Add", key="add_to_watchlist") and new_symbol:
            if new_symbol not in session_state["watchlist"]:
                session_state["watchlist"].append(new_symbol)
                st.success(f"Added {new_symbol} to watchlist")
                st.rerun()
            else:
                st.warning(f"{new_symbol} already in watchlist")
    
    if session_state["watchlist"]:
        # Get quotes for watchlist
        with st.spinner("Loading watchlist..."):
            watchlist_quotes = session_state["market_provider"].get_multiple_quotes(
                session_state["watchlist"]
            )
        
        if watchlist_quotes:
            # Create watchlist table
            watchlist_data = []
            for quote in watchlist_quotes:
                watchlist_data.append({
                    "Symbol": quote.symbol,
                    "Price": f"${quote.price:.2f}",
                    "Change": f"{quote.change:+.2f}",
                    "Change %": f"{quote.change_percent:+.2f}%",
                    "Volume": f"{quote.volume:,}",
                    "Action": "Remove"
                })
            
            df = pd.DataFrame(watchlist_data)
            
            # Display the table with remove buttons
            for i, row in df.iterrows():
                cols = st.columns([1, 1, 1, 1, 1, 1])
                
                with cols[0]:
                    st.text(row["Symbol"])
                with cols[1]:
                    st.text(row["Price"])
                with cols[2]:
                    color = "🟢" if "+" in row["Change"] else "🔴"
                    st.text(f"{color} {row['Change']}")
                with cols[3]:
                    st.text(row["Change %"])
                with cols[4]:
                    st.text(row["Volume"])
                with cols[5]:
                    if st.button("❌", key=f"remove_{row['Symbol']}"):
                        session_state["watchlist"].remove(row["Symbol"])
                        st.rerun()
    else:
        st.info("Your watchlist is empty. Add some symbols to track them here.")

def render_market_analysis(session_state: Dict[str, Any]):
    """Render market analysis section"""
    st.subheader("🧠 AI Market Analysis")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        analysis_query = st.text_input(
            "Ask about market conditions",
            placeholder="e.g., 'How are tech stocks performing today?'",
            key="market_analysis_input"
        )
    
    with col2:
        analyze_button = st.button("Analyze", key="analyze_market", type="primary")
    
    # Example queries
    st.write("**Example Questions:**")
    example_queries = [
        "How are the markets performing today?",
        "What's driving AAPL's movement?",
        "Compare AAPL vs MSFT performance",
        "Find technology stocks",
        "Market outlook for this week"
    ]
    
    cols = st.columns(len(example_queries))
    for i, query in enumerate(example_queries):
        with cols[i]:
            if st.button(query[:20] + "...", key=f"example_query_{i}"):
                session_state["market_query"] = query
                st.rerun()
    
    # Handle analysis request
    target_query = None
    if analyze_button and analysis_query:
        target_query = analysis_query
    elif session_state.get("market_query"):
        target_query = session_state["market_query"]
        session_state["market_query"] = None  # Clear after use
    
    if target_query:
        with st.spinner("Analyzing market conditions..."):
            # Use market agent for analysis
            analysis_state = {"user_query": target_query}
            result = session_state["market_agent"].execute(analysis_state)
            
            st.subheader("📊 Analysis Results")
            st.write(result["agent_response"])
            
            # Display any market data that was retrieved
            if result.get("market_data") and result["market_data"].get("quotes"):
                st.subheader("📈 Market Data")
                for quote in result["market_data"]["quotes"]:
                    display_quote_card(quote)

def display_stock_quote(symbol: str, session_state: Dict[str, Any]):
    """Display detailed quote information for a stock"""
    with st.spinner(f"Loading quote for {symbol}..."):
        quote = session_state["market_provider"].get_quote(symbol)
    
    if not quote:
        st.error(f"Unable to find quote for symbol: {symbol}")
        return
    
    st.subheader(f"📊 {symbol} Quote Details")
    
    # Main price display
    col1, col2, col3 = st.columns(3)
    
    with col1:
        delta_color = "normal" if quote.change >= 0 else "inverse"
        st.metric(
            label="Current Price",
            value=f"${quote.price:.2f}",
            delta=f"{quote.change:+.2f} ({quote.change_percent:+.2f}%)",
            delta_color=delta_color
        )
    
    with col2:
        st.metric("Volume", f"{quote.volume:,}")
    
    with col3:
        st.metric("Previous Close", f"${quote.previous_close:.2f}")
    
    # Additional details
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Day High", f"${quote.high:.2f}")
    
    with col2:
        st.metric("Day Low", f"${quote.low:.2f}")
    
    # Price chart (simple visualization)
    create_stock_chart(quote)

def display_quote_card(quote: MarketQuote):
    """Display a quote in a card format"""
    with st.container():
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.write(f"**{quote.symbol}**")
        
        with col2:
            st.write(f"${quote.price:.2f}")
        
        with col3:
            color = "🟢" if quote.change >= 0 else "🔴"
            st.write(f"{color} {quote.change:+.2f} ({quote.change_percent:+.2f}%)")

def create_market_overview_chart(overview_data: Dict[str, MarketQuote]):
    """Create a market overview chart"""
    if not overview_data:
        return
    
    st.subheader("📈 Market Performance Chart")
    
    # Prepare data for chart
    symbols = list(overview_data.keys())
    changes = [quote.change_percent for quote in overview_data.values()]
    colors = ['green' if change >= 0 else 'red' for change in changes]
    
    # Create bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=symbols,
            y=changes,
            marker_color=colors,
            text=[f"{change:+.2f}%" for change in changes],
            textposition='auto'
        )
    ])
    
    fig.update_layout(
        title="Market Indices Performance (%)",
        xaxis_title="Index",
        yaxis_title="Change (%)",
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_stock_chart(quote: MarketQuote):
    """Create a simple stock price chart"""
    st.subheader("📊 Price Chart")
    
    # Create a simple OHLC-style chart with available data
    fig = go.Figure()
    
    # Add candlestick-like display with available data
    fig.add_trace(go.Scatter(
        x=['Open', 'Low', 'High', 'Current'],
        y=[quote.open, quote.low, quote.high, quote.price],
        mode='lines+markers',
        name=quote.symbol,
        line=dict(color='blue', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title=f"{quote.symbol} Price Movement",
        xaxis_title="Price Points",
        yaxis_title="Price ($)",
        height=300,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display trading range
    trading_range = quote.high - quote.low
    st.info(f"**Trading Range**: ${quote.low:.2f} - ${quote.high:.2f} (Range: ${trading_range:.2f})")

def display_market_data(market_data: Dict[str, Any]):
    """Display market data and charts"""
    if not market_data:
        st.warning("No market data available")
        return
    
    if market_data.get("quotes"):
        for quote in market_data["quotes"]:
            display_quote_card(quote)
    
    if market_data.get("overview"):
        create_market_overview_chart(market_data["overview"])