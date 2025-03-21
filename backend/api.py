# import os
# import sys
# import uuid
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# from backend.vectordb.chroma_db import ChromaDBManager
# from backend.llm.meta_llama import ask_meta_llama_rag
# from fastapi import FastAPI, HTTPException, UploadFile, File
# from pydantic import BaseModel

# app = FastAPI()
# vectordb = ChromaDBManager()

# # Chat Memory: Stores conversations per session
# chat_memory = {}

# #################################
# # Doc retrieving and processing #
# #################################

# @app.post("/upload_pdf/")
# async def upload_pdf(file: UploadFile = File(...)):
#     """Uploads a PDF, assigns a document ID, extracts text, embeds it, and stores it in ChromaDB."""
#     document_id = str(uuid.uuid4())[:8]  # Generate a short unique document ID
#     file_path = f"./data/{document_id}_{file.filename}"

#     try:
#         with open(file_path, "wb") as buffer:
#             buffer.write(await file.read())

#         # Store the PDF in ChromaDB under its unique document ID
#         vectordb.add_pdf(file_path, document_id)

#         return {
#             "message": f"PDF '{file.filename}' uploaded successfully!",
#             "document_id": document_id
#         }
    
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


# class QueryRequest(BaseModel):
#     query: str
#     document_id: str = None
#     session_id: str

# class ResetChatRequest(BaseModel):
#     session_id: str


# #################
# # RAG operation #
# #################

# @app.post("/rag")
# def rag_query(request: QueryRequest):
#     """Handles retrieval-augmented generation (RAG). Supports querying a specific document."""
#     query = request.query
#     document_id = request.document_id  # If provided, only query this document
#     session_id = request.session_id

#     # Initialize session chat history if it doesn't exist
#     if session_id not in chat_memory:
#         chat_memory[session_id] = []

#     # Retrieve previous context
#     previous_conversations = "\n".join(chat_memory[session_id][-5:])  # Use last 5 exchanges

#     # Retrieve relevant documents
#     retrieved_docs = vectordb.query(query, document_id=document_id, top_k=3)
#     context = "\n".join(retrieved_docs) if retrieved_docs else "No relevant information found."

#     # Construct a conversational-aware prompt
#     full_prompt = (
#         f"Use the following conversation history and document context to answer the user's question.\n\n"
#         f"### Conversation History:\n{previous_conversations}\n\n"
#         f"### Document Context:\n{context}\n\n"
#         f"### User Query:\n{query}\n\n"
#         f"Provide a structured response."
#     )


#     print(f"📝 Received query: '{query}' for document_id: {document_id}") # For debugging

#     retrieved_docs = vectordb.query(query, document_id=document_id, top_k=3)

#     print(f"🔍 Retrieved Docs: {retrieved_docs}") # For debugging

#     if retrieved_docs and any(len(doc.strip()) > 10 for doc in retrieved_docs):
#         response = ask_meta_llama_rag(query)
#     else:
#         response = ask_meta_llama_rag(f"(No relevant docs found) {query}")

#     print(f"📝 Final Response: {response}")
#     # response = ask_meta_llama_rag(full_prompt)

#     chat_memory[session_id].append(f"User: {query}\nBot: {response}")
#     print(f"chat_memory for debugging: {chat_memory}")

#     return {
#         "query": query,
#         # "response": {
#         #     "summary": response.split("\n\n")[0] if response else "No response",
#         #     "detailed_response": response,
#         #     "format": "markdown"
#         # }
#         "response": response,
#         "session_id": session_id,
#         "chat_history": chat_memory[session_id]
#     }

# ##############
# # Chat reset #
# ##############
# @app.post("/reset_chat/")
# def reset_chat(request: ResetChatRequest):
#     """Clears chat history for a specific session."""
#     session_id = request.session_id
#     print(f"\n\nsession_id: {session_id}")
#     print(f"\n\nchat_memory: {chat_memory}")
#     if session_id in chat_memory:
#         chat_memory[session_id] = []
#         return {"message": f"Chat history for session '{session_id}' cleared."}
#     else:
#         return {"message": f"No chat history found for session '{session_id}'."}


