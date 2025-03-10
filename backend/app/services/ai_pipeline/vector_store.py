"""
vector_store.py - Handles storage and retrieval using ChromaDB.
"""

from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from typing import List

class VectorStore:
    """
    A class for storing and retrieving embeddings using ChromaDB.
    """
    def __init__(self, persist_dir: str = "./vector_store"):
        """
        Initializes ChromaDB vector store.

        Args:
            persist_dir (str): Directory for storing the database.
        """
        self.persist_dir = persist_dir
        self.embedding_model = HuggingFaceEmbeddings(model_name="BAAI/bge-large-en-v1.5") #BAAI/bge-large-en-v1.5
        self.vector_store = Chroma(persist_directory=persist_dir, embedding_function=self.embedding_model)

    def add_documents(self, documents: List[Document]):
        """
        Adds documents to the vector store.

        Args:
            documents (List[Document]): List of LangChain Document objects.
        """
        # self.vector_store.add_documents(documents)
        # Modify add_documents function to include metadata
        self.vector_store.add_documents(documents, metadatas=[{"source": doc.metadata.get("page", 0)} for doc in documents])


    def query(self, query_text: str, top_k: int = 5) -> List[str]:
        """
        Retrieves the most relevant documents based on the query.

        Args:
            query_text (str): The search query.
            top_k (int): Number of top results to retrieve.

        Returns:
            List[str]: Retrieved document content.
        """
        results = self.vector_store.similarity_search(query_text, k=top_k)
        return [doc.page_content for doc in results]