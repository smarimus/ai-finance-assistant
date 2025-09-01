# Create a Market Analysis Agent with Alpha Vantage integration
# Fetch real-time market data, analyze trends, provide market insights
# Implement caching strategy and error handling for API failures
# Generate market summaries and stock analysis

import re
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from src.agents.base_agent import BaseFinanceAgent
from src.data.market_data import MarketDataProvider, MarketQuote

class MarketAnalysisAgent(BaseFinanceAgent):
    """
    Market Analysis Agent for real-time market data and insights
    
    Capabilities:
    - Fetch real-time stock quotes using Alpha Vantage API
    - Analyze market trends and provide insights
    - Generate market summaries and sector analysis
    - Handle individual stock analysis and comparisons
    - Provide market context for investment decisions
    - Search for stock symbols and company information
    """
    
    def __init__(self, llm, market_provider: Optional[MarketDataProvider] = None):
        system_prompt = """
        You are a market analysis expert providing real-time market insights. Your role is to:
        
        1. **Market Data Analysis**: Provide current market data and analysis in clear, actionable terms
        2. **Educational Explanations**: Explain market movements and trends for both beginners and experienced investors
        3. **Contextual Insights**: Offer context for market conditions without predicting future prices
        4. **Investment Context**: Help users understand how market conditions might affect their investment goals
        5. **Risk Awareness**: Focus on factual analysis rather than speculation, always include appropriate disclaimers
        
        **Analysis Framework:**
        - Current market conditions and recent trends
        - Individual stock fundamentals and performance
        - Market context for portfolio decisions
        - Risk factors and market volatility discussion
        - Educational explanations of market concepts
        
        **When providing market data:**
        - Include current price, change, and percentage change
        - Explain what the numbers mean in practical terms
        - Provide context about whether movements are significant
        - Discuss volume and other relevant metrics when appropriate
        - Compare to historical ranges or market averages when relevant
        
        **Market Sentiment Analysis:**
        - Analyze overall market direction based on multiple indicators
        - Explain what's driving current market movements
        - Discuss sector performance and rotation
        - Provide context for volatility levels
        
        **Educational Focus:**
        - Explain market concepts in accessible language
        - Help users understand correlation between different markets
        - Discuss the importance of diversification
        - Explain how economic indicators affect markets
        
        **Always remind users that:**
        - Past performance doesn't guarantee future results
        - Market data is for informational purposes only
        - Investment decisions should consider individual financial situations
        - Professional financial advice should be sought for major decisions
        - Markets can be volatile and unpredictable
        
        **Response Format:**
        - Start with the most important information (price/trend)
        - Provide context and analysis
        - Include educational insights
        - End with appropriate disclaimers
        - Use emojis and formatting to make responses engaging but professional
        """
        super().__init__(llm, [], "market_analysis", system_prompt)
        self.market_provider = market_provider or MarketDataProvider()
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze market conditions and provide insights
        
        Steps:
        1. Parse market-related query from user input
        2. Fetch relevant market data with caching
        3. Analyze trends and market conditions
        4. Generate insights and context using LLM
        5. Prepare response with market data and analysis
        """
        query = state.get("user_query", "")
        
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
                "agent_name": "market_analysis"
            }
            
        except Exception as e:
            return {
                "agent_response": f"I encountered an error while fetching market data: {str(e)}. Please try again or ask about general market concepts.",
                "sources": ["Market Analysis Agent"],
                "confidence": 0.3,
                "market_data": {},
                "next_agent": "finance_qa",
                "agent_name": "market_analysis"
            }
    
    def _parse_market_query(self, query: str) -> Dict[str, Any]:
        """
        Parse user query to identify:
        - Specific stocks or indices requested
        - Type of analysis needed (quote, trends, comparison)
        - Intent (price check, analysis, overview)
        """
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
        """
        Fetch market data based on parsed request
        Handle different query types appropriately
        """
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
            # Get major market indices
            overview = self.market_provider.get_market_overview()
            market_data["overview"] = overview
            market_data["quotes"] = list(overview.values())
            
        elif query_type == 'stock_quote' and symbols:
            # Get quotes for specific symbols
            quotes = self.market_provider.get_multiple_quotes(symbols)
            market_data["quotes"] = quotes
            
        elif query_type == 'symbol_search':
            # Search for symbols based on search terms
            search_terms = ' '.join(request["search_terms"])
            search_results = self.market_provider.search_symbols(search_terms)
            market_data["search_results"] = search_results
            
        elif query_type == 'comparison' and len(symbols) > 1:
            # Get quotes for comparison
            quotes = self.market_provider.get_multiple_quotes(symbols)
            market_data["quotes"] = quotes
            
        elif symbols:
            # Default: get quotes for any mentioned symbols
            quotes = self.market_provider.get_multiple_quotes(symbols)
            market_data["quotes"] = quotes
            
        else:
            # No specific symbols, provide market overview
            overview = self.market_provider.get_market_overview()
            market_data["overview"] = overview
            market_data["quotes"] = list(overview.values())
        
        return market_data
    
    def _generate_market_analysis(self, market_data: Dict[str, Any], request: Dict[str, Any], original_query: str) -> Dict[str, Any]:
        """
        Generate human-readable market analysis using LLM
        Include market data context and educational insights
        """
        # Prepare market data summary for LLM
        data_summary = self._format_market_data_for_llm(market_data)
        
        # Create enhanced analysis prompt
        analysis_prompt = f"""
        User Query: {original_query}
        
        Market Data Retrieved:
        {data_summary}
        
        Please provide a comprehensive market analysis response that:
        
        1. **Direct Response**: Address the user's specific question immediately
        2. **Market Context**: Explain what the current data means in practical terms
        3. **Trend Analysis**: Discuss any notable patterns or movements visible in the data
        4. **Educational Insights**: Explain relevant market concepts for learning
        5. **Risk Considerations**: Mention important factors affecting these investments
        6. **Actionable Context**: Help users understand how this information might relate to their goals
        
        **Formatting Guidelines:**
        - Use clear headings and bullet points for readability
        - Include emojis for visual appeal (📈📉📊💡⚠️)
        - Explain technical terms in simple language
        - Provide specific data points to support your analysis
        - Keep explanations accessible to both beginners and experienced investors
        
        **Always Include:**
        - Appropriate disclaimers about market volatility
        - Reminder that this is educational information only
        - Suggestion to consult financial advisors for investment decisions
        
        Make your response informative, engaging, and educational while maintaining professional standards.
        """
        
        try:
            # Get LLM analysis
            llm_response = self.llm.invoke(analysis_prompt)
            response_text = llm_response.content if hasattr(llm_response, 'content') else str(llm_response)
            
            # Enhance response with additional context
            enhanced_response = self._enhance_response_with_context(response_text, market_data, request)
            
            return {
                "response": enhanced_response,
                "sources": ["Alpha Vantage API", "Market Analysis Agent", "Real-time Market Data"],
                "confidence": 0.90
            }
            
        except Exception as e:
            # Fallback to enhanced template response
            return self._generate_enhanced_fallback_response(market_data, request, original_query)
    
    def _format_market_data_for_llm(self, market_data: Dict[str, Any]) -> str:
        """Format market data into readable text for LLM processing"""
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
            for result in market_data["search_results"][:5]:  # Limit to top 5
                summary_parts.append(f"- {result['symbol']}: {result['name']} ({result['type']})")
        
        summary_parts.append(f"\nData Source: {market_data.get('data_source', 'Unknown')}")
        summary_parts.append(f"Timestamp: {market_data.get('timestamp', 'Unknown')}")
        
        return "\n".join(summary_parts)
    
    def _generate_fallback_response(self, market_data: Dict[str, Any], request: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a template response when LLM is unavailable"""
        response_parts = ["📈 **Market Analysis Report**\n"]
        
        if market_data.get("quotes"):
            response_parts.append("**📊 Current Market Data:**")
            for quote in market_data["quotes"]:
                if isinstance(quote, MarketQuote):
                    change_icon = "📈" if quote.change >= 0 else "📉"
                    performance = "gaining" if quote.change >= 0 else "declining"
                    
                    response_parts.append(
                        f"{change_icon} **{quote.symbol}**: ${quote.price:.2f} "
                        f"({performance} {abs(quote.change):.2f} or {abs(quote.change_percent):.2f}%)"
                    )
                    
                    # Add volume context
                    if quote.volume > 1000000:
                        volume_context = "high volume"
                    elif quote.volume > 500000:
                        volume_context = "moderate volume"
                    else:
                        volume_context = "light volume"
                    
                    response_parts.append(f"   └─ Trading at {volume_context}: {quote.volume:,} shares")
        
        if market_data.get("search_results"):
            response_parts.append("\n**🔍 Search Results:**")
            for result in market_data["search_results"][:3]:
                response_parts.append(f"• {result['symbol']}: {result['name']} ({result['type']})")
        
        # Add market context
        if market_data.get("overview"):
            positive_count = sum(1 for quote in market_data["overview"].values() if quote.change >= 0)
            total_count = len(market_data["overview"])
            
            if positive_count > total_count * 0.6:
                market_sentiment = "📈 **Positive market sentiment** - Most indices showing gains"
            elif positive_count < total_count * 0.4:
                market_sentiment = "📉 **Cautious market sentiment** - Most indices declining"
            else:
                market_sentiment = "⚖️ **Mixed market sentiment** - Balanced performance across indices"
            
            response_parts.append(f"\n**🎯 Market Overview:**")
            response_parts.append(market_sentiment)
        
        response_parts.extend([
            "\n**💡 Key Insights:**",
            "• Monitor volume levels for confirmation of price movements",
            "• Consider market-wide trends when evaluating individual stocks",
            "• Economic factors and news events can significantly impact prices",
            "",
            "**⚠️ Important Disclaimers:**",
            "• Market data is for informational purposes only",
            "• Past performance does not guarantee future results",
            "• Investment decisions should consider your individual financial situation",
            "• Consult with a qualified financial advisor before making investment decisions",
            "• Markets are subject to volatility and can change rapidly"
        ])
        
        return {
            "response": "\n".join(response_parts),
            "sources": ["Market Analysis Agent", "Alpha Vantage API", "Real-time Market Data"],
            "confidence": 0.75
        }
    
    def _enhance_response_with_context(self, response: str, market_data: Dict[str, Any], request: Dict[str, Any]) -> str:
        """Enhance LLM response with additional market context"""
        enhanced_parts = [response]
        
        # Add data source and timestamp info
        data_source = "Alpha Vantage API" if not self.market_provider.mock_mode else "Demo Mode"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        enhanced_parts.extend([
            "\n---",
            f"**📊 Data Source**: {data_source}",
            f"**🕐 Last Updated**: {timestamp}",
        ])
        
        # Add quick summary if multiple quotes
        if market_data.get("quotes") and len(market_data["quotes"]) > 1:
            gainers = sum(1 for q in market_data["quotes"] if q.change >= 0)
            total = len(market_data["quotes"])
            
            enhanced_parts.append(f"**📈 Performance Summary**: {gainers}/{total} stocks showing gains")
        
        return "\n".join(enhanced_parts)
    
    def _generate_enhanced_fallback_response(self, market_data: Dict[str, Any], request: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Generate enhanced fallback response with better formatting and context"""
        response_parts = [f"📈 **Market Analysis for**: *{query}*\n"]
        
        # Handle different query types with specific responses
        query_type = request.get("query_type", "general_analysis")
        
        if query_type == "market_overview" and market_data.get("overview"):
            response_parts.extend(self._format_overview_response(market_data["overview"]))
        elif query_type == "stock_quote" and market_data.get("quotes"):
            response_parts.extend(self._format_quote_response(market_data["quotes"]))
        elif query_type == "comparison" and market_data.get("quotes"):
            response_parts.extend(self._format_comparison_response(market_data["quotes"]))
        elif query_type == "symbol_search" and market_data.get("search_results"):
            response_parts.extend(self._format_search_response(market_data["search_results"]))
        else:
            response_parts.extend(self._format_general_response(market_data))
        
        # Add educational context
        response_parts.extend([
            "\n**💡 Educational Context:**",
            self._get_educational_insight(query_type, market_data),
            "",
            "**⚠️ Investment Disclaimer:**",
            "This analysis is for educational purposes only. Market conditions can change rapidly, "
            "and past performance doesn't guarantee future results. Always conduct thorough research "
            "and consider consulting with a financial advisor before making investment decisions."
        ])
        
        return {
            "response": "\n".join(response_parts),
            "sources": ["Market Analysis Agent", "Alpha Vantage API", "Educational Content"],
            "confidence": 0.80
        }
    
    def _format_overview_response(self, overview_data: Dict[str, MarketQuote]) -> List[str]:
        """Format market overview response"""
        parts = ["**📊 Market Overview:**"]
        
        index_names = {
            "SPY": "S&P 500",
            "QQQ": "NASDAQ-100", 
            "DIA": "Dow Jones",
            "IWM": "Russell 2000"
        }
        
        for symbol, quote in overview_data.items():
            index_name = index_names.get(symbol, symbol)
            change_icon = "📈" if quote.change >= 0 else "📉"
            parts.append(
                f"{change_icon} **{index_name} ({symbol})**: ${quote.price:.2f} "
                f"({quote.change:+.2f}, {quote.change_percent:+.2f}%)"
            )
        
        # Market sentiment
        positive = sum(1 for q in overview_data.values() if q.change >= 0)
        total = len(overview_data)
        sentiment_score = positive / total
        
        if sentiment_score >= 0.75:
            sentiment = "🟢 **Strong Bullish Sentiment** - Broad market strength"
        elif sentiment_score >= 0.5:
            sentiment = "🟡 **Moderate Bullish Sentiment** - Generally positive"
        elif sentiment_score >= 0.25:
            sentiment = "🟡 **Moderate Bearish Sentiment** - Some weakness"
        else:
            sentiment = "🔴 **Bearish Sentiment** - Broad market decline"
        
        parts.extend(["\n**🎯 Market Sentiment:**", sentiment])
        return parts
    
    def _format_quote_response(self, quotes: List[MarketQuote]) -> List[str]:
        """Format individual stock quote response"""
        parts = ["**📊 Stock Performance:**"]
        
        for quote in quotes:
            change_icon = "📈" if quote.change >= 0 else "📉"
            performance = "gaining" if quote.change >= 0 else "declining"
            
            parts.extend([
                f"{change_icon} **{quote.symbol}**: ${quote.price:.2f}",
                f"   ├─ {performance.title()} {abs(quote.change):.2f} ({abs(quote.change_percent):.2f}%)",
                f"   ├─ Trading Range: ${quote.low:.2f} - ${quote.high:.2f}",
                f"   └─ Volume: {quote.volume:,} shares"
            ])
        
        return parts
    
    def _format_comparison_response(self, quotes: List[MarketQuote]) -> List[str]:
        """Format stock comparison response"""
        parts = ["**⚖️ Stock Comparison:**"]
        
        if len(quotes) >= 2:
            # Sort by performance
            sorted_quotes = sorted(quotes, key=lambda x: x.change_percent, reverse=True)
            
            parts.append(f"**Best Performer**: {sorted_quotes[0].symbol} (+{sorted_quotes[0].change_percent:.2f}%)")
            if len(sorted_quotes) > 1:
                parts.append(f"**Weakest Performer**: {sorted_quotes[-1].symbol} ({sorted_quotes[-1].change_percent:+.2f}%)")
            
            parts.append("\n**Detailed Comparison:**")
            for quote in quotes:
                change_icon = "📈" if quote.change >= 0 else "📉"
                parts.append(
                    f"{change_icon} {quote.symbol}: ${quote.price:.2f} "
                    f"({quote.change:+.2f}, {quote.change_percent:+.2f}%)"
                )
        
        return parts
    
    def _format_search_response(self, search_results: List[Dict[str, str]]) -> List[str]:
        """Format symbol search response"""
        parts = ["**🔍 Symbol Search Results:**"]
        
        for i, result in enumerate(search_results[:5], 1):
            parts.append(
                f"{i}. **{result['symbol']}** - {result['name']}"
                f" ({result.get('type', 'Stock')}, {result.get('region', 'US')})"
            )
        
        if len(search_results) > 5:
            parts.append(f"\n*Showing top 5 of {len(search_results)} results*")
        
        return parts
    
    def _format_general_response(self, market_data: Dict[str, Any]) -> List[str]:
        """Format general market response"""
        parts = ["**📊 Market Information:**"]
        
        if market_data.get("quotes"):
            parts.extend(self._format_quote_response(market_data["quotes"]))
        elif market_data.get("overview"):
            parts.extend(self._format_overview_response(market_data["overview"]))
        else:
            parts.append("Market data retrieved successfully. Please specify what you'd like to analyze.")
        
        return parts
    
    def _get_educational_insight(self, query_type: str, market_data: Dict[str, Any]) -> str:
        """Get educational insight based on query type"""
        insights = {
            "market_overview": "Market indices represent the performance of specific market segments. "
                             "The S&P 500 tracks large-cap stocks, NASDAQ focuses on technology, "
                             "and the Dow Jones represents 30 major companies.",
            
            "stock_quote": "Stock prices reflect investor sentiment and company fundamentals. "
                          "Volume indicates trading interest, while daily ranges show volatility. "
                          "Consider these factors alongside company news and earnings.",
            
            "comparison": "When comparing stocks, consider not just price performance but also "
                         "market capitalization, sector trends, and fundamental metrics. "
                         "Correlation between stocks can indicate sector-wide movements.",
            
            "symbol_search": "Stock symbols (tickers) are unique identifiers for publicly traded companies. "
                           "Research companies thoroughly using financial statements, news, and analyst reports "
                           "before making investment decisions.",
            
            "general_analysis": "Market analysis involves examining price trends, volume patterns, "
                              "economic indicators, and company fundamentals. Always consider "
                              "multiple data points and maintain a long-term perspective."
        }
        
        return insights.get(query_type, insights["general_analysis"])
    
    def get_market_overview(self) -> Dict[str, Any]:
        """Get general market overview for dashboard display"""
        overview_data = self.market_provider.get_market_overview()
        return {
            "data": overview_data,
            "timestamp": datetime.now().isoformat(),
            "summary": self._create_overview_summary(overview_data)
        }
    
    def _create_overview_summary(self, overview_data: Dict[str, MarketQuote]) -> str:
        """Create a brief summary of market overview"""
        if not overview_data:
            return "Market data unavailable"
        
        positive_count = sum(1 for quote in overview_data.values() if quote.change >= 0)
        total_count = len(overview_data)
        
        if positive_count > total_count / 2:
            sentiment = "Generally positive"
        elif positive_count < total_count / 2:
            sentiment = "Generally negative"
        else:
            sentiment = "Mixed"
        
        return f"{sentiment} market sentiment across major indices"