#!/usr/bin/env python3
"""
Streamlit Finance Assistant - MVP Version
Simple interactive interface for testing the Finance Q&A Agent
"""

import streamlit as st
import sys
import os
from datetime import datetime
from typing import Dict, Any, List

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Mock LLM for demonstration (replace with real LLM in production)
class MockLLM:
    """Simple mock LLM for demonstration purposes"""
    
    def invoke(self, prompt: str) -> 'MockResponse':
        """Generate a mock response based on the prompt"""
        prompt_lower = prompt.lower()
        
        if "diversification" in prompt_lower:
            content = """Diversification is a risk management strategy that involves spreading your investments across different assets, sectors, or markets to reduce overall portfolio risk. Think of it like the saying "don't put all your eggs in one basket."

Key benefits of diversification:
1. **Risk Reduction**: By investing in different assets, you reduce the impact of any single investment's poor performance
2. **Smoother Returns**: Diversified portfolios tend to have more stable returns over time
3. **Protection Against Volatility**: Different assets often perform differently under various market conditions

Example: Instead of buying stock in just one company, you might buy stocks from different industries (technology, healthcare, finance) or different types of investments (stocks, bonds, real estate).

**Disclaimer**: This is educational information only and not personalized investment advice."""

        elif "compound interest" in prompt_lower:
            content = """Compound interest is often called "the eighth wonder of the world" because it's the process where you earn interest not just on your original investment, but also on the interest you've already earned.

Here's how it works:
1. **Year 1**: You invest $1,000 at 10% interest = $1,100
2. **Year 2**: You earn 10% on $1,100 = $1,210  
3. **Year 3**: You earn 10% on $1,210 = $1,331

The key is time - the longer you let compound interest work, the more powerful it becomes. This is why starting to invest early is so important for retirement planning."""

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
- Principal returned at maturity"""

        elif "portfolio" in prompt_lower:
            content = """A portfolio is your collection of investments. Here are key principles for building a good portfolio:

1. **Asset Allocation**: Mix of stocks, bonds, and other investments
2. **Diversification**: Spread investments across different sectors and asset classes
3. **Risk Tolerance**: Match investments to your comfort with volatility
4. **Time Horizon**: Longer timeline allows for more aggressive strategies
5. **Regular Rebalancing**: Maintain your target allocation over time

A simple starting portfolio might be:
- 60% stocks (for growth)
- 40% bonds (for stability)

Adjust based on your age, goals, and risk tolerance."""

        elif "retirement" in prompt_lower:
            content = """Retirement planning is one of the most important financial goals. Key strategies:

**Start Early**: Time is your biggest advantage due to compound interest
**Maximize Employer Match**: Free money from 401(k) matching
**Use Tax-Advantaged Accounts**: 401(k), IRA, Roth IRA
**Estimate Needs**: Plan for 70-90% of current income in retirement
**Diversify Income Sources**: Social Security, employer plans, personal savings

The "4% Rule": You can generally withdraw 4% of your retirement savings annually without running out of money.

Example: $1 million saved × 4% = $40,000 annual retirement income"""

        else:
            content = """I'd be happy to help explain financial concepts! Here are some topics I can assist with:

📊 **Investment Basics**
- Stocks, bonds, mutual funds, ETFs
- Risk vs. return concepts
- Portfolio diversification

💰 **Financial Planning**
- Retirement planning
- Emergency funds
- Goal setting and budgeting

🎯 **Investment Strategies**
- Asset allocation
- Dollar-cost averaging
- Rebalancing

📈 **Market Concepts**
- Market volatility
- Economic indicators
- Investment time horizons

Feel free to ask about any specific topic!

