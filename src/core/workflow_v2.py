# Simple LangGraph workflow implementation using typing_extensions
# Properly compatible with LangGraph 0.0.26+ and Python < 3.12

from typing import Dict, Any, List
from datetime import datetime
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END

# Define proper state schema for LangGraph
class WorkflowState(TypedDict, total=False):
    user_query: str
    conversation_history: List[Dict[str, Any]]
    current_agent: str
    agent_responses: List[Dict[str, Any]]
    portfolio_data: Dict[str, Any]
    market_context: Dict[str, Any]
    error_context: Dict[str, Any]
    timestamp: str

class FinanceAssistantWorkflowV2:
    """
    LangGraph workflow orchestrator for multi-agent finance assistant
    Using proper typing_extensions.TypedDict for LangGraph 0.0.26+ compatibility
    """
    
    def __init__(self, agents: Dict[str, Any]):
        self.agents = agents
        self.workflow = self._build_workflow()
        print(f"DEBUG: FinanceAssistantWorkflowV2 initialized with agents: {list(agents.keys())}")
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow with proper state management"""
        
        # Create workflow with TypedDict state
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("route_query", self._route_query)
        workflow.add_node("execute_agent", self._execute_agent)
        workflow.add_node("format_response", self._format_response)
        
        # Set entry point and edges
        workflow.set_entry_point("route_query")
        workflow.add_edge("route_query", "execute_agent")
        workflow.add_edge("execute_agent", "format_response")
        workflow.add_edge("format_response", END)
        
        return workflow.compile()
    
    def _route_query(self, state: WorkflowState) -> WorkflowState:
        """Route query to appropriate agent"""
        query = state["user_query"].lower()
        print(f"DEBUG: Routing query: {query[:50]}...")
        
        if self._is_portfolio_query(query):
            if "portfolio_analysis" in self.agents:
                state["current_agent"] = "portfolio_analysis"
                print("DEBUG: Routed to portfolio_analysis agent")
            else:
                state["current_agent"] = "finance_qa"
                print("DEBUG: Portfolio agent not available, falling back to finance_qa")
        elif self._is_market_query(query):
            if "market_analysis" in self.agents:
                state["current_agent"] = "market_analysis"
                print("DEBUG: Routed to market_analysis agent")
            else:
                state["current_agent"] = "finance_qa"
                print("DEBUG: Market agent not available, falling back to finance_qa")
        elif self._is_goal_query(query):
            if "goal_planning" in self.agents:
                state["current_agent"] = "goal_planning"
                print("DEBUG: Routed to goal_planning agent")
            else:
                state["current_agent"] = "finance_qa"
                print("DEBUG: Goal agent not available, falling back to finance_qa")
        else:
            state["current_agent"] = "finance_qa"
            print("DEBUG: Routed to default finance_qa agent")
        
        state["timestamp"] = datetime.now().isoformat()
        return state
    
    def _is_portfolio_query(self, query: str) -> bool:
        """Detect portfolio-related queries"""
        portfolio_keywords = [
            "portfolio", "allocation", "diversification", "holdings", "rebalance",
            "analyze my", "balance", "stocks", "bonds", "etf", "mutual fund",
            "asset allocation", "investment mix", "risk tolerance", "performance"
        ]
        return any(keyword in query for keyword in portfolio_keywords)
    
    def _is_market_query(self, query: str) -> bool:
        """Detect market-related queries"""
        market_keywords = [
            "market", "stock price", "ticker", "trend", "performance", "quote",
            "index", "nasdaq", "s&p", "dow", "spy", "apple", "microsoft",
            "earnings", "volatility", "trading", "share price", "market cap"
        ]
        return any(keyword in query for keyword in market_keywords)
    
    def _is_goal_query(self, query: str) -> bool:
        """Detect goal-planning queries"""
        goal_keywords = [
            "goal", "retirement", "save", "plan", "target", "future", "timeline",
            "achieve", "house", "education", "college", "emergency fund",
            "financial planning", "budgeting", "savings", "debt payoff"
        ]
        return any(keyword in query for keyword in goal_keywords)
    
    def _execute_agent(self, state: WorkflowState) -> WorkflowState:
        """Execute the selected agent"""
        current_agent = state.get("current_agent", "finance_qa")
        
        try:
            print(f"DEBUG: Executing agent: {current_agent}")
            print(f"DEBUG: Portfolio data in state: {state.get('portfolio_data')}")
            print(f"DEBUG: State keys: {list(state.keys())}")
            
            agent = self.agents.get(current_agent)
            if not agent:
                print(f"DEBUG: Agent {current_agent} not found, falling back to finance_qa")
                agent = self.agents.get("finance_qa")
            
            if agent:
                result = agent.execute(state)
                print(f"DEBUG: Agent execution successful, response length: {len(result.get('agent_response', ''))}")
                
                state["agent_responses"] = [{
                    "agent": current_agent,
                    "response": result.get("agent_response", ""),
                    "timestamp": datetime.now().isoformat(),
                    "confidence": result.get("confidence", 0.0),
                    "sources": result.get("sources", []),
                    "next_agent": result.get("next_agent")
                }]
            else:
                print("DEBUG: No agents available")
                state["error_context"] = {"error": "No agents available", "agent": current_agent}
                
        except Exception as e:
            print(f"DEBUG: Error executing agent {current_agent}: {e}")
            state["error_context"] = {"agent": current_agent, "error": str(e)}
        
        return state
    
    def _format_response(self, state: WorkflowState) -> WorkflowState:
        """Format final response"""
        responses = state.get("agent_responses", [])
        
        if responses:
            latest_response = responses[-1]
            state["conversation_history"].append({
                "user": state["user_query"],
                "assistant": latest_response["response"],
                "agent": latest_response["agent"],
                "timestamp": latest_response["timestamp"],
                "sources": latest_response.get("sources", []),
                "confidence": latest_response.get("confidence", 0.0)
            })
            print(f"DEBUG: Response formatted, conversation history length: {len(state['conversation_history'])}")
        else:
            # Handle error case
            fallback_response = self._create_fallback_response()
            state["conversation_history"].append({
                "user": state["user_query"],
                "assistant": fallback_response,
                "agent": "error_handler",
                "timestamp": datetime.now().isoformat(),
                "sources": [],
                "confidence": 0.3
            })
            
        return state
    
    def _create_fallback_response(self) -> str:
        """Create fallback response"""
        return """