# # Run the FastAPI server
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)


import os
import sys
import uuid
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.vectordb.chroma_db import ChromaDBManager
from backend.llm.meta_llama import ask_meta_llama_rag, check_document_relevance
from backend.utils.chat_memory import get_session_memory, reset_session_memory

app = FastAPI()
vectordb = ChromaDBManager()

###########################
# PDF Upload & Processing #
###########################
@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    document_id = str(uuid.uuid4())[:8]  
    file_path = f"./data/{document_id}_{file.filename}"

    try:
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        vectordb.add_pdf(file_path, document_id)

        indexed_docs = vectordb.get_documents(document_id)
        if not indexed_docs:
            raise HTTPException(status_code=500, detail="PDF indexing failed.")

        return {
            "message": f"PDF '{file.filename}' uploaded successfully!",
            "document_id": document_id,
            "indexed_documents": len(indexed_docs)  
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


################
# RAG Endpoint #
################
class QueryRequest(BaseModel):
    query: str
    document_id: str = None
    session_id: str

@app.post("/rag")
def rag_query(request: QueryRequest):
    """Handles retrieval-augmented generation (RAG) with conversational memory."""
    query = request.query
    document_id = request.document_id  # Optional: query specific document
    session_id = request.session_id

    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID is required")


    # Retrieve the session memory
    memory_instance = get_session_memory(session_id)
    previous_context = memory_instance.load_memory_variables({}).get("history", "")

    # Retrieve relevant documents from ChromaDB
    retrieved_docs = vectordb.query(query, document_id=document_id, top_k=5)
    filtered_docs = check_document_relevance(query, retrieved_docs)
    context = "\n".join(filtered_docs) if filtered_docs else "No relevant information found."

    # Construct a prompt that includes conversation history and document context.
    full_prompt = (
        f"Use the following conversation history and document context to answer the user's question.\n\n"
        f"### Conversation History:\n{previous_context}\n\n"
        f"### Document Context:\n{context}\n\n"
        f"### User Query:\n{query}\n\n"
        f"Provide a structured response in Markdown format."
    )

    # Generate response using your LLM function.
    response = ask_meta_llama_rag(full_prompt)

    # Update memory with the latest exchange.
    memory_instance.save_context({"input": query}, {"output": response})

    return {
        "query": query,
        "response": response,
        "session_id": session_id,
        "chat_history": memory_instance.load_memory_variables({}).get("history", "")
    }


# def summarize_chat_history(history):
#     return "\\n".join(history[-5:]) if len(history) > 10 else "\\n".join(history)

# @app.post("/rag")
# def rag_query(request: QueryRequest):
#     query = request.query
#     document_id = request.document_id
#     session_id = request.session_id

#     if session_id not in chat_memory:
#         chat_memory[session_id] = []

#     previous_conversations = summarize_chat_history(chat_memory[session_id])

#     retrieved_docs = vectordb.query(query, document_id=document_id, top_k=5)
#     filtered_docs = check_document_relevance(query, retrieved_docs)

#     context = "\\n".join(filtered_docs) if filtered_docs else "No relevant information found."

#     response = ask_meta_llama_rag(query, previous_conversations, context)
#     print(f"\nResponse: {response}")
#     chat_memory[session_id].append(f"User: {query}\\nBot: {response}")

#     return {
#         "query": query,
#         "response": response,
#         "session_id": session_id,
#         "chat_history": chat_memory[session_id]
#     }



##############
# Reset Chat #
##############
# class ResetChatRequest(BaseModel):
#     session_id: str

# @app.post("/reset_chat/")
# def reset_chat(request: ResetChatRequest):
#     session_id = request.session_id
#     if session_id in chat_memory:
#         chat_memory[session_id] = []
#         return {"message": f"Chat history for session '{session_id}' cleared."}
#     else:
#         return {"message": f"No chat history found for session '{session_id}'."}

class ResetChatRequest(BaseModel):
    session_id: str

@app.post("/reset_chat/")
def reset_chat(request: ResetChatRequest):
    session_id = request.session_id
    return reset_session_memory(session_id)


# Run FastAPI Server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
