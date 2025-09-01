# Create a comprehensive state management system for a multi-agent financial assistant
# Using LangGraph TypedDict for state management
# Include conversation history, portfolio data, market context, user preferences

from typing import List, Optional, Dict, Any
from datetime import datetime

# Force use of typing_extensions.TypedDict for LangGraph compatibility
from typing_extensions import TypedDict

class FinanceAssistantState(TypedDict, total=False):
    """
    Complete state schema for finance assistant with:
    - User query and conversation history
    - Portfolio data and analysis results
    - Market context and real-time data
    - Agent responses and routing information
    - User preferences and session data
    """
    # Required fields
    user_query: str
    conversation_history: List[Dict[str, Any]]
    
    # Optional fields for agent management
    current_agent: Optional[str]
    agent_responses: List[Dict[str, Any]]
    rag_context: List[str]
    
    # Portfolio management
    portfolio_data: Optional[Dict[str, Any]]
    portfolio_analysis: Optional[Dict[str, Any]]
    
    # Market data
    market_context: Optional[Dict[str, Any]]
    market_cache: Dict[str, Any]
    
    # User preferences
    risk_tolerance: Optional[str]
    investment_goals: List[Dict[str, Any]]
    user_profile: Dict[str, Any]
    
    # Session management
    session_id: str
    timestamp: datetime
    error_context: Optional[Dict[str, Any]]