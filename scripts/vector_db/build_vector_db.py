#!/usr/bin/env python3
"""
Build FAISS Vector Database from Financial Knowledge Base
This script loads all scraped articles and creates a searchable vector database
"""

import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import logging

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from langchain.schema import Document
from rag.vector_store import FinanceVectorStore
from rag.retriever import FinanceRetriever

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class KnowledgeBaseLoader:
    """Load and process financial knowledge base articles into vector database"""
    
    def __init__(self, knowledge_base_path: str = "src/data/knowledge_base/articles"):
        self.knowledge_base_path = Path(__file__).parent.parent.parent / knowledge_base_path
        self.articles = []
        
    def load_articles(self) -> List[Dict[str, Any]]:
        """Load all articles from the knowledge base directory"""
        logging.info(f"Loading articles from {self.knowledge_base_path}")
        
        if not self.knowledge_base_path.exists():
            logging.error(f"Knowledge base path does not exist: {self.knowledge_base_path}")
            return []
        
        article_files = list(self.knowledge_base_path.glob("*.json"))
        logging.info(f"Found {len(article_files)} article files")
        
        articles = []
        for article_file in article_files:
            try:
                with open(article_file, 'r', encoding='utf-8') as f:
                    article = json.load(f)
                    articles.append(article)
                    logging.debug(f"Loaded: {article.get('title', 'Unknown')}")
            except Exception as e:
                logging.error(f"Error loading {article_file}: {e}")
        
        self.articles = articles
        logging.info(f"Successfully loaded {len(articles)} articles")
        return articles
    
    def create_documents(self) -> List[Document]:
        """Convert articles to LangChain Document objects"""
        documents = []
        
        for i, article in enumerate(self.articles):
            # Create main content document
            content = article.get('content', '')
            title = article.get('title', f'Article {i+1}')
            
            if not content:
                logging.warning(f"Empty content for article: {title}")
                continue
            
            # Enhanced metadata
            metadata = {
                'doc_id': f"article_{i+1}",
                'title': title,
                'source': article.get('source', 'Unknown'),
                'category': article.get('category', 'general'),
                'url': article.get('url', ''),
                'word_count': article.get('word_count', len(content.split())),
                'scraped_at': article.get('scraped_at', ''),
                'author': article.get('author', 'Unknown')
            }
            
            # Create document with title and content
            full_content = f"Title: {title}\n\nContent: {content}"
            
            doc = Document(
                page_content=full_content,
                metadata=metadata
            )
            
            documents.append(doc)
            logging.debug(f"Created document: {title} ({len(full_content)} chars)")
        
        logging.info(f"Created {len(documents)} documents")
        return documents
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        if not self.articles:
            return {}
        
        total_words = sum(article.get('word_count', 0) for article in self.articles)
        categories = {}
        sources = {}
        
        for article in self.articles:
            category = article.get('category', 'unknown')
            source = article.get('source', 'unknown')
            
            categories[category] = categories.get(category, 0) + 1
            sources[source] = sources.get(source, 0) + 1
        
        return {
            'total_articles': len(self.articles),
            'total_words': total_words,
            'categories': categories,
            'sources': sources,
            'avg_words_per_article': total_words // len(self.articles) if self.articles else 0
        }


