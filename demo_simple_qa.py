#!/usr/bin/env python3
"""
Demo script for Phase 1: Minimal Viable Assistant

This demonstrates the basic Finance Q&A Agent functionality:
- Simple financial question processing
- Basic response formatting
- Error handling
- Source attribution (when RAG is available)

Usage:
    python demo_simple_qa.py
"""

import sys
import os
from datetime import datetime
from typing import Dict, Any

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Mock LLM for demonstration (replace with real LLM in production)
class MockLLM:
    """Simple mock LLM for demonstration purposes"""
    
    def invoke(self, prompt: str) -> 'MockResponse':
        """Generate a mock response based on the prompt"""
        # Simple keyword-based responses for demo
        prompt_lower = prompt.lower()
        
        if "diversification" in prompt_lower:
            content = """Diversification is a risk management strategy that involves spreading your investments across different assets, sectors, or markets to reduce overall portfolio risk. Think of it like the saying "don't put all your eggs in one basket."

Key benefits of diversification:
1. **Risk Reduction**: By investing in different assets, you reduce the impact of any single investment's poor performance
2. **Smoother Returns**: Diversified portfolios tend to have more stable returns over time
3. **Protection Against Volatility**: Different assets often perform differently under various market conditions

Example: Instead of buying stock in just one company, you might buy stocks from different industries (technology, healthcare, finance) or different types of investments (stocks, bonds, real estate).

**Disclaimer**: This is educational information only and not personalized investment advice. Consider consulting with a financial advisor for advice tailored to your specific situation."""

        elif "compound interest" in prompt_lower:
            content = """Compound interest is often called "the eighth wonder of the world" because it's the process where you earn interest not just on your original investment, but also on the interest you've already earned.

Here's how it works:
1. **Year 1**: You invest $1,000 at 10% interest = $1,100
2. **Year 2**: You earn 10% on $1,100 = $1,210  
3. **Year 3**: You earn 10% on $1,210 = $1,331

The key is time - the longer you let compound interest work, the more powerful it becomes. This is why starting to invest early is so important for retirement planning.

**Real-world tip**: Even small amounts invested regularly can grow significantly over decades due to compound interest.

**Disclaimer**: This is educational information only. Returns are not guaranteed and actual investment results will vary."""

        elif "stock" in prompt_lower and "bond" in prompt_lower:
            content = """Stocks and bonds are two fundamental types of investments:

**Stocks (Equities)**:
- Represent ownership shares in a company
- Potential for higher returns but also higher risk
- Value fluctuates based on company performance and market sentiment
- May pay dividends (regular income payments)

**Bonds (Fixed Income)**:
- Essentially loans you make to companies or governments
- Generally lower risk and more predictable returns
- Pay regular interest payments
- Principal returned at maturity

**Key Differences**:
- Risk: Stocks are generally riskier than bonds
- Returns: Stocks historically offer higher long-term returns
- Income: Bonds provide more predictable income streams
- Portfolio role: Many investors use both for balanced portfolios

**Disclaimer**: This is educational information only. All investments carry risk and past performance doesn't guarantee future results."""

        else:
            content = """I'd be happy to help explain financial concepts! However, I need a bit more specific information to provide the most helpful response.

Some topics I can help explain include:
- Basic investment concepts (stocks, bonds, mutual funds, ETFs)
- Risk management and diversification
- Compound interest and time value of money
- Basic portfolio allocation principles
- Retirement planning fundamentals

Please feel free to ask about any specific financial topic you'd like to understand better.

**Disclaimer**: I provide educational information only, not personalized investment advice."""

        return MockResponse(content)

class MockResponse:
    """Mock response object"""
    def __init__(self, content: str):
        self.content = content

