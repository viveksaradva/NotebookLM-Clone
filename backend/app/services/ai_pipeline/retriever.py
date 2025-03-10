"""
retriever.py - Full AI pipeline for document processing, embedding, and retrieval.
"""
from langchain.schema import Document
from .document_processor import DocumentProcessor
from .embedder import Embedder
from .vector_store import VectorStore

class DocumentRetriever:
    """
    Handles document ingestion, embedding, and retrieval.
    """
    def __init__(self):
        """
        Initializes document processing, embedding, and vector store.
        """
        self.embedder = Embedder()
        self.vector_store = VectorStore()

    def process_and_store(self, file_path: str):
        """
        Loads, embeds, and stores a document.

        Args:
            file_path (str): Path to the document.
        """
        processor = DocumentProcessor(file_path)
        texts = processor.load_document()

        documents = [Document(page_content=text) for text in texts]
        self.vector_store.add_documents(documents)
        print(f"✅ {file_path} processed and stored!")

    def retrieve(self, query: str, top_k: int = 5):
        """
        Retrieves the most relevant document chunks.

        Args:
            query (str): User query.
            top_k (int): Number of results.

        Returns:
            List[str]: Retrieved text chunks.
        """
        results = self.vector_store.query(query, top_k)
        return results