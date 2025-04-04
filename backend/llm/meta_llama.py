import os
import sys
import numpy as np
from together import Together
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity

# Ensure correct module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.vectordb.chroma_db import ChromaDBManager
from backend.embeddings.embedder import Embedder

# Load environment variables from .env file
load_dotenv()

# Initialize the Together.AI client
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
USER_AGENT = os.getenv("USER_AGENT")
if not TOGETHER_API_KEY:
    raise ValueError("TOGETHER_API_KEY is missing or not loaded correctly!")

client = Together(api_key=TOGETHER_API_KEY)
vectordb = ChromaDBManager()
embedder = Embedder()

# Cache embeddings to avoid redundant computation
embedding_cache = {}

def get_embedding_cached(text):
    """Retrieve embedding from cache or compute if missing."""
    if text not in embedding_cache:
        embedding_cache[text] = np.array(embedder.get_embedding(text))
    return embedding_cache[text]

def check_document_relevance(query, retrieved_docs, min_similarity=0.4):
    """Filters documents based on cosine similarity with the query."""
    if not retrieved_docs:
        return ["No relevant documents found."]
    
    if isinstance(retrieved_docs, dict) and "documents" in retrieved_docs:
        documents = retrieved_docs["documents"][0]
    elif isinstance(retrieved_docs, list):
        documents = retrieved_docs
    else:
        return ["Invalid document format."]
    
    # Compute query embedding
    query_vector = get_embedding_cached(query).reshape(1, -1)
    
    # Compute document embeddings
    doc_vectors = np.vstack([get_embedding_cached(doc) for doc in documents])
    
    # Compute cosine similarities
    similarities = cosine_similarity(query_vector, doc_vectors)[0]
    
    # Pair documents with similarity scores and sort
    scored_docs = sorted(zip(documents, similarities), key=lambda x: x[1], reverse=True)
    
    # Apply threshold filtering
    filtered_docs = [doc for doc, sim in scored_docs if sim >= min_similarity]

    return filtered_docs[:5] if filtered_docs else ["No highly relevant documents found."]

def construct_prompt(query, context, previous_conversations=""):
    """
    Constructs a highly optimized and structured prompt for Llama 3.3, ensuring maximum efficiency
    in document-based reasoning, response depth, and clarity. The prompt integrates conversation
    history, a cleaned and refined document context, and explicit instructions for generating
    Markdown-formatted, structured responses.
    """
    return (
        "You are a seasoned Document QA Expert and knowledgeable researcher. Your role is to carefully study and interpret the document context provided, " 
        "and answer the user's query with nuanced insights and a deep understanding of the material. " 
        "When formulating your response, consider all aspects of the content—its themes, data, structure, and any subtle nuances—without imposing a rigid structure such as always including 'Summary', 'Key Features', 'Benefits', or 'Conclusion' sections unless they naturally emerge from the document itself. " 
        "\n\nGuidelines:\n"
        "1. **Contextual Adaptation:** Tailor your response based solely on the document context and the conversation history. Your answer should be organically structured to best reflect the content's unique characteristics and the query's specific focus.\n"
        "2. **Expert Insight:** Explain complex ideas clearly and provide detailed, thoughtful analysis. Think like a human expert who synthesizes information rather than a mechanical system that outputs preset sections.\n"
        "3. **Conversational Tone:** Maintain a professional yet engaging and conversational tone. Avoid a static, template-driven response. Let your natural voice guide the structure of the answer.\n"
        "4. **Evidence-Based Reasoning:** Draw on the provided document details and explicitly reference key points where relevant. Your answer should help the user understand not just what the document says, but why those points matter.\n"
        "5. **Flexibility:** Adjust your style, tone, and structure dynamically based on the nature of the document. If the document is narrative, be descriptive; if it is technical, be precise; if it contains tables or data, interpret and integrate that information seamlessly.\n"
        "\n"
        f"### Conversation History:\n{previous_conversations}\n\n"
        f"### Relevant Document Context:\n{context}\n\n"
        f"### User Query:\n{query}\n\n"
        "Now, generate an insightful, comprehensive, and contextually adaptive response to the user query that reflects your expert understanding of the document. Do not impose any fixed section headers unless they are a natural part of the analysis."
    )
 

def ask_meta_llama_rag(query, previous_conversations="", context=""):
    """Retrieve relevant documents and generate a structured response."""
    full_prompt = construct_prompt(query, context, previous_conversations)

    try:
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
            messages=[{"role": "user", "content": full_prompt}],
            max_tokens=None,
            temperature=0.5,
            top_p=0.9,
            top_k=40,
            repetition_penalty=1.03,
            stop=["<|end_of_sentence|>"],
            stream=False
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Error in LLM response: {e}")
        return "Sorry, I encountered an error while processing your request."

# Example usage
if __name__ == "__main__":
    print(ask_meta_llama_rag("What is the treatement for Chicken pox?"))
