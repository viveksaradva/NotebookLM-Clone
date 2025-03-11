import chromadb
from chromadb.utils import embedding_functions
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.embeddings.embedder import Embedder

class ChromaDBManager:
    def __init__(self, collection_name="notebooklm_data", persist_dir="../../data/chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_dir)  # Persistent storage
        self.collection = self.client.get_or_create_collection(name=collection_name)
        self.embedder = Embedder()

    def add_text(self, text, doc_id):
        """Embed and store a single text chunk."""
        embedding = self.embedder.get_embedding(text)
        self.collection.add(ids=[doc_id], embeddings=[embedding], documents=[text])

    def add_pdf(self, pdf_path):
        """Extract text from a PDF, chunk it, and store in ChromaDB."""
        pdf_texts = self.embedder.load_pdf(pdf_path)
        for i, text in enumerate(pdf_texts):
            doc_id = f"{pdf_path}_page_{i}"
            self.add_text(text, doc_id)

    def query(self, query_text, top_k=3):
        """Retrieve the top-k most similar documents for a query."""
        query_embedding = self.embedder.get_embedding(query_text)
        results = self.collection.query(query_embeddings=[query_embedding], n_results=top_k)
        return results["documents"][0] if results and "documents" in results else []

# Example usage
if __name__ == "__main__":
    db = ChromaDBManager()

    # Store a PDF
    db.add_pdf("../../data/disease-handbook-complete.pdf")

    # Query
    print(db.query("What are the symptoms of Chicken pox?"))
