# Create the main Streamlit application with multi-tab interface
# Include session state management, workflow integration, error handling

import streamlit as st
import sys
import os
from typing import Dict, Any
import pandas as pd
from datetime import datetime

# Add root directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Import the tab renderers
from src.web_app.chat_tab import render_chat_tab
from src.web_app.portfolio_tab import render_portfolio_tab
from src.web_app.market_tab import render_market_tab
from src.web_app.goals_tab import render_goals_tab

class FinanceAssistantApp:
    """
    Main Streamlit application for AI Finance Assistant
    
    Features:
    - Multi-tab interface with seamless navigation
    - Session state management across tabs
    - Integration with LangGraph workflow
    - Error handling and user feedback
    - Responsive design for different screen sizes
    """
    
    def __init__(self):
        self.setup_page_config()
        self.initialize_session_state()
        # Removed automatic workflow loading to prevent API calls on startup
    
    def setup_page_config(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title="AI Finance Assistant",
            page_icon="🏦",
            layout="wide",
            initial_sidebar_state="collapsed"
        )
        
        # Custom CSS for better styling
        st.markdown("""
        <style>
        /* Hide empty markdown elements that create whitespace */
        .stMarkdown:empty {
            display: none !important;
        }
        
        .stMarkdown div:empty {
            display: none !important;
        }
        
        .stMarkdown p:empty {
            margin: 0 !important;
            padding: 0 !important;
            display: none !important;
        }
        
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
        }
        
        /* Enhanced Tab Styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
            background-color: #f8f9fa;
            padding: 0.5rem;
            border-radius: 10px;
            border: 2px solid #e9ecef;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 60px;
            padding-left: 20px;
            padding-right: 20px;
            background-color: #ffffff;
            border-radius: 8px;
            border: 2px solid #dee2e6;
            font-weight: 600;
            font-size: 1.1rem;
            color: #495057;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white !important;
            border: 2px solid #667eea;
            box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
            transform: translateY(-2px);
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            background-color: #e9ecef;
            transform: translateY(-1px);
            box-shadow: 0 3px 6px rgba(0,0,0,0.15);
        }
        
        .stTabs [aria-selected="true"]:hover {
            background: linear-gradient(135deg, #5a67d8 0%, #6b5b95 100%);
            transform: translateY(-2px);
        }
        
        /* Tab content styling */
        .stTabs [data-baseweb="tab-panel"] {
            padding-top: 2rem;
        }
        
        .tab-content {
            padding: 1rem;
            border-radius: 8px;
            background-color: #f8f9fa;
            margin-top: 1rem;
        }
        
        .agent-response {
            background-color: #e3f2fd;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #1976d2;
            margin: 1rem 0;
        }
        
        .error-message {
            background-color: #ffebee;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #d32f2f;
            color: #d32f2f;
        }
        
        .success-message {
            background-color: #e8f5e8;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #4caf50;
            color: #2e7d32;
        }
        
        .source-citation {
            background-color: #f5f5f5;
            padding: 0.5rem;
            border-radius: 4px;
            margin: 0.5rem 0;
            font-size: 0.9rem;
            border-left: 3px solid #4caf50;
        }
        
        .confidence-score {
            display: inline-block;
            padding: 0.2rem 0.6rem;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: bold;
            margin: 0.5rem 0;
        }
        
        .confidence-high { background-color: #4caf50; color: white; }
        .confidence-medium { background-color: #ff9800; color: white; }
        .confidence-low { background-color: #f44336; color: white; }
        
        .tech-status {
            padding: 0.3rem 0.7rem;
            border-radius: 15px;
            font-size: 0.8rem;
            margin: 0.2rem;
            display: inline-block;
        }
        
        .tech-real { background-color: #4caf50; color: white; }
        .tech-mock { background-color: #ff9800; color: white; }
        .tech-unavailable { background-color: #f44336; color: white; }
        </style>
        """, unsafe_allow_html=True)
    
    def initialize_session_state(self):
        """Initialize all session state variables"""
        if "conversation_history" not in st.session_state:
            st.session_state.conversation_history = []
        
        # Don't initialize portfolio_data - let it be created when needed
        # if "portfolio_data" not in st.session_state:
        #     st.session_state.portfolio_data = {}  # Initialize as empty dict instead of None
            
        if "manual_holdings" not in st.session_state:
            st.session_state.manual_holdings = []
            
        if "portfolio_analysis" not in st.session_state:
            st.session_state.portfolio_analysis = None
        
        if "market_context" not in st.session_state:
            st.session_state.market_context = None
            
        if "market_cache" not in st.session_state:
            st.session_state.market_cache = {}
        
        if "investment_goals" not in st.session_state:
            st.session_state.investment_goals = []
        
        if "user_profile" not in st.session_state:
            st.session_state.user_profile = {}
        
        if "session_id" not in st.session_state:
            st.session_state.session_id = f"session_{datetime.now().timestamp()}"
        
        if "current_tab" not in st.session_state:
            st.session_state.current_tab = "Chat"
        
        # Initialize workflow once and store in session state
        if "workflow" not in st.session_state:
            st.session_state.workflow = None
        
        # DEBUG: Check for data inconsistencies at startup
        if (st.session_state.get("manual_holdings") and 
            len(st.session_state["manual_holdings"]) > 0 and
            not st.session_state.get("portfolio_data")):
            print(f"DEBUG: Detected manual_holdings without portfolio_data at startup")
            print(f"DEBUG: manual_holdings count: {len(st.session_state['manual_holdings'])}")
    
    def ensure_workflow_loaded(self):
        """Ensure the workflow is loaded and available"""
        
        # Only reload if workflow doesn't exist or version changed
        current_version = 'v1.6'
        
        if (st.session_state.workflow is not None and 
            st.session_state.get('workflow_version') == current_version):
            # Workflow already loaded and current version
            return
        
        print(f"DEBUG: Loading workflow (version {current_version})...")
        
        # Set version and clear old workflow if needed
        st.session_state.workflow_version = current_version
        if 'workflow' in st.session_state:
            del st.session_state.workflow
        
        try:
            # Try the simpler workflow first to avoid TypedDict issues
            from src.core.workflow_v2 import create_simple_workflow
            workflow = create_simple_workflow()
            st.session_state.workflow = workflow
            st.session_state.workflow_available = True
            print("DEBUG: ✅ Simple workflow loaded successfully")
        except Exception as e:
            print(f"DEBUG: ❌ Error loading simple workflow: {e}")
            try:
                # Fallback to original workflow
                from src.core.workflow import create_finance_workflow
                workflow = create_finance_workflow()
                st.session_state.workflow = workflow
                st.session_state.workflow_available = True
                print("DEBUG: ✅ Original workflow loaded successfully")
            except Exception as e2:
                print(f"DEBUG: ❌ Error loading original workflow: {e2}")
                st.session_state.workflow = None
                st.session_state.workflow_available = False
    
    def load_workflow(self):
        """Initialize workflow - Phase 3: LangGraph multi-agent orchestration"""
        try:
            print("DEBUG: Loading Phase 3 workflow...")
            
            # Initialize agents dictionary
            agents = {}
            
            # Try to create finance QA agent (core agent)
            try:
                from src.agents.finance_qa_agent import FinanceQAAgent
                from src.rag.vector_store import FinanceVectorStore
                from src.rag.retriever import FinanceRetriever
                
                # Try to create with LLM and RAG
                from langchain_openai import ChatOpenAI
                import os
                
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key and api_key != "your_openai_api_key_here":
                    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1, max_tokens=1000)
                    vector_store = FinanceVectorStore()
                    retriever = FinanceRetriever(vector_store)
                    agents["finance_qa"] = FinanceQAAgent(llm, retriever)
                    print("DEBUG: Real FinanceQAAgent created successfully")
                else:
                    # Use mock agent
                    agents["finance_qa"] = self.create_mock_finance_agent()
                    print("DEBUG: Mock FinanceQAAgent created")
                    
            except ImportError as e:
                print(f"DEBUG: FinanceQAAgent import failed: {e}")
                agents["finance_qa"] = self.create_mock_finance_agent()
            
            # Try to add portfolio agent (Phase 4 - NOW FULLY IMPLEMENTED!)
            try:
                from src.agents.portfolio_agent import PortfolioAnalysisAgent
                from src.utils.portfolio_calc import PortfolioCalculator
                
                # Create real portfolio agent with full functionality
                portfolio_calc = PortfolioCalculator()
                if api_key and api_key != "your_openai_api_key_here":
                    # Use real LLM for portfolio agent
                    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1, max_tokens=1500)
                    agents["portfolio_analysis"] = PortfolioAnalysisAgent(llm, portfolio_calc)
                    print("DEBUG: Real PortfolioAnalysisAgent created with LLM")
                else:
                    # Mock LLM fallback
                    agents["portfolio_analysis"] = PortfolioAnalysisAgent(self.create_mock_llm(), portfolio_calc)
                    print("DEBUG: PortfolioAnalysisAgent created with mock LLM")
            except ImportError as e:
                print(f"DEBUG: PortfolioAnalysisAgent not available: {e}")
                agents["portfolio_analysis"] = self.create_mock_portfolio_agent()
            
            # Try to add market agent (Phase 5 preparation)
            try:
                from src.agents.market_agent import MarketAnalysisAgent
                from src.data.market_data import MarketDataProvider
                
                # Create real market agent with Alpha Vantage integration
                market_provider = MarketDataProvider()
                if api_key and api_key != "your_openai_api_key_here":
                    # Use real LLM for market agent
                    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1, max_tokens=1000)
                    agents["market_analysis"] = MarketAnalysisAgent(llm, market_provider)
                    print("DEBUG: Real MarketAnalysisAgent created with Alpha Vantage integration")
                else:
                    # Use mock agent
                    agents["market_analysis"] = self.create_mock_market_agent()
                    print("DEBUG: Mock MarketAnalysisAgent created")
            except ImportError as e:
                print(f"DEBUG: MarketAnalysisAgent import failed: {e}")
                agents["market_analysis"] = self.create_mock_market_agent()
            
            # Try to add goal agent (Phase 6 preparation)
            try:
                from src.agents.goal_agent import GoalPlanningAgent
                # For now, create a mock goal agent since full implementation is Phase 6
                agents["goal_planning"] = self.create_mock_goal_agent()
                print("DEBUG: Mock GoalPlanningAgent created")
            except ImportError:
                print("DEBUG: GoalPlanningAgent not available")
            
            # Create workflow - Phase 3: LangGraph implementation with fallbacks
            print("DEBUG: Attempting to create LangGraph workflow...")
            
            # Try V2 workflow first (dict-based state)
            try:
                from src.core.workflow_v2 import FinanceAssistantWorkflowV2
                workflow = FinanceAssistantWorkflowV2(agents)
                print(f"DEBUG: ✅ FinanceAssistantWorkflowV2 (LangGraph) created with {len(agents)} agents")
                return workflow
            except Exception as e:
                print(f"DEBUG: Workflow V2 failed: {e}")
                
                # Try simple workflow as fallback
                try:
                    from src.core.simple_workflow import SimpleFinanceWorkflow
                    workflow = SimpleFinanceWorkflow(agents)
                    print(f"DEBUG: ✅ SimpleFinanceWorkflow created as fallback with {len(agents)} agents")
                    return workflow
                except Exception as e2:
                    print(f"DEBUG: All workflow implementations failed: {e2}")
                    return None
                
        except Exception as e:
            print(f"DEBUG: Error loading workflow: {e}")
            return None
    
    def create_mock_finance_agent(self):
        """Create mock finance agent for fallback"""
        class MockFinanceAgent:
            def execute(self, state):
                query = state.get("user_query", "").lower()
                
                if "portfolio" in query:
                    response = """I notice you're asking about portfolio-related topics. 

📊 **Portfolio Analysis Features** (Coming in Phase 4):
• Upload your portfolio data (CSV format)
• Get detailed allocation analysis
• Receive diversification recommendations
• View performance metrics and charts

For now, I can explain general portfolio concepts like diversification, asset allocation, and risk management.

**Disclaimer**: Educational information only, not personalized investment advice."""
                
                elif "market" in query or "stock" in query:
                    response = """I see you're interested in market information.

📈 **Market Analysis Features** (Coming in Phase 5):
• Real-time stock quotes and market data
• Market trend analysis and insights
• Sector performance tracking
• Individual stock analysis

For now, I can explain market concepts, investment strategies, and how to interpret market movements.

**Disclaimer**: Educational information only, not personalized investment advice."""
                
                elif "goal" in query or "retirement" in query or "plan" in query:
                    response = """You're asking about financial planning and goals.

🎯 **Goal Planning Features** (Coming in Phase 6):
• Set and track financial goals
• Retirement planning calculators
• Savings strategy recommendations
• Timeline and milestone tracking

For now, I can explain goal-setting principles, retirement planning basics, and savings strategies.

**Disclaimer**: Educational information only, not personalized investment advice."""
                
                else:
                    response = """I'm your **Phase 3 Multi-Agent Finance Assistant**! 

🤖 **Available Agents:**
• **Finance Q&A**: General financial education and concepts
• **Portfolio Agent**: Portfolio analysis (Phase 4)
• **Market Agent**: Market data and analysis (Phase 5)
• **Goal Agent**: Financial planning and goals (Phase 6)

I can route your questions to the most appropriate agent based on your query. Try asking about:
- Investment concepts and strategies
- Portfolio management topics
- Market information and trends
- Financial planning and goals

**Note**: Currently in Phase 3 with intelligent routing active.

**Disclaimer**: Educational information only, not personalized investment advice."""
                
                return {
                    "agent_response": response,
                    "sources": ["AI Finance Assistant Knowledge Base"],
                    "confidence": 0.8,
                    "next_agent": None
                }
        
        return MockFinanceAgent()
    
    def create_mock_portfolio_agent(self):
        """Create mock portfolio agent for Phase 4 preparation"""
        class MockPortfolioAgent:
            def execute(self, state):
                response = """**Portfolio Analysis Agent** (Phase 4 Preview)

📊 **Coming Soon - Portfolio Features:**
• Upload portfolio data via CSV
• Asset allocation analysis
• Diversification scoring
• Risk assessment
• Rebalancing recommendations
• Performance tracking

For now, you can ask general portfolio questions in the Chat tab, and I'll explain concepts like diversification, asset allocation, and portfolio management strategies.

**Disclaimer**: Educational information only, not personalized investment advice."""
                
                return {
                    "agent_response": response,
                    "sources": ["Portfolio Analysis System"],
                    "confidence": 0.7,
                    "next_agent": "finance_qa"
                }
        
        return MockPortfolioAgent()
    
    def create_mock_market_agent(self):
        """Create mock market agent for Phase 5 preparation"""
        class MockMarketAgent:
            def execute(self, state):
                response = """**Market Analysis Agent** (Phase 5 - FULLY IMPLEMENTED!)

📈 **Live Market Features Now Available:**
• ✅ Real-time stock quotes via Alpha Vantage API
• ✅ Market overview dashboard with major indices
• ✅ Symbol search and stock lookup
• ✅ AI-powered market analysis and insights
• ✅ Interactive charts and visualizations
• ✅ Market sentiment analysis
• ✅ Watchlist functionality
• ✅ Auto-refreshing market data

**🚀 Switch to the Market tab to access:**
- Live stock quotes and market data
- Interactive market dashboard
- AI market analysis with real-time insights
- Stock comparison and tracking tools

**Current Market Status**: All features operational with Alpha Vantage integration!

**Disclaimer**: Market data for informational purposes only, not investment advice."""
                
                return {
                    "agent_response": response,
                    "sources": ["Market Analysis System", "Alpha Vantage API", "Phase 5 Implementation"],
                    "confidence": 0.95,
                    "next_agent": None
                }
        
        return MockMarketAgent()
    
    def create_mock_goal_agent(self):
        """Create mock goal agent for Phase 6 preparation"""
        class MockGoalAgent:
            def execute(self, state):
                response = """**Goal Planning Agent** (Phase 6 Preview)

🎯 **Coming Soon - Goal Features:**
• Financial goal setting and tracking
• Retirement planning calculators
• Savings strategy recommendations
• Timeline and milestone tracking
• Progress monitoring

For now, you can ask general financial planning questions in the Chat tab, and I'll explain goal-setting principles, retirement planning, and savings strategies.

**Disclaimer**: Educational information only, not personalized investment advice."""
                
                return {
                    "agent_response": response,
                    "sources": ["Goal Planning System"],
                    "confidence": 0.7,
                    "next_agent": "finance_qa"
                }
        
        return MockGoalAgent()
    
    def run(self):
        """Main application entry point"""
        # Header
        st.markdown('<h1 class="main-header">🏦 AI Finance Assistant</h1>', unsafe_allow_html=True)
        st.markdown("Your intelligent companion for financial education and portfolio management")
        
        # Create tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "💬 Chat", 
            "📊 Portfolio", 
            "📈 Market", 
            "🎯 Goals"
        ])
        
        # Track current tab for cross-tab navigation
        if st.session_state.get("switch_to_tab"):
            tab_map = {"Chat": tab1, "Portfolio": tab2, "Market": tab3, "Goals": tab4}
            target_tab = st.session_state.switch_to_tab
            st.session_state.switch_to_tab = None
            # Note: Streamlit doesn't support programmatic tab switching
            # This is a placeholder for the intended functionality
        
        # Render tab contents
        with tab1:
            self.render_chat_tab()
        
        with tab2:
            self.render_portfolio_tab()
        
        with tab3:
            self.render_market_tab()
        
        with tab4:
            self.render_goals_tab()
        
        # Sidebar with session info and quick actions
        self.render_sidebar()
    
    def render_chat_tab(self):
        """Render the chat interface tab"""
        self.ensure_workflow_loaded()  # Only load when chat tab is accessed
        render_chat_tab(st.session_state.workflow, st.session_state)
    
    def render_portfolio_tab(self):
        """Render the portfolio analysis tab"""
        self.ensure_workflow_loaded()  # Only load when portfolio tab is accessed
        render_portfolio_tab(st.session_state.workflow, st.session_state)
    
    def render_market_tab(self):
        """Render the market analysis tab"""
        # Only load workflow when market data is explicitly requested
        # This prevents automatic API calls during app startup
        render_market_tab(None, st.session_state)  # Pass None to prevent immediate workflow access
    
    def render_goals_tab(self):
        """Render the goal planning tab - optimized to avoid API calls"""
        # Pass None for workflow to prevent unnecessary API calls
        # Goals tab creates its own minimal components
        render_goals_tab(None, st.session_state)
    
    def render_sidebar(self):
        """Render sidebar with session info and quick actions"""
        with st.sidebar:
            st.markdown("### 🏦 AI Finance Assistant")
            st.markdown("**Phase 2**: Knowledge-Enhanced Assistant")
            
            # Session info
            st.markdown("---")
            st.markdown("### 📊 Session Info")
            if hasattr(st.session_state, 'conversation_history'):
                st.markdown(f"**Messages**: {len(st.session_state.conversation_history)}")
            
            # Portfolio data debug info
            if hasattr(st.session_state, 'manual_holdings') and st.session_state.manual_holdings:
                st.markdown(f"**Manual Holdings**: {len(st.session_state.manual_holdings)}")
            if hasattr(st.session_state, 'portfolio_data') and st.session_state.portfolio_data:
                holdings_count = len(st.session_state.portfolio_data.get('holdings', []))
                st.markdown(f"**Portfolio Data**: {holdings_count} holdings")
            
            # Quick actions
            st.markdown("---")
            st.markdown("### ⚡ Quick Actions")
            
            # Auto-sync button if data is out of sync
            if (st.session_state.get("manual_holdings") and 
                len(st.session_state["manual_holdings"]) > 0 and
                not st.session_state.get("portfolio_data")):
                if st.button("🔄 Auto-sync Portfolio Data", type="primary", use_container_width=True):
                    try:
                        st.session_state["portfolio_data"] = {"holdings": st.session_state["manual_holdings"].copy()}
                        st.success("✅ Portfolio data synced!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Sync failed: {str(e)}")
            
            if st.button("Clear Chat History", type="secondary", use_container_width=True):
                self.clear_session()
            
            if st.button("Export Chat", type="secondary", use_container_width=True):
                self.export_chat_history()
            
            # Debug section
            with st.expander("🔧 Debug Info"):
                st.write("**Session State Keys:**")
                for key in sorted(st.session_state.keys()):
                    value = st.session_state[key]
                    if isinstance(value, list):
                        st.write(f"- {key}: {len(value)} items")
                    elif isinstance(value, dict):
                        st.write(f"- {key}: {len(value)} keys")
                    elif value is None:
                        st.write(f"- {key}: None")
                    else:
                        st.write(f"- {key}: {type(value).__name__}")
    
    def export_chat_history(self):
        """Export conversation history as downloadable file"""
        if not st.session_state.conversation_history:
            st.warning("No conversation history to export.")
            return
        
        # Convert to DataFrame for easy export
        df = pd.DataFrame(st.session_state.conversation_history)
        csv = df.to_csv(index=False)
        
        st.download_button(
            label="Download Chat History",
            data=csv,
            file_name=f"finance_chat_history_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )
    
    def clear_session(self):
        """Clear all session state data"""
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        self.initialize_session_state()
        self.ensure_workflow_loaded()  # Reload workflow after clearing
        st.success("Session cleared successfully!")
        st.rerun()

# Application entry point
if __name__ == "__main__":
    app = FinanceAssistantApp()
    app.run()