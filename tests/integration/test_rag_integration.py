#!/usr/bin/env python3
"""
Test RAG Integration with FAISS Vector Database
This script demonstrates how to load and query your vector database
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.rag.vector_store import FinanceVectorStore
from src.rag.retriever import FinanceRetriever

def test_vector_database():
    """Test loading and querying the FAISS vector database"""
    
    print("🔍 Testing FAISS Vector Database Integration")
    print("=" * 50)
    
    # Load the existing vector store
    print("📁 Loading vector database...")
    vector_store = FinanceVectorStore(index_path="src/data/faiss_index")
    
    if not vector_store.documents:
        print("❌ No documents found! Make sure to run build_vector_db.py first.")
        return False
    
    print(f"✅ Loaded {len(vector_store.documents)} document chunks")
    
    # Initialize retriever
    retriever = FinanceRetriever(vector_store)
    
    # Test queries
    test_queries = [
        "What is a 401k retirement plan?",
        "How does investing in stocks work?",
        "What is the importance of credit score?",
        "Emergency fund planning strategies",
        "Traditional IRA vs Roth IRA differences"
    ]
    
    print(f"\n🧪 Testing {len(test_queries)} queries:")
    print("-" * 40)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: '{query}'")
        
        # Retrieve relevant documents
        results = retriever.retrieve(query, k=3)
        
        if results:
            print(f"   📋 Found {len(results)} relevant documents:")
            for j, result in enumerate(results, 1):
                score = result['score']
                source = result['metadata']['source']
                content_preview = result['content'][:150] + "..." if len(result['content']) > 150 else result['content']
                
                print(f"   {j}. Score: {score:.3f} | Source: {source}")
                print(f"      Preview: {content_preview}")
        else:
            print("   ❌ No relevant documents found")
        
        # Build context for LLM
        context = retriever.build_context(query, results)
        print(f"   📝 Context length: {len(context)} characters")
    
    return True

def test_category_filtering():
    """Test category-based filtering"""
    
    print(f"\n🏷️ Testing Category Filtering:")
    print("-" * 30)
    
    vector_store = FinanceVectorStore(index_path="src/data/faiss_index")
    retriever = FinanceRetriever(vector_store)
    
    # Test category filtering
    categories = ["retirement_planning", "personal_finance", "education"]
    
    for category in categories:
        results = retriever.retrieve_by_category(
            "investment strategies", 
            category=category, 
            k=2
        )
        
        print(f"   📂 {category}: {len(results)} results")
        if results:
            for result in results:
                print(f"      • {result['metadata']['source']} (Score: {result['score']:.3f})")

def demonstrate_rag_workflow():
    """Demonstrate a complete RAG workflow"""
    
    print(f"\n🤖 Complete RAG Workflow Demo:")
    print("-" * 35)
    
    # Load vector store and retriever
    vector_store = FinanceVectorStore(index_path="src/data/faiss_index")
    retriever = FinanceRetriever(vector_store)
    
    # User question
    user_question = "What should I know about 401k retirement planning?"
    print(f"👤 User Question: {user_question}")
    
    # Step 1: Retrieve relevant context
    print(f"\n1️⃣ Retrieving relevant information...")
    results = retriever.retrieve(user_question, k=5)
    print(f"   Found {len(results)} relevant documents")
    
    # Step 2: Build context for LLM
    print(f"\n2️⃣ Building context for LLM...")
    context = retriever.build_context(user_question, results)
    context_preview = context[:300] + "..." if len(context) > 300 else context
    print(f"   Context preview: {context_preview}")
    
    # Step 3: Show what would be sent to LLM
    print(f"\n3️⃣ Ready for LLM processing:")
    print(f"   Context length: {len(context)} characters")
    print(f"   Sources included: {len(set(r['metadata']['source'] for r in results))}")
    print(f"   Average confidence: {sum(r['score'] for r in results) / len(results):.3f}")
    
    print(f"\n💡 This context would now be sent to your LLM agent for response generation!")

def main():
    """Main execution function"""
    
    success = test_vector_database()
    
    if success:
        test_category_filtering()
        demonstrate_rag_workflow()
        
        print(f"\n🎉 RAG Integration Test Complete!")
        print(f"""
📖 How to use in your agents:

1. 🔍 Basic Integration:
   ```python
   from src.rag.vector_store import FinanceVectorStore
   from src.rag.retriever import FinanceRetriever
   
   # Load vector store (loads automatically from disk)
   vector_store = FinanceVectorStore(index_path="src/data/faiss_index")
   retriever = FinanceRetriever(vector_store)
   
   # Retrieve context for any query
   results = retriever.retrieve("investment advice", k=5)
   context = retriever.build_context("investment advice", results)
   ```

2. 🤖 Agent Integration:
   ```python
   class YourAgent:
       def __init__(self):
           self.vector_store = FinanceVectorStore(index_path="src/data/faiss_index")
           self.retriever = FinanceRetriever(self.vector_store)
       
       def answer_question(self, question):
           # Get relevant context
           results = self.retriever.retrieve(question, k=5)
           context = self.retriever.build_context(question, results)
           
           # Send to LLM with context
           prompt = f"{{context}}\\n\\nUser Question: {{question}}"
           response = your_llm.generate(prompt)
           return response
   ```

3. 🏷️ Category-Specific Queries:
   ```python
   # For retirement-specific questions
   retirement_results = retriever.retrieve_by_category(
       "investment strategies", 
       category="retirement_planning", 
       k=3
   )
   ```

✅ Your vector database is ready for production use!
""")
    else:
        print(f"\n❌ Please run the vector database builder first:")
        print(f"   python scripts/vector_db/build_vector_db.py")

if __name__ == "__main__":
    main()
