#!/usr/bin/env python3
"""
Simple test for Phase 4 Portfolio Analysis components without workflow
"""

import sys
import pandas as pd

def test_portfolio_calculator():
    """Test the portfolio calculator standalone"""
    print('=== TESTING PORTFOLIO CALCULATOR ===')
    
    try:
        from src.utils.portfolio_calc import PortfolioCalculator
        
        calc = PortfolioCalculator()
        
        # Test data
        portfolio_data = [
            {'symbol': 'AAPL', 'shares': 100, 'current_price': 150.0},
            {'symbol': 'GOOGL', 'shares': 50, 'current_price': 2500.0},
            {'symbol': 'TSLA', 'shares': 25, 'current_price': 200.0}
        ]
        
        # Convert to expected format (list of holdings)
        holdings = portfolio_data
        
        # Test individual methods
        total_value = calc.calculate_total_value(holdings)
        allocations = calc.calculate_allocation(holdings)
        div_score = calc.calculate_diversification_score(holdings)
        concentration = calc.calculate_concentration_risk(holdings)
        
        print(f'✓ Portfolio value: ${total_value:,.2f}')
        print(f'✓ Asset count: {len(holdings)}')
        print(f'✓ Allocation calculation works: {len(allocations)} assets')
        print(f'✓ Diversification score: {div_score:.2f}')
        print(f'✓ Concentration risk: {concentration["top_holding_percentage"]:.1f}%')
        
        # Test comprehensive metrics
        portfolio_data_dict = {"holdings": holdings}
        all_metrics = calc.calculate_all_metrics(portfolio_data_dict)
        print(f'✓ All metrics calculation: {len(all_metrics)} metrics calculated')
        
        return True
        
    except Exception as e:
        print(f'✗ Portfolio calculator test failed: {e}')
        import traceback
        traceback.print_exc()
        return False

def test_portfolio_agent():
    """Test the portfolio agent standalone"""
    print('\n=== TESTING PORTFOLIO AGENT ===')
    
    try:
        from src.agents.portfolio_agent import PortfolioAnalysisAgent
        from src.utils.portfolio_calc import PortfolioCalculator
        
        # Create a mock LLM for testing
        class MockLLM:
            def invoke(self, messages):
                return type('MockResponse', (), {
                    'content': 'Mock analysis: Your portfolio shows moderate diversification with tech stock concentration.'
                })()
        
        calc = PortfolioCalculator()
        mock_llm = MockLLM()
        agent = PortfolioAnalysisAgent(mock_llm, calc)
        
        # Test portfolio data in expected format (holdings list)
        holdings = [
            {'symbol': 'AAPL', 'shares': 100, 'current_price': 150.0},
            {'symbol': 'GOOGL', 'shares': 50, 'current_price': 2500.0},
            {'symbol': 'TSLA', 'shares': 25, 'current_price': 200.0}
        ]
        
        # Create state object that agent expects
        from src.core.state import FinanceAssistantState
        
        state = FinanceAssistantState()
        state.portfolio_data = {"holdings": holdings}
        state.intent = "portfolio_analysis"
        
        # Test analysis
        result = agent.execute(state)
        
        print(f'✓ Agent created successfully')
        print(f'✓ Analysis result type: {type(result)}')
        
        # Check if result contains expected response
        if isinstance(result, dict) and 'response' in result:
            response = result['response']
            print(f'✓ Response generated: {len(response)} characters')
            print(f'✓ Contains analysis content: {"analysis" in response.lower() or "portfolio" in response.lower()}')
        elif isinstance(result, str):
            print(f'✓ Analysis generated: {len(result)} characters') 
            print(f'✓ Contains analysis content: {"analysis" in result.lower() or "portfolio" in result.lower()}')
        else:
            print(f'✓ Result format: {result}')
        
        return True
        
    except Exception as e:
        print(f'✗ Portfolio agent test failed: {e}')
        import traceback
        traceback.print_exc()
        return False

def test_streamlit_components():
    """Test that streamlit components can be imported"""
    print('\n=== TESTING STREAMLIT COMPONENTS ===')
    
    try:
        from src.web_app.portfolio_tab import render_portfolio_tab
        print('✓ Portfolio tab can be imported')
        
        # Test if the function signature is correct
        import inspect
        sig = inspect.signature(render_portfolio_tab)
        print(f'✓ Portfolio tab function signature: {list(sig.parameters.keys())}')
        
        return True
        
    except Exception as e:
        print(f'✗ Streamlit component test failed: {e}')
        import traceback
        traceback.print_exc()
        return False

def main():
    print('=== PHASE 4 PORTFOLIO ANALYSIS COMPONENT TESTS ===')
    
    results = []
    results.append(test_portfolio_calculator())
    results.append(test_portfolio_agent())
    results.append(test_streamlit_components())
    
    success_count = sum(results)
    total_count = len(results)
    
    print(f'\n=== SUMMARY: {success_count}/{total_count} TESTS PASSED ===')
    
    if success_count == total_count:
        print('🎉 Phase 4 Portfolio Analysis implementation is working!')
        return True
    else:
        print('❌ Some components need fixing')
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
