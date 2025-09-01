# Portfolio calculation utilities
# Calculate portfolio metrics, allocations, and financial projections

from typing import Dict, Any, List, Optional, Tuple
import math
import pandas as pd
import numpy as np

class PortfolioCalculator:
    """
    Portfolio calculation utilities for financial analysis
    
    Features:
    - Asset allocation calculations
    - Diversification metrics
    - Risk assessment
    - Performance analysis
    """
    
    def __init__(self):
        # Asset class categorization for analysis
        self.asset_classes = {
            'stocks': ['stock', 'equity', 'etf', 'mutual fund'],
            'bonds': ['bond', 'treasury', 'corporate bond', 'municipal'],
            'cash': ['cash', 'money market', 'savings'],
            'alternatives': ['reit', 'commodity', 'crypto', 'alternative']
        }
        
        # Sector classifications
        self.sectors = {
            'technology': ['tech', 'software', 'hardware', 'semiconductor'],
            'healthcare': ['health', 'pharma', 'biotech', 'medical'],
            'financial': ['bank', 'insurance', 'financial services'],
            'consumer': ['consumer goods', 'retail', 'discretionary'],
            'industrial': ['industrial', 'manufacturing', 'aerospace'],
            'energy': ['oil', 'gas', 'energy', 'utilities'],
            'materials': ['materials', 'mining', 'chemicals'],
            'real_estate': ['reit', 'real estate']
        }
    
    def calculate_all_metrics(self, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive portfolio metrics"""
        holdings = portfolio_data.get('holdings', [])
        
        if not holdings:
            return self._empty_metrics()
        
        # Basic calculations
        total_value = self.calculate_total_value(holdings)
        allocation = self.calculate_allocation(holdings)
        
        # Advanced metrics
        diversification_score = self.calculate_diversification_score(holdings)
        asset_class_allocation = self.calculate_asset_class_allocation(holdings)
        sector_allocation = self.calculate_sector_allocation(holdings)
        concentration_risk = self.calculate_concentration_risk(holdings)
        
        # Risk metrics
        risk_score = self.calculate_risk_score(asset_class_allocation)
        
        return {
            'total_value': total_value,
            'num_holdings': len(holdings),
            'allocation': allocation,
            'asset_class_allocation': asset_class_allocation,
            'sector_allocation': sector_allocation,
            'diversification_score': diversification_score,
            'concentration_risk': concentration_risk,
            'risk_score': risk_score,
            'largest_holding_percent': max([h.get('percent', 0) for h in holdings]) if holdings else 0,
            'top_3_holdings_percent': sum(sorted([h.get('percent', 0) for h in holdings], reverse=True)[:3])
        }
    
    def calculate_total_value(self, holdings: List[Dict[str, Any]]) -> float:
        """Calculate total portfolio value"""
        return sum(holding.get('value', 0) for holding in holdings)
    
    def calculate_allocation(self, holdings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calculate asset allocation percentages"""
        total_value = self.calculate_total_value(holdings)
        
        if total_value == 0:
            return []
        
        allocation = []
        for holding in holdings:
            value = holding.get('value', 0)
            percent = (value / total_value) * 100
            allocation.append({
                'name': holding.get('name', 'Unknown'),
                'symbol': holding.get('symbol', ''),
                'value': value,
                'percent': round(percent, 2)
            })
        
        # Sort by percentage descending
        return sorted(allocation, key=lambda x: x['percent'], reverse=True)
    
    def calculate_asset_class_allocation(self, holdings: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate allocation by asset class"""
        total_value = self.calculate_total_value(holdings)
        
        if total_value == 0:
            return {}
        
        class_totals = {'stocks': 0, 'bonds': 0, 'cash': 0, 'alternatives': 0}
        
        for holding in holdings:
            asset_class = self._classify_asset(holding)
            class_totals[asset_class] += holding.get('value', 0)
        
        # Convert to percentages
        return {
            class_name: round((value / total_value) * 100, 2)
            for class_name, value in class_totals.items()
            if value > 0
        }
    
    def calculate_sector_allocation(self, holdings: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate allocation by sector"""
        total_value = self.calculate_total_value(holdings)
        
        if total_value == 0:
            return {}
        
        sector_totals = {sector: 0 for sector in self.sectors.keys()}
        sector_totals['other'] = 0
        
        for holding in holdings:
            sector = self._classify_sector(holding)
            sector_totals[sector] += holding.get('value', 0)
        
        # Convert to percentages and filter out zero values
        return {
            sector: round((value / total_value) * 100, 2)
            for sector, value in sector_totals.items()
            if value > 0
        }
    
    def calculate_diversification_score(self, holdings: List[Dict[str, Any]]) -> float:
        """
        Calculate portfolio diversification score (0-100)
        Higher score = better diversification
        """
        if len(holdings) == 0:
            return 0
        
        allocation = self.calculate_allocation(holdings)
        if not allocation:
            return 0
        
        # Calculate Herfindahl-Hirschman Index (HHI)
        hhi = sum((holding['percent'] / 100) ** 2 for holding in allocation)
        
        # Prevent division by zero
        if hhi <= 0:
            return 0
        
        # Convert to diversification score (inverse of concentration)
        # HHI ranges from 1/n to 1, we convert to 0-100 scale
        max_diversification = 1 / len(holdings)  # Perfect diversification
        diversification_ratio = max_diversification / hhi
        
        # Scale to 0-100
        score = min(diversification_ratio * 50, 100)  # Cap at 100
        
        return round(score, 1)
    
    def calculate_concentration_risk(self, holdings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate concentration risk metrics"""
        if not holdings:
            return {'level': 'unknown', 'description': 'No holdings to analyze'}
        
        allocation = self.calculate_allocation(holdings)
        largest_holding = allocation[0]['percent'] if allocation else 0
        top_3_total = sum(h['percent'] for h in allocation[:3])
        top_5_total = sum(h['percent'] for h in allocation[:5])
        
        # Determine risk level
        if largest_holding > 50:
            level = 'very_high'
            description = f"Very high concentration risk: largest holding is {largest_holding:.1f}%"
        elif largest_holding > 25:
            level = 'high'
            description = f"High concentration risk: largest holding is {largest_holding:.1f}%"
        elif top_3_total > 75:
            level = 'moderate'
            description = f"Moderate concentration risk: top 3 holdings are {top_3_total:.1f}%"
        elif top_5_total > 80:
            level = 'low'
            description = f"Low concentration risk: top 5 holdings are {top_5_total:.1f}%"
        else:
            level = 'very_low'
            description = "Very low concentration risk: well diversified"
        
        return {
            'level': level,
            'description': description,
            'largest_holding_percent': largest_holding,
            'top_3_percent': top_3_total,
            'top_5_percent': top_5_total
        }
    
    def calculate_risk_score(self, asset_class_allocation: Dict[str, float]) -> Dict[str, Any]:
        """Calculate overall portfolio risk score based on asset allocation"""
        if not asset_class_allocation:
            return {'score': 50, 'level': 'moderate', 'description': 'Unable to determine risk'}
        
        # Risk weights for different asset classes
        risk_weights = {
            'stocks': 0.8,      # Higher risk
            'alternatives': 0.9, # Highest risk
            'bonds': 0.3,       # Lower risk
            'cash': 0.1         # Lowest risk
        }
        
        # Calculate weighted average risk
        total_percent = sum(asset_class_allocation.values())
        if total_percent == 0:
            return {'score': 50, 'level': 'moderate', 'description': 'Unable to determine risk'}
        
        weighted_risk = sum(
            (percent / total_percent) * risk_weights.get(asset_class, 0.5)
            for asset_class, percent in asset_class_allocation.items()
        )
        
        # Convert to 0-100 scale
        risk_score = weighted_risk * 100
        
        # Determine risk level
        if risk_score < 30:
            level = 'conservative'
            description = 'Conservative portfolio with lower risk and returns'
        elif risk_score < 50:
            level = 'moderate'
            description = 'Moderate portfolio with balanced risk and returns'
        elif risk_score < 70:
            level = 'growth'
            description = 'Growth-oriented portfolio with higher risk and return potential'
        else:
            level = 'aggressive'
            description = 'Aggressive portfolio with high risk and high return potential'
        
        return {
            'score': round(risk_score, 1),
            'level': level,
            'description': description
        }
    
    def _classify_asset(self, holding: Dict[str, Any]) -> str:
        """Classify holding into asset class"""
        name = holding.get('name', '').lower()
        asset_type = holding.get('type', '').lower()
        description = holding.get('description', '').lower()
        
        text_to_check = f"{name} {asset_type} {description}"
        
        for asset_class, keywords in self.asset_classes.items():
            if any(keyword in text_to_check for keyword in keywords):
                return asset_class
        
        return 'stocks'  # Default to stocks
    
    def _classify_sector(self, holding: Dict[str, Any]) -> str:
        """Classify holding into sector"""
        name = holding.get('name', '').lower()
        sector = holding.get('sector', '').lower()
        description = holding.get('description', '').lower()
        
        text_to_check = f"{name} {sector} {description}"
        
        for sector_name, keywords in self.sectors.items():
            if any(keyword in text_to_check for keyword in keywords):
                return sector_name
        
        return 'other'
    
    def _empty_metrics(self) -> Dict[str, Any]:
        """Return empty metrics structure"""
        return {
            'total_value': 0,
            'num_holdings': 0,
            'allocation': [],
            'asset_class_allocation': {},
            'sector_allocation': {},
            'diversification_score': 0,
            'concentration_risk': {'level': 'unknown', 'description': 'No holdings to analyze'},
            'risk_score': {'score': 50, 'level': 'moderate', 'description': 'No data available'},
            'largest_holding_percent': 0,
            'top_3_holdings_percent': 0
        }

class FinancialCalculator:
    """
    Financial calculation utilities for goal planning and projections
    
    Features:
    - Future value and present value calculations
    - Annuity and savings projections
    - Retirement planning calculations
    - Loan and debt analysis
    """
    
    def future_value(self, present_value: float, rate: float, periods: int) -> float:
        """Calculate future value with compound interest"""
        if rate == 0:
            return present_value + (present_value * rate * periods)
        return present_value * (1 + rate) ** periods
    
    def present_value(self, future_value: float, rate: float, periods: int) -> float:
        """Calculate present value"""
        if rate == 0:
            return future_value
        return future_value / (1 + rate) ** periods
    
    def monthly_savings_required(self, goal_amount: float, rate: float, years: int) -> float:
        """Calculate monthly savings required to reach goal"""
        months = years * 12
        monthly_rate = rate / 12
        
        if monthly_rate == 0:
            return goal_amount / months
        
        return goal_amount * monthly_rate / ((1 + monthly_rate) ** months - 1)
    
    def future_value_annuity(self, payment: float, rate: float, periods: int) -> float:
        """Calculate future value of ordinary annuity"""
        if rate == 0:
            return payment * periods
        return payment * (((1 + rate) ** periods - 1) / rate)
    
    def retirement_withdrawal_amount(self, balance: float, rate: float, years: int) -> float:
        """Calculate safe annual withdrawal amount for retirement (4% rule)"""
        # Conservative approach using present value of annuity
        if rate == 0:
            return balance / years
        
        # Calculate maximum annual withdrawal that depletes balance over specified years
        return balance * (rate / (1 - (1 + rate) ** -years))
    
    def retirement_savings_needed(self, desired_annual_income: float, rate: float = 0.04) -> float:
        """Calculate retirement savings needed for desired annual income (25x rule)"""
        return desired_annual_income / rate
    
    def inflation_adjusted_amount(self, amount: float, inflation_rate: float, years: int) -> float:
        """Calculate inflation-adjusted future amount"""
        return amount * (1 + inflation_rate) ** years
    
    def real_return_rate(self, nominal_rate: float, inflation_rate: float) -> float:
        """Calculate real return rate adjusted for inflation"""
        return (1 + nominal_rate) / (1 + inflation_rate) - 1
    
    def compound_annual_growth_rate(self, beginning_value: float, ending_value: float, years: int) -> float:
        """Calculate compound annual growth rate (CAGR)"""
        if beginning_value <= 0 or ending_value <= 0 or years <= 0:
            return 0
        return (ending_value / beginning_value) ** (1 / years) - 1
    
    def loan_payment(self, principal: float, rate: float, years: int) -> float:
        """Calculate monthly loan payment"""
        months = years * 12
        monthly_rate = rate / 12
        
        if monthly_rate == 0:
            return principal / months
        
        return principal * (monthly_rate * (1 + monthly_rate) ** months) / ((1 + monthly_rate) ** months - 1)
    
    def emergency_fund_target(self, monthly_expenses: float, months: int = 6) -> float:
        """Calculate recommended emergency fund target"""
        return monthly_expenses * months
    
    def savings_rate_needed(self, current_income: float, goal_amount: float, rate: float, years: int) -> float:
        """Calculate percentage of income needed to save for goal"""
        monthly_income = current_income / 12
        monthly_savings_needed = self.monthly_savings_required(goal_amount, rate, years)
        
        if monthly_income <= 0:
            return 0
        
        return (monthly_savings_needed / monthly_income) * 100
    
    def debt_payoff_time(self, balance: float, payment: float, apr: float) -> Dict[str, Any]:
        """Calculate time to pay off debt with given payment"""
        monthly_rate = apr / 12
        
        if payment <= balance * monthly_rate:
            return {
                'months': float('inf'),
                'years': float('inf'),
                'total_interest': float('inf'),
                'warning': 'Payment is too low to pay off debt (payment <= interest)'
            }
        
        if monthly_rate == 0:
            months = balance / payment
        else:
            months = -np.log(1 - (balance * monthly_rate) / payment) / np.log(1 + monthly_rate)
        
        total_payments = payment * months
        total_interest = total_payments - balance
        
        return {
            'months': round(months, 1),
            'years': round(months / 12, 1),
            'total_payments': round(total_payments, 2),
            'total_interest': round(total_interest, 2),
            'interest_saved_vs_minimum': 0  # Can be calculated with minimum payment comparison
        }
    
    def college_savings_projection(self, current_cost: float, years_until_college: int, 
                                 education_inflation: float = 0.05, investment_return: float = 0.07) -> Dict[str, Any]:
        """Calculate college savings projections"""
        
        # Future cost of college with education inflation
        future_cost = self.inflation_adjusted_amount(current_cost, education_inflation, years_until_college)
        
        # Monthly savings needed
        monthly_savings = self.monthly_savings_required(future_cost, investment_return, years_until_college)
        
        return {
            'current_annual_cost': current_cost,
            'future_annual_cost': round(future_cost, 2),
            'total_future_cost': round(future_cost * 4, 2),  # 4 years
            'monthly_savings_needed': round(monthly_savings, 2),
            'annual_savings_needed': round(monthly_savings * 12, 2),
            'education_inflation_rate': education_inflation,
            'assumed_investment_return': investment_return
        }
    
    def tax_advantaged_savings_benefit(self, contribution: float, tax_rate: float, 
                                     account_type: str = 'traditional') -> Dict[str, Any]:
        """Calculate tax benefits of different retirement account types"""
        
        if account_type.lower() == 'traditional':
            # Traditional 401k/IRA - tax deduction now, taxed on withdrawal
            immediate_tax_savings = contribution * tax_rate
            effective_contribution_cost = contribution - immediate_tax_savings
            
            return {
                'account_type': 'Traditional',
                'contribution': contribution,
                'immediate_tax_savings': round(immediate_tax_savings, 2),
                'effective_cost': round(effective_contribution_cost, 2),
                'tax_treatment': 'Deductible now, taxed on withdrawal'
            }
        
        elif account_type.lower() == 'roth':
            # Roth 401k/IRA - no immediate deduction, tax-free withdrawals
            return {
                'account_type': 'Roth',
                'contribution': contribution,
                'immediate_tax_savings': 0,
                'effective_cost': contribution,
                'tax_treatment': 'No deduction now, tax-free withdrawals'
            }
        
        else:
            return {
                'error': 'Account type must be "traditional" or "roth"'
            }