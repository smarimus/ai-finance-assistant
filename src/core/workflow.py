# Create a comprehensive LangGraph workflow for multi-agent orchestration
# Include query routing, agent execution, state management, error handling
# Implement conversation flow and agent handoff logic

from typing import Dict, Any, List
from datetime import datetime
from langgraph.graph import StateGraph, END
from src.core.state import FinanceAssistantState

# Import agents - using conditional imports for availability
try:
    from src.agents.finance_qa_agent import FinanceQAAgent
    FINANCE_QA_AVAILABLE = True
except ImportError:
    FINANCE_QA_AVAILABLE = False

try:
    from src.agents.portfolio_agent import PortfolioAnalysisAgent
    PORTFOLIO_AVAILABLE = True
except ImportError:
    PORTFOLIO_AVAILABLE = False

try:
    from src.agents.market_agent import MarketAnalysisAgent
    MARKET_AVAILABLE = True
except ImportError:
    MARKET_AVAILABLE = False

try:
    from src.agents.goal_agent import GoalPlanningAgent
    GOAL_AVAILABLE = True
except ImportError:
    GOAL_AVAILABLE = False

# Create a comprehensive LangGraph workflow for multi-agent orchestration
# Include query routing, agent execution, state management, error handling
# Implement conversation flow and agent handoff logic

from typing import Dict, Any, List
from datetime import datetime
from langgraph.graph import StateGraph, END
from src.core.state import FinanceAssistantState

# Import agents - using conditional imports for availability
try:
    from src.agents.finance_qa_agent import FinanceQAAgent
    FINANCE_QA_AVAILABLE = True
except ImportError:
    FINANCE_QA_AVAILABLE = False

try:
    from src.agents.portfolio_agent import PortfolioAnalysisAgent
    PORTFOLIO_AVAILABLE = True
except ImportError:
    PORTFOLIO_AVAILABLE = False

try:
    from src.agents.market_agent import MarketAnalysisAgent
    MARKET_AVAILABLE = True
except ImportError:
    MARKET_AVAILABLE = False

try:
    from src.agents.goal_agent import GoalPlanningAgent
    GOAL_AVAILABLE = True
except ImportError:
    GOAL_AVAILABLE = False