**Disclaimer**: This is educational information only, not personalized investment advice."""

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
        elif "compound" in query.lower():
            return [
                {
                    "content": "Compound interest is the addition of interest to the principal sum of a loan or deposit.",
                    "metadata": {"source": "Financial Mathematics Textbook"},
                    "score": 0.92
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

def setup_page():
    """Configure Streamlit page"""
    st.set_page_config(
        page_title="AI Finance Assistant",
        page_icon="🏦",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .agent-response {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1976d2;
        margin: 1rem 0;
    }
    
    .source-citation {
        background-color: #f5f5f5;
        padding: 0.5rem;
        border-radius: 4px;
        margin: 0.5rem 0;
        font-size: 0.9rem;
        border-left: 3px solid #4caf50;
    }
    
    .confidence-score {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    
    .confidence-high { background-color: #4caf50; color: white; }
    .confidence-medium { background-color: #ff9800; color: white; }
    .confidence-low { background-color: #f44336; color: white; }
    </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    
    if "qa_agent" not in st.session_state:
        # Create a simple mock agent for demonstration
        st.session_state.qa_agent = SimpleFinanceAgent()

class SimpleFinanceAgent:
    """Simple Finance Agent for MVP testing"""
    
    def __init__(self):
        self.llm = MockLLM()
        self.retriever = MockRetriever()
        self.agent_name = "finance_qa"
    
    def execute(self, state):
        """Execute the finance Q&A logic"""
        try:
            query = state["user_query"]
            
            # Get retrieved documents for context
            retrieved_docs = self.retriever.retrieve(query)
            
            # Build context for LLM
            context = self.retriever.build_context(query, retrieved_docs)
            
            # Generate response using MockLLM
            llm_response = self.llm.invoke(f"Context: {context}\n\nQuestion: {query}")
            
            # Extract sources
            sources = [doc["metadata"]["source"] for doc in retrieved_docs]
            
            # Calculate simple confidence
            confidence = 0.8 if retrieved_docs else 0.6
            
            # Format response
            response_text = llm_response.content
            if sources:
                response_text += f"\n\n**Sources:**\n"
                for i, source in enumerate(sources, 1):
                    response_text += f"{i}. {source}\n"
            
            return {
                "agent_response": response_text,
                "sources": sources,
                "confidence": confidence,
                "agent_name": self.agent_name,
                "query_classification": {
                    "primary_category": "basic_concepts",
                    "complexity": "basic"
                },
                "next_agent": None,
                "updated_context": {}
            }
            
        except Exception as e:
            return {
                "agent_response": f"I apologize, but I encountered an error processing your question: {str(e)}. Please try rephrasing your question.",
                "sources": [],
                "confidence": 0.0,
                "agent_name": self.agent_name,
                "next_agent": None,
                "updated_context": {"error": str(e)}
            }

def render_sidebar():
    """Render sidebar with app info and controls"""
    with st.sidebar:
        st.markdown("### 🏦 AI Finance Assistant")
        st.markdown("**Phase 1: Minimal Viable Assistant**")
        
        st.markdown("---")
        st.markdown("### Features")
        st.markdown("✅ Basic financial Q&A")
        st.markdown("✅ Query classification")
        st.markdown("✅ Source citations")
        st.markdown("✅ Confidence scoring")
        st.markdown("✅ Error handling")
        
        st.markdown("---")
        st.markdown("### Sample Questions")
        sample_questions = [
            "What is diversification?",
            "Explain compound interest",
            "Difference between stocks and bonds?",
            "How to build a portfolio?",
            "Retirement planning basics"
        ]
        
        for question in sample_questions:
            if st.button(question, key=f"sample_{question}", use_container_width=True):
                st.session_state.suggested_question = question
        
        st.markdown("---")
        # Session info
        st.markdown("### Session Info")
        st.markdown(f"**Messages**: {len(st.session_state.conversation_history)}")
        
        if st.button("Clear Chat History", type="secondary", use_container_width=True):
            st.session_state.conversation_history = []
            st.rerun()

def render_conversation_history():
    """Display conversation history"""
    if not st.session_state.conversation_history:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; color: #666;">
            👋 Welcome! Ask me any financial question to get started.<br>
            Try questions about investing, retirement planning, or portfolio management.
        </div>
        """, unsafe_allow_html=True)
        return
    
    for message in st.session_state.conversation_history:
        # User message
        with st.chat_message("user"):
            st.write(message["user"])
        
        # Assistant message
        with st.chat_message("assistant"):
            st.write(message["assistant"])
            
            # Show sources if available
            if message.get("sources"):
                st.markdown("**Sources:**")
                for i, source in enumerate(message["sources"], 1):
                    st.markdown(f'<div class="source-citation">{i}. {source}</div>', unsafe_allow_html=True)
            
            # Show confidence score
            if message.get("confidence"):
                confidence = message["confidence"]
                if confidence >= 0.8:
                    confidence_class = "confidence-high"
                    confidence_text = "High"
                elif confidence >= 0.6:
                    confidence_class = "confidence-medium"
                    confidence_text = "Medium"
                else:
                    confidence_class = "confidence-low"
                    confidence_text = "Low"
                
                st.markdown(f'<span class="confidence-score {confidence_class}">Confidence: {confidence_text} ({confidence:.2f})</span>', unsafe_allow_html=True)

