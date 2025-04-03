from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from sklearn.feature_extraction.text import TfidfVectorizer
from langchain_community.document_loaders import PyPDFLoader
from sentence_transformers import SentenceTransformer

class Embedder:
    def __init__(self, model_name="BAAI/bge-m3"):
        self.model = SentenceTransformer(model_name)
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

    # def get_embedding(self, text):
    #     """Convert text into an embedding vector."""
    #     return self.model.encode(text).tolist() if text.strip() else None
    def get_embedding(self, text):
        """Convert text into an embedding vector, ensuring valid input."""
        cleaned_text = text.strip()
        if len(cleaned_text) < 5:  # Ignore very short texts
            return None
        return self.model.encode(cleaned_text).tolist()


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
    
    def load_pdf(self, pdf_path):
        """
        Extracts text from a PDF and chunks it using RecursiveCharacterTextSplitter.
        Returns a list of dictionaries containing chunk text, embeddings, and metadata.
        """
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()

        # Combine extracted text
        raw_text = " ".join([doc.page_content for doc in docs])

        # Split text using LangChain's RecursiveCharacterTextSplitter
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
    
    def load_web_article(self, url):
        """
        Extracts text from a URL and chunks it using RecursiveCharacterTextSplitter.
        Returns both chunked data and the article's metadata.
        """
        loader = WebBaseLoader(url)  # Fixed incorrect loader name
        docs = loader.load()

        if not docs:
            return {"error": "Failed to load content from the URL."}

        raw_text = " ".join([doc.page_content for doc in docs])

        text_chunks = self.text_splitter.split_text(raw_text)

        # Extract metadata (from the first document)
        article_metadata = docs[0].metadata if docs else {}

        # Extract keywords for hybrid search
        keywords_list = self.extract_keywords(text_chunks)

        # Prepare structured output
        chunk_data = []
        for i, chunk_text in enumerate(text_chunks):
            chunk_data.append({
                "text": chunk_text,
                "embedding": self.get_embedding(chunk_text),
                "keywords": keywords_list[i]
            })

        return {
            "chunks": chunk_data,
            "metadata": article_metadata  # Returning metadata separately
        }
