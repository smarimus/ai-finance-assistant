# Alpha Vantage LangChain Tools for market data
# Implement LangChain BaseTool pattern for tool calling agents

from typing import Optional, List, Dict, Any, Type
from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun
from pydantic import BaseModel, Field
import json
import logging

from src.data.market_data import MarketDataProvider, MarketQuote

logger = logging.getLogger(__name__)


class StockQuoteInput(BaseModel):
    """Input schema for stock quote tool"""
    symbol: str = Field(..., description="Stock ticker symbol (e.g., 'AAPL', 'MSFT')")


class MultipleQuotesInput(BaseModel):
    """Input schema for multiple quotes tool"""
    symbols: List[str] = Field(..., description="List of stock ticker symbols")


class SymbolSearchInput(BaseModel):
    """Input schema for symbol search tool"""
    query: str = Field(..., description="Search query for stock symbols or company names")


class AlphaVantageQuoteTool(BaseTool):
    """
    LangChain tool for fetching real-time stock quotes using Alpha Vantage API
    
    This tool allows the LLM to autonomously fetch stock price data
    when users ask about specific stocks.
    """
    
    name: str = "get_stock_quote"
    description: str = """
    Get real-time stock quote data for a specific stock symbol.
    Use this tool when users ask about current stock prices, market performance of specific stocks,
    or want to know "how is [STOCK] doing today".
    
    Input should be a stock ticker symbol like 'AAPL', 'MSFT', 'GOOGL', etc.
    Returns current price, change, percentage change, volume, and other market data.
    """
    args_schema: Type[BaseModel] = StockQuoteInput
    market_provider: MarketDataProvider = Field(default_factory=MarketDataProvider)
    
    def __init__(self, market_provider: Optional[MarketDataProvider] = None, **kwargs):
        super().__init__(**kwargs)
        if market_provider:
            object.__setattr__(self, 'market_provider', market_provider)
    
    def _run(
        self,
        symbol: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Execute the tool to get stock quote"""
        try:
            quote = self.market_provider.get_quote(symbol.upper())
            
            if not quote:
                return f"Unable to fetch quote data for {symbol}. Please check the symbol and try again."
            
            # Format the response for the LLM
            change_direction = "📈" if quote.change >= 0 else "📉"
            result = f"""
Stock Quote for {quote.symbol}:
{change_direction} Price: ${quote.price:.2f}
📊 Change: {quote.change:+.2f} ({quote.change_percent:+.2f}%)
📈 High: ${quote.high:.2f}
📉 Low: ${quote.low:.2f}
🔄 Volume: {quote.volume:,}
🕐 Previous Close: ${quote.previous_close:.2f}
⏰ Last Updated: {quote.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

Data Source: {"Alpha Vantage API" if not self.market_provider.mock_mode else "Mock Data"}
            """.strip()
            
            logger.info(f"Tool executed successfully for {symbol}")
            return result
            
        except Exception as e:
            logger.error(f"Error in stock quote tool for {symbol}: {str(e)}")
            return f"Error fetching quote for {symbol}: {str(e)}"


class AlphaVantageMultipleQuotesTool(BaseTool):
    """
    LangChain tool for fetching multiple stock quotes at once
    
    Useful for portfolio analysis or comparing multiple stocks
    """
    
    name: str = "get_multiple_quotes"
    description: str = """
    Get real-time quotes for multiple stock symbols at once.
    Use this tool when users want to compare multiple stocks or ask about portfolio performance.
    
    Input should be a list of stock ticker symbols.
    Returns formatted data for all requested stocks.
    """
    args_schema: Type[BaseModel] = MultipleQuotesInput
    market_provider: MarketDataProvider = Field(default_factory=MarketDataProvider)
    
    def __init__(self, market_provider: Optional[MarketDataProvider] = None, **kwargs):
        super().__init__(**kwargs)
        if market_provider:
            object.__setattr__(self, 'market_provider', market_provider)
    
    def _run(
        self,
        symbols: List[str],
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Execute the tool to get multiple stock quotes"""
        try:
            # Clean and uppercase symbols
            clean_symbols = [s.upper().strip() for s in symbols]
            quotes = self.market_provider.get_multiple_quotes(clean_symbols)
            
            if not quotes:
                return f"Unable to fetch quote data for symbols: {', '.join(clean_symbols)}"
            
            # Format results
            result_parts = ["📊 **Multiple Stock Quotes:**\n"]
            
            for quote in quotes:
                change_direction = "📈" if quote.change >= 0 else "📉"
                result_parts.append(
                    f"{change_direction} **{quote.symbol}**: ${quote.price:.2f} "
                    f"({quote.change:+.2f}, {quote.change_percent:+.2f}%)"
                )
            
            data_source = "Alpha Vantage API" if not self.market_provider.mock_mode else "Mock Data"
            result_parts.append(f"\n*Data Source: {data_source}*")
            
            logger.info(f"Tool executed successfully for {len(quotes)} symbols")
            return "\n".join(result_parts)
            
        except Exception as e:
            logger.error(f"Error in multiple quotes tool: {str(e)}")
            return f"Error fetching quotes: {str(e)}"


class AlphaVantageMarketOverviewTool(BaseTool):
    """
    LangChain tool for getting general market overview
    
    Provides data on major market indices
    """
    
    name: str = "get_market_overview"
    description: str = """
    Get a general market overview showing major market indices performance.
    Use this tool when users ask about "how are the markets doing", "market overview", 
    or general market conditions.
    
    No input required. Returns data for major indices like S&P 500, NASDAQ, etc.
    """
    market_provider: MarketDataProvider = Field(default_factory=MarketDataProvider)
    
    def __init__(self, market_provider: Optional[MarketDataProvider] = None, **kwargs):
        super().__init__(**kwargs)
        if market_provider:
            object.__setattr__(self, 'market_provider', market_provider)
    
    def _run(
        self,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Execute the tool to get market overview"""
        try:
            overview = self.market_provider.get_market_overview()
            
            if not overview:
                return "Unable to fetch market overview data."
            
            # Format results
            result_parts = ["📈 **Market Overview:**\n"]
            
            index_names = {
                "SPY": "S&P 500",
                "QQQ": "NASDAQ-100", 
                "DIA": "Dow Jones",
                "IWM": "Russell 2000"
            }
            
            for symbol, quote in overview.items():
                index_name = index_names.get(symbol, symbol)
                change_direction = "📈" if quote.change >= 0 else "📉"
                result_parts.append(
                    f"{change_direction} **{index_name} ({symbol})**: ${quote.price:.2f} "
                    f"({quote.change:+.2f}, {quote.change_percent:+.2f}%)"
                )
            
            # Calculate market sentiment
            positive_moves = sum(1 for quote in overview.values() if quote.change >= 0)
            total_indices = len(overview)
            
            if positive_moves > total_indices / 2:
                sentiment = "📈 Generally positive market sentiment"
            elif positive_moves < total_indices / 2:
                sentiment = "📉 Generally negative market sentiment"
            else:
                sentiment = "⚖️ Mixed market sentiment"
            
            result_parts.append(f"\n{sentiment}")
            
            data_source = "Alpha Vantage API" if not self.market_provider.mock_mode else "Mock Data"
            result_parts.append(f"\n*Data Source: {data_source}*")
            
            logger.info("Market overview tool executed successfully")
            return "\n".join(result_parts)
            
        except Exception as e:
            logger.error(f"Error in market overview tool: {str(e)}")
            return f"Error fetching market overview: {str(e)}"


class AlphaVantageSymbolSearchTool(BaseTool):
    """
    LangChain tool for searching stock symbols
    
    Helps users find stock symbols for companies
    """
    
    name: str = "search_stock_symbols"
    description: str = """
    Search for stock symbols by company name or keywords.
    Use this tool when users ask to "find stocks for [company/industry]" or 
    want to look up ticker symbols for specific companies.
    
    Input should be company names, industry terms, or keywords.
    Returns matching stock symbols with company names.
    """
    args_schema: Type[BaseModel] = SymbolSearchInput
    market_provider: MarketDataProvider = Field(default_factory=MarketDataProvider)
    
    def __init__(self, market_provider: Optional[MarketDataProvider] = None, **kwargs):
        super().__init__(**kwargs)
        if market_provider:
            object.__setattr__(self, 'market_provider', market_provider)
    
    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Execute the tool to search for stock symbols"""
        try:
            results = self.market_provider.search_symbols(query)
            
            if not results:
                return f"No matching stocks found for query: '{query}'"
            
            # Format results
            result_parts = [f"🔍 **Stock Search Results for '{query}':**\n"]
            
            for i, result in enumerate(results[:10], 1):  # Limit to top 10
                result_parts.append(
                    f"{i}. **{result['symbol']}** - {result['name']} "
                    f"({result['type']}, {result['region']})"
                )
            
            if len(results) > 10:
                result_parts.append(f"\n*Showing top 10 of {len(results)} results*")
            
            data_source = "Alpha Vantage API" if not self.market_provider.mock_mode else "Mock Data"
            result_parts.append(f"\n*Data Source: {data_source}*")
            
            logger.info(f"Symbol search tool executed successfully for '{query}'")
            return "\n".join(result_parts)
            
        except Exception as e:
            logger.error(f"Error in symbol search tool for '{query}': {str(e)}")
            return f"Error searching for symbols: {str(e)}"


def create_market_tools(market_provider: Optional[MarketDataProvider] = None) -> List[BaseTool]:
    """
    Factory function to create all Alpha Vantage tools
    
    Args:
        market_provider: Optional market data provider instance
        
    Returns:
        List of configured Alpha Vantage tools
    """
    provider = market_provider or MarketDataProvider()
    
    tools = [
        AlphaVantageQuoteTool(provider),
        AlphaVantageMultipleQuotesTool(provider),
        AlphaVantageMarketOverviewTool(provider),
        AlphaVantageSymbolSearchTool(provider)
    ]
    
    logger.info(f"Created {len(tools)} Alpha Vantage tools")
    return tools


# Tool registry for easy access
MARKET_TOOLS_REGISTRY = {
    "stock_quote": AlphaVantageQuoteTool,
    "multiple_quotes": AlphaVantageMultipleQuotesTool,
    "market_overview": AlphaVantageMarketOverviewTool,
    "symbol_search": AlphaVantageSymbolSearchTool
}
