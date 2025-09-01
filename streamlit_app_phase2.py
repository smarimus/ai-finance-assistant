#!/usr/bin/env python3
"""
Streamlit Finance Assistant - Phase 2: Knowledge-Enhanced Assistant
Real LLM integration with FAISS vector database
"""

import streamlit as st
import sys
import os
from datetime import datetime
from typing import Dict, Any, List
import logging

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Try to import real components, fall back to mock if needed
try:
    from openai import OpenAI
    import dotenv
    dotenv.load_dotenv()
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from src.rag.vector_store import FinanceVectorStore
    from src.rag.retriever import FinanceRetriever
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealLLM:
    """Real OpenAI LLM integration"""
    
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        if not api_key:
            api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
        
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def invoke(self, prompt: str) -> 'RealResponse':
        """Generate response using OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful financial education assistant. Provide clear, accurate, and educational responses about financial topics. Always include appropriate disclaimers about not providing personalized investment advice."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            return RealResponse(content)
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return RealResponse(f"I apologize, but I'm having trouble processing your request right now. Please try again later. Error: {str(e)}")

class RealResponse:
    """Real response object"""
    def __init__(self, content: str):
        self.content = content

# Fallback Mock classes (same as Phase 1)
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

        else:
            content = """I'd be happy to help explain financial concepts! Here are some topics I can assist with:

📊 **Investment Basics**
- Stocks, bonds, mutual funds, ETFs
- Risk vs. return concepts
- Portfolio diversification

Feel free to ask about any specific topic!

**Disclaimer**: This is educational information only, not personalized investment advice."""

        return MockResponse(content)

class MockResponse:
    """Mock response object"""
    def __init__(self, content: str):
        self.content = content

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
        page_title="AI Finance Assistant - Phase 2",
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
    
    .phase-indicator {
        background: linear-gradient(90deg, #4CAF50, #2196F3);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 1rem;
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
    
    .tech-status {
        padding: 0.3rem 0.7rem;
        border-radius: 15px;
        font-size: 0.8rem;
        margin: 0.2rem;
        display: inline-block;
    }
    
    .tech-real { background-color: #4caf50; color: white; }
    .tech-mock { background-color: #ff9800; color: white; }
    .tech-unavailable { background-color: #f44336; color: white; }
    </style>
    """, unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    
    if "qa_agent" not in st.session_state:
        # Try to initialize with real components, fall back to mock
        st.session_state.qa_agent = create_finance_agent()

def create_finance_agent():
    """Create the Finance Agent with real or mock components"""
    try:
        # Try to use real components
        if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
            llm = RealLLM()
            llm_status = "real"
        else:
            llm = MockLLM()
            llm_status = "mock"
        
        if RAG_AVAILABLE and os.path.exists("src/data/faiss_index.faiss"):
            # Use real FAISS vector store
            vector_store = FinanceVectorStore(index_path="src/data/faiss_index")
            retriever = FinanceRetriever(vector_store)
            rag_status = "real"
        else:
            # Use mock retriever
            retriever = MockRetriever()
            rag_status = "mock"
        
        return EnhancedFinanceAgent(llm, retriever, llm_status, rag_status)
        
    except Exception as e:
        logger.error(f"Error creating finance agent: {e}")
        # Fall back to all mock components
        return EnhancedFinanceAgent(MockLLM(), MockRetriever(), "mock", "mock")

