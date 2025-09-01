# Create a comprehensive FAISS vector store for financial knowledge base
# Include document chunking, embedding generation, similarity search
# Support for metadata filtering and source attribution

import faiss
import numpy as np
import pickle
from typing import List, Dict, Any, Optional
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import os

# Try to import sentence transformers directly for better control
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

class SimpleEmbeddings:
    """Simple wrapper for sentence transformers to avoid segfaults"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError("sentence-transformers not available")
        
        # Check for available devices
        import torch
        if torch.backends.mps.is_available():
            device = "mps"  # Apple Silicon GPU
            print(f"Using Apple Silicon GPU (MPS) for embeddings")
        elif torch.cuda.is_available():
            device = "cuda"  # NVIDIA GPU
            print(f"Using CUDA GPU for embeddings")
        else:
            device = "cpu"
            print(f"Using CPU for embeddings")
        
        self.model = SentenceTransformer(model_name, device=device)
        self.device = device
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents"""
        embeddings = self.model.encode(
            texts, 
            convert_to_numpy=True, 
            show_progress_bar=True,
            batch_size=32 if self.device != "cpu" else 8  # Larger batch for GPU
        )
        return embeddings.tolist()
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query"""
        embedding = self.model.encode([text], convert_to_numpy=True)
        return embedding[0].tolist()

class FinanceVectorStore:
    """
    FAISS-based vector store for financial knowledge base
    
    Features:
    - Document chunking with overlap for context preservation
    - OpenAI embeddings for semantic similarity
    - Metadata storage for source attribution
    - Efficient similarity search with filtering
    - Persistence and loading of index
    """
    
    def __init__(self, embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2", index_path: str = "data/faiss_index"):
        # Support both OpenAI and local models
        if embedding_model.startswith("text-embedding"):
            # OpenAI model
            self.embeddings = OpenAIEmbeddings(model=embedding_model)
        else:
            # Local sentence-transformers model
            if embedding_model.startswith("sentence-transformers/"):
                model_name = embedding_model.split("/", 1)[1]
            else:
                model_name = embedding_model
            
            try:
                self.embeddings = SimpleEmbeddings(model_name=model_name)
                print(f"Using local embedding model: {model_name}")
            except Exception as e:
                print(f"Error loading local model: {e}")
                print("Falling back to OpenAI embeddings...")
                self.embeddings = OpenAIEmbeddings()
        
        self.index_path = index_path
        self.index = None
        self.documents = []
        self.metadata = []
        
        # Text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Load existing index if available
        self._load_index()
    
    def add_documents(self, documents: List[Document]) -> None:
        """
        Add documents to the vector store
        
        Steps:
        1. Chunk documents into smaller pieces
        2. Generate embeddings for each chunk
        3. Add to FAISS index with metadata
        4. Save updated index
        """
        print(f"Processing {len(documents)} documents...")
        
        # Chunk all documents
        chunks = []
        chunk_metadata = []
        
        for doc in documents:
            doc_chunks = self.text_splitter.split_text(doc.page_content)
            for i, chunk in enumerate(doc_chunks):
                chunks.append(chunk)
                chunk_metadata.append({
                    "source": doc.metadata.get("source", "unknown"),
                    "category": doc.metadata.get("category", "general"),
                    "chunk_id": f"{doc.metadata.get('source', 'unknown')}_{i}",
                    "original_doc_id": doc.metadata.get("doc_id", "unknown")
                })
        
        print(f"Created {len(chunks)} chunks from documents")
        
        # Generate embeddings in larger batches for GPU, smaller for CPU
        if hasattr(self.embeddings, 'device') and self.embeddings.device != "cpu":
            batch_size = 32  # Larger batch for GPU
        else:
            batch_size = 8   # Smaller batch for CPU
        
        all_embeddings = []
        
        for i in range(0, len(chunks), batch_size):
            batch_chunks = chunks[i:i+batch_size]
            print(f"Processing batch {i//batch_size + 1}/{(len(chunks) + batch_size - 1)//batch_size}")
            
            try:
                batch_embeddings = self.embeddings.embed_documents(batch_chunks)
                all_embeddings.extend(batch_embeddings)
            except Exception as e:
                print(f"Error processing batch: {e}")
                # Try processing one by one if batch fails
                for chunk in batch_chunks:
                    try:
                        embedding = self.embeddings.embed_documents([chunk])
                        all_embeddings.extend(embedding)
                    except Exception as chunk_e:
                        print(f"Error processing individual chunk: {chunk_e}")
                        # Skip this chunk if it fails
                        continue
        
        if not all_embeddings:
            print("No embeddings generated successfully!")
            return
            
        embeddings_array = np.array(all_embeddings).astype('float32')
        
        # Create or update FAISS index
        if self.index is None:
            dimension = embeddings_array.shape[1]
            self.index = faiss.IndexFlatIP(dimension)  # Inner product for similarity
        
        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings_array)
        
        # Add to index
        self.index.add(embeddings_array)
        
        # Store documents and metadata (only for successfully processed chunks)
        self.documents.extend(chunks[:len(all_embeddings)])
        self.metadata.extend(chunk_metadata[:len(all_embeddings)])
        
        print(f"Successfully added {len(all_embeddings)} embeddings to index")
        
        # Save index
        self._save_index()
    
    def similarity_search(self, query: str, k: int = 5, category_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Perform similarity search with optional category filtering
        
        Returns list of documents with scores and metadata
        """
        if self.index is None:
            return []
        
        # Generate query embedding
        query_embedding = self.embeddings.embed_query(query)
        query_vector = np.array([query_embedding]).astype('float32')
        faiss.normalize_L2(query_vector)
        
        # Search
        scores, indices = self.index.search(query_vector, k * 2)  # Get more results for filtering
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx >= len(self.documents):
                continue
                
            metadata = self.metadata[idx]
            
            # Apply category filter if specified
            if category_filter and metadata.get("category") != category_filter:
                continue
            
            results.append({
                "content": self.documents[idx],
                "score": float(score),
                "metadata": metadata,
                "source": metadata.get("source", "unknown")
            })
            
            if len(results) >= k:
                break
        
        return results
    
    def _save_index(self) -> None:
        """Save FAISS index and metadata to disk"""
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        
        if self.index is not None:
            faiss.write_index(self.index, f"{self.index_path}.faiss")
        
        with open(f"{self.index_path}_docs.pkl", "wb") as f:
            pickle.dump(self.documents, f)
            
        with open(f"{self.index_path}_metadata.pkl", "wb") as f:
            pickle.dump(self.metadata, f)
    
    def _load_index(self) -> None:
        """Load existing FAISS index and metadata from disk"""
        try:
            if os.path.exists(f"{self.index_path}.faiss"):
                self.index = faiss.read_index(f"{self.index_path}.faiss")
                
            if os.path.exists(f"{self.index_path}_docs.pkl"):
                with open(f"{self.index_path}_docs.pkl", "rb") as f:
                    self.documents = pickle.load(f)
                    
            if os.path.exists(f"{self.index_path}_metadata.pkl"):
                with open(f"{self.index_path}_metadata.pkl", "rb") as f:
                    self.metadata = pickle.load(f)
        except Exception as e:
            print(f"Error loading index: {e}")
            self.index = None
            self.documents = []
            self.metadata = []