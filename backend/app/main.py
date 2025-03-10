"""
main.py - FastAPI server for querying Phi-2 RAG.
"""

from fastapi import FastAPI
from .services.ai_pipeline.phi2_rag import Phi2RAG

app = FastAPI()
rag_model = Phi2RAG()

@app.get("/rag/")
def  get_rag_answer(query: str):
    """
    API Endpoint for RAG-based answering.

    Args:
        query (str): User question.

    Returns:
        dict: Answer generated using RAG + Phi-2.
    """
    answer = rag_model.generate_answer(query=query)
    return {"query": query, "answer": answer}