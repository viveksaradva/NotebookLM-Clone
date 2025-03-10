"""
phi2_rag.py - Implements RAG using Phi-2 as the LLM.
"""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from .retriever import DocumentRetriever

class Phi2RAG:
    """
    Implements retrieval-augmented generation (RAG) using Phi-2.
    """
    def __init__(self, model_name: str = "microsoft/phi-2"):
        """
        Loads the Phi-2 model and tokenizer.

        Args:
            model_name (str): The Hugging Face model ID.
        """
        self.device = "cpu"  # Phi-2 is optimized for CPU
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float32).to(self.device)
        self.retriever = DocumentRetriever()

    def generate_answer(self, query: str, top_k: int = 3) -> str:
        """
        Retrieves relevant documents and generates a response.

        Args:
            query (str): User query.
            top_k (int): Number of document chunks to retrieve.

        Returns:
            str: Generated response.
        """
        retrieved_docs = self.retriever.retrieve(query, top_k=top_k)
        context = "\n".join(retrieved_docs)

        prompt = f"Use the following document snippets to answer the question:\n\n{context}\n\nQuestion: {query}\n\nAnswer:"
        inputs = self.tokenizer(prompt, return_tensors="pt", padding=True, truncation=True, max_length=1024).to(self.device)

        with torch.no_grad():
            output = self.model.generate(**inputs, max_new_tokens=150)

        return self.tokenizer.decode(output[0], skip_special_tokens=True)
