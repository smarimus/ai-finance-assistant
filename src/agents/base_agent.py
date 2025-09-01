# Create a sophisticated base agent class for financial assistant
# Include LLM integration, tool management, error handling, logging
# Support for context preservation and response formatting

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from langchain.llms.base import LLM
from langchain.tools import BaseTool
import logging
from src.core.state import FinanceAssistantState

class BaseFinanceAgent(ABC):
    """
    Abstract base class for all financial assistant agents
    
    Features:
    - OpenAI LLM integration with error handling
    - Tool management and execution
    - Context preservation and memory
    - Response formatting with source attribution
    - Logging and debugging capabilities
    """
    
    def __init__(
        self, 
        llm: LLM, 
        tools: List[BaseTool], 
        agent_name: str,
        system_prompt: str
    ):
        self.llm = llm
        self.tools = tools
        self.agent_name = agent_name
        self.system_prompt = system_prompt
        self.logger = logging.getLogger(f"agent.{agent_name}")
    
    @abstractmethod
    def execute(self, state: FinanceAssistantState) -> Dict[str, Any]:
        """
        Execute agent logic and return response
        
        Returns:
        - agent_response: str - The formatted response
        - sources: List[str] - Source citations
        - confidence: float - Response confidence score
        - next_agent: Optional[str] - Suggested next agent
        - updated_context: Dict - Updated context information
        """
        pass
    
    def format_response(self, content: str, sources: List[str] = None, confidence: float = 0.8) -> Dict[str, Any]:
        """
        Format agent response with sources and metadata
        
        Phase 1: Basic response formatting with source attribution
        """
        try:
            # Basic response structure
            response = {
                "agent_response": content,
                "sources": sources or [],
                "confidence": confidence,
                "agent_name": self.agent_name,
                "timestamp": "now",  # Will be enhanced in later phases
                "next_agent": None,
                "updated_context": {}
            }
            
            # Add source citations to response text if sources exist
            if sources:
                formatted_content = f"{content}\n\n**Sources:**\n"
                for i, source in enumerate(sources, 1):
                    formatted_content += f"{i}. {source}\n"
                response["agent_response"] = formatted_content
            
            self.logger.info(f"Agent {self.agent_name} formatted response with {len(sources)} sources")
            return response
            
        except Exception as e:
            self.logger.error(f"Error formatting response: {str(e)}")
            return self.handle_error(e, "response_formatting")
    
    def handle_error(self, error: Exception, context: str) -> Dict[str, Any]:
        """
        Handle errors gracefully with fallback responses
        
        Phase 1: Basic error handling with user-friendly messages
        """
        error_message = f"I encountered an issue while processing your request. Error context: {context}"
        
        # Log the detailed error for debugging
        self.logger.error(f"Agent {self.agent_name} error in {context}: {str(error)}")
        
        # Return user-friendly error response
        return {
            "agent_response": error_message,
            "sources": [],
            "confidence": 0.0,
            "agent_name": self.agent_name,
            "timestamp": "now",
            "next_agent": None,
            "updated_context": {"error": str(error), "context": context}
        }
    
    def should_escalate(self, query: str, context: Dict[str, Any]) -> Optional[str]:
        """
        Determine if query should be escalated to another agent
        
        Phase 1: Simple keyword-based routing
        """
        query_lower = query.lower()
        
        # Portfolio-related queries
        portfolio_keywords = ["portfolio", "allocation", "holdings", "rebalance", "performance"]
        if any(keyword in query_lower for keyword in portfolio_keywords):
            return "portfolio_agent"
        
        # Market data queries
        market_keywords = ["stock price", "market", "ticker", "quote", "earnings"]
        if any(keyword in query_lower for keyword in market_keywords):
            return "market_agent"
        
        # Goal setting queries
        goal_keywords = ["retirement", "goal", "plan", "save", "target"]
        if any(keyword in query_lower for keyword in goal_keywords):
            return "goal_agent"
        
        # Default to staying with current agent for general Q&A
        return None
    
    def _prepare_llm_input(self, state: FinanceAssistantState) -> str:
        """
        Prepare input for LLM based on current state
        
        Phase 1: Basic prompt construction with system prompt and user query
        """
        user_query = state.get("user_query", "")
        conversation_history = state.get("conversation_history", [])
        
        # Build conversation context
        context_parts = [self.system_prompt]
        
        # Add recent conversation history (last 3 exchanges)
        if conversation_history:
            context_parts.append("\nRecent conversation:")
            for exchange in conversation_history[-3:]:
                if "user" in exchange:
                    context_parts.append(f"User: {exchange['user']}")
                if "assistant" in exchange:
                    context_parts.append(f"Assistant: {exchange['assistant']}")
        
        # Add current query
        context_parts.append(f"\nCurrent question: {user_query}")
        context_parts.append("\nPlease provide a helpful and accurate response:")
        
        return "\n".join(context_parts)
    
    def _extract_sources_from_context(self, rag_context: List[str]) -> List[str]:
        """
        Extract source citations from RAG context
        
        Phase 1: Simple source extraction
        """
        sources = []
        for context in rag_context:
            # Look for source indicators in the context
            if "[Source" in context:
                # Extract source information
                import re
                source_matches = re.findall(r'\[Source \d+: ([^\]]+)\]', context)
                sources.extend(source_matches)
        
        return list(set(sources))  # Remove duplicates
    
    def _calculate_confidence(self, response: str, sources: List[str]) -> float:
        """
        Calculate confidence score for the response
        
        Phase 1: Simple heuristic-based confidence scoring
        """
        base_confidence = 0.5
        
        # Increase confidence based on sources
        if sources:
            base_confidence += min(len(sources) * 0.1, 0.3)
        
        # Increase confidence for longer, more detailed responses
        if len(response) > 100:
            base_confidence += 0.1
        
        # Decrease confidence for vague responses
        vague_indicators = ["might", "could be", "possibly", "unclear", "not sure"]
        if any(indicator in response.lower() for indicator in vague_indicators):
            base_confidence -= 0.2
        
        return min(max(base_confidence, 0.0), 1.0)
    
    def validate_tools(self) -> bool:
        """
        Validate that all required tools are available and working
        
        Phase 1: Basic tool validation
        """
        try:
            for tool in self.tools:
                if not hasattr(tool, 'name') or not hasattr(tool, 'run'):
                    self.logger.warning(f"Tool {tool} missing required attributes")
                    return False
            
            self.logger.info(f"Agent {self.agent_name} validated {len(self.tools)} tools")
            return True
            
        except Exception as e:
            self.logger.error(f"Tool validation failed: {str(e)}")
            return False