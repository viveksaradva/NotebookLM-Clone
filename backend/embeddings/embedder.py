import nltk
from nltk.tokenize import sent_tokenize
from sentence_transformers import SentenceTransformer
from langchain_community.document_loaders import PyPDFLoader

# Ensure you have the required NLTK data
nltk.download("punkt")

class Embedder:
    def __init__(self, model_name="BAAI/bge-m3"):
        self.model = SentenceTransformer(model_name)

    def get_embedding(self, text):
        """Convert text into an embedding vector."""
        if not text.strip():  # Handle empty or whitespace-only strings
            return None
        return self.model.encode(text).tolist()

    def load_pdf(self, pdf_path, chunk_size=300, overlap=50):
        """
        Extract text from a PDF and chunk it into smaller parts for embedding.
        Returns a list of (chunk, embedding) tuples.
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

        return chunks  # Only return text chunks (embedding happens in ChromaDB)

        # chunks = []
        # start_idx = 0
        # while start_idx < len(sentences):
        #     chunk = " ".join(sentences[start_idx : start_idx + chunk_size])
        #     chunks.append(chunk)
        #     start_idx += chunk_size - overlap  # Move window forward with overlap

        # return chunks