class FinanceAssistantWorkflow:
    """
    LangGraph workflow orchestrator for multi-agent finance assistant
    
    Phase 3 Implementation:
    - Intelligent query routing based on intent classification
    - State management across agent interactions
    - Error handling and fallback mechanisms
    - Conversation flow control and agent handoffs
    """
    
    def __init__(self, agents: Dict[str, Any]):
        self.agents = agents
        self.workflow = self._build_workflow()
        print(f"DEBUG: FinanceAssistantWorkflow initialized with agents: {list(agents.keys())}")
    
    def _build_workflow(self) -> StateGraph:
        """
        Build the LangGraph workflow with nodes and edges
        
        Simplified Phase 3 workflow:
        1. START -> Query Router
        2. Query Router -> Execute appropriate agent
        3. Format response
        4. END
        """
        # Create StateGraph with proper state schema
        workflow = StateGraph(FinanceAssistantState)
        
        # Add core nodes
        workflow.add_node("route_query", self._route_query)
        workflow.add_node("execute_agent", self._execute_agent)
        workflow.add_node("format_response", self._format_response)
        
        # Set entry point
        workflow.set_entry_point("route_query")
        
        # Add edges
        workflow.add_edge("route_query", "execute_agent")
        workflow.add_edge("execute_agent", "format_response")
        workflow.add_edge("format_response", END)
        
        return workflow.compile()
    
    def _route_query(self, state: FinanceAssistantState) -> FinanceAssistantState:
        """
        Analyze user query and determine which agent should handle it
        Phase 3: Enhanced routing with intent classification
        """
        query = state["user_query"].lower()
        full_query = state["user_query"]  # Keep original case
        print(f"DEBUG: Routing query: {query[:50]}...")
        
        # Extract portfolio data if present in the query
        is_portfolio = self._is_portfolio_query(query)
        contains_data = self._contains_portfolio_data(full_query)
        print(f"DEBUG: Is portfolio query: {is_portfolio}, Contains portfolio data: {contains_data}")
        
        if is_portfolio and contains_data:
            portfolio_data = self._extract_portfolio_data(full_query)
            if portfolio_data and portfolio_data.get("holdings"):
                state["portfolio_data"] = portfolio_data
                print(f"DEBUG: Extracted portfolio data: {len(portfolio_data['holdings'])} holdings")
            else:
                print(f"DEBUG: Portfolio data extraction returned: {portfolio_data}")
        elif is_portfolio:
            print("DEBUG: Portfolio query detected but no portfolio data found in text")
        
        # Determine target agent based on query content
        if self._is_portfolio_query(query):
            state["current_agent"] = "portfolio_analysis"
            print("DEBUG: Routed to portfolio_analysis agent")
        elif self._is_market_query(query):
            state["current_agent"] = "market_analysis"
            print("DEBUG: Routed to market_analysis agent")
        elif self._is_goal_query(query):
            state["current_agent"] = "goal_planning"
            print("DEBUG: Routed to goal_planning agent")
        else:
            state["current_agent"] = "finance_qa"
            print("DEBUG: Routed to finance_qa agent")
        
        return state
    
    def _is_portfolio_query(self, query: str) -> bool:
        """Detect portfolio-related queries with enhanced keywords"""
        portfolio_keywords = [
            "portfolio", "allocation", "diversification", "holdings", "rebalance",
            "analyze my", "balance", "stocks", "bonds", "etf", "mutual fund",
            "asset allocation", "investment mix", "risk tolerance", "performance"
        ]
        return any(keyword in query for keyword in portfolio_keywords)
    
    def _is_market_query(self, query: str) -> bool:
        """Detect market-related queries with enhanced keywords"""
        market_keywords = [
            "market", "stock price", "ticker", "trend", "performance", "quote",
            "index", "nasdaq", "s&p", "dow", "spy", "apple", "microsoft",
            "earnings", "volatility", "trading", "share price", "market cap"
        ]
        return any(keyword in query for keyword in market_keywords)
    
    def _is_goal_query(self, query: str) -> bool:
        """Detect goal-planning queries with enhanced keywords"""
        goal_keywords = [
            "goal", "retirement", "save", "plan", "target", "future", "timeline",
            "achieve", "house", "education", "college", "emergency fund",
            "financial planning", "budgeting", "savings", "debt payoff"
        ]
        return any(keyword in query for keyword in goal_keywords)
    
    def _contains_portfolio_data(self, query: str) -> bool:
        """Check if query contains portfolio data (holdings with values)"""
        import re
        # Look for patterns like "Stock: $1000" or "AAPL $500" or "$10,000" or "stock: 35000"
        money_patterns = [
            r'[\$]?[0-9,]+(?:\.[0-9]{2})?',  # $1000 or 1000
            r'[a-zA-Z]+\s*(?:stock|shares?)\s*[:]\s*[\$]?[0-9,]+',  # Meta stock: $35000
            r'[a-zA-Z]+\s*[:]\s*[\$]?[0-9,]+'  # Meta: 35000
        ]
        
        for pattern in money_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return True
        return False
    
    def _extract_portfolio_data(self, query: str) -> Dict[str, Any]:
        """Extract portfolio holdings from text query"""
        try:
            holdings = []
            lines = query.strip().split('\n')
            
            print(f"DEBUG: Extracting portfolio data from {len(lines)} lines")
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                print(f"DEBUG: Processing line: '{line}'")
                
                # Try to extract name and value
                # Formats: "Apple: $1000", "Meta stock: $35000", "Amazon stock: $5000"
                import re
                
                # Enhanced patterns to match various formats
                patterns = [
                    r'([a-zA-Z\s]+?)(?:stock|shares?)?\s*[:]\s*\$?([0-9,]+(?:\.[0-9]{2})?)',
                    r'([a-zA-Z\s]+?)\s*\$([0-9,]+(?:\.[0-9]{2})?)',
                    r'([a-zA-Z\s]+?)\s*[:]\s*([0-9,]+(?:\.[0-9]{2})?)'
                ]
                
                for pattern in patterns:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        name = match.group(1).strip()
                        value_str = match.group(2).replace(',', '')
                        
                        try:
                            value = float(value_str)
                            
                            # Clean up the name
                            name = re.sub(r'\s*(stock|shares?|fund|etf)\s*', '', name, flags=re.IGNORECASE).strip()
                            
                            if name and value > 0:
                                holding = {
                                    'name': name.title(),
                                    'symbol': name.upper() if len(name) <= 5 else '',
                                    'value': value,
                                    'type': 'stock'
                                }
                                holdings.append(holding)
                                print(f"DEBUG: Extracted holding: {holding}")
                                break
                        except ValueError:
                            continue
            
            result = {"holdings": holdings} if holdings else {}
            print(f"DEBUG: Final extracted portfolio data: {result}")
            return result
            
        except Exception as e:
            print(f"DEBUG: Error extracting portfolio data: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def _execute_agent(self, state: FinanceAssistantState) -> FinanceAssistantState:
        """Execute the selected agent and update state"""
        current_agent = state.get("current_agent", "finance_qa")
        
        try:
            print(f"DEBUG: Executing agent: {current_agent}")
            
            # Get the agent
            agent = self.agents.get(current_agent)
            if not agent:
                print(f"DEBUG: Agent {current_agent} not found, falling back to finance_qa")
                agent = self.agents.get("finance_qa")
            
            if agent:
                # Execute agent
                result = agent.execute(state)
                print(f"DEBUG: Agent execution successful, response length: {len(result.get('agent_response', ''))}")
                
                # Update state with agent response
                state["agent_responses"] = [{
                    "agent": current_agent,
                    "response": result.get("agent_response", ""),
                    "timestamp": datetime.now().isoformat(),
                    "confidence": result.get("confidence", 0.0),
                    "sources": result.get("sources", []),
                    "next_agent": result.get("next_agent")
                }]
                
                # Update specific state fields based on agent type
                if current_agent == "portfolio_analysis" and "portfolio_metrics" in result:
                    state["portfolio_analysis"] = result
                elif current_agent == "market_analysis" and "market_data" in result:
                    state["market_context"] = result
                    
            else:
                print("DEBUG: No agents available")
                state["error_context"] = {"error": "No agents available", "agent": current_agent}
                
        except Exception as e:
            print(f"DEBUG: Error executing agent {current_agent}: {e}")
            state["error_context"] = {"agent": current_agent, "error": str(e)}
        
        return state
    
    def _format_response(self, state: FinanceAssistantState) -> FinanceAssistantState:
        """Format final response for user interface"""
        responses = state.get("agent_responses", [])
        
        if responses:
            latest_response = responses[-1]
            
            # Add to conversation history
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
            error_context = state.get("error_context", {})
            fallback_response = self._create_fallback_response(error_context)
            
            state["conversation_history"].append({
                "user": state["user_query"],
                "assistant": fallback_response,
                "agent": "error_handler",
                "timestamp": datetime.now().isoformat(),
                "sources": [],
                "confidence": 0.3
            })
            
        return state
    
    def _create_fallback_response(self, error_context: Dict[str, Any]) -> str:
        """Create a user-friendly fallback response when agents fail"""
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
        """
        Run the complete workflow for a user query
        Phase 3: Enhanced workflow execution with state management
        """
        print(f"DEBUG: Starting LangGraph workflow for query: {user_query[:50]}...")
        
        # Initialize state with proper defaults
        initial_state = {
            "user_query": user_query,
            "conversation_history": session_state.get("conversation_history", []) if session_state else [],
            "current_agent": None,
            "portfolio_data": session_state.get("portfolio_data") if session_state else None,
            "portfolio_analysis": None,
            "market_context": session_state.get("market_context") if session_state else None,
            "market_cache": session_state.get("market_cache", {}) if session_state else {},
            "agent_responses": [],
            "rag_context": [],
            "risk_tolerance": session_state.get("risk_tolerance") if session_state else None,
            "investment_goals": session_state.get("investment_goals", []) if session_state else [],
            "user_profile": session_state.get("user_profile", {}) if session_state else {},
            "session_id": session_state.get("session_id", f"session_{datetime.now().timestamp()}") if session_state else f"session_{datetime.now().timestamp()}",
            "timestamp": datetime.now(),
            "error_context": None
        }
        
        try:
            # Execute workflow
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
                # Fallback if no responses
                return {
                    "response": self._create_fallback_response({}),
                    "agent": "fallback",
                    "sources": [],
                    "confidence": 0.3,
                    "updated_state": final_state,
                    "conversation_history": final_state["conversation_history"]
                }
                
        except Exception as e:
            print(f"DEBUG: Workflow execution failed: {e}")
            # Emergency fallback
            return {
                "response": f"I apologize, but I encountered a system error: {str(e)}. Please try again.",
                "agent": "error",
                "sources": [],
                "confidence": 0.0,
                "updated_state": initial_state,
                "conversation_history": initial_state["conversation_history"]
            }