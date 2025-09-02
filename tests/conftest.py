# Test configuration and fixtures for AI Finance Assistant tests

import pytest
from unittest.mock import Mock, MagicMock
from typing import Dict, Any
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.state import FinanceAssistantState
from src.utils.portfolio_calc import PortfolioCalculator, FinancialCalculator

@pytest.fixture
def mock_llm():
    """Mock LLM for testing"""
    llm = Mock()
    llm.predict = Mock(return_value="Mocked LLM response")
    return llm

@pytest.fixture
def mock_retriever():
    """Mock retriever for testing"""
    retriever = Mock()
    retriever.retrieve = Mock(return_value=[
        {
            "content": "Diversification is the practice of spreading investments across various financial instruments.",
            "score": 0.9,
            "metadata": {"source": "investment_basics.pdf"},
            "source": "investment_basics.pdf"
        }
    ])
    return retriever

@pytest.fixture
def sample_portfolio_data():
    """Sample portfolio data for testing"""
    return {
        "holdings": [
            {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "quantity": 10,
                "current_price": 150.00,
                "cost_basis": 140.00,
                "sector": "Technology"
            },
            {
                "symbol": "MSFT",
                "name": "Microsoft Corporation",
                "quantity": 5,
                "current_price": 300.00,
                "cost_basis": 280.00,
                "sector": "Technology"
            },
            {
                "symbol": "JNJ",
                "name": "Johnson & Johnson",
                "quantity": 8,
                "current_price": 165.00,
                "cost_basis": 160.00,
                "sector": "Healthcare"
            }
        ],
        "cash": 1000.00,
        "last_updated": "2024-01-15"
    }

@pytest.fixture
def sample_finance_state():
    """Sample FinanceAssistantState for testing"""
    return FinanceAssistantState(
        user_query="What is diversification?",
        conversation_history=[],
        current_agent=None,
        portfolio_data=None,
        portfolio_analysis=None,
        market_context=None,
        market_cache={},
        agent_responses=[],
        rag_context=[],
        risk_tolerance=None,
        investment_goals=[],
        user_profile={},
        session_id="test_session_123",
        timestamp="2024-01-15T10:00:00",
        error_context=None
    )

@pytest.fixture
def portfolio_calculator():
    """PortfolioCalculator instance for testing"""
    return PortfolioCalculator()

@pytest.fixture
def financial_calculator():
    """FinancialCalculator instance for testing"""
    return FinancialCalculator()

@pytest.fixture
def mock_market_data():
    """Mock market data responses"""
    return {
        "AAPL": {
            "symbol": "AAPL",
            "price": 150.00,
            "change": 2.50,
            "change_percent": "1.69",
            "volume": 50000000,
            "latest_trading_day": "2024-01-15",
            "previous_close": 147.50
        },
        "MSFT": {
            "symbol": "MSFT",
            "price": 300.00,
            "change": -5.00,
            "change_percent": "-1.64",
            "volume": 30000000,
            "latest_trading_day": "2024-01-15",
            "previous_close": 305.00
        }
    }

@pytest.fixture
def mock_api_response():
    """Mock API response for Alpha Vantage"""
    return {
        "Global Quote": {
            "01. symbol": "AAPL",
            "05. price": "150.0000",
            "09. change": "2.5000",
            "10. change percent": "1.69%",
            "06. volume": "50000000",
            "07. latest trading day": "2024-01-15",
            "08. previous close": "147.5000"
        }
    }

# Test utilities
class TestHelpers:
    @staticmethod
    def assert_valid_agent_response(response: Dict[str, Any]):
        """Assert that an agent response has required fields"""
        required_fields = ["agent_response", "sources", "confidence"]
        for field in required_fields:
            assert field in response, f"Missing required field: {field}"
        
        assert isinstance(response["agent_response"], str), "agent_response must be string"
        assert isinstance(response["sources"], list), "sources must be list"
        assert isinstance(response["confidence"], (int, float)), "confidence must be numeric"
        assert 0 <= response["confidence"] <= 1, "confidence must be between 0 and 1"
    
    @staticmethod
    def assert_valid_portfolio_metrics(metrics: Dict[str, Any]):
        """Assert that portfolio metrics have required fields"""
        required_fields = ["total_portfolio_value", "allocation"]
        for field in required_fields:
            assert field in metrics, f"Missing required field: {field}"
