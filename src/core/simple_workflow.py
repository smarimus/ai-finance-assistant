# Simple workflow implementation for Phase 3 without LangGraph complexity
# Implements intelligent agent routing and state management

from typing import Dict, Any, List
from datetime import datetime

class SimpleFinanceWorkflow:
    """
    Simple multi-agent workflow orchestrator for Phase 3
    
    Features:
    - Intelligent query routing based on intent classification
    - State management across agent interactions
    - Error handling and fallback mechanisms
    - Agent coordination without complex graph dependencies
    """
    
    def __init__(self, agents: Dict[str, Any]):
        self.agents = agents
        print(f"DEBUG: SimpleFinanceWorkflow initialized with agents: {list(agents.keys())}")
    
    def route_query(self, query: str) -> str:
        """
        Analyze user query and determine which agent should handle it
        Phase 3: Enhanced routing with intent classification
        """
        query_lower = query.lower()
        print(f"DEBUG: Routing query: {query[:50]}...")
        
        # Enhanced intent classification
        if self._is_portfolio_query(query_lower):
            if "portfolio_analysis" in self.agents:
                print("DEBUG: Routed to portfolio_analysis agent")
                return "portfolio_analysis"
            else:
                print("DEBUG: Portfolio agent not available, falling back to finance_qa")
                return "finance_qa"
        elif self._is_market_query(query_lower):
            if "market_analysis" in self.agents:
                print("DEBUG: Routed to market_analysis agent")
                return "market_analysis"
            else:
                print("DEBUG: Market agent not available, falling back to finance_qa")
                return "finance_qa"
        elif self._is_goal_query(query_lower):
            if "goal_planning" in self.agents:
                print("DEBUG: Routed to goal_planning agent")
                return "goal_planning"
            else:
                print("DEBUG: Goal agent not available, falling back to finance_qa")
                return "finance_qa"
        else:
            print("DEBUG: Routed to default finance_qa agent")
            return "finance_qa"
    
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
    
    def execute_agent(self, agent_name: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the selected agent and return response"""
        try:
            print(f"DEBUG: Executing agent: {agent_name}")
            
            # Get the agent
            agent = self.agents.get(agent_name)
            if not agent:
                print(f"DEBUG: Agent {agent_name} not found, falling back to finance_qa")
                agent = self.agents.get("finance_qa")
            
            if agent:
                # Execute agent
                result = agent.execute(state)
                print(f"DEBUG: Agent execution successful, response length: {len(result.get('agent_response', ''))}")
                return result
            else:
                print("DEBUG: No agents available")
                raise Exception("No agents available")
                
        except Exception as e:
            print(f"DEBUG: Error executing agent {agent_name}: {e}")
            raise e
    
    def create_fallback_response(self, error_context: Dict[str, Any] = None) -> str:
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
        Phase 3: Simple workflow execution with agent routing
        """
        print(f"DEBUG: Starting simple workflow for query: {user_query[:50]}...")
        
        try:
            # Step 1: Route query to appropriate agent
            agent_name = self.route_query(user_query)
            
            # Step 2: Prepare state for agent execution
            state = {
                "user_query": user_query,
                "conversation_history": session_state.get("conversation_history", []) if session_state else [],
                "portfolio_data": session_state.get("portfolio_data") if session_state else None,
                "market_context": session_state.get("market_context") if session_state else None,
                "investment_goals": session_state.get("investment_goals", []) if session_state else [],
                "user_profile": session_state.get("user_profile", {}) if session_state else {},
                "timestamp": datetime.now()
            }
            
            # Step 3: Execute agent
            result = self.execute_agent(agent_name, state)
            
            # Step 4: Format response
            return {
                "response": result.get("agent_response", "No response generated"),
                "agent": agent_name,
                "sources": result.get("sources", []),
                "confidence": result.get("confidence", 0.0),
                "next_agent": result.get("next_agent"),
                "updated_state": state,
                "conversation_history": state["conversation_history"]
            }
            
        except Exception as e:
            print(f"DEBUG: Workflow execution failed: {e}")
            # Emergency fallback
            return {
                "response": self.create_fallback_response(),
                "agent": "error",
                "sources": [],
                "confidence": 0.0,
                "next_agent": None,
                "updated_state": session_state or {},
                "conversation_history": session_state.get("conversation_history", []) if session_state else []
            }
