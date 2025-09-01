# Helper utilities for the finance assistant
# Common functions, data validation, formatting utilities

from typing import Any, Dict, List, Optional
import re
from datetime import datetime

def validate_portfolio_data(data: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate portfolio data format and content
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not isinstance(data, dict):
        return False, "Portfolio data must be a dictionary"
    
    required_fields = ["holdings"]
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    return True, ""

def format_currency(amount: float, currency: str = "USD") -> str:
    """Format amount as currency string"""
    if currency == "USD":
        return f"${amount:,.2f}"
    return f"{amount:,.2f} {currency}"

def format_percentage(value: float, decimal_places: int = 2) -> str:
    """Format value as percentage string"""
    return f"{value:.{decimal_places}f}%"

def parse_ticker_symbol(text: str) -> Optional[str]:
    """Extract ticker symbol from text"""
    # Simple regex for ticker symbols (1-5 uppercase letters)
    pattern = r'\b[A-Z]{1,5}\b'
    matches = re.findall(pattern, text)
    return matches[0] if matches else None

def calculate_time_difference(start_date: datetime, end_date: datetime) -> Dict[str, int]:
    """Calculate time difference in years, months, days"""
    diff = end_date - start_date
    years = diff.days // 365
    remaining_days = diff.days % 365
    months = remaining_days // 30
    days = remaining_days % 30
    
    return {
        "years": years,
        "months": months,
        "days": days,
        "total_days": diff.days
    }

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, return default if denominator is zero"""
    return numerator / denominator if denominator != 0 else default