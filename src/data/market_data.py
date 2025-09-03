# Market data provider for Alpha Vantage API integration
# Handle API calls, caching, and data formatting

import os
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import time
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class MarketQuote:
    """Structure for market quote data"""
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    high: float
    low: float
    open: float
    previous_close: float
    timestamp: datetime

class MarketDataProvider:
    """
    Enhanced Market data provider using Alpha Vantage API
    
    Features:
    - Real-time stock quotes with structured data
    - Historical data retrieval
    - API rate limiting and intelligent caching
    - Error handling and mock data fallbacks
    - Symbol search functionality
    - Market overview dashboard
    """
    
    def __init__(self, api_key: Optional[str] = None, cache_ttl: int = 300):
        self.api_key = api_key or os.getenv("ALPHA_VANTAGE_API_KEY")
        self.base_url = "https://www.alphavantage.co/query"
        self.cache = {}
        self.cache_ttl = cache_ttl
        self.last_request_time = 0
        self.min_request_interval = 12  # 5 requests per minute = 12 seconds between requests
        
        # Check if we should use mock mode
        if not self.api_key or self.api_key == "your_alpha_vantage_api_key_here":
            logger.warning("Alpha Vantage API key not configured - using mock data")
            self.mock_mode = True
        else:
            self.mock_mode = False
            logger.info("Alpha Vantage API initialized successfully")
    
    def get_quote(self, symbol: str) -> Optional[MarketQuote]:
        """
        Get real-time quote for a stock symbol
        
        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')
            
        Returns:
            MarketQuote object or None if error
        """
        cache_key = f"quote_{symbol}"
        
        # Check cache first
        if self._is_cached(cache_key):
            logger.info(f"Returning cached quote for {symbol}")
            return self.cache[cache_key]["data"]
        
        if self.mock_mode:
            quote = self._get_mock_quote(symbol)
            self._cache_data(cache_key, quote)
            return quote
        
        # Rate limiting
        self._rate_limit()
        
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if "Global Quote" in data:
                quote_data = self._parse_quote_response(data["Global Quote"], symbol)
                if quote_data:
                    self._cache_data(cache_key, quote_data)
                    return quote_data
            else:
                logger.error(f"Unexpected API response for {symbol}: {data}")
                return self._get_mock_quote(symbol)  # Fallback to mock
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {symbol}: {e}")
            return self._get_mock_quote(symbol)  # Fallback to mock
    
    def get_market_overview(self) -> Dict[str, MarketQuote]:
        """Get general market overview with major indices"""
        indices = ["SPY", "QQQ", "DIA", "IWM"]  # S&P 500, NASDAQ, Dow Jones, Russell 2000 ETFs
        overview = {}
        
        for index in indices:
            quote = self.get_quote(index)
            if quote:
                overview[index] = quote
        
        return overview
    
    def get_multiple_quotes(self, symbols: List[str]) -> List[MarketQuote]:
        """Get quotes for multiple symbols"""
        quotes = []
        for symbol in symbols:
            quote = self.get_quote(symbol)
            if quote:
                quotes.append(quote)
        return quotes
    
    def search_symbols(self, query: str) -> List[Dict[str, str]]:
        """Search for stock symbols matching query"""
        if self.mock_mode:
            return self._get_mock_search_results(query)
        
        cache_key = f"search_{query}"
        if self._is_cached(cache_key):
            return self.cache[cache_key]["data"]
        
        try:
            self._rate_limit()
            
            params = {
                "function": "SYMBOL_SEARCH",
                "keywords": query,
                "apikey": self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            if "bestMatches" in data:
                for match in data["bestMatches"][:10]:
                    results.append({
                        "symbol": match.get("1. symbol", ""),
                        "name": match.get("2. name", ""),
                        "type": match.get("3. type", ""),
                        "region": match.get("4. region", ""),
                        "currency": match.get("8. currency", "")
                    })
            
            self._cache_data(cache_key, results)
            return results
            
        except Exception as e:
            logger.error(f"Error searching symbols for '{query}': {e}")
            return self._get_mock_search_results(query)
    
    def _parse_quote_response(self, raw_data: Dict[str, str], symbol: str) -> Optional[MarketQuote]:
        """Parse Alpha Vantage response into MarketQuote object"""
        try:
            return MarketQuote(
                symbol=raw_data.get("01. symbol", symbol),
                price=float(raw_data.get("05. price", 0)),
                change=float(raw_data.get("09. change", 0)),
                change_percent=float(raw_data.get("10. change percent", "0%").replace("%", "")),
                volume=int(raw_data.get("06. volume", 0)),
                high=float(raw_data.get("03. high", 0)),
                low=float(raw_data.get("04. low", 0)),
                open=float(raw_data.get("02. open", 0)),
                previous_close=float(raw_data.get("08. previous close", 0)),
                timestamp=datetime.now()
            )
        except (ValueError, KeyError) as e:
            logger.error(f"Error parsing quote data for {symbol}: {e}")
            return None
    
    def _get_mock_quote(self, symbol: str) -> MarketQuote:
        """Generate mock quote data for testing"""
        import random
        
        # Mock prices for common symbols
        base_prices = {
            "AAPL": 150.0, "MSFT": 300.0, "GOOGL": 2500.0, "AMZN": 3000.0, "TSLA": 800.0,
            "SPY": 400.0, "QQQ": 350.0, "DIA": 340.0, "IWM": 200.0,
            "NVDA": 400.0, "META": 250.0, "NFLX": 400.0
        }
        
        base_price = base_prices.get(symbol, 100.0)
        price = base_price * (1 + random.uniform(-0.05, 0.05))
        change = random.uniform(-5.0, 5.0)
        change_percent = (change / price) * 100
        
        return MarketQuote(
            symbol=symbol,
            price=round(price, 2),
            change=round(change, 2),
            change_percent=round(change_percent, 2),
            volume=random.randint(1000000, 50000000),
            high=round(price * 1.02, 2),
            low=round(price * 0.98, 2),
            open=round(price * 1.005, 2),
            previous_close=round(price - change, 2),
            timestamp=datetime.now()
        )
    
    def _get_mock_search_results(self, query: str) -> List[Dict[str, str]]:
        """Generate mock search results"""
        mock_results = [
            {"symbol": "AAPL", "name": "Apple Inc.", "type": "Equity", "region": "United States", "currency": "USD"},
            {"symbol": "MSFT", "name": "Microsoft Corporation", "type": "Equity", "region": "United States", "currency": "USD"},
            {"symbol": "GOOGL", "name": "Alphabet Inc.", "type": "Equity", "region": "United States", "currency": "USD"},
            {"symbol": "TSLA", "name": "Tesla Inc.", "type": "Equity", "region": "United States", "currency": "USD"},
            {"symbol": "NVDA", "name": "NVIDIA Corporation", "type": "Equity", "region": "United States", "currency": "USD"}
        ]
        
        # Filter based on query
        filtered = [r for r in mock_results if query.lower() in r["symbol"].lower() or query.lower() in r["name"].lower()]
        return filtered if filtered else mock_results[:3]
    
    def _is_cached(self, cache_key: str) -> bool:
        """Check if data is in cache and still valid"""
        if cache_key not in self.cache:
            return False
        
        cache_time = self.cache[cache_key]["timestamp"]
        return (datetime.now() - cache_time).seconds < self.cache_ttl
    
    def _cache_data(self, cache_key: str, data: Any) -> None:
        """Store data in cache with timestamp"""
        self.cache[cache_key] = {
            "data": data,
            "timestamp": datetime.now()
        }
    
    def _rate_limit(self) -> None:
        """Implement rate limiting for API requests"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache.clear()
        logger.info("Market data cache cleared")