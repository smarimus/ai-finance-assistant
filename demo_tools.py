#!/usr/bin/env python3
"""
Simple demo of individual Alpha Vantage tools
Shows how tools work independently of agents
"""

import os
import sys
from dotenv import load_dotenv

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from src.tools.market_tools import (
    AlphaVantageQuoteTool,
    AlphaVantageMarketOverviewTool,
    AlphaVantageSymbolSearchTool,
    create_market_tools
)
from src.data.market_data import MarketDataProvider

def demo_individual_tools():
    """Demonstrate individual tool usage"""
    print("🛠️ **Alpha Vantage Tools Demo**\n")
    
    # Create market provider
    provider = MarketDataProvider()
    print(f"📊 Market Provider: {'Mock Mode' if provider.mock_mode else 'Live API'}\n")
    
    # Demo 1: Stock Quote Tool
    print("1️⃣ **Stock Quote Tool Demo**")
    print("─" * 40)
    quote_tool = AlphaVantageQuoteTool(provider)
    
    try:
        result = quote_tool._run("AAPL")
        print(f"Tool Name: {quote_tool.name}")
        print(f"Description: {quote_tool.description[:100]}...")
        print(f"Result:\n{result}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n")
    
    # Demo 2: Market Overview Tool
    print("2️⃣ **Market Overview Tool Demo**")
    print("─" * 40)
    overview_tool = AlphaVantageMarketOverviewTool(provider)
    
    try:
        result = overview_tool._run()
        print(f"Tool Name: {overview_tool.name}")
        print(f"Result:\n{result}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n")
    
    # Demo 3: Symbol Search Tool
    print("3️⃣ **Symbol Search Tool Demo**")
    print("─" * 40)
    search_tool = AlphaVantageSymbolSearchTool(provider)
    
    try:
        result = search_tool._run("artificial intelligence")
        print(f"Tool Name: {search_tool.name}")
        print(f"Result:\n{result}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n")
    
    # Demo 4: All Tools via Factory
    print("4️⃣ **All Tools via Factory**")
    print("─" * 40)
    all_tools = create_market_tools(provider)
    
    print(f"Created {len(all_tools)} tools:")
    for i, tool in enumerate(all_tools, 1):
        print(f"   {i}. {tool.name}: {tool.description[:60]}...")
    
    print(f"\n✅ **Demo Complete!**")
    print("\n💡 **Key Points:**")
    print("🔹 Each tool is a self-contained LangChain BaseTool")
    print("🔹 Tools can be used independently or with agents")
    print("🔹 Tools handle their own error cases and formatting")
    print("🔹 LLMs can decide when and how to use these tools")

if __name__ == "__main__":
    demo_individual_tools()
