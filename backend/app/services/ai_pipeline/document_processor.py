"""
document_processor.py - Handles document loading and text extraction.
Uses langchain_community for loading PDFs, text, and other formats.
"""

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List
import os

class DocumentProcessor:
    """
    A class for loading and extracting text from documents.
    """
    def __init__(self, file_path: str):
        """
        Initializes the document processor.

        Args:
            file_path (str): Path to the document.
        """
        self.file_path = file_path

    def load_document(self) -> List[str]:
        """
        Loads and extracts text from the document.

        Returns:
            List[str]: List of extracted text chunks.
        """
        ext = os.path.splitext(self.file_path)[1].lower()

        if ext == ".pdf":
            loader = PyPDFLoader(self.file_path)
        elif ext == ".txt":
            loader = TextLoader(self.file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_text(" ".join([doc.page_content for doc in docs]))
        return chunks