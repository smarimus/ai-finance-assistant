# Create a Goal Planning Agent for financial goal setting and tracking
# Calculate time-value-of-money scenarios, retirement planning, savings goals
# Generate projection charts and actionable savings plans
# Integrate with portfolio data for goal-based recommendations

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
import re
import json
from src.agents.base_agent import BaseFinanceAgent
from src.utils.portfolio_calc import FinancialCalculator

class GoalPlanningAgent(BaseFinanceAgent):
    """
    Goal Planning Agent for comprehensive financial goal setting and tracking
    
    Capabilities:
    - Help users set realistic financial goals with timelines
    - Calculate required savings rates and investment returns
    - Generate multiple scenarios (conservative, moderate, aggressive)
    - Provide actionable steps to achieve goals
    - Track progress against established goals
    - Retirement planning with detailed projections
    - Emergency fund planning
    - Major purchase planning (house, education, etc.)
    """
    
    def __init__(self, llm, financial_calculator: Optional[FinancialCalculator] = None):
        system_prompt = """
        You are a comprehensive financial planning expert specializing in goal-based investing and life planning. Your role is to:
        
        1. **Goal Definition**: Help users define clear, specific, measurable financial goals
        2. **Realistic Planning**: Calculate achievable timelines and savings requirements based on current situation
        3. **Scenario Analysis**: Provide multiple projection scenarios with different risk levels and assumptions
        4. **Action Planning**: Break down complex goals into specific monthly/yearly actionable steps
        5. **Progress Tracking**: Monitor goal progress and adjust plans based on changing circumstances
        6. **Risk Assessment**: Align investment strategies with goal timelines and risk tolerance
        7. **Education**: Explain financial concepts and help users understand their planning options
        
        **Goal Categories You Handle:**
        - **Retirement Planning**: 401k, IRA, pension planning with detailed projections
        - **Emergency Fund**: 3-6 months expenses with liquid savings recommendations
        - **Major Purchases**: Home buying, education funding, major life events
        - **Investment Goals**: Wealth building, income generation, specific financial targets
        - **Debt Management**: Payoff strategies integrated with savings goals
        
        **Planning Framework:**
        - **Current Assessment**: Analyze existing financial situation and resources
        - **Goal Prioritization**: Help users prioritize multiple competing goals
        - **Timeline Planning**: Create realistic timelines with milestone checkpoints
        - **Savings Strategy**: Calculate required monthly/annual contributions
        - **Investment Allocation**: Recommend appropriate investment mix for each goal
        - **Risk Management**: Consider inflation, market volatility, and life changes
        - **Progress Monitoring**: Track actual vs. projected progress with adjustments
        
        **Response Guidelines:**
        - Provide specific, actionable recommendations with clear next steps
        - Include multiple scenarios (conservative, moderate, aggressive) when relevant
        - Explain assumptions clearly and highlight key risks/considerations
        - Use examples and analogies to make complex concepts accessible
        - Always include appropriate disclaimers about projections and assumptions
        - Encourage regular review and adjustment of plans
        
        **Mathematical Accuracy:**
        - Use proper time-value-of-money calculations
        - Account for inflation in long-term projections
        - Consider tax implications where relevant
        - Provide sensitivity analysis for key variables
        
        Make your advice practical, encouraging, and focused on achievable outcomes while maintaining realistic expectations about market performance and life changes.
        """
        super().__init__(llm, [], "goal_planning", system_prompt)
        self.calculator = financial_calculator or FinancialCalculator()
        
        # Goal type definitions and typical parameters
        self.goal_types = {
            'retirement': {
                'typical_timeline': 30,
                'typical_amount_multiplier': 25,  # 25x annual expenses
                'return_assumptions': {'conservative': 0.05, 'moderate': 0.07, 'aggressive': 0.09}
            },
            'emergency_fund': {
                'typical_timeline': 1,
                'typical_amount_multiplier': 6,  # 6 months expenses
                'return_assumptions': {'conservative': 0.02, 'moderate': 0.03, 'aggressive': 0.04}
            },
            'house': {
                'typical_timeline': 5,
                'down_payment_percent': 0.20,
                'return_assumptions': {'conservative': 0.04, 'moderate': 0.06, 'aggressive': 0.08}
            },
            'education': {
                'typical_timeline': 18,
                'inflation_rate': 0.06,  # Education inflation higher than general
                'return_assumptions': {'conservative': 0.05, 'moderate': 0.07, 'aggressive': 0.09}
            },
            'investment': {
                'typical_timeline': 10,
                'return_assumptions': {'conservative': 0.06, 'moderate': 0.08, 'aggressive': 0.10}
            }
        }
    
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process goal planning request and generate comprehensive plan
        
        Steps:
        1. Extract goal details from user query
        2. Assess current financial situation from state
        3. Calculate multiple projection scenarios
        4. Generate actionable savings plan
        5. Prepare visualization data for goal tracking
        """
        query = state.get("user_query", "")
        portfolio_data = state.get("portfolio_data", {})
        existing_goals = state.get("investment_goals", [])
        user_profile = state.get("user_profile", {})
        
        try:
            # Parse goal request
            goal_details = self._parse_goal_request(query)
            
            # Calculate scenarios
            scenarios = self._calculate_goal_scenarios(goal_details, portfolio_data, user_profile)
            
            # Generate action plan
            action_plan = self._create_action_plan(scenarios, goal_details, user_profile)
            
            # Prepare tracking data
            tracking_data = self._prepare_goal_tracking(scenarios, goal_details)
            
            # Generate comprehensive response
            response = self._format_goal_plan(scenarios, action_plan, goal_details)
            
            return {
                "agent_response": response,
                "goal_scenarios": scenarios,
                "action_plan": action_plan,
                "tracking_data": tracking_data,
                "visualization_data": self._prepare_goal_viz_data(scenarios),
                "goal_details": goal_details,
                "sources": ["Financial Planning Calculations", "Time-Value-of-Money Analysis", "Goal Planning Best Practices"],
                "confidence": 0.90,
                "next_agent": None,
                "agent_name": "goal_planning"
            }
            
        except Exception as e:
            return self._generate_fallback_response(query, str(e))
    
    def _parse_goal_request(self, query: str) -> Dict[str, Any]:
        """
        Extract goal details from user query using LLM analysis and pattern matching
        """
        query_lower = query.lower()
        
        # Determine goal type
        goal_type = 'investment'  # default
        if any(word in query_lower for word in ['retire', 'retirement', '401k', 'ira', 'pension']):
            goal_type = 'retirement'
        elif any(word in query_lower for word in ['emergency', 'fund', 'rainy day']):
            goal_type = 'emergency_fund'
        elif any(word in query_lower for word in ['house', 'home', 'down payment', 'mortgage']):
            goal_type = 'house'
        elif any(word in query_lower for word in ['education', 'college', 'tuition', 'school']):
            goal_type = 'education'
        
        # Extract numerical values
        amounts = re.findall(r'\$?[\d,]+\.?\d*', query)
        years = re.findall(r'(\d+)\s*(?:years?|yrs?)', query_lower)
        
        # Parse amounts
        target_amount = None
        if amounts:
            try:
                amount_str = amounts[0].replace('$', '').replace(',', '')
                target_amount = float(amount_str)
            except ValueError:
                pass
        
        # Parse timeline
        timeline_years = None
        if years:
            try:
                timeline_years = int(years[0])
            except ValueError:
                pass
        
        # Extract age-related information for retirement planning
        current_age = None
        retirement_age = None
        age_mentions = re.findall(r'age\s*(\d+)', query_lower)
        if age_mentions:
            if 'retire' in query_lower or 'retirement' in query_lower:
                retirement_age = int(age_mentions[0])
            else:
                current_age = int(age_mentions[0])
        
        # Extract income/savings information
        income_mentions = re.findall(r'(?:income|earn|make)\s*\$?[\d,]+', query_lower)
        savings_mentions = re.findall(r'(?:save|saving)\s*\$?[\d,]+', query_lower)
        
        return {
            'goal_type': goal_type,
            'target_amount': target_amount,
            'timeline_years': timeline_years,
            'current_age': current_age,
            'retirement_age': retirement_age,
            'original_query': query,
            'income_mentioned': len(income_mentions) > 0,
            'savings_mentioned': len(savings_mentions) > 0
        }
    
    def _calculate_goal_scenarios(self, goal_details: Dict, portfolio_data: Dict, user_profile: Dict) -> Dict[str, Any]:
        """
        Calculate multiple scenarios with different return assumptions
        """
        goal_type = goal_details['goal_type']
        target_amount = goal_details.get('target_amount')
        timeline_years = goal_details.get('timeline_years')
        
        # Use defaults if not specified
        if not timeline_years:
            timeline_years = self.goal_types[goal_type]['typical_timeline']
        
        # Estimate target amount if not provided
        if not target_amount:
            target_amount = self._estimate_target_amount(goal_type, user_profile, timeline_years)
        
        # Get current savings
        current_savings = self._estimate_current_savings(portfolio_data, user_profile)
        
        # Calculate scenarios
        scenarios = {}
        return_assumptions = self.goal_types[goal_type]['return_assumptions']
        
        for scenario_name, annual_return in return_assumptions.items():
            scenarios[scenario_name] = self._calculate_scenario(
                target_amount=target_amount,
                timeline_years=timeline_years,
                annual_return=annual_return,
                current_savings=current_savings,
                goal_type=goal_type,
                user_profile=user_profile
            )
        
        # Add feasibility analysis
        scenarios['feasibility'] = self._assess_feasibility(scenarios, user_profile)
        
        return {
            'goal_details': goal_details,
            'target_amount': target_amount,
            'timeline_years': timeline_years,
            'current_savings': current_savings,
            'scenarios': scenarios
        }
    
    def _calculate_scenario(self, target_amount: float, timeline_years: int, annual_return: float, 
                          current_savings: float, goal_type: str, user_profile: Dict = None) -> Dict[str, Any]:
        """Calculate specific scenario projections"""
        
        if user_profile is None:
            user_profile = {}
        
        # Future value of current savings
        fv_current_savings = self.calculator.future_value(current_savings, annual_return, timeline_years)
        
        # Additional amount needed
        additional_needed = max(0, target_amount - fv_current_savings)
        
        # Monthly savings required
        monthly_savings = 0
        if additional_needed > 0:
            monthly_savings = self.calculator.monthly_savings_required(
                additional_needed, annual_return, timeline_years
            )
        
        # Create year-by-year projections
        projections = []
        balance = current_savings
        annual_contributions = monthly_savings * 12
        
        for year in range(timeline_years + 1):
            if year > 0:
                # Add annual return
                balance *= (1 + annual_return)
                # Add annual contributions
                balance += annual_contributions
            
            projections.append({
                'year': year,
                'age': (user_profile.get('current_age', 30) + year) if user_profile.get('current_age') else None,
                'balance': round(balance, 2),
                'annual_contribution': annual_contributions if year > 0 else 0,
                'cumulative_contributions': round(current_savings + (annual_contributions * year), 2)
            })
        
        return {
            'annual_return': annual_return,
            'monthly_savings_required': round(monthly_savings, 2),
            'annual_savings_required': round(annual_contributions, 2),
            'total_contributions': round(current_savings + (annual_contributions * timeline_years), 2),
            'final_balance': round(balance, 2),
            'goal_achieved': balance >= target_amount,
            'surplus_or_deficit': round(balance - target_amount, 2),
            'projections': projections
        }
    
    def _estimate_target_amount(self, goal_type: str, user_profile: Dict, timeline_years: int) -> float:
        """Estimate target amount based on goal type and user profile"""
        
        annual_income = user_profile.get('annual_income', 75000)  # Default estimate
        annual_expenses = user_profile.get('annual_expenses', annual_income * 0.8)
        
        if goal_type == 'retirement':
            # 25x annual expenses (4% withdrawal rule)
            return annual_expenses * 25
        elif goal_type == 'emergency_fund':
            # 6 months of expenses
            return annual_expenses * 0.5
        elif goal_type == 'house':
            # Estimate based on typical home prices (regional variation)
            home_price = user_profile.get('target_home_price', 400000)
            down_payment_percent = self.goal_types['house']['down_payment_percent']
            return home_price * down_payment_percent
        elif goal_type == 'education':
            # Estimate college costs with inflation
            current_annual_cost = 50000  # Average private college
            inflation_rate = self.goal_types['education']['inflation_rate']
            inflated_cost = current_annual_cost * ((1 + inflation_rate) ** timeline_years)
            return inflated_cost * 4  # 4 years of college
        else:
            # General investment goal
            return 100000  # Default target
    
    def _estimate_current_savings(self, portfolio_data: Dict, user_profile: Dict) -> float:
        """Estimate current savings available for the goal"""
        
        # From portfolio data
        portfolio_value = 0
        if portfolio_data and portfolio_data.get('holdings'):
            portfolio_value = sum(holding.get('value', 0) for holding in portfolio_data['holdings'])
        
        # From user profile
        savings_balance = user_profile.get('savings_balance', 0)
        
        # Conservative estimate: use portion of portfolio + savings
        available_savings = savings_balance + (portfolio_value * 0.5)  # Assume 50% of portfolio available
        
        return max(0, available_savings)
    
    def _assess_feasibility(self, scenarios: Dict, user_profile: Dict) -> Dict[str, Any]:
        """Assess feasibility of goal scenarios"""
        
        annual_income = user_profile.get('annual_income', 75000)
        monthly_income = annual_income / 12
        
        feasibility = {}
        
        for scenario_name, scenario in scenarios.items():
            if scenario_name == 'feasibility':
                continue
                
            monthly_required = scenario['monthly_savings_required']
            savings_rate = (monthly_required / monthly_income) * 100 if monthly_income > 0 else 0
            
            if savings_rate <= 10:
                difficulty = 'easy'
                description = 'Very achievable savings rate'
            elif savings_rate <= 20:
                difficulty = 'moderate'
                description = 'Reasonable savings rate with some lifestyle adjustments'
            elif savings_rate <= 30:
                difficulty = 'challenging'
                description = 'Requires significant lifestyle changes and discipline'
            else:
                difficulty = 'difficult'
                description = 'May require major lifestyle changes or extended timeline'
            
            feasibility[scenario_name] = {
                'monthly_required': monthly_required,
                'savings_rate_percent': round(savings_rate, 1),
                'difficulty': difficulty,
                'description': description
            }
        
        return feasibility
    
    def _create_action_plan(self, scenarios: Dict, goal_details: Dict, user_profile: Dict) -> List[Dict[str, Any]]:
        """Generate specific, actionable steps to achieve the goal"""
        
        goal_type = goal_details['goal_type']
        best_scenario = self._select_best_scenario(scenarios)
        
        action_plan = []
        
        # Step 1: Goal setup and tracking
        action_plan.append({
            'category': 'Setup',
            'title': 'Define and Document Your Goal',
            'description': f'Formally document your {goal_type} goal with specific target amount and timeline',
            'actions': [
                f"Set target amount: ${scenarios['target_amount']:,.0f}",
                f"Set target timeline: {scenarios['timeline_years']} years",
                'Write down your "why" - the motivation behind this goal',
                'Set up progress tracking (spreadsheet, app, or financial advisor)'
            ],
            'timeline': 'This week',
            'priority': 'high'
        })
        
        # Step 2: Monthly savings plan
        monthly_target = best_scenario['monthly_savings_required']
        action_plan.append({
            'category': 'Savings',
            'title': 'Implement Monthly Savings Plan',
            'description': f'Save ${monthly_target:.0f} per month to reach your goal',
            'actions': [
                f"Set up automatic transfer of ${monthly_target:.0f} monthly",
                'Open dedicated savings/investment account for this goal',
                'Reduce expenses or increase income to fund savings',
                'Review and adjust monthly contribution quarterly'
            ],
            'timeline': 'Next 30 days',
            'priority': 'high'
        })
        
        # Step 3: Investment strategy
        investment_actions = self._get_investment_recommendations(goal_type, scenarios['timeline_years'])
        action_plan.append({
            'category': 'Investment',
            'title': 'Optimize Investment Strategy',
            'description': f'Invest appropriately for your {scenarios["timeline_years"]}-year timeline',
            'actions': investment_actions,
            'timeline': 'Next 60 days',
            'priority': 'medium'
        })
        
        # Step 4: Goal-specific actions
        specific_actions = self._get_goal_specific_actions(goal_type, scenarios)
        if specific_actions:
            action_plan.append({
                'category': 'Goal-Specific',
                'title': f'{goal_type.title()} Planning Steps',
                'description': f'Specific actions for {goal_type} planning',
                'actions': specific_actions,
                'timeline': 'Next 90 days',
                'priority': 'medium'
            })
        
        # Step 5: Monitoring and adjustment
        action_plan.append({
            'category': 'Monitoring',
            'title': 'Regular Review and Adjustment',
            'description': 'Stay on track with regular progress reviews',
            'actions': [
                'Review progress monthly and adjust contributions as needed',
                'Reassess timeline and target amount annually',
                'Rebalance investments annually or as life circumstances change',
                'Consider increasing contributions with salary raises or bonuses'
            ],
            'timeline': 'Ongoing',
            'priority': 'medium'
        })
        
        return action_plan
    
    def _select_best_scenario(self, scenarios: Dict) -> Dict[str, Any]:
        """Select the most appropriate scenario based on feasibility"""
        feasibility = scenarios.get('feasibility', {})
        
        # Prefer moderate scenario if feasible, otherwise conservative
        if 'moderate' in feasibility and feasibility['moderate']['savings_rate_percent'] <= 20:
            return scenarios['scenarios']['moderate']
        elif 'conservative' in feasibility:
            return scenarios['scenarios']['conservative']
        else:
            return scenarios['scenarios'].get('moderate', scenarios['scenarios'].get('conservative', {}))
    
    def _get_investment_recommendations(self, goal_type: str, timeline_years: int) -> List[str]:
        """Get investment recommendations based on goal type and timeline"""
        
        if goal_type == 'emergency_fund':
            return [
                'Keep in high-yield savings account or money market fund',
                'Prioritize liquidity and capital preservation over returns',
                'Consider short-term CDs for portion of fund',
                'Avoid stock market investments for emergency funds'
            ]
        elif timeline_years <= 2:
            return [
                'Use conservative investments: high-yield savings, CDs, short-term bonds',
                'Prioritize capital preservation over growth',
                'Avoid volatile investments with short timeline',
                'Consider Treasury bills or stable value funds'
            ]
        elif timeline_years <= 5:
            return [
                'Use moderate allocation: 30-50% stocks, 50-70% bonds',
                'Consider target-date funds or balanced funds',
                'Include some international diversification',
                'Gradually shift to more conservative as goal approaches'
            ]
        else:
            return [
                'Use growth-oriented allocation: 60-80% stocks, 20-40% bonds',
                'Include domestic and international stock funds',
                'Consider low-cost index funds or ETFs',
                'Rebalance annually and shift to conservative as timeline shortens'
            ]
    
    def _get_goal_specific_actions(self, goal_type: str, scenarios: Dict) -> List[str]:
        """Get specific actions based on goal type"""
        
        if goal_type == 'retirement':
            return [
                'Maximize employer 401(k) match if available',
                'Consider opening IRA for additional tax-advantaged savings',
                'Review and increase 401(k) contribution percentage annually',
                'Plan for healthcare costs in retirement',
                'Consider Roth vs traditional IRA based on tax situation'
            ]
        elif goal_type == 'house':
            return [
                'Research home prices in target areas',
                'Start improving credit score for better mortgage rates',
                'Research first-time buyer programs and incentives',
                'Factor in closing costs, moving expenses, and immediate repairs',
                'Consider house-hacking or multi-family properties'
            ]
        elif goal_type == 'education':
            return [
                'Research 529 education savings plan benefits',
                'Look into education tax credits and deductions',
                'Consider in-state vs out-of-state tuition costs',
                'Explore scholarship and grant opportunities',
                'Plan for education inflation (typically 5-6% annually)'
            ]
        else:
            return []
    
    def _format_goal_plan(self, scenarios: Dict, action_plan: List, goal_details: Dict) -> str:
        """Format comprehensive goal planning response"""
        
        goal_type = goal_details['goal_type']
        target_amount = scenarios['target_amount']
        timeline_years = scenarios['timeline_years']
        
        response_parts = [
            f"🎯 **{goal_type.title()} Goal Planning Analysis**\n",
            f"**Goal**: ${target_amount:,.0f} in {timeline_years} years",
            f"**Current Savings**: ${scenarios['current_savings']:,.0f}",
            ""
        ]
        
        # Scenario comparison
        response_parts.append("📊 **Savings Scenarios:**")
        
        feasibility = scenarios['scenarios'].get('feasibility', {})
        for scenario_name, scenario in scenarios['scenarios'].items():
            if scenario_name == 'feasibility':
                continue
                
            monthly_required = scenario['monthly_savings_required']
            feasibility_info = feasibility.get(scenario_name, {})
            savings_rate = feasibility_info.get('savings_rate_percent', 0)
            difficulty = feasibility_info.get('difficulty', 'unknown')
            
            emoji = {'easy': '🟢', 'moderate': '🟡', 'challenging': '🟠', 'difficult': '🔴'}.get(difficulty, '⚪')
            
            response_parts.extend([
                f"{emoji} **{scenario_name.title()} ({scenario['annual_return']:.1%} return)**:",
                f"   • Monthly savings: ${monthly_required:,.0f} ({savings_rate:.1f}% of income)",
                f"   • Final balance: ${scenario['final_balance']:,.0f}",
                f"   • Assessment: {feasibility_info.get('description', 'Unknown')}"
            ])
        
        response_parts.append("")
        
        # Recommended plan
        best_scenario = self._select_best_scenario(scenarios)
        response_parts.extend([
            "🎯 **Recommended Plan:**",
            f"• **Monthly Target**: ${best_scenario['monthly_savings_required']:,.0f}",
            f"• **Investment Approach**: {self._get_investment_summary(goal_type, timeline_years)}",
            f"• **Success Probability**: {self._get_success_probability(best_scenario)}",
            ""
        ])
        
        # Action plan summary
        response_parts.extend([
            "📋 **Next Steps:**",
            f"1. **This Week**: {action_plan[0]['actions'][0]}",
            f"2. **Next 30 Days**: {action_plan[1]['actions'][0]}",
            f"3. **Next 60 Days**: {action_plan[2]['actions'][0]}",
            f"4. **Ongoing**: Review progress monthly and adjust as needed",
            ""
        ])
        
        # Key insights
        response_parts.extend([
            "💡 **Key Insights:**",
            self._get_key_insights(goal_type, scenarios, timeline_years),
            ""
        ])
        
        # Disclaimers
        response_parts.extend([
            "⚠️ **Important Notes:**",
            "• Projections assume consistent contributions and estimated returns",
            "• Actual investment returns will vary and may be negative in some years",
            "• Review and adjust your plan annually or with life changes",
            "• Consider consulting with a financial advisor for personalized advice",
            "• This analysis is for educational purposes only"
        ])
        
        return "\n".join(response_parts)
    
    def _get_investment_summary(self, goal_type: str, timeline_years: int) -> str:
        """Get brief investment approach summary"""
        if goal_type == 'emergency_fund':
            return "High-yield savings (prioritize liquidity)"
        elif timeline_years <= 2:
            return "Conservative (savings, CDs, short-term bonds)"
        elif timeline_years <= 5:
            return "Moderate (balanced stock/bond allocation)"
        else:
            return "Growth-oriented (stock-heavy with bond buffer)"
    
    def _get_success_probability(self, scenario: Dict) -> str:
        """Estimate success probability based on scenario"""
        if scenario.get('goal_achieved', False):
            surplus = scenario.get('surplus_or_deficit', 0)
            if surplus > 0:
                return "High (goal exceeded in projection)"
            else:
                return "High (goal met in projection)"
        else:
            deficit = abs(scenario.get('surplus_or_deficit', 0))
            target = scenario.get('final_balance', 0) + deficit
            shortfall_percent = (deficit / target) * 100 if target > 0 else 100
            
            if shortfall_percent < 10:
                return "Moderate (close to goal)"
            else:
                return "Lower (may need timeline or contribution adjustment)"
    
    def _get_key_insights(self, goal_type: str, scenarios: Dict, timeline_years: int) -> str:
        """Generate key insights based on analysis"""
        insights = []
        
        # Timeline insight
        if timeline_years >= 10:
            insights.append("• Long timeline allows for growth-oriented investments and compound interest")
        elif timeline_years >= 5:
            insights.append("• Medium timeline requires balanced approach between growth and stability")
        else:
            insights.append("• Short timeline requires conservative approach to protect principal")
        
        # Savings rate insight
        feasibility = scenarios['scenarios'].get('feasibility', {})
        moderate_feasibility = feasibility.get('moderate', {})
        savings_rate = moderate_feasibility.get('savings_rate_percent', 0)
        
        if savings_rate <= 10:
            insights.append("• Required savings rate is very manageable with current income")
        elif savings_rate <= 20:
            insights.append("• Required savings rate is reasonable but may require budget adjustments")
        else:
            insights.append("• Consider extending timeline or increasing income to make goal more achievable")
        
        # Goal-specific insight
        goal_insights = {
            'retirement': "• Starting early maximizes compound interest - even small amounts make a big difference",
            'emergency_fund': "• Prioritize building this foundation before other investment goals",
            'house': "• Factor in additional costs beyond down payment (closing, moving, repairs)",
            'education': "• Education inflation is typically higher than general inflation",
            'investment': "• Regular contributions and staying invested long-term are key to success"
        }
        
        if goal_type in goal_insights:
            insights.append(goal_insights[goal_type])
        
        return "\n".join(insights)
    
    def _prepare_goal_tracking(self, scenarios: Dict, goal_details: Dict) -> Dict[str, Any]:
        """Prepare data structure for goal tracking"""
        best_scenario = self._select_best_scenario(scenarios)
        
        return {
            'goal_id': f"{goal_details['goal_type']}_{int(datetime.now().timestamp())}",
            'goal_type': goal_details['goal_type'],
            'target_amount': scenarios['target_amount'],
            'timeline_years': scenarios['timeline_years'],
            'monthly_target': best_scenario['monthly_savings_required'],
            'current_balance': scenarios['current_savings'],
            'created_date': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'projections': best_scenario['projections'],
            'milestones': self._create_milestones(best_scenario['projections'])
        }
    
    def _create_milestones(self, projections: List[Dict]) -> List[Dict]:
        """Create milestone checkpoints for goal tracking"""
        if not projections:
            return []
        
        final_balance = projections[-1]['balance']
        milestones = []
        
        # Create milestones at 25%, 50%, 75%, and 100%
        for percent in [0.25, 0.50, 0.75, 1.0]:
            target_balance = final_balance * percent
            
            # Find the year when this milestone should be reached
            milestone_year = None
            for projection in projections:
                if projection['balance'] >= target_balance:
                    milestone_year = projection['year']
                    break
            
            if milestone_year is not None:
                milestones.append({
                    'percent': int(percent * 100),
                    'target_balance': round(target_balance, 2),
                    'target_year': milestone_year,
                    'achieved': False,
                    'achieved_date': None
                })
        
        return milestones
    
    def _prepare_goal_viz_data(self, scenarios: Dict) -> Dict[str, Any]:
        """Prepare data for goal visualization charts"""
        viz_data = {
            'projection_charts': {},
            'comparison_data': {},
            'milestone_data': {}
        }
        
        # Projection charts for each scenario
        for scenario_name, scenario in scenarios['scenarios'].items():
            if scenario_name == 'feasibility':
                continue
                
            projections = scenario.get('projections', [])
            if projections:
                viz_data['projection_charts'][scenario_name] = {
                    'years': [p['year'] for p in projections],
                    'balances': [p['balance'] for p in projections],
                    'contributions': [p['cumulative_contributions'] for p in projections]
                }
        
        # Comparison data for savings requirements
        comparison_data = []
        for scenario_name, scenario in scenarios['scenarios'].items():
            if scenario_name == 'feasibility':
                continue
            comparison_data.append({
                'scenario': scenario_name.title(),
                'monthly_savings': scenario['monthly_savings_required'],
                'annual_return': scenario['annual_return'],
                'final_balance': scenario['final_balance']
            })
        
        viz_data['comparison_data'] = comparison_data
        
        return viz_data
    
    def _generate_fallback_response(self, query: str, error: str) -> Dict[str, Any]:
        """Generate fallback response when goal planning fails"""
        response = f"""🎯 **Goal Planning Assistant**

