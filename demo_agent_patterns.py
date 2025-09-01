#!/usr/bin/env python3
"""
Demo script to test both integration patterns for Market Agent
This script shows the difference between direct integration and tool calling
"""

import os
import sys
from dotenv import load_dotenv

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

from langchain_openai import ChatOpenAI
from src.agents.enhanced_market_agent import EnhancedMarketAnalysisAgent
from src.core.config import AgentConfig, load_config
from src.data.market_data import MarketDataProvider

def test_integration_patterns():
    """Test both direct and tool calling integration patterns"""
    
    print("🚀 **Testing Market Agent Integration Patterns**\n")
    
    # Initialize LLM
    try:
        llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.1,
            max_tokens=1000
        )
        print("✅ LLM initialized")
    except Exception as e:
        print(f"❌ Failed to initialize LLM: {e}")
        return
    
    # Load configuration
    config = load_config()
    market_provider = MarketDataProvider()
    
    print(f"📊 Market Provider Status: {'Mock Mode' if market_provider.mock_mode else 'Live API'}")
    print()
    
    # Test queries
    test_queries = [
        "What's the current price of AAPL?",
        "How are the markets doing today?",
        "Compare AAPL and MSFT stock performance",
        "Find stocks related to artificial intelligence"
    ]
    
    # Test both integration patterns
    for mode in ["direct", "tools"]:
        print(f"{'='*60}")
        print(f"🧪 **Testing {mode.upper()} Integration Pattern**")
        print(f"{'='*60}\n")
        
        # Create agent config for this mode
        agent_config = AgentConfig(
            integration_mode=mode,
            enable_tool_calling=(mode == "tools"),
            max_tool_calls=5
        )
        
        # Create agent
        try:
            agent = EnhancedMarketAnalysisAgent(
                llm=llm,
                agent_config=agent_config,
                market_provider=market_provider
            )
            
            # Show integration info
            info = agent.get_integration_info()
            print(f"🔧 Integration Info:")
            print(f"   - Mode: {info['integration_mode']}")
            print(f"   - Tools Available: {info['tools_available']}")
            print(f"   - Tool Names: {', '.join(info['tool_names']) if info['tool_names'] else 'None'}")
            print(f"   - Has Agent Executor: {info['has_agent_executor']}")
            print()
            
        except Exception as e:
            print(f"❌ Failed to create agent in {mode} mode: {e}")
            continue
        
        # Test each query
        for i, query in enumerate(test_queries, 1):
            print(f"📝 **Query {i}**: {query}")
            print(f"{'─'*40}")
            
            try:
                # Execute query
                result = agent.execute({"user_query": query})
                
                # Show results
                print(f"🤖 **Response**:")
                print(f"{result.get('agent_response', 'No response')[:300]}...")
                print()
                print(f"📊 **Metadata**:")
                print(f"   - Integration Mode: {result.get('integration_mode', 'Unknown')}")
                print(f"   - Confidence: {result.get('confidence', 0):.2f}")
                print(f"   - Sources: {', '.join(result.get('sources', []))}")
                if 'tools_used' in result:
                    print(f"   - Tools Used: {', '.join(result['tools_used'])}")
                print()
                
            except Exception as e:
                print(f"❌ Error executing query: {e}")
                print()
            
            print(f"{'─'*40}\n")
        
        print(f"✅ Completed testing {mode.upper()} mode\n")
    
    print("🎉 **Testing Complete!**")
    print("\n📚 **Key Differences Observed:**")
    print("🔸 **Direct Mode**: Agent controls data fetching, faster execution")
    print("🔸 **Tools Mode**: LLM decides when/how to use tools, more flexible")
    print("\n💡 **Learning Points:**")
    print("🔹 Tool calling allows LLM autonomy in decision making")
    print("🔹 Direct integration gives more predictable control flow")
    print("🔹 Both patterns have their use cases in AI agent development")

def test_configuration_switching():
    """Test switching configurations dynamically"""
    print("\n🔄 **Testing Configuration Switching**\n")
    
    # Load config and show current settings
    config = load_config()
    market_config = config.agents.get('market_agent')
    
    print(f"📋 **Current Config from YAML**:")
    print(f"   - Integration Mode: {market_config.integration_mode}")
    print(f"   - Tool Calling Enabled: {market_config.enable_tool_calling}")
    print(f"   - Max Tool Calls: {market_config.max_tool_calls}")
    print()
    
    print("💡 **To switch modes, edit config.yaml:**")
    print("```yaml")
    print("agents:")
    print("  market_agent:")
    print("    integration_mode: 'direct'  # or 'tools'")
    print("    enable_tool_calling: false  # or true")
    print("```")

if __name__ == "__main__":
    # Run the tests
    test_integration_patterns()
    test_configuration_switching()