class EnhancedFinanceAgent:
    """Enhanced Finance Agent for Phase 2 with real LLM and RAG"""
    
    def __init__(self, llm, retriever, llm_status="real", rag_status="real"):
        self.llm = llm
        self.retriever = retriever
        self.agent_name = "finance_qa_enhanced"
        self.llm_status = llm_status
        self.rag_status = rag_status
    
    def execute(self, state):
        """Execute the enhanced finance Q&A logic"""
        try:
            query = state["user_query"]
            
            # Get retrieved documents for context
            retrieved_docs = self.retriever.retrieve(query, k=5)
            
            # Build enhanced context for LLM
            context = self.build_enhanced_context(query, retrieved_docs)
            
            # Generate response using real or mock LLM
            llm_response = self.llm.invoke(context)
            
            # Extract sources
            sources = [doc["metadata"]["source"] for doc in retrieved_docs] if retrieved_docs else []
            
            # Calculate confidence based on retrieval quality
            confidence = self.calculate_confidence(retrieved_docs, query)
            
            # Format response with enhanced features
            response_text = llm_response.content
            
            return {
                "agent_response": response_text,
                "sources": sources,
                "confidence": confidence,
                "agent_name": self.agent_name,
                "llm_status": self.llm_status,
                "rag_status": self.rag_status,
                "retrieved_docs_count": len(retrieved_docs),
                "query_classification": {
                    "primary_category": "financial_education",
                    "complexity": "intermediate"
                },
                "next_agent": None,
                "updated_context": {}
            }
            
        except Exception as e:
            logger.error(f"Error in enhanced agent execution: {e}")
            return {
                "agent_response": f"I apologize, but I encountered an error processing your question: {str(e)}. Please try rephrasing your question.",
                "sources": [],
                "confidence": 0.0,
                "agent_name": self.agent_name,
                "llm_status": "error",
                "rag_status": self.rag_status,
                "next_agent": None,
                "updated_context": {"error": str(e)}
            }
    
    def build_enhanced_context(self, query: str, docs: List) -> str:
        """Build enhanced context for LLM with better formatting"""
        context_parts = []
        
        # Add instructions
        context_parts.append("""You are a financial education assistant. Please provide a comprehensive, educational response based on the provided context and your knowledge. Follow these guidelines:

1. Use clear, beginner-friendly language
2. Include practical examples when helpful
3. Provide structured information (use bullet points, numbered lists)
4. Always include appropriate disclaimers
5. If the context is limited, supplement with your general knowledge while noting the limitation

Context from knowledge base:""")
        
        if docs:
            for i, doc in enumerate(docs, 1):
                source = doc["metadata"]["source"]
                content = doc["content"]
                score = doc.get("score", 0.0)
                context_parts.append(f"\n[Source {i}: {source} (relevance: {score:.2f})]\n{content}")
        else:
            context_parts.append("\nNo specific context found in knowledge base. Please provide a general educational response.")
        
        context_parts.append(f"\n\nUser Question: {query}")
        context_parts.append("\nPlease provide a comprehensive educational response:")
        
        return "\n".join(context_parts)
    
    def calculate_confidence(self, docs: List, query: str) -> float:
        """Calculate confidence based on retrieval quality and query"""
        if not docs:
            return 0.6  # Base confidence for general knowledge
        
        # Factor in number of relevant documents
        doc_count_score = min(len(docs) / 5.0, 1.0)  # Max at 5 docs
        
        # Factor in average relevance score
        avg_score = sum(doc.get("score", 0.0) for doc in docs) / len(docs)
        
        # Combine factors
        confidence = (doc_count_score * 0.3) + (avg_score * 0.7)
        
        # Ensure confidence is in reasonable range
        return max(0.6, min(0.95, confidence))

