#!/usr/bin/env python3
"""
Complete Setup Guide for FAISS Vector Database
Step-by-step guide to get your financial knowledge base working with vector search
"""

import os
import sys
from pathlib import Path

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking Requirements...")
    print("=" * 30)
    
    issues = []
    
    # Check knowledge base
    kb_path = Path("src/data/knowledge_base/articles")
    if kb_path.exists():
        articles = list(kb_path.glob("*.json"))
        print(f"✅ Knowledge base: {len(articles)} articles found")
    else:
        print("❌ Knowledge base: Not found")
        issues.append("Knowledge base missing - run 'python run_scraper.py'")
    
    # Check Python packages
    try:
        import faiss
        print("✅ FAISS: Installed")
    except ImportError:
        print("❌ FAISS: Not installed")
        issues.append("Install FAISS: pip install faiss-cpu")
    
    try:
        import langchain
        print("✅ LangChain: Installed")
    except ImportError:
        print("❌ LangChain: Not installed")
        issues.append("Install LangChain: pip install langchain")
    
    # Check OpenAI API key
    if os.getenv('OPENAI_API_KEY'):
        print("✅ OpenAI API Key: Set")
    else:
        print("⚠️  OpenAI API Key: Not set")
        issues.append("Set OpenAI API key: export OPENAI_API_KEY='your-key'")
    
    return issues

def show_usage_guide():
    """Show complete usage guide"""
    print(f"""
🚀 FAISS Vector Database Setup Complete!
=======================================

📖 STEP-BY-STEP USAGE GUIDE:

1️⃣  SET UP OPENAI API KEY (Required for embeddings):
   
   export OPENAI_API_KEY='your-openai-api-key-here'
   
   # Or add to .env file:
   echo "OPENAI_API_KEY=your-key-here" > .env

2️⃣  BUILD VECTOR DATABASE:
   
   python build_vector_db.py
   
   This will:
   • Load all 41 articles from your knowledge base
   • Create document chunks for better search
   • Generate embeddings using OpenAI
   • Build FAISS index for fast similarity search
   • Save everything to src/data/faiss_index

3️⃣  TEST THE DATABASE:
   
   python test_vector_db.py
   
   This will test:
   • Loading the vector store
   • Search functionality
   • Different query types
   • Performance metrics

4️⃣  TRY INTERACTIVE EXAMPLES:
   
   python vector_db_examples.py
   
   This includes:
   • Financial Q&A examples
   • Advanced search features
   • Interactive chatbot simulation

💡 BASIC USAGE IN YOUR CODE:

```python
from src.rag.vector_store import FinanceVectorStore
from src.rag.retriever import FinanceRetriever

# Load the vector database
vector_store = FinanceVectorStore(index_path="src/data/faiss_index")
retriever = FinanceRetriever(vector_store)

# Search for information
results = retriever.retrieve("What is a 401k plan?", k=5)

# Print results
for i, result in enumerate(results, 1):
    print(f"{{i}}. {{result['metadata']['title']}}")
    print(f"   Score: {{result['score']:.3f}}")
    print(f"   Preview: {{result['content'][:100]}}...")
```

🔍 SEARCH EXAMPLES:

• "What is a 401k retirement plan?"
• "How to improve credit score?"  
• "Stock market analysis techniques"
• "Cryptocurrency investment basics"
• "Emergency fund savings strategies"

🏷️  CATEGORY SEARCH:

```python
# Search only retirement planning articles
retirement_results = retriever.retrieve_by_category(
    "IRA vs 401k comparison", 
    category="retirement_planning", 
    k=3
)

# Search personal finance articles
finance_results = retriever.retrieve_by_category(
    "budgeting tips", 
    category="personal_finance", 
    k=3
)
```

🤖 AI AGENT INTEGRATION:

```python
# Build context for your AI assistant
query = "How much should I save for retirement?"
results = retriever.retrieve(query, k=5)
context = retriever.build_context(query, results)

# Use with any LLM
prompt = f\"\"\"
Context: {{context}}

User Question: {{query}}

Please provide a comprehensive answer based on the context above.
\"\"\"

# Send to OpenAI, Claude, or any other LLM
response = your_llm.generate(prompt)
```

📊 YOUR KNOWLEDGE BASE CONTAINS:

• 🏦 Retirement Planning (7 articles): 401k, IRA, Social Security
• 💰 Personal Finance (8 articles): Credit, budgeting, insurance  
• 📈 Investment Analysis (26 articles): Stocks, crypto, financial ratios
• 📝 Total: 77,283 words of professional financial content

🎯 NEXT STEPS:

1. Set your OpenAI API key
2. Run: python build_vector_db.py
3. Run: python test_vector_db.py
4. Try: python vector_db_examples.py
5. Integrate into your AI agents!

🔗 HELPFUL FILES:

• build_vector_db.py - Creates the vector database
• test_vector_db.py - Tests functionality
• vector_db_examples.py - Usage examples
• src/rag/vector_store.py - Core vector store class
• src/rag/retriever.py - Intelligent retriever

💡 Pro Tips:

• Use retrieve() for general searches
• Use retrieve_by_category() for focused searches
• Use build_context() to prepare LLM prompts
• Vector database persists between runs
• Search is semantic (meaning-based), not just keyword matching
• Higher scores = more relevant results

Happy building! 🚀
""")

def main():
    """Main setup function"""
    print("🏗️  FAISS Vector Database Setup Guide")
    print("=" * 40)
    
    # Check requirements
    issues = check_requirements()
    
    if issues:
        print(f"\n⚠️  Issues Found:")
        for issue in issues:
            print(f"   • {issue}")
        print(f"\n🔧 Please resolve these issues first.")
    else:
        print(f"\n✅ All requirements met!")
    
    # Show usage guide
    show_usage_guide()
    
    print(f"\n📚 Documentation:")
    print(f"   • README.md - Project overview")
    print(f"   • This script shows complete setup process")
    print(f"   • All scripts include help: python script.py --help")

if __name__ == "__main__":
    main()
