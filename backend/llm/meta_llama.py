import os
import sys
from together import Together
from dotenv import dotenv_values
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.vectordb.chroma_db import ChromaDBManager
from backend.embeddings.embedder import Embedder

# Initialize the Together.AI client
TOGETHER_API_KEY = dotenv_values(".env").get("TOGETHER_API_KEY")
client = Together(api_key=TOGETHER_API_KEY)
vectordb = ChromaDBManager()
embedder = Embedder()

# For Cosin-similarity
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def check_document_relevance(query, retrieved_docs, min_similarity=0.4):
    """Filters documents based on cosine similarity with the query.
    
    Args:
        query (str): The user's query.
        retrieved_docs (dict or list): Output from ChromaDB.query():
            - If `document_id` was given: ChromaDB dict ({"documents": [...], ...}).
            - If no `document_id`: Flattened list of document texts.
        min_similarity (float): Minimum similarity threshold (default: 0.4).
    
    Returns:
        List[str]: Top relevant documents (or a fallback message if none found).
    """
    if not retrieved_docs:
        return ["No relevant documents found."]
    
    # Case 1: ChromaDB dictionary (when querying a specific document)
    if isinstance(retrieved_docs, dict) and "documents" in retrieved_docs:
        documents = retrieved_docs["documents"][0]  # Extract inner list
    # Case 2: Already a list (when querying all documents)
    elif isinstance(retrieved_docs, list):
        documents = retrieved_docs
    else:
        return ["Invalid document format."]
    
    # Compute query embedding
    query_vector = np.array(embedder.get_embedding(query)).reshape(1, -1)
    
    # Compute embeddings for all retrieved docs
    doc_vectors = np.array([embedder.get_embedding(doc) for doc in documents])
    
    if doc_vectors.ndim == 1:
        doc_vectors = doc_vectors.reshape(1, -1)
    
    # Compute cosine similarities
    similarities = cosine_similarity(query_vector, doc_vectors)[0]
    print(f"Similarities: {similarities}")
    
    # Pair each document with its similarity score and filter
    scored_docs = list(zip(documents, similarities))
    filtered_docs = [
        doc for doc, sim in sorted(scored_docs, key=lambda x: x[1], reverse=True)
        if sim >= min_similarity
    ]
    
    return filtered_docs[:5] if filtered_docs else ["No highly relevant documents found."]


def construct_prompt(query, context, previous_conversations=""):
    """Constructs an optimized prompt with improved table extraction."""
    full_prompt = (
        f"### Conversation History:\n{previous_conversations}\n\n"
        f"### Relevant Document Context:\n{context}\n\n"
        f"### User Query:\n{query}\n\n"
        f"Generate a **detailed and structured response** in Markdown format.\n\n"
        f"- If the document contains a table, **extract it completely** and format it as a **Markdown table**.\n"
        f"- Do **not** mention 'No table is present' if none exists.\n"
        f"- Ensure the response is **well-organized** and **informative**."
    )
    return full_prompt

def ask_meta_llama_rag(query, previous_conversations="", context=""):
    """Retrieve relevant documents and generate a structured response."""
    
    # Construct the full LLM prompt
    full_prompt = construct_prompt(query, context, previous_conversations)

    try:
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
            messages=[{"role": "user", "content": full_prompt}],
            max_tokens=None,
            temperature=0.7,
            top_p=0.9,
            top_k=50,
            repetition_penalty=1.05,
            stop=["<|end_of_sentence|>"],
            stream=False
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("Error:", e)
        return "Sorry, I encountered an error."


# Example usage
if __name__ == "__main__":
    print(ask_meta_llama_rag("What is the treatement for Chicken pox?"))
