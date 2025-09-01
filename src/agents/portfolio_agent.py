# Create a sophisticated Portfolio Analysis Agent
# Analyze portfolio data, calculate key metrics, provide recommendations
# Handle multiple input formats (CSV, manual entry, JSON)
# Generate comprehensive portfolio reports with visualizations data

import pandas as pd
import io
from typing import Dict, Any, List, Optional
from src.agents.base_agent import BaseFinanceAgent
from src.utils.portfolio_calc import PortfolioCalculator
from src.core.state import FinanceAssistantState

class PortfolioAnalysisAgent(BaseFinanceAgent):
    """
    Portfolio Analysis Agent for investment portfolio evaluation
    
    Capabilities:
    - Parse and validate portfolio data from multiple formats
    - Calculate key metrics: allocation, diversification, risk, expense ratios
    - Provide actionable recommendations for portfolio improvement
    - Generate visualization data for charts and graphs
    - Assess portfolio against common benchmarks and best practices
    """
    
    def __init__(self, llm, portfolio_calculator: PortfolioCalculator = None):
        system_prompt = """
        You are an expert portfolio analyst. Your role is to:
        1. Analyze investment portfolios objectively and comprehensively
        2. Calculate and explain key portfolio metrics clearly
        3. Provide actionable recommendations for improvement
        4. Explain complex concepts in beginner-friendly terms
        5. Focus on diversification, risk management, and cost efficiency
        
        Analysis Framework:
        - Asset allocation and diversification analysis
        - Cost analysis (expense ratios, fees)
        - Risk assessment based on asset classes
        - Benchmark comparisons where appropriate
        - Specific, actionable recommendations
        
        Guidelines:
        - Use clear, beginner-friendly language
        - Provide specific percentage targets for improvements
        - Explain the reasoning behind each recommendation
        - Include appropriate disclaimers about investment advice
        - Focus on long-term wealth building principles
        """
        super().__init__(llm, [], "portfolio_analysis", system_prompt)
        self.calculator = portfolio_calculator or PortfolioCalculator()
    
    def execute(self, state: FinanceAssistantState) -> Dict[str, Any]:
        """
        Analyze portfolio and provide comprehensive report
        
        Steps:
        1. Extract and validate portfolio data from state
        2. Calculate key portfolio metrics and ratios
        3. Perform diversification and risk analysis
        4. Generate recommendations based on analysis
        5. Prepare visualization data for charts
        6. Format comprehensive response
        """
        try:
            portfolio_data = state.get("portfolio_data")
            user_query = state.get("user_query", "")
            
            print(f"DEBUG: Portfolio agent received portfolio_data: {portfolio_data}")
            print(f"DEBUG: Portfolio agent query: {user_query[:100]}...")
            print(f"DEBUG: Portfolio data type: {type(portfolio_data)}")
            print(f"DEBUG: Portfolio data keys: {list(portfolio_data.keys()) if isinstance(portfolio_data, dict) else 'Not a dict'}")
            
            # Try to extract portfolio data from the user query if not available in state
            if not portfolio_data and user_query:
                print("DEBUG: Attempting to extract portfolio data from user query")
                portfolio_data = self._extract_portfolio_from_query(user_query)
                if portfolio_data:
                    print(f"DEBUG: Successfully extracted portfolio data from query: {portfolio_data}")
            
            # Improved portfolio data validation
            if not portfolio_data:
                print("DEBUG: No portfolio data found, returning request message")
                return self._request_portfolio_data()
            
            # Handle different portfolio data formats
            holdings = []
            
            if isinstance(portfolio_data, dict):
                # Check for holdings key
                if "holdings" in portfolio_data:
                    holdings = portfolio_data["holdings"]
                    print(f"DEBUG: Found {len(holdings)} holdings in portfolio_data['holdings']")
                # Check if portfolio_data itself contains holding-like data
                elif "name" in portfolio_data or "value" in portfolio_data:
                    holdings = [portfolio_data]
                    print(f"DEBUG: Treating portfolio_data as single holding")
                # Check if it's a list of holdings directly
                elif isinstance(list(portfolio_data.values())[0], dict):
                    holdings = list(portfolio_data.values())
                    print(f"DEBUG: Converting portfolio_data values to holdings list")
            elif isinstance(portfolio_data, list):
                holdings = portfolio_data
                print(f"DEBUG: Portfolio data is already a list with {len(holdings)} items")
            
            if not holdings:
                print("DEBUG: No holdings found after parsing portfolio data")
                return self._request_portfolio_data()
            
            print(f"DEBUG: Final holdings count: {len(holdings)}")
            print(f"DEBUG: Sample holding: {holdings[0] if holdings else 'None'}")
            
            # Ensure holdings are properly formatted
            formatted_holdings = []
            for holding in holdings:
                if isinstance(holding, dict):
                    # Ensure required fields exist
                    if 'name' in holding and 'value' in holding:
                        formatted_holdings.append(holding)
                    else:
                        print(f"DEBUG: Skipping invalid holding: {holding}")
                        continue
                        
            if not formatted_holdings:
                print("DEBUG: No valid holdings found after formatting")
                return self._request_portfolio_data()
            
            # Create properly formatted portfolio data for calculations
            formatted_portfolio_data = {"holdings": formatted_holdings}
            print(f"DEBUG: Formatted portfolio data with {len(formatted_holdings)} holdings")
            
            # Calculate portfolio metrics
            metrics = self.calculator.calculate_all_metrics(formatted_portfolio_data)
            print(f"DEBUG: Portfolio metrics calculated: {list(metrics.keys()) if metrics else 'None'}")
            
            # Perform analysis
            analysis = self._analyze_portfolio(metrics, formatted_portfolio_data)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(analysis, metrics)
            
            # Prepare visualization data
            viz_data = self._prepare_visualization_data(formatted_portfolio_data, metrics)
            
            # Generate LLM response
            llm_context = self._build_analysis_context(metrics, analysis, recommendations, user_query)
            llm_response = self.llm.invoke(llm_context)
            response_text = llm_response.content if hasattr(llm_response, 'content') else str(llm_response)
            
            return {
                "agent_response": response_text,
                "portfolio_metrics": metrics,
                "analysis": analysis,
                "recommendations": recommendations,
                "visualization_data": viz_data,
                "sources": ["Portfolio analysis calculations", "Modern Portfolio Theory", "Diversification principles"],
                "confidence": 0.9,
                "next_agent": self._suggest_follow_up_agent(analysis),
                "metadata": {
                    "total_value": metrics.get("total_value", 0),
                    "num_holdings": metrics.get("num_holdings", 0),
                    "risk_level": metrics.get("risk_score", {}).get("level", "unknown")
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error in portfolio analysis: {str(e)}")
            return self.handle_error(e, "portfolio_analysis")
    
    def _extract_portfolio_from_query(self, query: str) -> Dict[str, Any]:
        """Extract portfolio holdings from user query text"""
        import re
        
        holdings = []
        
        # Look for patterns like "Apple $25,000", "AAPL: $25k", "I have $30,000 in VOO"
        patterns = [
            r'(\w+(?:\s+\w+)*)\s*[:\-]?\s*\$([0-9,]+(?:k|K|thousand|million)?)',
            r'\$([0-9,]+(?:k|K|thousand|million)?)\s+(?:in\s+)?(\w+(?:\s+\w+)*)',
            r'(\w+)\s+\$([0-9,]+(?:k|K|thousand|million)?)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            for match in matches:
                if len(match) == 2:
                    name, value_str = match
                    # Parse value string
                    value = self._parse_value_string(value_str)
                    if value > 0:
                        holdings.append({
                            'name': name.strip(),
                            'value': value
                        })
        
        if holdings:
            print(f"DEBUG: Extracted {len(holdings)} holdings from query")
            return {"holdings": holdings}
        
        return None
    
    def _parse_value_string(self, value_str: str) -> float:
        """Parse value strings like '$25,000', '25k', '$30k', etc."""
        import re
        
        # Remove dollar signs and spaces
        clean_str = re.sub(r'[$\s,]', '', value_str.lower())
        
        # Handle k/thousand multipliers
        if 'k' in clean_str or 'thousand' in clean_str:
            number = re.sub(r'[kthousand]', '', clean_str)
            try:
                return float(number) * 1000
            except ValueError:
                return 0
        
        # Handle million multipliers
        if 'm' in clean_str or 'million' in clean_str:
            number = re.sub(r'[mmillion]', '', clean_str)
            try:
                return float(number) * 1000000
            except ValueError:
                return 0
        
        # Regular number
        try:
            return float(clean_str)
        except ValueError:
            return 0
    
    def _analyze_portfolio(self, metrics: Dict, portfolio_data: Dict) -> Dict[str, Any]:
        """
        Comprehensive portfolio analysis including:
        - Asset allocation analysis
        - Diversification assessment
        - Risk evaluation
        - Cost analysis
        - Benchmark comparison
        """
        analysis = {
            "strengths": [],
            "weaknesses": [],
            "risk_assessment": {},
            "diversification_assessment": {},
            "allocation_assessment": {}
        }
        
        # Risk assessment
        risk_score = metrics.get("risk_score", {})
        analysis["risk_assessment"] = {
            "level": risk_score.get("level", "unknown"),
            "score": risk_score.get("score", 50),
            "description": risk_score.get("description", "")
        }
        
        # Diversification assessment
        div_score = metrics.get("diversification_score", 0)
        concentration_risk = metrics.get("concentration_risk", {})
        
        analysis["diversification_assessment"] = {
            "score": div_score,
            "concentration_level": concentration_risk.get("level", "unknown"),
            "largest_holding": metrics.get("largest_holding_percent", 0),
            "needs_improvement": div_score < 60 or concentration_risk.get("level") in ["high", "very_high"]
        }
        
        # Asset allocation assessment
        asset_allocation = metrics.get("asset_class_allocation", {})
        analysis["allocation_assessment"] = {
            "stock_heavy": asset_allocation.get("stocks", 0) > 80,
            "bond_light": asset_allocation.get("bonds", 0) < 10,
            "cash_heavy": asset_allocation.get("cash", 0) > 20,
            "well_balanced": 60 <= asset_allocation.get("stocks", 0) <= 80 and asset_allocation.get("bonds", 0) >= 15
        }
        
        # Identify strengths
        if div_score >= 70:
            analysis["strengths"].append("Well-diversified portfolio")
        if concentration_risk.get("level") in ["low", "very_low"]:
            analysis["strengths"].append("Low concentration risk")
        if analysis["allocation_assessment"]["well_balanced"]:
            analysis["strengths"].append("Balanced asset allocation")
        
        # Identify weaknesses
        if div_score < 50:
            analysis["weaknesses"].append("Poor diversification")
        if concentration_risk.get("level") in ["high", "very_high"]:
            analysis["weaknesses"].append("High concentration risk")
        if analysis["allocation_assessment"]["stock_heavy"]:
            analysis["weaknesses"].append("Overweight in stocks")
        if analysis["allocation_assessment"]["bond_light"]:
            analysis["weaknesses"].append("Underweight in bonds")
        
        return analysis
    
    def _generate_recommendations(self, analysis: Dict, metrics: Dict) -> List[Dict[str, Any]]:
        """
        Generate specific, actionable portfolio recommendations
        Prioritized by impact and ease of implementation
        """
        recommendations = []
        
        # Diversification recommendations
        if analysis["diversification_assessment"]["needs_improvement"]:
            if metrics.get("largest_holding_percent", 0) > 25:
                recommendations.append({
                    "type": "diversification",
                    "priority": "high",
                    "title": "Reduce concentration risk",
                    "description": f"Your largest holding represents {metrics.get('largest_holding_percent', 0):.1f}% of your portfolio. Consider reducing it to below 20%.",
                    "action": "Sell some of your largest position and diversify into other investments",
                    "target": "Largest holding <20% of portfolio"
                })
        
        # Asset allocation recommendations
        asset_allocation = metrics.get("asset_class_allocation", {})
        
        if asset_allocation.get("stocks", 0) > 85:
            recommendations.append({
                "type": "allocation",
                "priority": "medium",
                "title": "Add bonds for stability",
                "description": f"Your portfolio is {asset_allocation.get('stocks', 0):.1f}% stocks. Consider adding bonds for stability.",
                "action": "Allocate 15-25% to bond funds or ETFs",
                "target": "15-25% in bonds"
            })
        
        if asset_allocation.get("cash", 0) > 15:
            recommendations.append({
                "type": "allocation",
                "priority": "medium",
                "title": "Reduce cash allocation",
                "description": f"You have {asset_allocation.get('cash', 0):.1f}% in cash. Consider investing more for growth.",
                "action": "Invest excess cash in diversified funds",
                "target": "Keep only 3-6 months expenses in cash"
            })
        
        # Add low-cost index fund recommendation if needed
        if metrics.get("num_holdings", 0) < 5:
            recommendations.append({
                "type": "diversification",
                "priority": "high",
                "title": "Add broad market exposure",
                "description": "Consider adding low-cost index funds for instant diversification.",
                "action": "Add total stock market or S&P 500 index fund",
                "target": "Core holding of 30-50% in broad market fund"
            })
        
        # Ensure at least one recommendation
        if not recommendations:
            recommendations.append({
                "type": "maintenance",
                "priority": "low",
                "title": "Portfolio looks well-balanced",
                "description": "Your portfolio shows good diversification and allocation.",
                "action": "Continue regular rebalancing and review annually",
                "target": "Maintain current allocation with periodic rebalancing"
            })
        
        return recommendations[:4]  # Limit to top 4 recommendations
    
    def _prepare_visualization_data(self, portfolio_data: Dict, metrics: Dict) -> Dict[str, Any]:
        """
        Prepare data structures for Streamlit visualizations:
        - Pie chart data for allocation
        - Bar chart data for sectors/regions
        - Metrics table data
        """
        return {
            "allocation_pie": {
                "labels": [h["name"] for h in metrics.get("allocation", [])],
                "values": [h["percent"] for h in metrics.get("allocation", [])],
                "colors": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FECA57", "#FF9FF3", "#54A0FF"]
            },
            "asset_class_pie": {
                "labels": list(metrics.get("asset_class_allocation", {}).keys()),
                "values": list(metrics.get("asset_class_allocation", {}).values()),
                "colors": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4"]
            },
            "sector_bar": {
                "labels": list(metrics.get("sector_allocation", {}).keys()),
                "values": list(metrics.get("sector_allocation", {}).values())
            },
            "metrics_table": [
                {"Metric": "Total Value", "Value": f"${metrics.get('total_value', 0):,.2f}"},
                {"Metric": "Number of Holdings", "Value": str(metrics.get('num_holdings', 0))},
                {"Metric": "Diversification Score", "Value": f"{metrics.get('diversification_score', 0)}/100"},
                {"Metric": "Risk Level", "Value": metrics.get('risk_score', {}).get('level', 'Unknown').title()},
                {"Metric": "Largest Holding", "Value": f"{metrics.get('largest_holding_percent', 0):.1f}%"},
                {"Metric": "Top 3 Holdings", "Value": f"{metrics.get('top_3_holdings_percent', 0):.1f}%"}
            ]
        }
    
    def _build_analysis_context(self, metrics: Dict, analysis: Dict, recommendations: List, user_query: str) -> str:
        """Build context for LLM to generate portfolio analysis response"""
        
        context = f"""
Based on the portfolio analysis data below, provide a comprehensive portfolio review that addresses the user's question: "{user_query}"

PORTFOLIO METRICS:
- Total Value: ${metrics.get('total_value', 0):,.2f}
- Number of Holdings: {metrics.get('num_holdings', 0)}
- Diversification Score: {metrics.get('diversification_score', 0)}/100
- Risk Level: {metrics.get('risk_score', {}).get('level', 'unknown').title()}
- Largest Holding: {metrics.get('largest_holding_percent', 0):.1f}%

ASSET ALLOCATION:
{self._format_allocation_text(metrics.get('asset_class_allocation', {}))}

ANALYSIS SUMMARY:
Strengths: {', '.join(analysis.get('strengths', []))}
Areas for Improvement: {', '.join(analysis.get('weaknesses', []))}

KEY RECOMMENDATIONS:
{self._format_recommendations_text(recommendations)}

Please provide:
1. An overall assessment of the portfolio's health
2. Explanation of key metrics in beginner-friendly terms
3. Specific, actionable advice based on the recommendations
4. Appropriate disclaimers about investment advice

Use a helpful, educational tone suitable for someone learning about investing.
"""
        return context
    
    def _format_allocation_text(self, allocation: Dict[str, float]) -> str:
        """Format asset allocation for context"""
        if not allocation:
            return "No allocation data available"
        
        formatted = []
        for asset_class, percent in allocation.items():
            formatted.append(f"- {asset_class.title()}: {percent}%")
        return "\n".join(formatted)
    
    def _format_recommendations_text(self, recommendations: List[Dict]) -> str:
        """Format recommendations for context"""
        if not recommendations:
            return "No specific recommendations at this time"
        
        formatted = []
        for i, rec in enumerate(recommendations, 1):
            formatted.append(f"{i}. {rec['title']}: {rec['description']}")
        return "\n".join(formatted)
    
    def _request_portfolio_data(self) -> Dict[str, Any]:
        """Return response requesting portfolio data upload"""
        response_text = """To analyze your portfolio, I need access to your portfolio data. Here are your options:

📊 **How to provide your portfolio data:**

1. **Portfolio Tab**: Go to the 📊 Portfolio tab and:
   - Upload a CSV file, OR
   - Add holdings manually using the "Manual Entry" tab, OR
   - Enter your portfolio in text format

2. **Chat Method**: Tell me your holdings directly here in the chat like:
   - "I have $25,000 in Apple stock, $30,000 in VOO ETF, and $15,000 in bonds"
   - "My portfolio: AAPL $25k, SPY $30k, BND $15k"

**Example Portfolio Data:**
- Apple Stock (AAPL): $25,000
- Vanguard S&P 500 ETF (VOO): $30,000  
- Bond Fund (BND): $15,000
- Cash: $5,000

Once you provide your portfolio data, I can analyze:
✅ Asset allocation and diversification
✅ Risk assessment
✅ Specific recommendations for improvement
✅ Interactive visualizations

**💡 Tip**: If you already added your portfolio in the Portfolio tab, make sure to click "📊 Analyze Portfolio" to save the data, then return here to ask your question again."""

        return {
            "agent_response": response_text,
            "sources": [],
            "confidence": 1.0,
            "metadata": {"requires_portfolio_data": True}
        }
    
    def _suggest_follow_up_agent(self, analysis: Dict) -> Optional[str]:
        """Suggest which agent should handle follow-up questions"""
        if analysis.get("risk_assessment", {}).get("level") == "aggressive":
            return "goal_agent"  # For risk tolerance discussion
        return None
    
    def parse_portfolio_input(self, input_data: Any) -> Dict[str, Any]:
        """
        Parse portfolio data from various input formats:
        - CSV files with ticker symbols and quantities
        - Manual entry with asset names and values
        - JSON structured data
        """
        try:
            if isinstance(input_data, str):
                # Try to parse as CSV string
                if ',' in input_data and '\n' in input_data:
                    df = pd.read_csv(io.StringIO(input_data))
                    return self._parse_dataframe(df)
                else:
                    # Parse as text list
                    return self._parse_text_input(input_data)
            
            elif hasattr(input_data, 'read'):
                # File-like object (uploaded file)
                df = pd.read_csv(input_data)
                return self._parse_dataframe(df)
            
            elif isinstance(input_data, dict):
                # Already structured data
                return input_data
            
            else:
                raise ValueError("Unsupported input format")
                
        except Exception as e:
            self.logger.error(f"Error parsing portfolio input: {str(e)}")
            return {"holdings": [], "error": str(e)}
    
    def _parse_dataframe(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Parse portfolio data from pandas DataFrame"""
        holdings = []
        
        # Standardize column names
        df.columns = df.columns.str.lower().str.strip()
        
        for _, row in df.iterrows():
            holding = {}
            
            # Required fields
            holding['name'] = str(row.get('name', row.get('symbol', 'Unknown')))
            holding['value'] = float(row.get('value', row.get('amount', 0)))
            
            # Optional fields
            if 'symbol' in row:
                holding['symbol'] = str(row['symbol'])
            if 'type' in row:
                holding['type'] = str(row['type'])
            if 'sector' in row:
                holding['sector'] = str(row['sector'])
            
            holdings.append(holding)
        
        return {"holdings": holdings}
    
    def _parse_text_input(self, text: str) -> Dict[str, Any]:
        """Parse portfolio data from text input"""
        holdings = []
        lines = text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Try to extract name and value
            # Formats: "Apple: $1000", "AAPL - $1000", "Apple Stock $1000"
            import re
            
            # Remove currency symbols and extract number
            value_match = re.search(r'[\$]?([0-9,]+(?:\.[0-9]{2})?)', line)
            if value_match:
                value = float(value_match.group(1).replace(',', ''))
                name = line[:value_match.start()].strip(' :-$')
                
                holdings.append({
                    'name': name,
                    'value': value
                })
        
        return {"holdings": holdings}