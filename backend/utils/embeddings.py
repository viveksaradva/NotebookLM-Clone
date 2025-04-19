from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
import os

class Embedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=10,
            stop_words="english"
        )
    
    def get_embedding(self, text: str) -> List[float]:
        """Generate embeddings for a text string."""
        return self.model.encode(text).tolist()
    
    def extract_keywords(self, texts: List[str], top_n: int = 5) -> List[List[str]]:
        """Extract keywords from a list of texts using TF-IDF."""
        # Fit the vectorizer on all texts
        self.tfidf_vectorizer.fit(texts)
        
        # Get feature names (words)
        feature_names = self.tfidf_vectorizer.get_feature_names_out()
        
        # Extract keywords for each text
        keywords_list = []
        for text in texts:
            # Transform the text to get TF-IDF scores
            tfidf_matrix = self.tfidf_vectorizer.transform([text])
            
            # Get indices of top N scores
            indices = tfidf_matrix.toarray()[0].argsort()[-top_n:][::-1]
            
            # Get the corresponding words
            keywords = [feature_names[i] for i in indices]
            keywords_list.append(keywords)
        
        return keywords_list
    
    def load_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Load and chunk a PDF file."""
        # Check if file exists
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Load PDF
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        
        # Combine extracted text
        raw_text = " ".join([doc.page_content for doc in docs])
        
        # Split text into chunks
        text_chunks = self.text_splitter.split_text(raw_text)
        
        # Extract keywords for hybrid search
        keywords_list = self.extract_keywords(text_chunks)
        
        # Prepare structured output
        chunk_data = []
        for i, chunk_text in enumerate(text_chunks):
            chunk_data.append({
                "text": chunk_text,
                "embedding": self.get_embedding(chunk_text),
                "keywords": keywords_list[i],
            })
        
        return chunk_data
    
    def load_web_article(self, url: str) -> Dict[str, Any]:
        """Load and chunk a web article."""
        # Load web article
        loader = WebBaseLoader(url)
        docs = loader.load()
        
        # Extract metadata
        metadata = {
            "url": url,
            "title": docs[0].metadata.get("title", ""),
            "description": docs[0].metadata.get("description", ""),
        }
        
        # Combine extracted text
        raw_text = " ".join([doc.page_content for doc in docs])
        
        # Split text into chunks
        text_chunks = self.text_splitter.split_text(raw_text)
        
        # Extract keywords for hybrid search
        keywords_list = self.extract_keywords(text_chunks)
        
        # Prepare structured output
        chunk_data = []
        for i, chunk_text in enumerate(text_chunks):
            chunk_data.append({
                "text": chunk_text,
                "embedding": self.get_embedding(chunk_text),
                "keywords": keywords_list[i],
            })
        
        return {
            "metadata": metadata,
            "chunks": chunk_data,
        }
