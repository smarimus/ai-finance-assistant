# Test LangGraph workflow orchestration

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.core.workflow import FinanceAssistantWorkflow
from tests.conftest import TestHelpers

class TestFinanceAssistantWorkflow:
    """Test suite for the main workflow orchestrator"""
    
    def test_workflow_initialization(self):
        """Test workflow initialization with agents"""
        mock_agents = {
            "finance_qa": Mock(),
            "portfolio_analysis": Mock(),
            "market_analysis": Mock(),
            "goal_planning": Mock()
        }
        
        workflow = FinanceAssistantWorkflow(mock_agents)
        
        assert workflow.agents == mock_agents
        assert workflow.graph is not None
    
    def test_query_routing_to_finance_qa(self):
        """Test routing basic financial questions to Finance Q&A agent"""
        mock_agents = {
            "finance_qa": Mock(),
            "portfolio_analysis": Mock(),
            "market_analysis": Mock(),
            "goal_planning": Mock()
        }
        
        workflow = FinanceAssistantWorkflow(mock_agents)
        
        # Test basic financial education queries
        test_queries = [
            "What is a stock?",
            "Explain diversification",
            "How do bonds work?",
            "What is compound interest?"
        ]
        
        for query in test_queries:
            # Mock state
            state = {
                "user_query": query,
                "conversation_history": [],
                "current_agent": None,
                "portfolio_data": None,
                "portfolio_analysis": None,
                "market_context": None,
                "market_cache": {},
                "agent_responses": [],
                "rag_context": [],
                "risk_tolerance": None,
                "investment_goals": [],
                "user_profile": {},
                "session_id": "test",
                "timestamp": "2024-01-15T10:00:00",
                "error_context": None
            }
            
            # Test routing logic
            result_state = workflow._route_query(state)
            assert result_state["current_agent"] == "finance_qa"
    
    def test_query_routing_to_portfolio_analysis(self):
        """Test routing portfolio-related queries to Portfolio agent"""
        mock_agents = {
            "finance_qa": Mock(),
            "portfolio_analysis": Mock(),
            "market_analysis": Mock(),
            "goal_planning": Mock()
        }
        
        workflow = FinanceAssistantWorkflow(mock_agents)
        
        # Test portfolio analysis queries
        portfolio_queries = [
            "Analyze my portfolio",
            "What's my portfolio allocation?",
            "Review my holdings",
            "How diversified am I?",
            "Check my portfolio balance"
        ]
        
        for query in portfolio_queries:
            state = {
                "user_query": query,
                "conversation_history": [],
                "current_agent": None,
                "portfolio_data": None,
                "portfolio_analysis": None,
                "market_context": None,
                "market_cache": {},
                "agent_responses": [],
                "rag_context": [],
                "risk_tolerance": None,
                "investment_goals": [],
                "user_profile": {},
                "session_id": "test",
                "timestamp": "2024-01-15T10:00:00",
                "error_context": None
            }
            
            result_state = workflow._route_query(state)
            assert result_state["current_agent"] == "portfolio_analysis"
    
    def test_query_routing_to_market_analysis(self):
        """Test routing market-related queries to Market agent"""
        mock_agents = {
            "finance_qa": Mock(),
            "portfolio_analysis": Mock(),
            "market_analysis": Mock(),
            "goal_planning": Mock()
        }
        
        workflow = FinanceAssistantWorkflow(mock_agents)
        
        # Test market analysis queries
        market_queries = [
            "What's the price of AAPL?",
            "How is the market doing?",
            "Show me TSLA performance",
            "Market trends today",
            "S&P 500 index"
        ]
        
        for query in market_queries:
            state = {
                "user_query": query,
                "conversation_history": [],
                "current_agent": None,
                "portfolio_data": None,
                "portfolio_analysis": None,
                "market_context": None,
                "market_cache": {},
                "agent_responses": [],
                "rag_context": [],
                "risk_tolerance": None,
                "investment_goals": [],
                "user_profile": {},
                "session_id": "test",
                "timestamp": "2024-01-15T10:00:00",
                "error_context": None
            }
            
            result_state = workflow._route_query(state)
            assert result_state["current_agent"] == "market_analysis"
    
    def test_query_routing_to_goal_planning(self):
        """Test routing goal-related queries to Goal Planning agent"""
        mock_agents = {
            "finance_qa": Mock(),
            "portfolio_analysis": Mock(),
            "market_analysis": Mock(),
            "goal_planning": Mock()
        }
        
        workflow = FinanceAssistantWorkflow(mock_agents)
        
        # Test goal planning queries
        goal_queries = [
            "Help me plan for retirement",
            "How much should I save?",
            "Set a savings goal",
            "Plan for buying a house",
            "Education savings target"
        ]
        
        for query in goal_queries:
            state = {
                "user_query": query,
                "conversation_history": [],
                "current_agent": None,
                "portfolio_data": None,
                "portfolio_analysis": None,
                "market_context": None,
                "market_cache": {},
                "agent_responses": [],
                "rag_context": [],
                "risk_tolerance": None,
                "investment_goals": [],
                "user_profile": {},
                "session_id": "test",
                "timestamp": "2024-01-15T10:00:00",
                "error_context": None
            }
            
            result_state = workflow._route_query(state)
            assert result_state["current_agent"] == "goal_planning"
    
    def test_agent_execution_success(self):
        """Test successful agent execution"""
        mock_finance_qa = Mock()
        mock_finance_qa.execute.return_value = {
            "agent_response": "Stocks represent ownership in a company.",
            "sources": ["financial_basics.pdf"],
            "confidence": 0.9
        }
        
        mock_agents = {
            "finance_qa": mock_finance_qa,
            "portfolio_analysis": Mock(),
            "market_analysis": Mock(),
            "goal_planning": Mock()
        }
        
        workflow = FinanceAssistantWorkflow(mock_agents)
        
        state = {
            "user_query": "What is a stock?",
            "conversation_history": [],
            "current_agent": "finance_qa",
            "portfolio_data": None,
            "portfolio_analysis": None,
            "market_context": None,
            "market_cache": {},
            "agent_responses": [],
            "rag_context": [],
            "risk_tolerance": None,
            "investment_goals": [],
            "user_profile": {},
            "session_id": "test",
            "timestamp": "2024-01-15T10:00:00",
            "error_context": None
        }
        
        result_state = workflow._execute_finance_qa(state)
        
        assert len(result_state["agent_responses"]) == 1
        assert result_state["agent_responses"][0]["agent"] == "finance_qa"
        assert result_state["agent_responses"][0]["confidence"] == 0.9
        mock_finance_qa.execute.assert_called_once()
    
    def test_agent_execution_error(self):
        """Test agent execution with error handling"""
        mock_finance_qa = Mock()
        mock_finance_qa.execute.side_effect = Exception("Agent execution failed")
        
        mock_agents = {
            "finance_qa": mock_finance_qa,
            "portfolio_analysis": Mock(),
            "market_analysis": Mock(),
            "goal_planning": Mock()
        }
        
        workflow = FinanceAssistantWorkflow(mock_agents)
        
        state = {
            "user_query": "What is a stock?",
            "conversation_history": [],
            "current_agent": "finance_qa",
            "portfolio_data": None,
            "portfolio_analysis": None,
            "market_context": None,
            "market_cache": {},
            "agent_responses": [],
            "rag_context": [],
            "risk_tolerance": None,
            "investment_goals": [],
            "user_profile": {},
            "session_id": "test",
            "timestamp": "2024-01-15T10:00:00",
            "error_context": None
        }
        
        result_state = workflow._execute_finance_qa(state)
        
        assert result_state["error_context"] is not None
        assert result_state["error_context"]["agent"] == "finance_qa"
        assert "Agent execution failed" in result_state["error_context"]["error"]
    
    def test_workflow_completion_logic(self):
        """Test workflow completion and continuation logic"""
        mock_agents = {
            "finance_qa": Mock(),
            "portfolio_analysis": Mock(),
            "market_analysis": Mock(),
            "goal_planning": Mock()
        }
        
        workflow = FinanceAssistantWorkflow(mock_agents)
        
        # Test high confidence should end workflow
        state_high_confidence = {
            "agent_responses": [
                {
                    "agent": "finance_qa",
                    "response": "Complete answer",
                    "confidence": 0.95,
                    "sources": ["source.pdf"]
                }
            ]
        }
        
        result = workflow._check_completion(state_high_confidence)
        assert result == "end"
        
        # Test low confidence should continue
        state_low_confidence = {
            "agent_responses": [
                {
                    "agent": "finance_qa",
                    "response": "Partial answer",
                    "confidence": 0.5,
                    "sources": []
                }
            ]
        }
        
        result = workflow._check_completion(state_low_confidence)
        assert result == "continue"
    
    def test_error_handling_workflow(self):
        """Test error handling in workflow"""
        mock_agents = {
            "finance_qa": Mock(),
            "portfolio_analysis": Mock(),
            "market_analysis": Mock(),
            "goal_planning": Mock()
        }
        
        workflow = FinanceAssistantWorkflow(mock_agents)
        
        error_state = {
            "error_context": {
                "agent": "finance_qa",
                "error": "Something went wrong"
            },
            "agent_responses": []
        }
        
        result_state = workflow._handle_errors(error_state)
        
        assert len(result_state["agent_responses"]) == 1
        assert result_state["agent_responses"][0]["agent"] == "error_handler"
        assert result_state["agent_responses"][0]["error"] == True
        assert "apologize" in result_state["agent_responses"][0]["response"].lower()
    
    def test_full_workflow_run(self):
        """Test complete workflow execution"""
        # Mock successful agent
        mock_finance_qa = Mock()
        mock_finance_qa.execute.return_value = {
            "agent_response": "Diversification reduces risk by spreading investments.",
            "sources": ["investment_guide.pdf"],
            "confidence": 0.9
        }
        
        mock_agents = {
            "finance_qa": mock_finance_qa,
            "portfolio_analysis": Mock(),
            "market_analysis": Mock(),
            "goal_planning": Mock()
        }
        
        # Mock the graph execution
        with patch('src.core.workflow.StateGraph') as mock_graph_class:
            mock_graph = Mock()
            mock_graph.invoke.return_value = {
                "user_query": "What is diversification?",
                "conversation_history": [
                    {
                        "user": "What is diversification?",
                        "assistant": "Diversification reduces risk by spreading investments.",
                        "agent": "finance_qa",
                        "timestamp": "2024-01-15T10:00:00",
                        "sources": ["investment_guide.pdf"]
                    }
                ],
                "agent_responses": [
                    {
                        "agent": "finance_qa",
                        "response": "Diversification reduces risk by spreading investments.",
                        "confidence": 0.9,
                        "sources": ["investment_guide.pdf"]
                    }
                ]
            }
            mock_graph_class.return_value.compile.return_value = mock_graph
            
            workflow = FinanceAssistantWorkflow(mock_agents)
            result = workflow.run("What is diversification?")
            
            assert result["response"] == "Diversification reduces risk by spreading investments."
            assert result["agent"] == "finance_qa"
            assert len(result["sources"]) > 0
            assert result["conversation_history"] is not None