def process_user_input(user_input: str):
    """Process user input and get agent response - simplified version"""
    if not st.session_state.qa_agent:
        return "Finance Q&A Agent not initialized. Please check the setup."
    
    try:
        # Create state for the query
        from src.core.state import FinanceAssistantState
        
        state: FinanceAssistantState = {
            "user_query": user_input,
            "conversation_history": st.session_state.conversation_history,
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
            "session_id": f"streamlit_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now(),
            "error_context": None
        }
        
        # Execute the agent
        response = st.session_state.qa_agent.execute(state)
        return response
        
    except Exception as e:
        return {
            "agent_response": f"Error processing your question: {str(e)}",
            "sources": [],
            "confidence": 0.0
        }

def main():
    """Main application"""
    setup_page()
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🏦 AI Finance Assistant</h1>', unsafe_allow_html=True)
    st.markdown("**Phase 1: Minimal Viable Assistant** - Ask financial questions and get educational answers")
    
    # Render sidebar
    render_sidebar()
    
    # Main chat interface
    st.markdown("### 💬 Chat with Your Finance Assistant")
    
    # Display conversation history
    render_conversation_history()
    
    # Handle suggested question from sidebar first
    if hasattr(st.session_state, 'suggested_question'):
        suggested_input = st.session_state.suggested_question
        delattr(st.session_state, 'suggested_question')
        
        # Add to conversation history immediately
        conversation_entry = {
            "user": suggested_input,
            "assistant": "Processing your question...",
            "sources": [],
            "confidence": 0.0,
            "timestamp": datetime.now().isoformat()
        }
        
        # Process the suggested question
        try:
            # Simple state for the mock agent
            state = {
                "user_query": suggested_input,
                "conversation_history": st.session_state.conversation_history
            }
            
            if st.session_state.qa_agent:
                response = st.session_state.qa_agent.execute(state)
                conversation_entry["assistant"] = response["agent_response"]
                conversation_entry["sources"] = response.get("sources", [])
                conversation_entry["confidence"] = response.get("confidence", 0.0)
            else:
                conversation_entry["assistant"] = "Sorry, the finance agent is not available right now."
                
        except Exception as e:
            conversation_entry["assistant"] = f"Error processing question: {str(e)}"
        
        st.session_state.conversation_history.append(conversation_entry)
        st.rerun()
    
    # Chat input
    user_input = st.chat_input("Ask me anything about finance, investing, or retirement planning...")
    
    # Process input from chat
    if user_input:
        # Add to conversation history
        conversation_entry = {
            "user": user_input,
            "assistant": "Processing your question...",
            "sources": [],
            "confidence": 0.0,
            "timestamp": datetime.now().isoformat()
        }
        
        # Process the user input
        try:
            # Simple state for the mock agent
            state = {
                "user_query": user_input,
                "conversation_history": st.session_state.conversation_history
            }
            
            if st.session_state.qa_agent:
                response = st.session_state.qa_agent.execute(state)
                conversation_entry["assistant"] = response["agent_response"]
                conversation_entry["sources"] = response.get("sources", [])
                conversation_entry["confidence"] = response.get("confidence", 0.0)
            else:
                conversation_entry["assistant"] = "Sorry, the finance agent is not available right now."
                
        except Exception as e:
            conversation_entry["assistant"] = f"Error processing question: {str(e)}"
        
        st.session_state.conversation_history.append(conversation_entry)
        st.rerun()

if __name__ == "__main__":
    main()
