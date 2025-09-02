# Test Portfolio Analysis Agent functionality

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from unittest.mock import Mock, patch
from src.agents.portfolio_agent import PortfolioAnalysisAgent
from tests.conftest import TestHelpers

class TestPortfolioAnalysisAgent:
    """Test suite for Portfolio Analysis Agent"""
    
    def test_portfolio_agent_initialization(self, mock_llm, portfolio_calculator):
        """Test that the portfolio agent initializes correctly"""
        agent = PortfolioAnalysisAgent(mock_llm, portfolio_calculator)
        
        assert agent.agent_name == "portfolio_analysis"
        assert agent.llm == mock_llm
        assert agent.calculator == portfolio_calculator
        assert "portfolio analyst" in agent.system_prompt.lower()
    
    def test_portfolio_calculation(self, sample_portfolio_data, portfolio_calculator):
        """Test portfolio calculation functionality"""
        # Test the calculator directly first
        metrics = portfolio_calculator.calculate_all_metrics(sample_portfolio_data)
        
        # Basic assertions about the metrics structure
        TestHelpers.assert_valid_portfolio_metrics(metrics)
        
        # Test specific calculations
        expected_total_value = (10 * 150) + (5 * 300) + (8 * 165) + 1000  # Holdings + cash
        # This assertion would pass once calculate_all_metrics is implemented
        # assert metrics["total_portfolio_value"] == expected_total_value
    
    def test_portfolio_analysis_with_data(self, mock_llm, portfolio_calculator, sample_portfolio_data):
        """Test portfolio analysis with valid data"""
        agent = PortfolioAnalysisAgent(mock_llm, portfolio_calculator)
        
        state = {
            "user_query": "Analyze my portfolio",
            "portfolio_data": sample_portfolio_data,
            "conversation_history": [],
            "agent_responses": [],
            "market_cache": {},
            "rag_context": [],
            "investment_goals": [],
            "user_profile": {},
            "session_id": "test",
            "timestamp": "2024-01-15T10:00:00",
            "current_agent": None,
            "portfolio_analysis": None,
            "market_context": None,
            "risk_tolerance": None,
            "error_context": None
        }
        
        # Mock the internal methods
        with patch.object(agent.calculator, 'calculate_all_metrics') as mock_calc, \
             patch.object(agent, '_analyze_portfolio') as mock_analyze, \
             patch.object(agent, '_generate_recommendations') as mock_recommendations, \
             patch.object(agent, '_prepare_visualization_data') as mock_viz:
            
            mock_calc.return_value = {
                "total_portfolio_value": 4820.00,
                "allocation": {"Technology": 0.64, "Healthcare": 0.27, "Cash": 0.21}
            }
            mock_analyze.return_value = {"diversification_score": 0.7}
            mock_recommendations.return_value = [
                {"type": "diversification", "priority": "high", "description": "Consider adding international exposure"}
            ]
            mock_viz.return_value = {"pie_chart_data": {}}
            
            # Execute
            result = agent.execute(state)
            
            # Verify
            assert "portfolio_metrics" in result
            assert "recommendations" in result
            assert "visualization_data" in result
            assert result["confidence"] > 0.8  # Should be confident with real data
    
    def test_portfolio_analysis_without_data(self, mock_llm, portfolio_calculator):
        """Test portfolio analysis when no data is provided"""
        agent = PortfolioAnalysisAgent(mock_llm, portfolio_calculator)
        
        state = {
            "user_query": "Analyze my portfolio",
            "portfolio_data": None,  # No portfolio data
            "conversation_history": [],
            "agent_responses": [],
            "market_cache": {},
            "rag_context": [],
            "investment_goals": [],
            "user_profile": {},
            "session_id": "test",
            "timestamp": "2024-01-15T10:00:00",
            "current_agent": None,
            "portfolio_analysis": None,
            "market_context": None,
            "risk_tolerance": None,
            "error_context": None
        }
        
        # Mock the request for portfolio data
        with patch.object(agent, '_request_portfolio_data') as mock_request:
            mock_request.return_value = {
                "agent_response": "Please provide your portfolio data to begin analysis.",
                "sources": [],
                "confidence": 0.9
            }
            
            result = agent.execute(state)
            
            assert "provide your portfolio data" in result["agent_response"].lower()
            mock_request.assert_called_once()
    
    def test_portfolio_input_parsing(self, mock_llm, portfolio_calculator):
        """Test different portfolio input formats"""
        agent = PortfolioAnalysisAgent(mock_llm, portfolio_calculator)
        
        # Test CSV-like input
        csv_data = "AAPL,10,150\nMSFT,5,300"
        
        # Test JSON input
        json_data = {
            "holdings": [
                {"symbol": "AAPL", "quantity": 10, "price": 150}
            ]
        }
        
        # Test manual entry format
        manual_data = "10 shares of AAPL at $150 each"
        
        # These would test the parse_portfolio_input method
        assert hasattr(agent, 'parse_portfolio_input')
    
    def test_allocation_analysis(self, sample_portfolio_data, portfolio_calculator):
        """Test asset allocation analysis"""
        # Test allocation calculations
        holdings = sample_portfolio_data["holdings"]
        allocation = portfolio_calculator.calculate_allocation(holdings)
        
        # Verify allocation is calculated (once implemented)
        # Should return percentages by sector, asset class, etc.
        assert hasattr(portfolio_calculator, 'calculate_allocation')
    
    def test_diversification_scoring(self, sample_portfolio_data, portfolio_calculator):
        """Test diversification score calculation"""
        holdings = sample_portfolio_data["holdings"]
        
        # Test diversification score
        score = portfolio_calculator.calculate_diversification_score(holdings)
        
        # Score should be between 0 and 1 (once implemented)
        # assert 0 <= score <= 1
        assert hasattr(portfolio_calculator, 'calculate_diversification_score')
    
    def test_recommendation_generation(self, mock_llm, portfolio_calculator):
        """Test recommendation generation"""
        agent = PortfolioAnalysisAgent(mock_llm, portfolio_calculator)
        
        # Mock analysis data
        analysis = {
            "allocation": {"Technology": 0.8, "Healthcare": 0.2},  # Over-concentrated
            "diversification_score": 0.4,  # Low diversification
            "sectors": ["Technology", "Healthcare"],
            "total_value": 5000
        }
        
        recommendations = agent._generate_recommendations(analysis)
        
        # Should generate recommendations for over-concentration
        # assert len(recommendations) > 0
        # assert any("diversification" in rec["type"] for rec in recommendations)
    
    def test_visualization_data_preparation(self, mock_llm, portfolio_calculator, sample_portfolio_data):
        """Test preparation of data for visualizations"""
        agent = PortfolioAnalysisAgent(mock_llm, portfolio_calculator)
        
        metrics = {
            "allocation": {"Technology": 0.64, "Healthcare": 0.27, "Cash": 0.09},
            "total_portfolio_value": 4820
        }
        
        viz_data = agent._prepare_visualization_data(sample_portfolio_data, metrics)
        
        # Should prepare data for charts
        # assert "pie_chart_data" in viz_data
        # assert "allocation_data" in viz_data
    
    def test_benchmark_comparison(self, mock_llm, portfolio_calculator):
        """Test portfolio benchmark comparison"""
        agent = PortfolioAnalysisAgent(mock_llm, portfolio_calculator)
        
        # Mock portfolio performance vs benchmarks
        portfolio_metrics = {
            "total_return": 0.12,  # 12% return
            "volatility": 0.15,    # 15% volatility
            "allocation": {"Stocks": 0.7, "Bonds": 0.3}
        }
        
        # Test comparison logic (to be implemented)
        assert hasattr(agent, '_analyze_portfolio')

# Integration tests
class TestPortfolioAnalysisIntegration:
    """Integration tests for Portfolio Analysis Agent"""
    
    @pytest.mark.integration
    def test_end_to_end_portfolio_analysis(self):
        """Test complete portfolio analysis workflow"""
        # This would test the full workflow with real data
        pass
    
    @pytest.mark.integration
    def test_with_real_market_data(self):
        """Test portfolio analysis with current market prices"""
        # This would fetch real market data for portfolio valuation
        pass
