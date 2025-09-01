#!/usr/bin/env python3
"""
Test portfolio data extraction
"""
import re

def test_contains_portfolio_data(query: str) -> bool:
    """Check if query contains portfolio data (holdings with values)"""
    # Look for patterns like "Stock: $1000" or "AAPL $500" or "$10,000" or "stock: 35000"
    money_patterns = [
        r'[\$]?[0-9,]+(?:\.[0-9]{2})?',  # $1000 or 1000
        r'[a-zA-Z]+\s*(?:stock|shares?)\s*[:]\s*[\$]?[0-9,]+',  # Meta stock: $35000
        r'[a-zA-Z]+\s*[:]\s*[\$]?[0-9,]+'  # Meta: 35000
    ]
    
    for pattern in money_patterns:
        if re.search(pattern, query, re.IGNORECASE):
            print(f"Pattern '{pattern}' matched in query")
            return True
    return False

def test_extract_portfolio_data(query: str):
    """Extract portfolio holdings from text query"""
    try:
        holdings = []
        lines = query.strip().split('\n')
        
        print(f"Extracting portfolio data from {len(lines)} lines")
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            print(f"Processing line: '{line}'")
            
            # Enhanced patterns to match various formats
            patterns = [
                r'([a-zA-Z\s]+?)(?:stock|shares?)?\s*[:]\s*\$?([0-9,]+(?:\.[0-9]{2})?)',
                r'([a-zA-Z\s]+?)\s*\$([0-9,]+(?:\.[0-9]{2})?)',
                r'([a-zA-Z\s]+?)\s*[:]\s*([0-9,]+(?:\.[0-9]{2})?)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    name = match.group(1).strip()
                    value_str = match.group(2).replace(',', '')
                    
                    try:
                        value = float(value_str)
                        
                        # Clean up the name
                        name = re.sub(r'\s*(stock|shares?|fund|etf)\s*', '', name, flags=re.IGNORECASE).strip()
                        
                        if name and value > 0:
                            holding = {
                                'name': name.title(),
                                'symbol': name.upper() if len(name) <= 5 else '',
                                'value': value,
                                'type': 'stock'
                            }
                            holdings.append(holding)
                            print(f"Extracted holding: {holding}")
                            break
                    except ValueError:
                        continue
        
        result = {"holdings": holdings} if holdings else {}
        print(f"Final extracted portfolio data: {result}")
        return result
        
    except Exception as e:
        print(f"Error extracting portfolio data: {e}")
        import traceback
        traceback.print_exc()
        return {}

# Test the problematic query
test_query = """What's my portfolio risk level?
Meta stock: $35000
Amazon stock: $5000"""

print("=== TESTING PORTFOLIO DATA EXTRACTION ===")
print(f"Query: {repr(test_query)}")
print()

print("1. Testing contains_portfolio_data:")
contains_data = test_contains_portfolio_data(test_query)
print(f"Result: {contains_data}")
print()

print("2. Testing extract_portfolio_data:")
extracted_data = test_extract_portfolio_data(test_query)
print(f"Final result: {extracted_data}")
