import chromadb
import os
import sys
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.embeddings.embedder import Embedder
from langsmith import traceable
from tqdm import tqdm

class ChromaDBManager:
    def __init__(self, persist_dir="data/chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.embedder = Embedder()
        self.tfidf_vectorizer = TfidfVectorizer(stop_words="english")

    def _get_collection(self, document_id):
        return self.client.get_collection(f"doc_{document_id}")

    def add_pdf(self, pdf_path, document_id):
        """Extracts text from a PDF, chunks it, embeds it, and stores it under a unique document_id."""
        collection_name = f"doc_{document_id}"  # Unique collection for each PDF
        collection = self.client.get_or_create_collection(name=collection_name)

        # Extract and embed text
        pdf_chunks = self.embedder.load_pdf(pdf_path)
        pdf_chunks = [chunk["text"] if isinstance(chunk, dict) else chunk for chunk in pdf_chunks]

        print("DEBUG: pdf_chunks =", pdf_chunks)
        tfidf_keywords = self.embedder.extract_keywords(pdf_chunks)

        batch_size = 16
        batch_docs, batch_ids, batch_embeddings, batch_metadata = [], [], [], []

        print(f"📘 Processing {len(pdf_chunks)} chunks from {pdf_path} (ID: {document_id})...")

        for i, chunk in tqdm(enumerate(pdf_chunks), total=len(pdf_chunks), desc="Embedding Chunks"):
            doc_id = f"{document_id}_chunk_{i}"

            # Skip if already exists
            existing = collection.get(ids=[doc_id])
            if existing and existing["ids"]:
                continue

            batch_docs.append(chunk)
            batch_ids.append(doc_id)
            batch_embeddings.append(self.embedder.get_embedding(chunk))
            batch_metadata.append({"keywords": tfidf_keywords[i]})

            # Process in batches
            if len(batch_docs) >= batch_size:
                collection.add(ids=batch_ids, embeddings=batch_embeddings, documents=batch_docs, metadatas=batch_metadata)
                batch_docs, batch_ids, batch_embeddings, batch_metadata = [], [], [], []

        # Insert remaining documents
        if batch_docs:
            collection.add(ids=batch_ids, embeddings=batch_embeddings, documents=batch_docs, metadatas=batch_metadata)

        print(f"✅ PDF '{pdf_path}' stored as '{collection_name}' in ChromaDB!")

    def query(self, query_text, document_id=None, top_k=3):
        """Retrieve the top-k most similar documents for a query. Supports querying a specific document."""
        query_embedding = self.embedder.get_embedding(query_text)
        query_keywords = set(query_text.lower().split())

        if document_id:
            # Query a specific document collection
            collection_name = f"doc_{document_id}"
            collection = self._get_collection(document_id)  # ✅ Explicitly get the collection

            available_chunks = collection.count()
            print(f"📚 Querying document '{document_id}' with {available_chunks} chunks available.")

            if available_chunks == 0:
                return ["No documents found."]

            results = collection.query(query_embeddings=[query_embedding], n_results=min(top_k, available_chunks))
        
        else:
            # Query across all document collections
            results = []
            collection_names = self.client.list_collections()  # ✅ Extract collection names
            for collection_name in collection_names:
                collection = self._get_collection(document_id)  # ✅ Explicitly fetch collection
                available_chunks = collection.count()
                print(f"📚 Querying collection '{collection_name}' with {available_chunks} chunks available.")

                if available_chunks > 0:
                    res = collection.query(query_embeddings=[query_embedding], n_results=min(top_k, available_chunks))
                    if res and "documents" in res:
                        # Apply keyword filtering
                        filtered_results = []
                        for doc, metadata in zip(res["documents"][0], res["metadatas"][0]):
                            doc_keywords = set(metadata["keywords"])
                            if query_keywords & doc_keywords:
                                filtered_results.append(doc)
                        results.extend(filtered_results)

        return results if results else []

    @traceable(run_type="retriever")
    def get_documents(self, document_id):
        """Retrieve all stored documents (chunks) for a given document_id."""
        collection_name = f"doc_{document_id}"

        try:
            collection = self._get_collection(document_id)
            results = collection.get()  # Retrieve all stored chunks

            if results and "documents" in results:
                return results["documents"]
        except Exception as e:
            print(f"Error retrieving documents for {document_id}: {e}")
        
        return []
    
    def hybrid_query(self, query_text, document_id=None, top_k=5):
        """Performs a hybrid search using embeddings + keyword matching."""
        query_embedding = self.embedder.get_embedding(query_text)
        query_keywords = set(query_text.lower().split())

        retrieved_docs = []
        retrieved_metadata = []

        if document_id:
            collection = self._get_collection(document_id)
            if collection.count() > 0:
                res = collection.query(query_embeddings=[query_embedding], n_results=top_k)
                if res and "documents" in res:
                    for doc, metadata in zip(res["documents"][0], res["metadatas"][0]):
                        doc_keywords = set(metadata["keywords"])
                        if query_keywords & doc_keywords:  # Check if any keywords match
                            retrieved_docs.append(doc)
                            retrieved_metadata.append(metadata)

        else:
            collection_names = self.client.list_collections()
            for collection_name in collection_names:
                collection = self._get_collection(document_id)
                if collection.count() > 0:
                    res = collection.query(query_embeddings=[query_embedding], n_results=top_k)
                    if res and "documents" in res:
                        for doc, metadata in zip(res["documents"][0], res["metadatas"][0]):
                            doc_keywords = set(metadata["keywords"])
                            if query_keywords & doc_keywords:
                                retrieved_docs.append(doc)
                                retrieved_metadata.append(metadata)

        return retrieved_docs, retrieved_metadata
    
    def add_web_article(self, url: str, document_id: str):
        """Loads web content, embeds it, and stores it in ChromaDB."""
        # Get the collection
        collection_name = f"doc_{document_id}"
        collection = self.client.get_or_create_collection(name=collection_name)

        article_data = self.embedder.load_web_article(url)

        print(f"\n\n\narticle_data: {article_data}\n\n\n")

        web_article_chunks = article_data["chunks"]
        web_article_chunks = [chunk["text"] if isinstance(chunk, dict) else chunk for chunk in web_article_chunks]

        tfidf_keywords = self.embedder.extract_keywords(web_article_chunks)

        batch_size = 16
        batch_docs, batch_ids, batch_embeddings, batch_metadata = [], [], [], []

        print(f"🌐 Processing {len(web_article_chunks)} chunks from {url} (ID: {document_id})...")

        for i, chunk in tqdm(enumerate(web_article_chunks), total=len(web_article_chunks), desc="Embedding Chunks"):
            doc_id = f"{document_id}_chunk_{i}"

            # Skip if already exists
            existing = collection.get(ids=[doc_id])
            if existing and existing["ids"]:
                continue

            # Merge metadata (TF-IDF keywords + article metadata)
            metadata = {**article_data["metadata"], "keywords": tfidf_keywords[i]}

            batch_docs.append(chunk)
            batch_ids.append(doc_id)
            batch_embeddings.append(self.embedder.get_embedding(chunk))
            batch_metadata.append(metadata)

            # Ensure metadata values are stored as valid types
            for meta in batch_metadata:
                for key, value in meta.items():
                    if isinstance(value, list):  
                        meta[key] = ", ".join(value)

            # Process in batches
            if len(batch_docs) >= batch_size:
                collection.add(ids=batch_ids, embeddings=batch_embeddings, documents=batch_docs, metadatas=batch_metadata)
                batch_docs, batch_ids, batch_embeddings, batch_metadata = [], [], [], []

        # Insert remaining documents
        if batch_docs:
            collection.add(ids=batch_ids, embeddings=batch_embeddings, documents=batch_docs, metadatas=batch_metadata)

        print(f"✅ Web article '{url}' stored as '{collection_name}' in ChromaDB!")

        return {"message": "Web article added successfully!", "document_id": document_id}
