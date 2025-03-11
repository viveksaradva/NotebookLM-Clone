# import os
# from together import Together

# # Initialize the Together.AI client
# client = Together(api_key=os.getenv("TOGETHER_API_KEY"))

# def ask_meta_llama(prompt):
#     try:
#         response = client.chat.completions.create(
#             model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",  # Correct model
#             messages=[{"role": "user", "content": prompt}],
#             max_tokens=256,
#             temperature=0.7,
#             top_p=0.7,
#             top_k=50,
#             repetition_penalty=1,
#             stop=["<|end_of_sentence|>"],
#             stream=False  # Set to False for normal response handling
#         )

#         # Extract response text
#         raw_text = response.choices[0].message.content

#         return raw_text

#     except Exception as e:
#         print("Error:", e)
#         return None

# # Example usage
# print(ask_meta_llama("What is the capital of Japan?"))

import os
import sys
from together import Together
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.vectordb.chroma_db import ChromaDBManager

# Initialize the Together.AI client
client = Together(api_key=os.getenv("TOGETHER_API_KEY"))
vectordb = ChromaDBManager()

def ask_meta_llama_rag(query, top_k=3):
    """Retrieve relevant documents and generate a response."""
    retrieved_docs = vectordb.query(query, top_k=top_k)

    # Construct system prompt with retrieved context
    context = "\n".join(retrieved_docs) if retrieved_docs else "No relevant information found."
    full_prompt = f"Context:\n{context}\n\nUser Query:\n{query}\n\nAnswer:"

    try:
        response = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
            messages=[{"role": "user", "content": full_prompt}],
            max_tokens=None,
            temperature=0.7,
            top_p=0.7,
            top_k=50,
            repetition_penalty=1.05,
            stop=["<|end_of_sentence|>"],
            stream=False
        )

        return response.choices[0].message.content

    except Exception as e:
        print("Error:", e)
        return "Sorry, I encountered an error."

# Example usage
if __name__ == "__main__":
    print(ask_meta_llama_rag("What is the treatement for Chicken pox?"))

