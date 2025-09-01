# Create a comprehensive Finance Q&A Agent that inherits from BaseFinanceAgent
# Integrate with RAG system for knowledge retrieval
# Handle basic financial education queries with source attribution
# Include query classification and response confidence scoring

from typing import Dict, Any, List, Optional
from src.agents.base_agent import BaseFinanceAgent
from src.rag.retriever import FinanceRetriever
from src.core.state import FinanceAssistantState

class FinanceQAAgent(BaseFinanceAgent):
    """
    Finance Q&A Agent for educational queries
    
    Capabilities:
    - Answer basic financial concepts (stocks, bonds, ETFs, diversification)
    - Retrieve relevant information from knowledge base using RAG
    - Provide source citations and confidence scores
    - Classify query complexity and escalate when needed
    - Handle follow-up questions with context
    """
    
    def __init__(self, llm, retriever: FinanceRetriever):
        system_prompt = """
        You are a helpful financial education assistant. Your role is to:
        1. Explain financial concepts in simple, beginner-friendly language
        2. Always cite your sources when providing information
        3. Avoid giving specific investment advice - focus on education
        4. Ask clarifying questions when queries are ambiguous
        5. Suggest escalation to specialized agents when appropriate
        
        Guidelines:
        - Use analogies and examples to explain complex concepts
        - Include relevant definitions for financial terms
        - Provide balanced perspectives on investment strategies
        - Always include appropriate disclaimers
        """
        super().__init__(llm, [], "finance_qa", system_prompt)
        self.retriever = retriever
    
    def execute(self, state: FinanceAssistantState) -> Dict[str, Any]:
        """
        Process financial education query
        
        Steps:
        1. Extract and classify the financial question
        2. Retrieve relevant context from knowledge base
        3. Generate educational response with sources
        4. Determine confidence score and next steps
        5. Update conversation context
        """
        try:
            query = state["user_query"]
            
            # Classify the query for better processing
            query_classification = self._classify_query(query)
            self.logger.info(f"Query classified as: {query_classification['primary_category']} "
                           f"(complexity: {query_classification['complexity']})")
            
            # Retrieve relevant financial content based on classification
            if query_classification["complexity"] == "advanced":
                # For advanced queries, get more sources
                retrieved_docs = self.retriever.retrieve(query, k=5)
            else:
                # For basic/intermediate queries, fewer sources are sufficient
                retrieved_docs = self.retriever.retrieve(query, k=3)
            
            # Build context for LLM
            context = self._build_context(query, retrieved_docs, state)
            
            # Generate response with classification context
            response = self._generate_response(context, query_classification)
            
            # Determine next agent based on classification and query
            next_agent = self._suggest_next_agent(query, query_classification)
            
            # Format and return response
            formatted_response = self.format_response(
                content=response["content"],
                sources=response["sources"],
                confidence=response["confidence"]
            )
            
            # Add classification info and next agent suggestion
            formatted_response["query_classification"] = query_classification
            formatted_response["next_agent"] = next_agent
            formatted_response["updated_context"] = {
                "last_query_type": query_classification["primary_category"],
                "complexity_level": query_classification["complexity"]
            }
            
            return formatted_response
            
        except Exception as e:
            self.logger.error(f"Error in FinanceQA execute: {str(e)}")
            return self.handle_error(e, "query_processing")
    
    def _classify_query(self, query: str) -> Dict[str, Any]:
        """
        Classify the type of financial query for better routing
        
        Phase 1: Simple keyword-based classification
        """
        query_lower = query.lower()
        
        # Define query categories with keywords
        categories = {
            "basic_concepts": ["what is", "define", "explain", "how does", "meaning"],
            "investment_education": ["investing", "stocks", "bonds", "etf", "mutual fund", "diversification"],
            "retirement_planning": ["retirement", "401k", "ira", "pension", "social security"],
            "risk_management": ["risk", "volatility", "hedge", "insurance", "emergency fund"],
            "market_education": ["market", "economy", "inflation", "recession", "bull market", "bear market"],
            "financial_planning": ["budget", "save", "plan", "goal", "debt", "credit"]
        }
        
        # Score each category
        category_scores = {}
        for category, keywords in categories.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                category_scores[category] = score
        
        # Determine primary category
        if category_scores:
            primary_category = max(category_scores, key=category_scores.get)
            confidence = category_scores[primary_category] / len(query.split())
        else:
            primary_category = "general"
            confidence = 0.5
        
        return {
            "primary_category": primary_category,
            "confidence": min(confidence, 1.0),
            "all_scores": category_scores,
            "complexity": self._assess_complexity(query)
        }
    
    def _assess_complexity(self, query: str) -> str:
        """
        Assess the complexity level of the query
        
        Returns: "basic", "intermediate", or "advanced"
        """
        query_lower = query.lower()
        
        # Advanced indicators
        advanced_terms = ["derivatives", "options", "futures", "hedge fund", "private equity", 
                         "arbitrage", "alpha", "beta", "sharpe ratio", "modern portfolio theory"]
        if any(term in query_lower for term in advanced_terms):
            return "advanced"
        
        # Intermediate indicators
        intermediate_terms = ["asset allocation", "rebalancing", "expense ratio", "dividend yield",
                             "pe ratio", "market cap", "volatility", "correlation"]
        if any(term in query_lower for term in intermediate_terms):
            return "intermediate"
        
        # Basic by default
        return "basic"
    
    def _build_context(self, query: str, docs: List, state: FinanceAssistantState) -> str:
        """Build comprehensive context for LLM response generation"""
        if not docs:
            return f"Query: {query}\n\nNo relevant information found in knowledge base. Please provide a general response based on your training data and include appropriate disclaimers."
        
        # Use retriever to build formatted context
        context = self.retriever.build_context(query, docs)
        
        # Add conversation history if available
        conversation_history = state.get("conversation_history", [])
        if conversation_history:
            recent_context = "\n".join([f"Previous: {item}" for item in conversation_history[-2:]])
            context = f"Recent conversation:\n{recent_context}\n\n{context}"
        
        return context
    
    def _generate_response(self, context: str, query_classification: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate educational response using LLM with retrieved context
        
        Enhanced with query classification for better response tailoring
        """
        
        # Tailor prompt based on query classification
        complexity = query_classification.get("complexity", "basic") if query_classification else "basic"
        category = query_classification.get("primary_category", "general") if query_classification else "general"
        
        # Adjust response style based on complexity
        if complexity == "basic":
            style_instruction = "Use simple, beginner-friendly language with analogies and examples."
        elif complexity == "intermediate":
            style_instruction = "Provide a balanced explanation suitable for someone with basic financial knowledge."
        else:  # advanced
            style_instruction = "Provide a comprehensive, detailed explanation with technical accuracy."
        
        # Enhanced prompt for financial education
        full_prompt = f"""
{context}

Query Category: {category}
Complexity Level: {complexity}

Instructions:
1. {style_instruction}
2. Include relevant definitions for financial terms (adjust detail level based on complexity)
3. Cite the sources from the provided context
4. Add appropriate disclaimers (this is educational, not investment advice)
5. Suggest follow-up questions if relevant
6. For basic queries: Use analogies and real-world examples
7. For advanced queries: Include relevant formulas or technical details if helpful

Please provide a comprehensive but appropriately-leveled answer.
"""
        
        try:
            # Generate response using the LLM
            llm_response = self.llm.invoke(full_prompt)
            
            # Extract sources from context
            sources = self._extract_sources_from_context(context)
            
            # Calculate confidence based on source quality and response
            response_text = llm_response.content if hasattr(llm_response, 'content') else str(llm_response)
            confidence = self._calculate_confidence(sources, response_text)
            
            return {
                "content": response_text,
                "sources": sources,
                "confidence": confidence
            }
            
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            return {
                "content": "I apologize, but I'm having trouble processing your question right now. Please try rephrasing your question or contact support if the issue persists.",
                "sources": [],
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _extract_sources_from_context(self, context: str) -> List[str]:
        """Extract source names from the formatted context"""
        sources = []
        lines = context.split('\n')
        for line in lines:
            if line.startswith('[Source') and ']:' in line:
                source = line.split(']:')[1].strip()
                if source not in sources:
                    sources.append(source)
        return sources
    
    def _calculate_confidence(self, sources: List[str], response: str) -> float:
        """Calculate confidence score based on sources and response quality"""
        base_confidence = 0.5
        
        # Boost confidence if we have good sources
        if sources:
            source_boost = min(len(sources) * 0.15, 0.3)
            base_confidence += source_boost
        
        # Check for disclaimers (good practice)
        if any(word in response.lower() for word in ['disclaimer', 'not advice', 'consult', 'professional']):
            base_confidence += 0.1
        
        # Check response length (substantial responses are better)
        if len(response) > 200:
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)
    
    def _suggest_next_agent(self, query: str, query_classification: Dict[str, Any] = None) -> Optional[str]:
        """
        Suggest which agent should handle follow-up questions
        Enhanced with query classification for better routing
        """
        query_lower = query.lower()
        category = query_classification.get("primary_category", "general") if query_classification else "general"
        
        # Use classification to improve routing decisions
        if category == "retirement_planning":
            return "goal_agent"
        elif category == "investment_education" and any(word in query_lower for word in ['portfolio', 'allocation']):
            return "portfolio_agent"
        elif category == "market_education" or any(word in query_lower for word in ['price', 'analysis', 'performance']):
            return "market_agent"
        
        # Fallback to keyword-based routing
        if any(word in query_lower for word in ['portfolio', 'allocation', 'balance', 'diversification']):
            return "portfolio_agent"
        elif any(word in query_lower for word in ['goal', 'target', 'plan', 'timeline', 'save']):
            return "goal_agent"
        elif any(word in query_lower for word in ['market', 'price', 'stock', 'analysis', 'performance']):
            return "market_agent"
        else:
            return None  # Stay with QA agent