#!/usr/bin/env python3
"""
Example: Using FAISS Vector Database for Financial Q&A
Demonstrates how to integrate the vector database with an AI assistant
"""

import sys
from pathlib import Path
import os

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from rag.vector_store import FinanceVectorStore
from rag.retriever import FinanceRetriever

def simple_financial_qa_example():
    """Simple example of using vector database for financial Q&A"""
    
    print("💡 Financial Q&A with Vector Database")
    print("=" * 40)
    
    # Load the vector database
    print("📂 Loading financial knowledge base...")
    vector_store = FinanceVectorStore(index_path="src/data/faiss_index")
    
    if vector_store.index is None:
        print("❌ Vector database not found!")
        print("   Please run: python build_vector_db.py")
        return
    
    retriever = FinanceRetriever(vector_store)
    print(f"✅ Loaded {len(vector_store.documents)} knowledge chunks")
    
    # Example questions and answers
    questions = [
        "What is a 401k and how does it work?",
        "Should I choose a traditional IRA or Roth IRA?",
        "How can I improve my credit score?",
        "What's the difference between stocks and bonds?",
        "How much should I save for retirement?"
    ]
    
    print(f"\n🤖 Answering common financial questions...\n")
    
    for i, question in enumerate(questions, 1):
        print(f"❓ Question {i}: {question}")
        
        # Retrieve relevant information
        results = retriever.retrieve(question, k=3)
        
        if results:
            # Build context for the AI
            context = retriever.build_context(question, results)
            
            print(f"📚 Found {len(results)} relevant sources:")
            for j, result in enumerate(results, 1):
                source = result['metadata']['source']
                score = result['score']
                category = result['metadata']['category']
                print(f"   {j}. {source} (score: {score:.3f}, category: {category})")
            
            # In a real application, you would send this context to an LLM
            print(f"💬 AI Response: [Context provided to LLM - {len(context)} chars]")
            print(f"    Sample context: {context[:200]}...")
            
        else:
            print(f"❌ No relevant information found")
        
        print("-" * 50)

def advanced_search_examples():
    """Advanced search examples showing different features"""
    
    print(f"\n🔍 Advanced Search Examples")
    print("=" * 30)
    
    vector_store = FinanceVectorStore(index_path="src/data/faiss_index")
    retriever = FinanceRetriever(vector_store)
    
    # Example 1: Category-specific search
    print(f"1. 🏦 Retirement Planning Search:")
    retirement_results = retriever.retrieve_by_category(
        "investment strategies", 
        category="retirement_planning", 
        k=2
    )
    for result in retirement_results:
        title = result['metadata'].get('title', 'Unknown')
        print(f"   • {title}")
    
    # Example 2: Personal finance search
    print(f"\n2. 💰 Personal Finance Search:")
    finance_results = retriever.retrieve_by_category(
        "saving money", 
        category="personal_finance", 
        k=2
    )
    for result in finance_results:
        title = result['metadata'].get('title', 'Unknown')
        print(f"   • {title}")
    
    # Example 3: Enhanced query search
    print(f"\n3. 🚀 Enhanced Query Search:")
    enhanced_results = retriever.retrieve(
        "portfolio management", 
        k=3, 
        enhance_query=True
    )
    for result in enhanced_results:
        title = result['metadata'].get('title', 'Unknown')
        score = result['score']
        print(f"   • {title} (score: {score:.3f})")

def chatbot_simulation():
    """Simulate a financial chatbot using the vector database"""
    
    print(f"\n🤖 Financial Chatbot Simulation")
    print("=" * 35)
    print("Ask me financial questions! Type 'quit' to exit.")
    
    vector_store = FinanceVectorStore(index_path="src/data/faiss_index")
    retriever = FinanceRetriever(vector_store)
    
    if vector_store.index is None:
        print("❌ Vector database not available!")
        return
    
    conversation_history = []
    
    while True:
        user_input = input(f"\n👤 You: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print(f"🤖 Assistant: Goodbye! Happy investing! 💰")
            break
        
        if not user_input:
            continue
        
        # Retrieve relevant information
        print(f"🔍 Searching knowledge base...")
        results = retriever.retrieve(user_input, k=3)
        
        if results:
            # Simulate AI response based on retrieved context
            top_result = results[0]
            source = top_result['metadata']['source']
            category = top_result['metadata']['category']
            
            print(f"🤖 Assistant: Based on our financial knowledge base, I found information from {source} (category: {category}).")
            print(f"              Here's what I can tell you:")
            print(f"              {top_result['content'][:300]}...")
            print(f"\\n              📚 This information comes from {len(results)} sources in our database.")
            
            # Track conversation
            conversation_history.append({
                'question': user_input,
                'sources_used': len(results),
                'top_score': top_result['score']
            })
            
        else:
            print(f"🤖 Assistant: I'm sorry, I couldn't find specific information about that in my financial knowledge base.")
            print(f"              You might want to try rephrasing your question or asking about topics like:")
            print(f"              • Retirement planning (401k, IRA)")
            print(f"              • Personal finance (budgeting, credit)")
            print(f"              • Investing (stocks, analysis)")
    
    # Show conversation summary
    if conversation_history:
        print(f"\\n📊 Conversation Summary:")
        print(f"   Questions answered: {len(conversation_history)}")
        avg_score = sum(q['top_score'] for q in conversation_history) / len(conversation_history)
        print(f"   Average relevance score: {avg_score:.3f}")

def main():
    """Run example demonstrations"""
    
    print("🚀 FAISS Vector Database Usage Examples")
    print("=" * 45)
    
    # Check if vector database exists
    index_path = Path(__file__).parent.parent.parent / "src/data/faiss_index.faiss"
    if not index_path.exists():
        print("❌ Vector database not found!")
        print("   Please run 'python build_vector_db.py' first to create the database.")
        return
    
    # Run examples
    simple_financial_qa_example()
    advanced_search_examples()
    
    # Optional interactive chatbot
    response = input(f"\\n🤖 Would you like to try the interactive chatbot? (y/N): ")
    if response.lower() == 'y':
        chatbot_simulation()
    
    print(f"\\n🎉 Examples completed!")
    print(f"\\n💡 Integration Tips:")
    print(f"   • Use retrieve() for general questions")
    print(f"   • Use retrieve_by_category() for focused searches")
    print(f"   • Use build_context() to prepare LLM prompts")
    print(f"   • Combine multiple results for comprehensive answers")

if __name__ == "__main__":
    main()
