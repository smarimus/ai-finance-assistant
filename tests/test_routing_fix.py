#!/usr/bin/env python3

"""
Test script to verify the routing logic fix for educational vs portfolio queries
"""

import sys
import os
# Add the parent directory to sys.path to find the src module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.workflow_v2 import FinanceAssistantWorkflowV2

def test_routing():
    # Create a minimal workflow instance just to test routing
    workflow = FinanceAssistantWorkflowV2(agents={})
    
    # Test cases
    test_queries = [
        # Educational questions that should go to finance_qa
        ("What is diversification and why is it important?", "finance_qa"),
        ("How do ETFs work?", "finance_qa"),
        ("What is an ETF?", "finance_qa"),
        ("Explain compound interest", "finance_qa"),
        ("Define asset allocation", "finance_qa"),
        ("Tell me about bonds", "finance_qa"),
        ("Why is diversification important?", "finance_qa"),
        ("Help me understand mutual funds", "finance_qa"),
        
        # Portfolio analysis questions that should go to portfolio_analysis
        ("Analyze my portfolio", "portfolio_analysis"),
        ("My portfolio needs rebalancing", "portfolio_analysis"),
        ("Check my asset allocation", "portfolio_analysis"),
        ("Analyze my ETF holdings", "portfolio_analysis"),
        ("My diversification strategy", "portfolio_analysis"),
        ("Rebalance my investments", "portfolio_analysis"),
        
        # Market questions that should go to market_analysis or finance_qa
        ("What's the current price of Apple?", "market_analysis"),
        ("Show me S&P 500 performance", "market_analysis"),
        
        # Goal questions that should go to goal_planning
        ("Help me plan for retirement", "goal_planning"),
        ("Set a savings goal", "goal_planning"),
    ]
    
    print("Testing Enhanced Routing Logic")
    print("=" * 50)
    
    correct_routes = 0
    total_tests = len(test_queries)
    
    for query, expected_agent in test_queries:
        # Test the portfolio query detection
        is_portfolio = workflow._is_portfolio_query(query.lower())
        is_market = workflow._is_market_query(query.lower())
        is_goal = workflow._is_goal_query(query.lower())
        
        # Determine expected route based on detection
        if is_portfolio:
            actual_agent = "portfolio_analysis"
        elif is_market:
            actual_agent = "market_analysis"
        elif is_goal:
            actual_agent = "goal_planning"
        else:
            actual_agent = "finance_qa"
        
        # Check if routing is correct
        is_correct = actual_agent == expected_agent
        status = "✅ PASS" if is_correct else "❌ FAIL"
        
        if is_correct:
            correct_routes += 1
        
        print(f"{status} '{query}' → {actual_agent} (expected: {expected_agent})")
        
        if not is_correct:
            print(f"    Portfolio: {is_portfolio}, Market: {is_market}, Goal: {is_goal}")
    
    print("\n" + "=" * 50)
    print(f"Results: {correct_routes}/{total_tests} tests passed ({correct_routes/total_tests*100:.1f}%)")
    
    if correct_routes == total_tests:
        print("🎉 All routing tests passed!")
    else:
        print("⚠️  Some routing tests failed - check the logic above")

if __name__ == "__main__":
    test_routing()
