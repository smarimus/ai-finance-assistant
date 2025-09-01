# Enhanced Market Analysis Agent with dual integration patterns
# Supports both direct integration and tool calling patterns
# Configurable behavior based on config settings

import re
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import BaseTool

from src.agents.base_agent import BaseFinanceAgent
from src.data.market_data import MarketDataProvider, MarketQuote
from src.tools.market_tools import create_market_tools
from src.core.config import AgentConfig

class EnhancedMarketAnalysisAgent(BaseFinanceAgent):
    """
    Enhanced Market Analysis Agent supporting both integration patterns:
    
    1. Direct Integration (Original): Agent directly calls MarketDataProvider
    2. Tool Calling: LLM autonomously uses LangChain tools
    
    Configuration determines which pattern to use.
    """
    
    def __init__(
        self, 
        llm, 
        agent_config: AgentConfig,
        market_provider: Optional[MarketDataProvider] = None
    ):
        self.agent_config = agent_config
        self.integration_mode = agent_config.integration_mode
        
        # Initialize market provider for both modes
        self.market_provider = market_provider or MarketDataProvider()
        
        # System prompts for different modes
        if self.integration_mode == "tools":
            system_prompt = self._create_tool_calling_prompt()
            tools = create_market_tools(self.market_provider)
        else:
            system_prompt = self._create_direct_integration_prompt()
            tools = []
        
        super().__init__(llm, tools, "market_analysis", system_prompt)
        
        # Setup tool calling agent if needed
        if self.integration_mode == "tools" and tools:
            self._setup_tool_calling_agent()
        
        print(f"✅ Market Agent initialized in '{self.integration_mode}' mode with {len(tools)} tools")
    
    def _create_tool_calling_prompt(self) -> str:
        """Create system prompt optimized for tool calling"""
        return """
You are an expert market analyst with access to real-time market data tools.

Your role is to:
1. Help users understand market conditions and stock performance
2. Use available tools to fetch current market data when needed
3. Provide educational insights about market movements and trends
4. Explain complex market concepts in beginner-friendly terms
5. Always include appropriate disclaimers about investment risks

Available Tools:
- get_stock_quote: Get real-time data for specific stocks
- get_multiple_quotes: Compare multiple stocks at once
- get_market_overview: Get major market indices performance
- search_stock_symbols: Find stocks by company name

Guidelines:
- Use tools when users ask about specific stocks or market data
- Always explain what the data means in practical terms
- Provide context about whether price movements are significant
- Include appropriate disclaimers about investment risks
- Focus on education rather than giving investment advice

When users ask about stocks or market conditions, use the appropriate tools to get current data.
"""
    
    def _create_direct_integration_prompt(self) -> str:
        """Create system prompt for direct integration (original behavior)"""
        return """
You are a market analysis expert with access to real-time market data.

Your role is to:
1. Provide current market data and analysis in clear, actionable terms
2. Explain market movements and trends for both beginners and experienced investors
3. Offer context for market conditions without predicting future prices
4. Help users understand how market conditions might affect their investment goals
5. Focus on factual analysis rather than speculation
6. Always include appropriate disclaimers about market volatility and investment risks

Analysis Framework:
- Current market conditions and recent trends
- Individual stock fundamentals and performance
- Market context for portfolio decisions
- Risk factors and market volatility discussion
- Educational explanations of market concepts

Always remind users that:
- Past performance doesn't guarantee future results
- Market data is for informational purposes only
- Investment decisions should consider individual financial situations
- Professional financial advice should be sought for major decisions
"""
    
    def _setup_tool_calling_agent(self):
        """Setup LangChain agent executor for tool calling"""
        try:
            # Create chat prompt template with tool calling support
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_prompt),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ])
            
            # Create the agent
            agent = create_openai_tools_agent(self.llm, self.tools, prompt)
            
            # Create executor
            self.agent_executor = AgentExecutor(
                agent=agent,
                tools=self.tools,
                verbose=True,
                max_iterations=self.agent_config.max_tool_calls,
                return_intermediate_steps=True,
                handle_parsing_errors=True
            )
            
            print(f"✅ Tool calling agent executor created with {len(self.tools)} tools")
            
        except Exception as e:
            print(f"⚠️ Failed to setup tool calling agent: {e}")
            print("📝 Falling back to direct integration mode")
            self.integration_mode = "direct"
            self.agent_executor = None
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute market analysis using the configured integration pattern
        """
        query = state.get("user_query", "")
        
        try:
            if self.integration_mode == "tools" and hasattr(self, 'agent_executor'):
                return self._execute_with_tools(query, state)
            else:
                return self._execute_direct_integration(query, state)
                
        except Exception as e:
            return {
                "agent_response": f"I encountered an error while processing your market query: {str(e)}. Please try again or ask about general market concepts.",
                "sources": ["Market Analysis Agent"],
                "confidence": 0.3,
                "market_data": {},
                "next_agent": "finance_qa",
                "agent_name": "market_analysis",
                "integration_mode": self.integration_mode
            }
    
    def _execute_with_tools(self, query: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute using LangChain tool calling pattern"""
        try:
            # Let the LLM decide which tools to use
            result = self.agent_executor.invoke({
                "input": query
            })
            
            # Extract response and tool information
            response = result.get("output", "")
            intermediate_steps = result.get("intermediate_steps", [])
            
            # Extract tools used
            tools_used = []
            market_data = {}
            
            for step in intermediate_steps:
                if len(step) >= 2:
                    tool_action, tool_result = step[0], step[1]
                    tools_used.append(tool_action.tool)
                    
                    # Try to extract structured data if possible
                    if hasattr(tool_action, 'tool_input'):
                        market_data[tool_action.tool] = tool_action.tool_input
            
            sources = ["Alpha Vantage API", "Tool Calling Agent"] + tools_used
            
            return {
                "agent_response": response,
                "sources": sources,
                "confidence": 0.9,
                "market_data": market_data,
                "tools_used": tools_used,
                "next_agent": None,
                "agent_name": "market_analysis",
                "integration_mode": "tools"
            }
            
        except Exception as e:
            # Fallback to direct integration on tool errors
            print(f"⚠️ Tool calling failed: {e}")
            print("📝 Falling back to direct integration")
            return self._execute_direct_integration(query, state)
    
    def _execute_direct_integration(self, query: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute using direct integration pattern (original behavior)"""
        try:
            # Parse the market query to understand what user wants
            market_request = self._parse_market_query(query)
            
            # Fetch market data based on request
            market_data = self._fetch_market_data(market_request)
            
            # Generate analysis and insights
            analysis_response = self._generate_market_analysis(market_data, market_request, query)
            
            return {
                "agent_response": analysis_response["response"],
                "sources": analysis_response["sources"],
                "confidence": analysis_response["confidence"],
                "market_data": market_data,
                "next_agent": None,
                "agent_name": "market_analysis",
                "integration_mode": "direct"
            }
            
        except Exception as e:
            return {
                "agent_response": f"I encountered an error while fetching market data: {str(e)}. Please try again or ask about general market concepts.",
                "sources": ["Market Analysis Agent"],
                "confidence": 0.3,
                "market_data": {},
                "next_agent": "finance_qa",
                "agent_name": "market_analysis",
                "integration_mode": "direct"
            }
    
    # Keep all the original direct integration methods
    def _parse_market_query(self, query: str) -> Dict[str, Any]:
        """Parse user query for direct integration mode"""
        query_lower = query.lower()
        
        # Extract stock symbols (common patterns)
        symbol_patterns = [
            r'\b([A-Z]{1,5})\b',  # 1-5 letter symbols
            r'\$([A-Z]{1,5})\b'   # Symbols with $ prefix
        ]
        
        potential_symbols = []
        for pattern in symbol_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            potential_symbols.extend([s.upper() for s in matches])
        
        # Remove common false positives
        false_positives = {'THE', 'AND', 'OR', 'FOR', 'TO', 'OF', 'IN', 'ON', 'AT', 'BY'}
        symbols = [s for s in potential_symbols if s not in false_positives and len(s) <= 5]
        
        # Determine query type
        if any(word in query_lower for word in ['overview', 'market', 'indices', 'general']):
            query_type = 'market_overview'
        elif any(word in query_lower for word in ['price', 'quote', 'current', 'trading']):
            query_type = 'stock_quote'
        elif any(word in query_lower for word in ['search', 'find', 'lookup']):
            query_type = 'symbol_search'
        elif any(word in query_lower for word in ['compare', 'comparison', 'vs', 'versus']):
            query_type = 'comparison'
        else:
            query_type = 'general_analysis'
        
        return {
            "symbols": symbols,
            "query_type": query_type,
            "original_query": query,
            "search_terms": [word for word in query.split() if len(word) > 2]
        }
    
    def _fetch_market_data(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch market data for direct integration mode"""
        query_type = request["query_type"]
        symbols = request["symbols"]
        
        market_data = {
            "quotes": [],
            "overview": {},
            "search_results": [],
            "timestamp": datetime.now().isoformat(),
            "data_source": "Alpha Vantage" if not self.market_provider.mock_mode else "Mock Data"
        }
        
        if query_type == 'market_overview':
            overview = self.market_provider.get_market_overview()
            market_data["overview"] = overview
            market_data["quotes"] = list(overview.values())
            
        elif query_type == 'stock_quote' and symbols:
            quotes = self.market_provider.get_multiple_quotes(symbols)
            market_data["quotes"] = quotes
            
        elif query_type == 'symbol_search':
            search_terms = ' '.join(request["search_terms"])
            search_results = self.market_provider.search_symbols(search_terms)
            market_data["search_results"] = search_results
            
        elif query_type == 'comparison' and len(symbols) > 1:
            quotes = self.market_provider.get_multiple_quotes(symbols)
            market_data["quotes"] = quotes
            
        elif symbols:
            quotes = self.market_provider.get_multiple_quotes(symbols)
            market_data["quotes"] = quotes
            
        else:
            overview = self.market_provider.get_market_overview()
            market_data["overview"] = overview
            market_data["quotes"] = list(overview.values())
        
        return market_data
    
    def _generate_market_analysis(self, market_data: Dict[str, Any], request: Dict[str, Any], original_query: str) -> Dict[str, Any]:
        """Generate market analysis for direct integration mode"""
        # Prepare market data summary for LLM
        data_summary = self._format_market_data_for_llm(market_data)
        
        # Create analysis prompt
        analysis_prompt = f"""
        User Query: {original_query}
        
        Market Data Retrieved:
        {data_summary}
        
        Please provide a comprehensive market analysis response that:
        1. Directly addresses the user's question
        2. Explains the market data in clear, understandable terms
        3. Provides context about what the numbers mean
        4. Includes educational insights about market concepts
        5. Discusses any notable trends or movements
        6. Always includes appropriate disclaimers
        
        Format your response to be informative yet accessible to both beginners and experienced investors.
        """
        
        try:
            # Get LLM analysis
            llm_response = self.llm.invoke(analysis_prompt)
            response_text = llm_response.content if hasattr(llm_response, 'content') else str(llm_response)
            
            return {
                "response": response_text,
                "sources": ["Alpha Vantage API", "Market Analysis Agent"],
                "confidence": 0.85
            }
            
        except Exception as e:
            # Fallback to template response
            return self._generate_fallback_response(market_data, request)
    
    def _format_market_data_for_llm(self, market_data: Dict[str, Any]) -> str:
        """Format market data for LLM processing"""
        summary_parts = []
        
        # Format quotes
        if market_data.get("quotes"):
            summary_parts.append("Stock Quotes:")
            for quote in market_data["quotes"]:
                if isinstance(quote, MarketQuote):
                    change_direction = "up" if quote.change >= 0 else "down"
                    summary_parts.append(
                        f"- {quote.symbol}: ${quote.price:.2f} "
                        f"({change_direction} ${abs(quote.change):.2f}, {quote.change_percent:.2f}%) "
                        f"Volume: {quote.volume:,}"
                    )
        
        # Format overview
        if market_data.get("overview"):
            summary_parts.append("\nMarket Overview:")
            for symbol, quote in market_data["overview"].items():
                if isinstance(quote, MarketQuote):
                    change_direction = "up" if quote.change >= 0 else "down"
                    summary_parts.append(
                        f"- {symbol}: ${quote.price:.2f} "
                        f"({change_direction} ${abs(quote.change):.2f}, {quote.change_percent:.2f}%)"
                    )
        
        # Format search results
        if market_data.get("search_results"):
            summary_parts.append("\nSymbol Search Results:")
            for result in market_data["search_results"][:5]:
                summary_parts.append(f"- {result['symbol']}: {result['name']} ({result['type']})")
        
        summary_parts.append(f"\nData Source: {market_data.get('data_source', 'Unknown')}")
        summary_parts.append(f"Timestamp: {market_data.get('timestamp', 'Unknown')}")
        
        return "\n".join(summary_parts)
    
    def _generate_fallback_response(self, market_data: Dict[str, Any], request: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback response when LLM fails"""
        response_parts = ["📈 **Market Analysis**\n"]
        
        if market_data.get("quotes"):
            response_parts.append("**Current Market Data:**")
            for quote in market_data["quotes"]:
                if isinstance(quote, MarketQuote):
                    change_icon = "📈" if quote.change >= 0 else "📉"
                    response_parts.append(
                        f"{change_icon} **{quote.symbol}**: ${quote.price:.2f} "
                        f"({quote.change:+.2f}, {quote.change_percent:+.2f}%)"
                    )
        
        if market_data.get("search_results"):
            response_parts.append("\n**Search Results:**")
            for result in market_data["search_results"][:3]:
                response_parts.append(f"• {result['symbol']}: {result['name']}")
        
        response_parts.extend([
            "\n**Disclaimer**: Market data is for informational purposes only.",
            "Past performance does not guarantee future results.",
            "Please consult with a financial advisor for investment decisions."
        ])
        
        return {
            "response": "\n".join(response_parts),
            "sources": ["Market Analysis Agent", "Alpha Vantage API"],
            "confidence": 0.7
        }
    
    def get_integration_info(self) -> Dict[str, Any]:
        """Get information about current integration mode"""
        return {
            "integration_mode": self.integration_mode,
            "tools_available": len(self.tools),
            "tool_names": [tool.name for tool in self.tools] if self.tools else [],
            "has_agent_executor": hasattr(self, 'agent_executor'),
            "provider_mock_mode": self.market_provider.mock_mode
        }