I'd be happy to help you plan for your financial goals! 

**I can help you with:**
• **Retirement Planning**: Calculate how much to save for retirement
• **Emergency Fund**: Build 3-6 months of expenses as financial security
• **Major Purchases**: Plan for home down payment, education costs, etc.
• **Investment Goals**: Set and track specific financial targets

**To provide the best plan, please tell me:**
1. What type of goal are you planning for?
2. What's your target amount (if you have one in mind)?
3. What's your timeline (how many years)?
4. What's your current age and approximate income?

**Example questions:**
• "Help me plan for retirement at age 65"
• "I want to save $50,000 for a house down payment in 5 years"
• "How much should I save monthly for my child's college education?"

**Disclaimer**: This analysis provides educational projections only. Actual results may vary, and you should consult with a financial advisor for personalized advice.
"""
        
        return {
            "agent_response": response,
            "sources": ["Goal Planning Assistant"],
            "confidence": 0.7,
            "next_agent": None,
            "agent_name": "goal_planning",
            "error": error
        }

    def assess_goal_feasibility(self, goal_amount: float, timeline_years: int, 
                               current_savings: float, monthly_capacity: float) -> Dict[str, Any]:
        """Assess whether a goal is realistic given current circumstances"""
        
        # Calculate required monthly savings for different return scenarios
        scenarios = {}
        for scenario_name, annual_return in [(0.04, 'conservative'), (0.07, 'moderate'), (0.09, 'aggressive')]:
            fv_current = self.calculator.future_value(current_savings, annual_return, timeline_years)
            additional_needed = max(0, goal_amount - fv_current)
            
            if additional_needed > 0:
                monthly_required = self.calculator.monthly_savings_required(
                    additional_needed, annual_return, timeline_years
                )
            else:
                monthly_required = 0
            
            scenarios[scenario_name] = {
                'monthly_required': monthly_required,
                'feasible': monthly_required <= monthly_capacity,
                'capacity_utilization': (monthly_required / monthly_capacity) * 100 if monthly_capacity > 0 else 0
            }
        
        # Overall assessment
        feasible_count = sum(1 for s in scenarios.values() if s['feasible'])
        
        if feasible_count >= 2:
            overall = 'highly_feasible'
        elif feasible_count == 1:
            overall = 'moderately_feasible'
        else:
            overall = 'challenging'
        
        return {
            'overall_assessment': overall,
            'scenarios': scenarios,
            'recommendation': self._get_feasibility_recommendation(overall, scenarios)
        }
    
    def _get_feasibility_recommendation(self, assessment: str, scenarios: Dict) -> str:
        """Get recommendation based on feasibility assessment"""
        if assessment == 'highly_feasible':
            return "Your goal appears very achievable with your current savings capacity."
        elif assessment == 'moderately_feasible':
            return "Your goal is achievable but may require some budget adjustments or a slightly longer timeline."
        else:
            return "Consider extending your timeline, reducing the target amount, or increasing your savings capacity."