I apologize, but I encountered an issue while processing your request. 
Let me provide some general guidance instead.

If you were asking about:
• **Investment basics**: I can explain stocks, bonds, ETFs, and diversification
• **Portfolio analysis**: Please ensure your data is formatted correctly
• **Market information**: Try asking about general market concepts or specific companies
• **Financial goals**: I can help you understand retirement and savings planning

Please try rephrasing your question, and I'll do my best to help!

**Disclaimer**: This provides educational information only, not personalized investment advice.
        """.strip()
    
    def run(self, user_query: str, session_state: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run the workflow"""
        print(f"DEBUG: Starting LangGraph workflow for query: {user_query[:50]}...")
        
        # Initialize state using WorkflowState structure
        initial_state: WorkflowState = {
            "user_query": user_query,
            "conversation_history": session_state.get("conversation_history", []) if session_state else [],
            "current_agent": "",
            "agent_responses": [],
            "portfolio_data": session_state.get("portfolio_data", {}) if session_state else {},
            "market_context": session_state.get("market_context", {}) if session_state else {},
            "error_context": {},
            "timestamp": datetime.now().isoformat()
        }
        
        # ENHANCED FALLBACK: Multiple checks for portfolio data sources
        portfolio_data_sources = []
        
        # Check for existing portfolio_data
        if initial_state.get("portfolio_data") and initial_state["portfolio_data"].get("holdings"):
            portfolio_data_sources.append("portfolio_data")
            print(f"DEBUG: Found portfolio_data with {len(initial_state['portfolio_data']['holdings'])} holdings")
        
        # Check for manual_holdings in session_state
        if session_state and session_state.get("manual_holdings"):
            manual_holdings = session_state.get("manual_holdings")
            if manual_holdings and len(manual_holdings) > 0:
                portfolio_data_sources.append("manual_holdings")
                print(f"DEBUG: Found manual_holdings with {len(manual_holdings)} holdings")
                
                # Use manual_holdings as fallback if no portfolio_data
                if not initial_state.get("portfolio_data") or not initial_state["portfolio_data"].get("holdings"):
                    initial_state["portfolio_data"] = {"holdings": manual_holdings}
                    print(f"DEBUG: Successfully set portfolio_data from manual_holdings: {len(manual_holdings)} holdings")
                    
                    # Also update session_state to sync the data
                    if session_state:
                        session_state["portfolio_data"] = {"holdings": manual_holdings}
                        print(f"DEBUG: Synced portfolio_data back to session_state")
        
        # Log the final state
        if portfolio_data_sources:
            print(f"DEBUG: Portfolio data sources found: {portfolio_data_sources}")
        else:
            print(f"DEBUG: No portfolio data sources found")
            
        # Final validation
        final_holdings = initial_state.get("portfolio_data", {}).get("holdings", [])
        if final_holdings:
            print(f"DEBUG: Final portfolio_data contains {len(final_holdings)} holdings")
        else:
            print(f"DEBUG: No holdings in final portfolio_data")
        
        try:
            print("DEBUG: Executing LangGraph workflow...")
            final_state = self.workflow.invoke(initial_state)
            print("DEBUG: Workflow execution completed successfully")
            
            # Extract response
            responses = final_state.get("agent_responses", [])
            if responses:
                latest_response = responses[-1]
                return {
                    "response": latest_response["response"],
                    "agent": latest_response["agent"],
                    "sources": latest_response.get("sources", []),
                    "confidence": latest_response.get("confidence", 0.0),
                    "updated_state": final_state,
                    "conversation_history": final_state["conversation_history"]
                }
            else:
                return {
                    "response": self._create_fallback_response(),
                    "agent": "fallback",
                    "sources": [],
                    "confidence": 0.3,
                    "updated_state": final_state,
                    "conversation_history": final_state["conversation_history"]
                }
                
        except Exception as e:
            print(f"DEBUG: Workflow execution failed: {e}")
            return {
                "response": f"I apologize, but I encountered a system error: {str(e)}. Please try again.",
                "agent": "error",
                "sources": [],
                "confidence": 0.0,
                "updated_state": initial_state,
                "conversation_history": initial_state["conversation_history"]
            }