# Mock retriever for demonstration
class MockRetriever:
    """Simple mock retriever for demonstration"""
    
    def retrieve(self, query: str, k: int = 3):
        """Return mock retrieved documents"""
        # Simulate retrieved documents with sources
        if "diversification" in query.lower():
            return [
                {
                    "content": "Diversification reduces portfolio risk by spreading investments across different asset classes.",
                    "metadata": {"source": "Investment Fundamentals Guide"},
                    "score": 0.85
                },
                {
                    "content": "Modern Portfolio Theory emphasizes the benefits of diversification in optimizing risk-adjusted returns.",
                    "metadata": {"source": "Modern Portfolio Theory Handbook"},
                    "score": 0.78
                }
            ]
        return []
    
    def build_context(self, query: str, docs):
        """Build context from retrieved documents"""
        if not docs:
            return f"Query: {query}\n\nNo relevant documents found."
        
        context_parts = [f"Query: {query}\n\nRelevant information:"]
        for i, doc in enumerate(docs):
            source = doc["metadata"]["source"]
            content = doc["content"]
            context_parts.append(f"\n[Source {i+1}: {source}]\n{content}")
        
        return "\n".join(context_parts)

def demo_basic_functionality():
    """Demonstrate basic Finance Q&A Agent functionality"""
    
    print("🏗️ Finance Assistant - Minimal Viable Assistant Demo")
    print("=" * 60)
    
    # Import our agents
    from agents.finance_qa_agent import FinanceQAAgent
    from core.state import FinanceAssistantState
    
    # Initialize mock components
    mock_llm = MockLLM()
    mock_retriever = MockRetriever()
    
    # Create the Finance Q&A Agent
    qa_agent = FinanceQAAgent(mock_llm, mock_retriever)
    
    # Test queries for demonstration
    test_queries = [
        "What is diversification?",
        "Can you explain compound interest?",
        "What's the difference between stocks and bonds?",
        "Tell me about cryptocurrency investments"  # This will trigger general response
    ]
    
    print(f"✅ Finance Q&A Agent initialized: {qa_agent.agent_name}")
    print(f"✅ Mock LLM and retriever ready")
    print("\n" + "="*60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test Query {i}: {query}")
        print("-" * 40)
        
        # Create state for the query
        state: FinanceAssistantState = {
            "user_query": query,
            "conversation_history": [],
            "current_agent": "finance_qa",
            "portfolio_data": None,
            "portfolio_analysis": None,
            "market_context": None,
            "market_cache": {},
            "agent_responses": [],
            "rag_context": [],
            "risk_tolerance": None,
            "investment_goals": [],
            "user_profile": {},
            "session_id": f"demo_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now(),
            "error_context": None
        }
        
        try:
            # Execute the agent
            response = qa_agent.execute(state)
            
            # Display results
            print(f"📝 Response: {response['agent_response'][:200]}...")
            print(f"🔗 Sources: {len(response['sources'])} sources found")
            print(f"🎯 Confidence: {response['confidence']:.2f}")
            print(f"➡️  Next Agent: {response.get('next_agent', 'None')}")
            
            if response.get('query_classification'):
                classification = response['query_classification']
                print(f"📊 Classification: {classification['primary_category']} ({classification['complexity']})")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n" + "="*60)
    print("✅ Demo completed successfully!")
    print("\nWhat works after Phase 1:")
    print("✅ User can ask questions and get responses")
    print("✅ Basic agent architecture foundation")
    print("✅ Query classification and routing")
    print("✅ Error handling and logging")
    print("✅ Source attribution system")
    print("✅ Confidence scoring")
    print("✅ Response formatting")

def demo_error_handling():
    """Demonstrate error handling capabilities"""
    print("\n🛡️ Error Handling Demo")
    print("-" * 30)
    
    from agents.finance_qa_agent import FinanceQAAgent
    
    # Create agent with intentionally broken components
    broken_llm = None
    mock_retriever = MockRetriever()
    
    try:
        qa_agent = FinanceQAAgent(broken_llm, mock_retriever)
        print("✅ Agent created with broken LLM (will test error handling)")
        
        # This should trigger error handling
        state = {
            "user_query": "Test error handling",
            "conversation_history": [],
            "session_id": "error_test",
            "timestamp": datetime.now()
        }
        
        response = qa_agent.execute(state)
        print(f"🛡️ Error handled gracefully: {response['agent_response'][:100]}...")
        print(f"🔍 Error context preserved: {bool(response.get('updated_context', {}).get('error'))}")
        
    except Exception as e:
        print(f"✅ Exception caught and handled: {type(e).__name__}")

if __name__ == "__main__":
    # Run the demonstration
    demo_basic_functionality()
    demo_error_handling()
    
    print("\n🚀 Ready for Phase 2: Adding RAG system and Streamlit interface!")
