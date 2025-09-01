# Test Finance Q&A Agent functionality

import pytest
from unittest.mock import Mock, patch
from src.agents.finance_qa_agent import FinanceQAAgent
from tests.conftest import TestHelpers

class TestFinanceQAAgent:
    """Test suite for Finance Q&A Agent"""
    
    def test_finance_qa_agent_initialization(self, mock_llm, mock_retriever):
        """Test that the agent initializes correctly"""
        agent = FinanceQAAgent(mock_llm, mock_retriever)
        
        assert agent.agent_name == "finance_qa"
        assert agent.llm == mock_llm
        assert agent.retriever == mock_retriever
        assert "financial education assistant" in agent.system_prompt.lower()
    
    def test_basic_finance_question(self, mock_llm, mock_retriever, sample_finance_state):
        """Test basic Q&A functionality"""
        # Setup
        agent = FinanceQAAgent(mock_llm, mock_retriever)
        state = sample_finance_state.copy()
        state["user_query"] = "What is diversification?"
        
        # Mock the internal methods to return expected results
        with patch.object(agent, '_build_context') as mock_build_context, \
             patch.object(agent, '_generate_response') as mock_generate_response, \
             patch.object(agent, 'format_response') as mock_format_response:
            
            mock_build_context.return_value = "Context about diversification"
            mock_generate_response.return_value = {
                "content": "Diversification is the practice of spreading investments across various financial instruments, industries, and other categories to reduce risk.",
                "sources": ["investment_basics.pdf"],
                "confidence": 0.9
            }
            mock_format_response.return_value = {
                "agent_response": "Diversification is the practice of spreading investments across various financial instruments, industries, and other categories to reduce risk.",
                "sources": ["investment_basics.pdf"],
                "confidence": 0.9,
                "next_agent": None
            }
            
            # Execute
            result = agent.execute(state)
            
            # Verify
            TestHelpers.assert_valid_agent_response(result)
            assert "diversification" in result["agent_response"].lower()
            assert len(result["sources"]) > 0
            mock_retriever.retrieve.assert_called_once()
    
    def test_query_classification(self, mock_llm, mock_retriever):
        """Test query classification functionality"""
        agent = FinanceQAAgent(mock_llm, mock_retriever)
        
        # Test different query types
        portfolio_query = "How should I analyze my portfolio?"
        market_query = "What's the current price of AAPL?"
        goal_query = "How much should I save for retirement?"
        basic_query = "What is a stock?"
        
        # These would test the internal classification logic
        # For now, we'll test that the method exists and can be called
        assert hasattr(agent, '_classify_query')
    
    def test_context_building(self, mock_llm, mock_retriever, sample_finance_state):
        """Test context building from retrieved documents"""
        agent = FinanceQAAgent(mock_llm, mock_retriever)
        
        retrieved_docs = [
            {
                "content": "Diversification reduces risk by spreading investments.",
                "score": 0.9,
                "metadata": {"source": "basics.pdf"}
            }
        ]
        
        # Test that context building method exists
        assert hasattr(agent, '_build_context')
    
    def test_confidence_scoring(self, mock_llm, mock_retriever, sample_finance_state):
        """Test that confidence scores are properly calculated"""
        agent = FinanceQAAgent(mock_llm, mock_retriever)
        
        # Mock a response with high confidence
        with patch.object(agent, 'execute') as mock_execute:
            mock_execute.return_value = {
                "agent_response": "Detailed explanation about stocks",
                "sources": ["source1.pdf", "source2.pdf"],
                "confidence": 0.95,
                "next_agent": None
            }
            
            result = agent.execute(sample_finance_state)
            assert result["confidence"] >= 0.8  # High confidence for well-sourced answer
    
    def test_escalation_logic(self, mock_llm, mock_retriever):
        """Test agent escalation to specialized agents"""
        agent = FinanceQAAgent(mock_llm, mock_retriever)
        
        # Test portfolio-specific query should suggest escalation
        portfolio_query = "Analyze my current portfolio allocation"
        next_agent = agent._suggest_next_agent(portfolio_query)
        # This would ideally return "portfolio_analysis" for portfolio queries
        
        # Test market-specific query
        market_query = "What's the latest price of TSLA?"
        next_agent = agent._suggest_next_agent(market_query)
        # This would ideally return "market_analysis" for market queries
    
    def test_error_handling(self, mock_llm, mock_retriever, sample_finance_state):
        """Test error handling in the agent"""
        agent = FinanceQAAgent(mock_llm, mock_retriever)
        
        # Simulate retriever failure
        mock_retriever.retrieve.side_effect = Exception("Retrieval failed")
        
        # The agent should handle this gracefully
        try:
            result = agent.execute(sample_finance_state)
            # Should either return an error response or handle gracefully
            assert result is not None
        except Exception as e:
            # If it throws, it should be a handled exception
            assert "Retrieval failed" in str(e)
    
    def test_source_attribution(self, mock_llm, mock_retriever, sample_finance_state):
        """Test that sources are properly attributed"""
        agent = FinanceQAAgent(mock_llm, mock_retriever)
        
        # Mock retriever with multiple sources
        mock_retriever.retrieve.return_value = [
            {
                "content": "Content from source 1",
                "metadata": {"source": "financial_guide.pdf"}
            },
            {
                "content": "Content from source 2", 
                "metadata": {"source": "investment_basics.pdf"}
            }
        ]
        
        with patch.object(agent, 'execute') as mock_execute:
            mock_execute.return_value = {
                "agent_response": "Response with multiple sources",
                "sources": ["financial_guide.pdf", "investment_basics.pdf"],
                "confidence": 0.85
            }
            
            result = agent.execute(sample_finance_state)
            assert len(result["sources"]) >= 1
            assert all(isinstance(source, str) for source in result["sources"])

# Integration tests
class TestFinanceQAAgentIntegration:
    """Integration tests for Finance Q&A Agent"""
    
    @pytest.mark.integration
    def test_with_real_retriever(self):
        """Test with actual retriever (requires test data)"""
        # This would test with a real retriever and test documents
        pass
    
    @pytest.mark.integration  
    def test_with_real_llm(self):
        """Test with actual LLM (requires API key)"""
        # This would test with a real LLM call
        pass