def build_vector_database(embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2", 
                         index_path: str = "src/data/faiss_index"):
    """
    Main function to build FAISS vector database from knowledge base
    
    Steps:
    1. Load all articles from knowledge base
    2. Convert to LangChain documents
    3. Create/update FAISS vector store
    4. Test retrieval functionality
    """
    
    print("🚀 Building FAISS Vector Database for Financial Knowledge Base")
    print("=" * 65)
    
    # Step 1: Load knowledge base
    loader = KnowledgeBaseLoader()
    articles = loader.load_articles()
    
    if not articles:
        print("❌ No articles found! Please run the scraper first.")
        return False
    
    # Display statistics
    stats = loader.get_statistics()
    print(f"\n📊 Knowledge Base Statistics:")
    print(f"   📄 Total Articles: {stats['total_articles']}")
    print(f"   📝 Total Words: {stats['total_words']:,}")
    print(f"   📖 Average Words/Article: {stats['avg_words_per_article']}")
    print(f"\n📂 Categories:")
    for category, count in stats['categories'].items():
        print(f"   • {category}: {count} articles")
    print(f"\n🌐 Sources:")
    for source, count in stats['sources'].items():
        print(f"   • {source}: {count} articles")
    
    # Step 2: Create documents
    print(f"\n🔄 Converting articles to documents...")
    documents = loader.create_documents()
    
    if not documents:
        print("❌ Failed to create documents!")
        return False
    
    # Step 3: Build vector store
    print(f"\n🔍 Building FAISS vector store...")
    print(f"   📍 Index path: {index_path}")
    print(f"   🧠 Embedding model: {embedding_model}")
    
    try:
        # Initialize vector store
        vector_store = FinanceVectorStore(
            embedding_model=embedding_model,
            index_path=index_path
        )
        
        # Add documents (this will chunk, embed, and index them)
        print(f"   ⚙️  Processing {len(documents)} documents...")
        vector_store.add_documents(documents)
        
        print(f"✅ Vector database built successfully!")
        print(f"   📁 Saved to: {index_path}")
        print(f"   🔢 Total document chunks: {len(vector_store.documents)}")
        
    except Exception as e:
        print(f"❌ Error building vector store: {e}")
        return False
    
    # Step 4: Test retrieval
    print(f"\n🧪 Testing retrieval functionality...")
    try:
        retriever = FinanceRetriever(vector_store)
        
        # Test queries
        test_queries = [
            "What is a 401k plan?",
            "How to invest in stocks?",
            "What is cryptocurrency?",
            "retirement planning strategies",
            "credit score importance"
        ]
        
        print(f"   🔍 Running test queries...")
        for query in test_queries[:3]:  # Test first 3 queries
            results = retriever.retrieve(query, k=2)
            if results:
                print(f"   ✅ '{query}' → {len(results)} results (top score: {results[0]['score']:.3f})")
            else:
                print(f"   ⚠️  '{query}' → No results")
        
        print(f"✅ Retrieval test completed!")
        
    except Exception as e:
        print(f"⚠️  Retrieval test failed: {e}")
    
    # Step 5: Usage instructions
    print(f"\n🎉 Vector Database Ready!")
    print(f"=" * 30)
    print(f"""
📖 How to use your FAISS vector database:

1. 🔍 Simple Search:
   ```python
   from src.rag.vector_store import FinanceVectorStore
   from src.rag.retriever import FinanceRetriever
   
   # Load vector store
   vector_store = FinanceVectorStore(index_path="{index_path}")
   retriever = FinanceRetriever(vector_store)
   
   # Search for relevant information
   results = retriever.retrieve("401k retirement planning", k=5)
   for result in results:
       print(f"Score: {{result['score']:.3f}}")
       print(f"Source: {{result['source']}}")
       print(f"Content: {{result['content'][:200]}}...")
   ```

2. 🏷️ Category-Specific Search:
   ```python
   # Search within specific categories
   retirement_results = retriever.retrieve_by_category(
       "investment strategies", 
       category="retirement_planning", 
       k=3
   )
   ```

3. 🤖 AI Agent Integration:
   ```python
   # Build context for LLM
   query = "How much should I save for retirement?"
   results = retriever.retrieve(query, k=5)
   context = retriever.build_context(query, results)
   
   # Use context with your LLM
   response = your_llm.generate(context + "\\n\\nUser Question: " + query)
   ```

📁 Your vector database is saved at: {index_path}
🔄 To rebuild: python build_vector_db.py
🧪 To test: python test_vector_db.py
""")
    
    return True


def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build FAISS vector database from financial knowledge base")
    parser.add_argument("--embedding-model", default="sentence-transformers/all-MiniLM-L6-v2", 
                       help="Embedding model to use (local HuggingFace model or OpenAI model)")
    parser.add_argument("--index-path", default="src/data/faiss_index", 
                       help="Path to save FAISS index")
    
    args = parser.parse_args()
    
    # Check for OpenAI API key only if using OpenAI models
    if args.embedding_model.startswith("text-embedding") and not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Warning: OPENAI_API_KEY environment variable not set!")
        print("   You'll need to set this for OpenAI embedding generation.")
        print("   Example: export OPENAI_API_KEY='your-api-key-here'")
        print("   Or use a local model like: --embedding-model sentence-transformers/all-MiniLM-L6-v2")
        response = input("\n   Continue anyway? (y/N): ")
        if response.lower() != 'y':
            return
    
    success = build_vector_database(
        embedding_model=args.embedding_model,
        index_path=args.index_path
    )
    
    if success:
        print(f"\n🎉 Success! Your financial knowledge base is now searchable!")
    else:
        print(f"\n❌ Failed to build vector database. Check the logs above.")


if __name__ == "__main__":
    main()
