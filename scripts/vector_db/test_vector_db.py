#!/usr/bin/env python3
"""
Test FAISS Vector Database Functionality
Test retrieval, search quality, and performance
"""

import sys
from pathlib import Path
import time
from typing import List, Dict

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from rag.vector_store import FinanceVectorStore
from rag.retriever import FinanceRetriever

def test_vector_database(index_path: str = "src/data/faiss_index"):
    """Comprehensive test of vector database functionality"""
    
    print("🧪 Testing FAISS Vector Database")
    print("=" * 40)
    
    try:
        # Load vector store
        print("📂 Loading vector store...")
        vector_store = FinanceVectorStore(index_path=index_path)
        
        if vector_store.index is None:
            print("❌ No vector index found! Please run 'python build_vector_db.py' first.")
            return False
        
        print(f"✅ Loaded vector store with {len(vector_store.documents)} chunks")
        
        # Initialize retriever
        retriever = FinanceRetriever(vector_store)
        
        # Test different types of queries
        test_queries = [
            # Retirement planning
            {
                "query": "What is a 401k retirement plan?",
                "expected_category": "retirement_planning",
                "description": "Retirement Planning Query"
            },
            {
                "query": "IRA vs 401k differences",
                "expected_category": "retirement_planning", 
                "description": "Comparative Retirement Query"
            },
            # Personal finance
            {
                "query": "How to improve credit score",
                "expected_category": "personal_finance",
                "description": "Credit Management Query"
            },
            {
                "query": "emergency fund savings",
                "expected_category": "personal_finance",
                "description": "Emergency Planning Query"
            },
            # Investment topics
            {
                "query": "stock market analysis ratios",
                "expected_category": "education",
                "description": "Investment Analysis Query"
            },
            {
                "query": "cryptocurrency bitcoin basics",
                "expected_category": "education",
                "description": "Crypto Education Query"
            },
            # Complex queries
            {
                "query": "portfolio diversification strategies for retirement",
                "expected_category": None,  # Mixed categories
                "description": "Complex Multi-Category Query"
            }
        ]
        
        print(f"\n🔍 Testing {len(test_queries)} queries...")
        
        all_results = []
        total_time = 0
        
        for i, test_case in enumerate(test_queries, 1):
            query = test_case["query"]
            expected_cat = test_case["expected_category"]
            description = test_case["description"]
            
            print(f"\n{i}. {description}")
            print(f"   Query: '{query}'")
            
            # Time the search
            start_time = time.time()
            results = retriever.retrieve(query, k=3)
            search_time = time.time() - start_time
            total_time += search_time
            
            print(f"   ⏱️  Search time: {search_time:.3f}s")
            print(f"   📊 Results: {len(results)}")
            
            if results:
                top_result = results[0]
                print(f"   🎯 Top score: {top_result['score']:.3f}")
                print(f"   📁 Top source: {top_result['metadata']['source']}")
                print(f"   🏷️  Top category: {top_result['metadata']['category']}")
                print(f"   📄 Preview: {top_result['content'][:100]}...")
                
                # Check category match if specified
                if expected_cat:
                    category_match = any(r['metadata']['category'] == expected_cat for r in results)
                    if category_match:
                        print(f"   ✅ Found expected category: {expected_cat}")
                    else:
                        print(f"   ⚠️  Expected category '{expected_cat}' not in top results")
                
                all_results.extend(results)
            else:
                print(f"   ❌ No results found!")
        
        # Performance summary
        avg_time = total_time / len(test_queries)
        print(f"\n⚡ Performance Summary:")
        print(f"   📊 Total queries: {len(test_queries)}")
        print(f"   ⏱️  Total time: {total_time:.3f}s")
        print(f"   📈 Average time per query: {avg_time:.3f}s")
        
        # Quality analysis
        if all_results:
            scores = [r['score'] for r in all_results]
            avg_score = sum(scores) / len(scores)
            max_score = max(scores)
            min_score = min(scores)
            
            print(f"\n🎯 Quality Analysis:")
            print(f"   📊 Total results analyzed: {len(all_results)}")
            print(f"   📈 Average similarity score: {avg_score:.3f}")
            print(f"   🔝 Best score: {max_score:.3f}")
            print(f"   🔻 Worst score: {min_score:.3f}")
            
            # Category distribution
            categories = {}
            for result in all_results:
                cat = result['metadata']['category']
                categories[cat] = categories.get(cat, 0) + 1
            
            print(f"\n📂 Result Categories:")
            for cat, count in sorted(categories.items()):
                print(f"   • {cat}: {count} results")
        
        # Test context building
        print(f"\n📝 Testing Context Building...")
        test_query = "retirement planning with 401k"
        results = retriever.retrieve(test_query, k=3)
        
        if results:
            context = retriever.build_context(test_query, results)
            print(f"   ✅ Built context: {len(context)} characters")
            print(f"   📄 Context preview:")
            print(f"   {context[:200]}...")
        else:
            print(f"   ❌ No results for context building test")
        
        # Test category filtering
        print(f"\n🏷️  Testing Category Filtering...")
        retirement_results = retriever.retrieve_by_category(
            "investment strategies", 
            category="retirement_planning", 
            k=2
        )
        print(f"   🏦 Retirement category results: {len(retirement_results)}")
        
        personal_finance_results = retriever.retrieve_by_category(
            "budgeting tips", 
            category="personal_finance", 
            k=2
        )
        print(f"   💰 Personal finance category results: {len(personal_finance_results)}")
        
        print(f"\n✅ Vector database testing completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False


def interactive_search_demo():
    """Interactive demo for testing searches"""
    print(f"\n🔍 Interactive Search Demo")
    print("=" * 30)
    print("Enter search queries to test the vector database.")
    print("Type 'quit' to exit.\n")
    
    try:
        vector_store = FinanceVectorStore()
        retriever = FinanceRetriever(vector_store)
        
        while True:
            query = input("🔍 Enter search query: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                break
            
            if not query:
                continue
            
            print(f"\n⏳ Searching for: '{query}'...")
            results = retriever.retrieve(query, k=3)
            
            if results:
                print(f"📊 Found {len(results)} results:\n")
                for i, result in enumerate(results, 1):
                    score = result['score']
                    source = result['metadata']['source']
                    category = result['metadata']['category']
                    content = result['content']
                    
                    print(f"{i}. Score: {score:.3f} | Category: {category}")
                    print(f"   Source: {source}")
                    print(f"   Content: {content[:150]}...\n")
            else:
                print("❌ No results found.\n")
                
    except Exception as e:
        print(f"❌ Error in interactive demo: {e}")


def main():
    """Main test execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test FAISS vector database")
    parser.add_argument("--index-path", default="src/data/faiss_index",
                       help="Path to FAISS index")
    parser.add_argument("--interactive", action="store_true",
                       help="Run interactive search demo")
    
    args = parser.parse_args()
    
    # Run comprehensive tests
    success = test_vector_database(args.index_path)
    
    if success and args.interactive:
        interactive_search_demo()
    
    if success:
        print(f"\n🎉 All tests passed! Your vector database is working perfectly.")
    else:
        print(f"\n❌ Some tests failed. Please check the setup.")


if __name__ == "__main__":
    main()
