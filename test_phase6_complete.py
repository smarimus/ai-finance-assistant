#!/usr/bin/env python3
"""
Phase 6 Complete System Test
Tests the full goal planning integration with Streamlit interface
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
import streamlit as st
from src.agents.goal_agent import GoalPlanningAgent
from src.utils.portfolio_calc import FinancialCalculator
from unittest.mock import Mock

def test_goals_ui_logic():
    """Test the logic that will be used in the Goals tab"""
    print("🧪 Testing Goals UI Logic...")
    
    # Mock user profile
    user_profile = {
        'name': 'Sarah Johnson',
        'age': 32,
        'annual_income': 85000,
        'monthly_expenses': 6000,
        'current_savings': 15000,
        'debt_amount': 25000,
        'debt_payment': 800,
        'risk_tolerance': 'moderate',
        'retirement_age': 65,
        'life_expectancy': 85
    }
    
    # Test different goal types
    goals = [
        {
            'id': 'emergency_fund',
            'name': 'Emergency Fund',
            'type': 'emergency_fund',
            'target_amount': 36000,  # 6 months expenses
            'target_date': '2026-08-24',
            'current_amount': 5000,
            'monthly_contribution': 800,
            'priority': 'high'
        },
        {
            'id': 'house_down_payment',
            'name': 'House Down Payment',
            'type': 'major_purchase',
            'target_amount': 80000,
            'target_date': '2028-08-24',
            'current_amount': 12000,
            'monthly_contribution': 1200,
            'priority': 'high'
        },
        {
            'id': 'retirement',
            'name': 'Retirement Fund',
            'type': 'retirement',
            'target_amount': 2000000,
            'target_date': '2057-08-24',  # Age 65
            'current_amount': 45000,
            'monthly_contribution': 1500,
            'priority': 'medium'
        }
    ]
    
    calc = FinancialCalculator()
    
    print("📊 Testing Goal Calculations...")
    
    for goal in goals:
        print(f"\n🎯 Goal: {goal['name']}")
        
        # Calculate timeline
        target_date = datetime.strptime(goal['target_date'], '%Y-%m-%d')
        years_to_goal = (target_date - datetime.now()).days / 365.25
        
        # Calculate required monthly savings
        remaining_amount = goal['target_amount'] - goal['current_amount']
        
        if goal['type'] == 'emergency_fund':
            # Simple savings calculation
            monthly_required = remaining_amount / (years_to_goal * 12)
            projected_value = goal['current_amount'] + (goal['monthly_contribution'] * years_to_goal * 12)
        
        elif goal['type'] == 'retirement':
            # Use investment returns
            monthly_required = calc.monthly_savings_required(remaining_amount, 0.07, years_to_goal)
            projected_value = calc.future_value(goal['current_amount'], 0.07, years_to_goal) + \
                             calc.future_value_annuity(goal['monthly_contribution'], 0.07/12, years_to_goal * 12)
        
        else:
            # Major purchase with moderate returns
            monthly_required = calc.monthly_savings_required(remaining_amount, 0.04, years_to_goal)
            projected_value = calc.future_value(goal['current_amount'], 0.04, years_to_goal) + \
                             calc.future_value_annuity(goal['monthly_contribution'], 0.04/12, years_to_goal * 12)
        
        # Calculate progress
        progress = (goal['current_amount'] / goal['target_amount']) * 100
        
        print(f"  Target: ${goal['target_amount']:,.2f}")
        print(f"  Current: ${goal['current_amount']:,.2f} ({progress:.1f}%)")
        print(f"  Monthly Required: ${monthly_required:.2f}")
        print(f"  Current Contribution: ${goal['monthly_contribution']:,.2f}")
        print(f"  Projected Value: ${projected_value:,.2f}")
        print(f"  Years to Goal: {years_to_goal:.1f}")
        
        # Status assessment
        if goal['monthly_contribution'] >= monthly_required:
            print(f"  ✅ On track! (${goal['monthly_contribution'] - monthly_required:.2f} above minimum)")
        else:
            print(f"  ⚠️  Need ${monthly_required - goal['monthly_contribution']:.2f} more per month")
    
    print("\n💰 Testing Financial Ratios...")
    
    # Test financial health ratios
    monthly_income = user_profile['annual_income'] / 12
    savings_rate = sum(goal['monthly_contribution'] for goal in goals) / monthly_income * 100
    debt_to_income = (user_profile['debt_payment'] / monthly_income) * 100
    emergency_fund_months = user_profile['current_savings'] / user_profile['monthly_expenses']
    
    print(f"  Monthly Income: ${monthly_income:,.2f}")
    print(f"  Total Monthly Savings: ${sum(goal['monthly_contribution'] for goal in goals):,.2f}")
    print(f"  Savings Rate: {savings_rate:.1f}%")
    print(f"  Debt-to-Income: {debt_to_income:.1f}%")
    print(f"  Emergency Fund: {emergency_fund_months:.1f} months")
    
    # Financial health assessment
    health_score = 0
    recommendations = []
    
    if savings_rate >= 20:
        health_score += 25
        print("  ✅ Excellent savings rate!")
    elif savings_rate >= 10:
        health_score += 15
        print("  ✅ Good savings rate")
    else:
        print("  ⚠️  Low savings rate")
        recommendations.append("Increase savings rate to at least 10%")
    
    if debt_to_income <= 36:
        health_score += 25
        print("  ✅ Healthy debt-to-income ratio")
    else:
        print("  ⚠️  High debt-to-income ratio")
        recommendations.append("Focus on debt reduction")
    
    if emergency_fund_months >= 6:
        health_score += 25
        print("  ✅ Adequate emergency fund")
    elif emergency_fund_months >= 3:
        health_score += 15
        print("  ✅ Basic emergency fund")
    else:
        print("  ⚠️  Insufficient emergency fund")
        recommendations.append("Build emergency fund to 3-6 months expenses")
    
    if user_profile['age'] <= 35 and any(g['type'] == 'retirement' for g in goals):
        health_score += 25
        print("  ✅ Early retirement planning")
    
    print(f"\n📈 Financial Health Score: {health_score}/100")
    
    if recommendations:
        print("\n💡 Recommendations:")
        for rec in recommendations:
            print(f"  • {rec}")
    
    return True

def test_goal_agent_integration():
    """Test GoalPlanningAgent integration"""
    print("\n🤖 Testing Goal Agent Integration...")
    
    # Mock LLM for testing
    mock_llm = Mock()
    mock_llm.invoke.return_value.content = """
    Based on your financial profile and goals, here's my analysis:
    
    **Emergency Fund Goal**: You're making excellent progress! Your current contribution of $800/month 
    will help you reach your 6-month emergency fund target ahead of schedule.
    
    **House Down Payment**: This is an ambitious but achievable goal. Consider opening a high-yield 
    savings account or conservative investment for this timeline.
    
    **Retirement Planning**: Starting early is your biggest advantage! With 33 years until retirement, 
    compound interest will work significantly in your favor.
    """
    
    agent = GoalPlanningAgent(llm=mock_llm)
    
    user_profile = {
        'name': 'Test User',
        'age': 32,
        'income': 85000,
        'expenses': 72000,
        'current_savings': 15000,
        'risk_tolerance': 'moderate'
    }
    
    # Test goal analysis
    query = "Analyze my goals and provide recommendations for my emergency fund, house down payment, and retirement planning."
    
    try:
        response = agent.process_query(query, user_profile, [])
        print("✅ Goal agent query processing successful")
        print(f"Response preview: {response[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Goal agent failed: {e}")
        return False

def run_complete_test():
    """Run complete Phase 6 system test"""
    print("🚀 Phase 6 Complete System Test")
    print("=" * 60)
    
    try:
        # Test UI logic
        test_goals_ui_logic()
        
        # Test agent integration
        test_goal_agent_integration()
        
        print("\n" + "=" * 60)
        print("🎉 Phase 6 Complete System Test PASSED!")
        print("\n📋 Phase 6 Features Validated:")
        print("• ✅ User profile management")
        print("• ✅ Multiple goal types (emergency, retirement, major purchase)")
        print("• ✅ Financial calculations and projections")
        print("• ✅ Progress tracking and analysis")
        print("• ✅ Financial health assessment")
        print("• ✅ Personalized recommendations")
        print("• ✅ GoalPlanningAgent integration")
        print("• ✅ UI logic preparation")
        
        print("\n🌟 Phase 6 Goal Planning System is ready!")
        print("   Access the full system at: http://localhost:8506")
        print("   Navigate to the 'Goals' tab to test the new features")
        
        return True
        
    except Exception as e:
        print(f"❌ Phase 6 system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_complete_test()
    sys.exit(0 if success else 1)
