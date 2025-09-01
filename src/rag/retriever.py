# Create an intelligent retriever that combines vector search with reranking
# Include query enhancement and context building for better LLM responses

from typing import List, Dict, Any, Optional
from src.rag.vector_store import FinanceVectorStore

class FinanceRetriever:
    """
    Intelligent retriever for financial knowledge base
    
    Features:
    - Multi-stage retrieval with reranking
    - Query enhancement and expansion
    - Context building for LLM consumption
    - Source diversity for comprehensive answers
    """
    
    def __init__(self, vector_store: FinanceVectorStore):
        self.vector_store = vector_store
        
        # Financial domain keywords for query enhancement
        self.domain_keywords = {
            "investment": ["stocks", "bonds", "ETFs", "mutual funds", "portfolio"],
            "retirement": ["401k", "IRA", "pension", "social security"],
            "risk": ["volatility", "diversification", "asset allocation"],
            "analysis": ["valuation", "ratios", "performance", "metrics"]
        }
    
    def retrieve(self, query: str, k: int = 5, enhance_query: bool = True) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents with optional query enhancement
        
        Steps:
        1. Enhance query with domain-specific terms
        2. Perform vector similarity search
        3. Rerank results for relevance and diversity
        4. Format results for LLM consumption
        """
        # Enhance query if requested
        if enhance_query:
            enhanced_query = self._enhance_query(query)
        else:
            enhanced_query = query
        
        # Retrieve candidates
        candidates = self.vector_store.similarity_search(enhanced_query, k=k*2)
        
        # Rerank for diversity and relevance
        final_results = self._rerank_results(candidates, query, k)
        
        return final_results
    
    def retrieve_by_category(self, query: str, category: str, k: int = 3) -> List[Dict[str, Any]]:
        """Retrieve documents filtered by category"""
        return self.vector_store.similarity_search(query, k=k, category_filter=category)
    
    def build_context(self, query: str, retrieved_docs: List[Dict[str, Any]]) -> str:
        """
        Build comprehensive context for LLM from retrieved documents
        
        Format:
        - Combine relevant chunks with source attribution
        - Prioritize substantive content over titles/headers
        - Include multiple chunks from same source for comprehensive coverage
        - Balance comprehensiveness with readability
        """
        if not retrieved_docs:
            return "No relevant information found in knowledge base."
        
        context_parts = []
        included_count = 0
        max_chunks = 5  # Limit for readability and token efficiency
        min_content_length = 50  # Skip very short content like titles
        
        context_parts.append(f"Based on the following information relevant to: '{query}'\n")
        
        for i, doc in enumerate(retrieved_docs):
            if included_count >= max_chunks:
                break
                
            source = doc["metadata"]["source"]
            content = doc["content"]
            score = doc["score"]
            
            # Skip very short content (likely titles or fragments)
            if len(content) < min_content_length:
                continue
            
            # Include substantive content with source attribution
            context_parts.append(f"\n[Source {included_count + 1}: {source} - Relevance: {score:.3f}]")
            context_parts.append(content)
            included_count += 1
        
        # Fallback if no substantive content found
        if included_count == 0:
            context_parts.append("\n[Available Information]")
            for i, doc in enumerate(retrieved_docs[:2]):  # Include at least some content
                context_parts.append(f"{doc['content']}")
        
        context_parts.append("\nPlease provide a comprehensive answer based on this information, citing the relevant sources.")
        
        return "\n".join(context_parts)
    
    def _enhance_query(self, query: str) -> str:
        """
        Enhance query with domain-specific terms and synonyms
        """
        enhanced_terms = []
        query_lower = query.lower()
        
        # Add related financial terms
        for category, keywords in self.domain_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                enhanced_terms.extend(keywords[:2])  # Add top 2 related terms
        
        # Combine original query with enhancements
        if enhanced_terms:
            return f"{query} {' '.join(set(enhanced_terms))}"
        
        return query
    
    def _rerank_results(self, candidates: List[Dict[str, Any]], original_query: str, k: int) -> List[Dict[str, Any]]:
        """
        Rerank results for relevance and source diversity
        
        Factors:
        - Similarity score
        - Source diversity
        - Content quality indicators
        """
        if not candidates:
            return []
        
        # Score each candidate
        scored_candidates = []
        source_counts = {}
        
        for candidate in candidates:
            source = candidate["metadata"]["source"]
            source_counts[source] = source_counts.get(source, 0) + 1
            
            # Calculate rerank score
            similarity_score = candidate["score"]
            diversity_bonus = 1.0 / source_counts[source]  # Favor diverse sources
            content_length_score = min(len(candidate["content"]) / 500, 1.0)  # Favor substantial content
            
            final_score = similarity_score * 0.7 + diversity_bonus * 0.2 + content_length_score * 0.1
            
            scored_candidates.append({
                **candidate,
                "rerank_score": final_score
            })
        
        # Sort by rerank score and return top k
        scored_candidates.sort(key=lambda x: x["rerank_score"], reverse=True)
        return scored_candidates[:k]