def create_simple_workflow():
    """Create and return a simple workflow instance"""
    print("DEBUG: Creating simple workflow...")
    
    # Initialize LLM and RAG components first
    llm = None
    retriever = None
    
    try:
        # Try to import and initialize LLM
        try:
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)
            print("DEBUG: ✅ ChatOpenAI LLM initialized")
        except ImportError:
            from langchain.chat_models import ChatOpenAI
            llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.1)
            print("DEBUG: ✅ Fallback ChatOpenAI LLM initialized")
    except Exception as e:
        print(f"DEBUG: ❌ Failed to initialize LLM: {e}")
    
    try:
        # Try to initialize retriever with vector store
        from src.rag.retriever import FinanceRetriever
        from src.rag.vector_store import FinanceVectorStore
        
        # Try to initialize vector store
        try:
            vector_store = FinanceVectorStore()
            retriever = FinanceRetriever(vector_store=vector_store)
            print("DEBUG: ✅ FinanceRetriever with vector store initialized")
        except Exception as vs_error:
            print(f"DEBUG: ⚠️ Vector store failed ({vs_error}), using mock retriever")
            # Create a mock retriever for basic functionality
            class MockRetriever:
                def retrieve(self, query: str, k: int = 5, enhance_query: bool = True):
                    return [{
                        "content": "General financial information related to your query.",
                        "source": "Mock Finance Database",
                        "confidence": 0.7
                    }]
            retriever = MockRetriever()
            print("DEBUG: ✅ Mock retriever initialized")
    except Exception as e:
        print(f"DEBUG: ❌ Failed to initialize retriever: {e}")
        retriever = None
    
    # Import agents with fallback handling
    agents = {}
    
    # Try to import available agents with proper initialization
    if llm:
        # FinanceQAAgent needs both LLM and retriever
        if retriever:
            try:
                from src.agents.finance_qa_agent import FinanceQAAgent
                agents["finance_qa"] = FinanceQAAgent(llm=llm, retriever=retriever)
                print("DEBUG: ✅ FinanceQAAgent loaded")
            except Exception as e:
                print(f"DEBUG: ❌ Failed to load FinanceQAAgent: {e}")
        else:
            print("DEBUG: ⚠️ FinanceQAAgent skipped - no retriever available")
        
        # Other agents need LLM and their specific dependencies
        try:
            from src.agents.portfolio_agent import PortfolioAnalysisAgent
            from src.utils.portfolio_calc import PortfolioCalculator
            portfolio_calculator = PortfolioCalculator()
            agents["portfolio_analysis"] = PortfolioAnalysisAgent(llm=llm, portfolio_calculator=portfolio_calculator)
            print("DEBUG: ✅ PortfolioAnalysisAgent loaded")
        except Exception as e:
            print(f"DEBUG: ❌ Failed to load PortfolioAnalysisAgent: {e}")
        
        try:
            from src.agents.market_agent import MarketAnalysisAgent
            from src.data.market_data import MarketDataProvider
            market_provider = MarketDataProvider()
            agents["market_analysis"] = MarketAnalysisAgent(llm=llm, market_provider=market_provider)
            print("DEBUG: ✅ MarketAnalysisAgent loaded")
        except Exception as e:
            print(f"DEBUG: ❌ Failed to load MarketAnalysisAgent: {e}")
        
        try:
            from src.agents.goal_agent import GoalPlanningAgent
            from src.utils.portfolio_calc import FinancialCalculator
            financial_calculator = FinancialCalculator()
            agents["goal_planning"] = GoalPlanningAgent(llm=llm, financial_calculator=financial_calculator)
            print("DEBUG: ✅ GoalPlanningAgent loaded")
        except Exception as e:
            print(f"DEBUG: ❌ Failed to load GoalPlanningAgent: {e}")
    else:
        print("DEBUG: ⚠️ LLM not available, using minimal agents")
    
    if not agents:
        print("DEBUG: ⚠️ No agents loaded, creating minimal workflow")
        # Create a minimal fallback agent
        class FallbackAgent:
            def execute(self, state):
                return {
                    "agent_response": "I'm currently in maintenance mode. Please try again later.",
                    "confidence": 0.1,
                    "sources": []
                }
        agents["finance_qa"] = FallbackAgent()
    
    # Create and return workflow
    workflow = FinanceAssistantWorkflowV2(agents)
    print(f"DEBUG: Simple workflow created with {len(agents)} agents")
    return workflow
