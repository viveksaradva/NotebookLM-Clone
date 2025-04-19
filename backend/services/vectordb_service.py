import chromadb
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from typing import List, Dict, Any, Tuple, Optional
from tqdm import tqdm

from backend.utils.embeddings import Embedder
from backend.core.config import settings

class VectorDBService:
    def __init__(self, persist_dir: Optional[str] = None):
        self.persist_dir = persist_dir or settings.VECTORDB_PATH
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.embedder = Embedder()
    
    def _get_collection(self, document_id: str):
        """Get a collection by document ID."""
        return self.client.get_collection(f"doc_{document_id}")
    
    def _sanitize_metadata(self, metadata_list: List[Dict[str, Any]]):
        """Convert list values in metadata to comma-separated strings."""
        for meta in metadata_list:
            for key, value in meta.items():
                if isinstance(value, list):
                    meta[key] = ", ".join(value)
    
    def add_document(self, document_id: str, chunks: List[Dict[str, Any]]) -> int:
        """Add document chunks to the vector database."""
        # Create or get collection
        collection_name = f"doc_{document_id}"
        collection = self.client.get_or_create_collection(name=collection_name)
        
        # Process chunks in batches
        batch_size = 16
        batch_docs, batch_ids, batch_embeddings, batch_metadata = [], [], [], []
        
        for i, chunk in tqdm(enumerate(chunks), total=len(chunks), desc="Embedding Chunks"):
            doc_id = f"{document_id}_chunk_{i}"
            
            # Skip if already exists
            existing = collection.get(ids=[doc_id])
            if existing and existing["ids"]:
                continue
            
            # Extract data
            text = chunk["text"]
            embedding = chunk["embedding"]
            keywords = chunk.get("keywords", [])
            
            # Add to batch
            batch_docs.append(text)
            batch_ids.append(doc_id)
            batch_embeddings.append(embedding)
            batch_metadata.append({"keywords": keywords})
            
            # Process batch if full
            if len(batch_docs) >= batch_size:
                self._sanitize_metadata(batch_metadata)
                collection.add(
                    ids=batch_ids,
                    embeddings=batch_embeddings,
                    documents=batch_docs,
                    metadatas=batch_metadata
                )
                batch_docs, batch_ids, batch_embeddings, batch_metadata = [], [], [], []
        
        # Process remaining documents
        if batch_docs:
            self._sanitize_metadata(batch_metadata)
            collection.add(
                ids=batch_ids,
                embeddings=batch_embeddings,
                documents=batch_docs,
                metadatas=batch_metadata
            )
        
        # Return the number of chunks added
        return collection.count()
    
    def add_pdf(self, pdf_path: str, document_id: str) -> int:
        """Process a PDF file and add it to the vector database."""
        # Extract and embed text
        pdf_chunks = self.embedder.load_pdf(pdf_path)
        
        # Add to vector database
        return self.add_document(document_id, pdf_chunks)
    
    def add_web_article(self, url: str, document_id: str) -> Dict[str, Any]:
        """Process a web article and add it to the vector database."""
        # Extract and embed text
        article_data = self.embedder.load_web_article(url)
        
        # Add to vector database
        chunk_count = self.add_document(document_id, article_data["chunks"])
        
        # Return metadata
        return {
            "message": "Web article added successfully!",
            "document_id": document_id,
            "chunk_count": chunk_count,
            "metadata": article_data["metadata"]
        }
    
    def get_documents(self, document_id: str) -> List[str]:
        """Retrieve all stored documents for a given document ID."""
        try:
            collection = self._get_collection(document_id)
            results = collection.get()
            
            if results and "documents" in results:
                return results["documents"]
        except Exception as e:
            print(f"Error retrieving documents for {document_id}: {e}")
        
        return []
    
    def query(self, query_text: str, document_id: Optional[str] = None, top_k: int = 5) -> Dict[str, Any]:
        """Retrieve the top-k most similar documents for a query."""
        query_embedding = self.embedder.get_embedding(query_text)
        query_keywords = set(query_text.lower().split())
        
        if document_id:
            # Query a specific document collection
            collection = self._get_collection(document_id)
            
            available_chunks = collection.count()
            if available_chunks == 0:
                return {"documents": [], "metadatas": []}
            
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=min(top_k, available_chunks)
            )
            
            return results
        else:
            # Query across all document collections
            all_results = {"documents": [], "metadatas": [], "ids": []}
            collection_names = self.client.list_collections()
            
            for collection_name in collection_names:
                collection = self.client.get_collection(collection_name.name)
                available_chunks = collection.count()
                
                if available_chunks > 0:
                    res = collection.query(
                        query_embeddings=[query_embedding],
                        n_results=min(top_k, available_chunks)
                    )
                    
                    if res and "documents" in res:
                        # Apply keyword filtering
                        filtered_docs = []
                        filtered_metadata = []
                        filtered_ids = []
                        
                        for doc, metadata, doc_id in zip(
                            res["documents"][0],
                            res["metadatas"][0],
                            res["ids"][0]
                        ):
                            doc_keywords = set(metadata["keywords"].split(", "))
                            if query_keywords & doc_keywords:
                                filtered_docs.append(doc)
                                filtered_metadata.append(metadata)
                                filtered_ids.append(doc_id)
                        
                        all_results["documents"].extend(filtered_docs)
                        all_results["metadatas"].extend(filtered_metadata)
                        all_results["ids"].extend(filtered_ids)
            
            return all_results
    
    def hybrid_query(self, query_text: str, document_id: Optional[str] = None, top_k: int = 5) -> Tuple[List[str], List[Dict[str, Any]]]:
        """Performs a hybrid search using embeddings + keyword matching."""
        query_embedding = self.embedder.get_embedding(query_text)
        
        # Remove stopwords from query for more meaningful matching
        query_keywords = set(
            word for word in query_text.lower().split() if word not in ENGLISH_STOP_WORDS
        )
        
        retrieved_docs = []
        retrieved_metadata = []
        
        collections = []
        
        if document_id:
            try:
                collection = self._get_collection(document_id)
                collections = [(document_id, collection)]
            except Exception as e:
                print(f"❌ Collection for document_id '{document_id}' not found: {e}")
                return [], []
        else:
            collections = [(col.name.replace("doc_", ""), self.client.get_collection(col.name))
                        for col in self.client.list_collections()]
        
        for doc_id, collection in collections:
            total_chunks = collection.count()
            if total_chunks == 0:
                print(f"⚠️ Skipping '{doc_id}' — No chunks available.")
                continue
            
            res = collection.query(
                query_embeddings=[query_embedding],
                n_results=min(top_k, total_chunks)
            )
            
            if res and "documents" in res:
                for doc, metadata in zip(res["documents"][0], res["metadatas"][0]):
                    keywords_field = metadata.get("keywords", "")
                    # Split if stored as comma-separated string
                    doc_keywords = (
                        set(keywords_field.split(", ")) if isinstance(keywords_field, str) else set(keywords_field)
                    )
                    
                    # Always include the document in results, regardless of keyword match
                    retrieved_docs.append(doc)
                    retrieved_metadata.append(metadata)
        
        return retrieved_docs, retrieved_metadata
