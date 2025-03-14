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

# def ask_meta_llama_rag(query, top_k=3):
#     """Retrieve relevant documents and generate a response."""
#     retrieved_docs = vectordb.query(query, top_k=top_k)

#     # Construct system prompt with retrieved context
#     context = "\n".join(retrieved_docs) if retrieved_docs else "No relevant information found."
#     full_prompt = (
#         f"Use the following document context to answer the query.\n"
#         f"Context:\n{context}\n\n"
#         f"User Query:\n{query}\n\n"
#         f"Provide a detailed and complete response."
#     )

#     try:
#         response = client.chat.completions.create(
#             model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
#             messages=[{"role": "user", "content": full_prompt}],
#             max_tokens=None,
#             temperature=0.7,
#             top_p=0.7,
#             top_k=50,
#             repetition_penalty=1.05,
#             stop=["<|end_of_sentence|>"],
#             stream=False
#         )

#         return response.choices[0].message.content

#     except Exception as e:
#         print("Error:", e)
#         return "Sorry, I encountered an error."

# For Cosin-similarity
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def check_document_relevance(query, documents):
    """Check document relevance based on cosine similarity with the query"""
    if not documents:
        return ["No relevant documents found."]
    
    query_vector = np.array(embedder.get_embedding(query)).reshape(1, -1)  # ✅ Convert to NumPy array
    doc_vectors = np.array([embedder.get_embedding(doc) for doc in documents])  # ✅ Convert to NumPy array

    if doc_vectors.ndim == 1:  # If there's only one document, reshape it
        doc_vectors = doc_vectors.reshape(1, -1)

    similarities = cosine_similarity(query_vector, doc_vectors)
    sorted_docs = [documents[i] for i in np.argsort(similarities[0], axis=0)[::-1]]  # Sort by similarity

    return sorted_docs[:3]  # Return top 3 most relevant documents

# Main RAG part
def ask_meta_llama_rag(query, top_k=3):
    """Retrieve relevant documents and generate a response."""
    retrieved_docs = vectordb.query(query, top_k=top_k)

    # Improve relevance checking and ensure content quality
    context = check_document_relevance(query, retrieved_docs)

    # Step 1: Check if the retrieved docs are actually relevant
    # if retrieved_docs and any(len(doc.strip()) > 10 for doc in retrieved_docs):
    #     context = "\n".join(retrieved_docs)
    # else:
    #     context = "No relevant information found in the document."

    # Step 2: Construct the system prompt
    # full_prompt = (
    #     f"Use the following document context to answer the query in Markdown format.\n"
    #     f"If the document contains a table, extract it completely without altering the format, otherwise no need to reponse like "There is no table present in the provided document context.".\n"
    #     f"Context:\n{context}\n\n"
    #     f"User Query:\n{query}\n\n"
    #     f"Provide a structured and detailed response in Markdown format."
    # )

    full_prompt = (
        f"Use the provided document context to answer the query in Markdown format.\n"
        f"If a table is present in the document, extract it in its entirety without modifying the format.\n"
        f"If no table exists, do not respond with statements like 'There is no table present in the provided document context.'\n"
        f"Context:\n{context}\n\n"
        f"User Query:\n{query}\n\n"
        f"Generate a well-structured and detailed response in Markdown format."
    )


    try:
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
            messages=[{"role": "user", "content": full_prompt}],
            max_tokens=None,  # Set a limit to prevent incomplete answers
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

