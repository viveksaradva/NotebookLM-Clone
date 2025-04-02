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
    query = request.query
    document_id = request.document_id
    session_id = request.session_id

    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID is required")

    # Retrieve session memory
    memory_instance = get_session_memory(session_id)
    previous_context = memory_instance.load_memory_variables({}).get("history", "")

    # 🔥 Hybrid Retrieval: Vector Similarity + Keyword Matching
    retrieved_docs, retrieved_metadata = vectordb.hybrid_query(query, document_id=document_id, top_k=5) 
    
    # Extract content and metadata (TF-IDF keywords)
    filtered_docs = check_document_relevance(query, retrieved_docs)
    
    # Format metadata into context
    context = "\n".join([
        f"{doc}\n[Keywords: {', '.join(metadata.get('keywords', []))}]"  
        for doc, metadata in zip(retrieved_docs, retrieved_metadata)  
    ])
 
    # Construct prompt with conversation + document context
    full_prompt = (
        f"Use the following conversation history and document context to answer the user's question.\n\n"
        f"### Conversation History:\n{previous_context}\n\n"
        f"### Document Context:\n{context}\n\n"
        f"### User Query:\n{query}\n\n"
        f"Provide a structured response in Markdown format."
    )

    # Generate LLM response
    response = ask_meta_llama_rag(full_prompt)

    # Update chat memory
    memory_instance.save_context({"input": query}, {"output": response})

    return {
        "query": query,
        "response": response,
        "session_id": session_id,
        "chat_history": memory_instance.load_memory_variables({}).get("history", "")
    }


##############
# Reset Chat #
##############
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