def render_sidebar():
    """Render sidebar with app info and controls"""
    with st.sidebar:
        st.markdown("### 🏦 AI Finance Assistant")
        st.markdown('<div class="phase-indicator">Phase 2: Knowledge-Enhanced</div>', unsafe_allow_html=True)
        
        # Technology Status
        st.markdown("### 🔧 Technology Status")
        if hasattr(st.session_state, 'qa_agent') and st.session_state.qa_agent:
            agent = st.session_state.qa_agent
            llm_class = "tech-real" if agent.llm_status == "real" else "tech-mock"
            rag_class = "tech-real" if agent.rag_status == "real" else "tech-mock"
            
            st.markdown(f'<span class="tech-status {llm_class}">LLM: {agent.llm_status.upper()}</span>', unsafe_allow_html=True)
            st.markdown(f'<span class="tech-status {rag_class}">RAG: {agent.rag_status.upper()}</span>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### ✨ Phase 2 Features")
        st.markdown("✅ Real LLM integration (OpenAI)")
        st.markdown("✅ FAISS vector database")
        st.markdown("✅ Enhanced source citations")
        st.markdown("✅ Improved answer quality")
        st.markdown("✅ Confidence scoring")
        
        st.markdown("---")
        st.markdown("### 🎯 Sample Questions")
        sample_questions = [
            "What is diversification and why is it important?",
            "Explain compound interest with examples",
            "How do I start investing as a beginner?",
            "What's the difference between ETFs and mutual funds?",
            "How should I plan for retirement?",
            "What is dollar-cost averaging?"
        ]
        
        for question in sample_questions:
            if st.button(question, key=f"sample_{question}", use_container_width=True):
                st.session_state.suggested_question = question
        
        st.markdown("---")
        # Session info
        st.markdown("### 📊 Session Info")
        st.markdown(f"**Messages**: {len(st.session_state.conversation_history)}")
        
        if st.button("Clear Chat History", type="secondary", use_container_width=True):
            st.session_state.conversation_history = []
            st.rerun()

def render_conversation_history():
    """Display conversation history with enhanced information"""
    if not st.session_state.conversation_history:
        st.markdown("""
        <div style="text-align: center; padding: 2rem; color: #666;">
            🚀 Welcome to Phase 2: Knowledge-Enhanced Assistant!<br>
            Ask me any financial question to see the improved RAG system in action.<br>
            Try questions about investing, retirement planning, or financial concepts.
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
            
            # Enhanced metadata display
            col1, col2, col3 = st.columns(3)
            
            with col1:
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
            
            with col2:
                # Show source count
                source_count = len(message.get("sources", []))
                st.markdown(f"📚 **Sources**: {source_count}")
            
            with col3:
                # Show tech status
                llm_status = message.get("llm_status", "unknown")
                rag_status = message.get("rag_status", "unknown")
                st.markdown(f"🤖 LLM: {llm_status} | 🔍 RAG: {rag_status}")
            
            # Show sources if available
            if message.get("sources"):
                with st.expander(f"📖 View {len(message['sources'])} Sources"):
                    for i, source in enumerate(message["sources"], 1):
                        st.markdown(f'<div class="source-citation">{i}. {source}</div>', unsafe_allow_html=True)

def main():
    """Main application"""
    setup_page()
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🏦 AI Finance Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<div class="phase-indicator">Phase 2: Knowledge-Enhanced Assistant with RAG</div>', unsafe_allow_html=True)
    
    # Check API key status
    if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
        st.success("✅ OpenAI API key detected - Using real LLM")
    else:
        st.warning("⚠️ OpenAI API key not found - Using mock responses. Set OPENAI_API_KEY environment variable for real LLM.")
    
    # Check RAG status
    if RAG_AVAILABLE and os.path.exists("src/data/faiss_index.faiss"):
        st.success("✅ FAISS vector database found - Using real RAG system")
    else:
        st.warning("⚠️ FAISS vector database not found - Using mock retrieval")
    
    # Render sidebar
    render_sidebar()
    
    # Main chat interface
    st.markdown("### 💬 Chat with Your Enhanced Finance Assistant")
    
    # Display conversation history
    render_conversation_history()
    
    # Handle suggested question from sidebar
    if hasattr(st.session_state, 'suggested_question'):
        suggested_input = st.session_state.suggested_question
        delattr(st.session_state, 'suggested_question')
        
        # Process the suggested question
        conversation_entry = {
            "user": suggested_input,
            "assistant": "Processing your question...",
            "sources": [],
            "confidence": 0.0,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            state = {"user_query": suggested_input, "conversation_history": st.session_state.conversation_history}
            
            if st.session_state.qa_agent:
                response = st.session_state.qa_agent.execute(state)
                conversation_entry.update({
                    "assistant": response["agent_response"],
                    "sources": response.get("sources", []),
                    "confidence": response.get("confidence", 0.0),
                    "llm_status": response.get("llm_status", "unknown"),
                    "rag_status": response.get("rag_status", "unknown"),
                    "retrieved_docs_count": response.get("retrieved_docs_count", 0)
                })
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
        conversation_entry = {
            "user": user_input,
            "assistant": "Processing your question...",
            "sources": [],
            "confidence": 0.0,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            state = {"user_query": user_input, "conversation_history": st.session_state.conversation_history}
            
            if st.session_state.qa_agent:
                response = st.session_state.qa_agent.execute(state)
                conversation_entry.update({
                    "assistant": response["agent_response"],
                    "sources": response.get("sources", []),
                    "confidence": response.get("confidence", 0.0),
                    "llm_status": response.get("llm_status", "unknown"),
                    "rag_status": response.get("rag_status", "unknown"),
                    "retrieved_docs_count": response.get("retrieved_docs_count", 0)
                })
            else:
                conversation_entry["assistant"] = "Sorry, the finance agent is not available right now."
                
        except Exception as e:
            conversation_entry["assistant"] = f"Error processing question: {str(e)}"
        
        st.session_state.conversation_history.append(conversation_entry)
        st.rerun()

if __name__ == "__main__":
    main()
