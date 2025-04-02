import nltk
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from langchain_community.document_loaders import PyPDFLoader
from sentence_transformers import SentenceTransformer

class Embedder:
    def __init__(self, model_name="BAAI/bge-m3"):
        self.model = SentenceTransformer(model_name)
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)

    def get_embedding(self, text):
        """Convert text into an embedding vector."""
        return self.model.encode(text).tolist() if text.strip() else None
    
    def extract_keywords(self, chunks):
        """Extracts top TF-IDF keywords for each chunk."""
        tfidf_matrix = self.vectorizer.fit_transform(chunks)
        feature_names = self.vectorizer.get_feature_names_out()
        keywords_per_chunk = []
        
        for row in tfidf_matrix:
            top_indices = row.toarray().flatten().argsort()[-5:][::-1]  # Top 5 keywords
            keywords = [feature_names[i] for i in top_indices]
            keywords_per_chunk.append(keywords)
        
        return keywords_per_chunk
    
    def load_pdf(self, pdf_path, chunk_size=300, overlap=50):
        """
        Extract text from a PDF and chunk it into smaller parts for embedding.
        Returns a list of dictionaries containing chunk text, embeddings, and metadata.
        """
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        
        raw_text = " ".join([doc.page_content for doc in docs])

        # Split text into sentences
        sentences = sent_tokenize(raw_text)
        
        # Create overlapping chunks
        chunks, chunk = [], []
        for sentence in sentences:
            chunk.append(sentence)
            if sum(len(s) for s in chunk) >= chunk_size:
                chunks.append(" ".join(chunk))
                chunk = []
        if chunk:
            chunks.append(" ".join(chunk))
        
        # Extract keywords for hybrid search
        keywords_list = self.extract_keywords(chunks)
        
        # Prepare structured output
        chunk_data = []
        for i, chunk_text in enumerate(chunks):
            chunk_data.append({
                "text": chunk_text,
                "embedding": self.get_embedding(chunk_text),
                "keywords": keywords_list[i],
            })
        
        return chunk_data