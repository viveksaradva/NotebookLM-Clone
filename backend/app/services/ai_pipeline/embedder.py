"""
embedder.py - Converts text into embeddings using bge-large-en-v1.5.
"""

from langchain_community.embeddings import HuggingFaceEmbeddings
from typing import List

class Embedder:
    """
    A class for generating text embeddings using bge-large-en-v1.5.
    """

    def __init__(self, model_name: str = "BAAI/bge-large-en-v1.5"):
        """
        Initializes the embedding model.

        Args:
            model_name (str): Hugging Face model name.
        """
        self.embedder = HuggingFaceEmbeddings(model_name=model_name)

    def get_embedding(self, text: str) -> List[float]:
        """
        Converts text into an embedding vector.

        Args:
            text (str): The input text.

        Returns:
            List[float]: The embedding vector.
        """
        return self.embedder.embed_query(text)