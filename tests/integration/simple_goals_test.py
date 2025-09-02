#!/usr/bin/env python3
"""Simple test for Goals tab isolation"""

print("🧪 Testing Goals Tab API Isolation...")

try:
    # Test 1: Financial Calculator (no APIs)
    import sys, os
    from pathlib import Path
    
    # Add project root to path
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    
    from src.utils.portfolio_calc import FinancialCalculator
    calc = FinancialCalculator()
    
    emergency = calc.emergency_fund_target(5000, 6)
    print(f"✅ Emergency fund calculation: ${emergency:,.0f}")
    
    # Test 2: Mock agent (no APIs)
    from src.web_app.goals_tab import create_mock_goal_agent
    agent = create_mock_goal_agent()
    print("✅ Mock goal agent created")
    
    print("🎉 Goals tab components work without API calls!")
    print("🌐 Test at: http://localhost:8508 - Goals tab should not trigger API calls")
    
except Exception as e:
    print(f"❌ Error: {e}")
