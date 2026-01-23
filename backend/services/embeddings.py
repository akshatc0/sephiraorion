"""
Embedding generation and vector database management
"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import json
from pathlib import Path
from loguru import logger
from openai import OpenAI
from backend.core.config import get_settings
import time


class EmbeddingService:
    """Service for generating embeddings and managing vector database"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = OpenAI(api_key=self.settings.openai_api_key)
        self.chroma_client = None
        self.collection = None
        
    def initialize_chromadb(self, collection_name: str = "sentiment_data"):
        """Initialize ChromaDB client and collection"""
        logger.info(f"Initializing ChromaDB at {self.settings.chromadb_path}")
        
        # Create directory if it doesn't exist
        Path(self.settings.chromadb_path).mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        self.chroma_client = chromadb.PersistentClient(
            path=self.settings.chromadb_path
        )
        
        # Get or create collection
        try:
            self.collection = self.chroma_client.get_collection(name=collection_name)
            logger.info(f"Loaded existing collection '{collection_name}' with {self.collection.count()} documents")
        except:
            self.collection = self.chroma_client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Created new collection '{collection_name}'")
        
        return self.collection
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text"""
        try:
            response = self.client.embeddings.create(
                model=self.settings.openai_embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def generate_embeddings_batch(self, texts: List[str], batch_size: int = 100) -> List[List[float]]:
        """Generate embeddings for multiple texts in batches"""
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            logger.info(f"Generating embeddings for batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1}")
            
            try:
                response = self.client.embeddings.create(
                    model=self.settings.openai_embedding_model,
                    input=batch
                )
                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)
                
                # Small delay to respect rate limits
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error generating embeddings for batch: {e}")
                raise
        
        return embeddings
    
    def add_chunks_to_db(self, chunks: List[Dict[str, Any]], batch_size: int = 100):
        """Add text chunks to ChromaDB with embeddings"""
        if self.collection is None:
            raise ValueError("ChromaDB collection not initialized. Call initialize_chromadb() first.")
        
        logger.info(f"Adding {len(chunks)} chunks to vector database...")
        
        # Prepare data
        texts = [chunk['text'] for chunk in chunks]
        ids = [chunk['chunk_id'] for chunk in chunks]
        metadatas = [chunk['metadata'] for chunk in chunks]
        
        # Generate embeddings in batches
        embeddings = self.generate_embeddings_batch(texts, batch_size=batch_size)
        
        # Add to ChromaDB in batches
        for i in range(0, len(chunks), batch_size):
            end_idx = min(i + batch_size, len(chunks))
            
            self.collection.add(
                ids=ids[i:end_idx],
                embeddings=embeddings[i:end_idx],
                documents=texts[i:end_idx],
                metadatas=metadatas[i:end_idx]
            )
            
            logger.info(f"Added batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1}")
        
        logger.info(f"Successfully added {len(chunks)} chunks to vector database")
        
    def query_similar_chunks(
        self, 
        query: str, 
        top_k: int = 10,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Query similar chunks from vector database"""
        if self.collection is None:
            raise ValueError("ChromaDB collection not initialized. Call initialize_chromadb() first.")
        
        # Generate query embedding
        query_embedding = self.generate_embedding(query)
        
        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_dict if filter_dict else None
        )
        
        # Format results
        formatted_results = {
            'documents': results['documents'][0] if results['documents'] else [],
            'metadatas': results['metadatas'][0] if results['metadatas'] else [],
            'distances': results['distances'][0] if results['distances'] else [],
            'ids': results['ids'][0] if results['ids'] else []
        }
        
        return formatted_results
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        if self.collection is None:
            raise ValueError("ChromaDB collection not initialized. Call initialize_chromadb() first.")
        
        count = self.collection.count()
        
        # Get sample to analyze chunk types
        sample = self.collection.get(limit=min(100, count))
        
        chunk_types = {}
        if sample['metadatas']:
            for metadata in sample['metadatas']:
                chunk_type = metadata.get('type', 'unknown')
                chunk_types[chunk_type] = chunk_types.get(chunk_type, 0) + 1
        
        return {
            'total_chunks': count,
            'chunk_types_sample': chunk_types
        }


def load_and_embed_data():
    """Load processed data and create embeddings"""
    settings = get_settings()
    
    # Load chunks from processed data
    chunks_path = Path(settings.processed_data_path) / "text_chunks.json"
    
    if not chunks_path.exists():
        logger.error(f"Chunks file not found at {chunks_path}")
        logger.info("Please run data_loader.py first to generate chunks")
        return
    
    logger.info(f"Loading chunks from {chunks_path}")
    with open(chunks_path, 'r') as f:
        chunks = json.load(f)
    
    logger.info(f"Loaded {len(chunks)} chunks")
    
    # Initialize embedding service
    embedding_service = EmbeddingService()
    embedding_service.initialize_chromadb()
    
    # Check if database already has data
    current_count = embedding_service.collection.count()
    if current_count > 0:
        logger.warning(f"Collection already has {current_count} documents")
        response = input("Do you want to clear and re-create? (yes/no): ")
        if response.lower() == 'yes':
            embedding_service.chroma_client.delete_collection("sentiment_data")
            embedding_service.initialize_chromadb()
        else:
            logger.info("Keeping existing collection")
            return
    
    # Add chunks to database
    embedding_service.add_chunks_to_db(chunks, batch_size=50)
    
    # Print stats
    stats = embedding_service.get_collection_stats()
    print("\n" + "="*50)
    print("Vector Database Summary")
    print("="*50)
    print(f"Total chunks in database: {stats['total_chunks']}")
    print(f"Chunk types: {stats['chunk_types_sample']}")
    print("="*50 + "\n")
    
    logger.info("Embedding generation complete!")


if __name__ == "__main__":
    load_and_embed_data()
