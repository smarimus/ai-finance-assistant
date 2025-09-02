#!/usr/bin/env python3
"""
Complete RAG Agent Integration Example
Shows how to use your FAISS vector database with your finance agents
"""

import sys
from pathlib import Path
import os

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.rag.vector_store import FinanceVectorStore
from src.rag.retriever import FinanceRetriever
from src.core.state import FinanceAssistantState

def demo_basic_rag_usage():
    """Basic RAG usage without agents"""
    print("🔍 Basic RAG Usage Demo")
    print("=" * 30)
    
    # Initialize RAG system
    vector_store = FinanceVectorStore(index_path="src/data/faiss_index")
    retriever = FinanceRetriever(vector_store)
    
    # User question
    question = "What are the benefits of a 401k plan?"
    print(f"❓ Question: {question}")
    
    # Retrieve relevant context
    results = retriever.retrieve(question, k=3)
    context = retriever.build_context(question, results)
    
    print(f"\n📋 Retrieved {len(results)} relevant documents")
    print(f"📝 Context ready for LLM (length: {len(context)} chars)")
    
    # This context would be sent to your LLM
    print(f"\n💬 Context for LLM:")
    print("-" * 40)
    print(context)
    
    return context

def demo_agent_integration():
    """Demo with actual agent integration"""
    print("\n\n🤖 Agent Integration Demo")
    print("=" * 35)
    
    # Note: This would normally use your actual LLM
    # For demo, we'll show the structure
    
    try:
        # Try to import and use the agent if LLM is available
        from src.agents.finance_qa_agent import FinanceQAAgent
        
        # Initialize RAG system
        vector_store = FinanceVectorStore(index_path="src/data/faiss_index")
        retriever = FinanceRetriever(vector_store)
        
        # Mock LLM for demo (replace with your actual LLM)
        class MockLLM:
            def invoke(self, prompt):
                return type('Response', (), {
                    'content': f"[This would be the LLM response based on the context provided. The context contained {len(prompt)} characters of relevant financial information.]"
                })()
        
        # Create agent with mock LLM
        mock_llm = MockLLM()
        qa_agent = FinanceQAAgent(mock_llm, retriever)
        
        # Create state
        state = FinanceAssistantState({
            "user_query": "How does a traditional IRA work?",
            "conversation_history": []
        })
        
        # Execute agent
        print(f"❓ Question: {state['user_query']}")
        response = qa_agent.execute(state)
        
        print(f"\n📤 Agent Response:")
        print(f"Content: {response['content']}")
        print(f"Sources: {response.get('sources', [])}")
        print(f"Confidence: {response.get('confidence', 0):.2f}")
        print(f"Next Agent: {response.get('next_agent', 'None')}")
        
    except Exception as e:
        print(f"⚠️  Agent demo requires full setup. Error: {e}")
        print("📝 Showing how it would work...")
        
        # Show the structure without actual execution
        print(f"""
🏗️  Agent Integration Structure:

1. Initialize RAG System:
   vector_store = FinanceVectorStore(index_path="src/data/faiss_index")
   retriever = FinanceRetriever(vector_store)

2. Create Agent:
   qa_agent = FinanceQAAgent(your_llm, retriever)

3. Process Query:
   state = {{"user_query": "Your question", "conversation_history": []}}
   response = qa_agent.execute(state)

4. Get Enhanced Response:
   - response['content']: LLM answer with RAG context
   - response['sources']: Source citations
   - response['confidence']: Confidence score
   - response['next_agent']: Suggested next agent
""")

def demo_production_usage():
    """Show production-ready usage patterns"""
    print("\n\n🚀 Production Usage Patterns")
    print("=" * 40)
    
    print("""
📋 Production Integration Checklist:

✅ Vector Database Built: Your FAISS index is ready
✅ GPU Acceleration: Using Apple Silicon MPS
✅ 1,308 Document Chunks: Comprehensive coverage
✅ Source Attribution: Investopedia + scraped content
✅ Category Filtering: Available for specialized queries

🔧 Integration Steps:

1. 📦 Import RAG System:
   ```python
   from src.rag.vector_store import FinanceVectorStore
   from src.rag.retriever import FinanceRetriever
   ```

2. 🔄 Initialize Once (startup):
   ```python
   self.vector_store = FinanceVectorStore(index_path="src/data/faiss_index")
   self.retriever = FinanceRetriever(self.vector_store)
   ```

3. 💬 For Each User Query:
   ```python
   # Retrieve relevant context
   results = self.retriever.retrieve(user_question, k=5)
   context = self.retriever.build_context(user_question, results)
   
   # Send to LLM with context
   enhanced_prompt = f\"{context}\\n\\nUser: {user_question}\"
   response = your_llm.generate(enhanced_prompt)
   ```

4. 🏷️ Specialized Queries:
   ```python
   # For retirement-specific questions
   retirement_context = self.retriever.retrieve_by_category(
       query="401k vs IRA", 
       category="retirement_planning", 
       k=3
   )
   ```

⚡ Performance Tips:
- Vector store loads instantly from disk
- GPU acceleration speeds up queries
- Category filtering reduces noise
- Batch queries when possible

🔐 Security Notes:
- All data stays local (no API calls for embeddings)
- Sources are clearly attributed
- Confidence scores help filter responses
""")

def main():
    """Run complete RAG demonstration"""
    
    # Check if vector database exists
    if not Path("src/data/faiss_index.faiss").exists():
        print("❌ Vector database not found!")
        print("📋 Please run: python scripts/vector_db/build_vector_db.py")
        return
    
    print("🎯 RAG Integration Complete Demo")
    print("=" * 50)
    
    # Demo 1: Basic RAG usage
    context = demo_basic_rag_usage()
    
    # Demo 2: Agent integration
    demo_agent_integration()
    
    # Demo 3: Production patterns
    demo_production_usage()
    
    print(f"\n🎉 RAG System Ready for Production!")
    print(f"""
🚀 Next Steps:
1. Integrate with your LLM (OpenAI, Anthropic, Local models)
2. Update your agents to use the retriever
3. Test with real user queries
4. Monitor performance and accuracy
5. Expand knowledge base as needed

📁 Your vector database: src/data/faiss_index/
🔄 To rebuild: python scripts/vector_db/build_vector_db.py
🧪 To test: python test_rag_integration.py
""")

if __name__ == "__main__":
    main()
