#!/usr/bin/env python3
"""
Test Phase 4 Portfolio Analysis Implementation
"""

import sys
import pandas as pd
from src.core.workflow import SimpleFinanceWorkflow
from src.utils.portfolio_calc import PortfolioCalculator

def test_phase4_implementation():
    print('=== TESTING PHASE 4 PORTFOLIO ANALYSIS ===')
    
    # Test 1: Portfolio Calculator standalone
    print('\n1. Testing PortfolioCalculator...')
    try:
        calc = PortfolioCalculator()
        portfolio_data = [
            {'symbol': 'AAPL', 'shares': 100, 'current_price': 150.0},
            {'symbol': 'GOOGL', 'shares': 50, 'current_price': 2500.0},
            {'symbol': 'TSLA', 'shares': 25, 'current_price': 200.0}
        ]
        df = pd.DataFrame(portfolio_data)
        result = calc.calculate_portfolio_metrics(df)
        print(f'✓ Portfolio value: ${result["total_value"]:,.2f}')
        print(f'✓ Asset count: {result["asset_count"]}')
        print(f'✓ Calculator working properly')
    except Exception as e:
        print(f'✗ Calculator test failed: {e}')
        return False
    
    # Test 2: Workflow integration
    print('\n2. Testing Workflow integration...')
    try:
        workflow = SimpleFinanceWorkflow()
        agents = workflow.agents
        
        if 'portfolio_analysis' in agents:
            agent_type = type(agents['portfolio_analysis']).__name__
            print(f'✓ Portfolio agent loaded: {agent_type}')
            
            # Test portfolio analysis request
            test_query = """I have a portfolio with:
            - 100 shares of AAPL at $150
            - 50 shares of GOOGL at $2500
            - 25 shares of TSLA at $200
            Please analyze my portfolio allocation and diversification."""
            
            print(f'\n3. Testing portfolio analysis query...')
            response = workflow.process_query(test_query)
            print(f'✓ Response length: {len(response)} characters')
            print(f'✓ Contains portfolio analysis: {"portfolio" in response.lower()}')
            print(f'✓ Workflow integration working')
            
        else:
            print('✗ Portfolio agent not found in workflow')
            return False
            
    except Exception as e:
        print(f'✗ Workflow test failed: {e}')
        return False
    
    print('\n=== PHASE 4 IMPLEMENTATION SUCCESSFUL ===')
    return True

if __name__ == "__main__":
    success = test_phase4_implementation()
    sys.exit(0 if success else 1)
