from sentence_transformers import SentenceTransformer
from langchain_community.document_loaders import PyPDFLoader

class Embedder:
    def __init__(self, model_name="BAAI/bge-m3"):
        self.model = SentenceTransformer(model_name)

    def get_embedding(self, text):
        return self.model.encode(text).tolist()

    def load_pdf(self, pdf_path):
        """Extract text from a PDF using PyPDFLoader."""
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        return [doc.page_content for doc in docs]  # Extract text from each page
