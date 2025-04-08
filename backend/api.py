import os
import sys
import uuid
import logging
from pydantic import BaseModel
from langsmith import traceable
from fastapi import FastAPI, HTTPException, UploadFile, File

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.vectordb.chroma_db import ChromaDBManager
from backend.utils.chat_memory import get_session_memory, reset_session_memory
from backend.llm.prompts import construct_prompt
from backend.llm.models import get_together_meta_llama_response

app = FastAPI()
vectordb = ChromaDBManager()
logger = logging.getLogger("uvicorn")

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

@traceable(run_type="chain")  
@app.post("/rag")
def rag_query(request: QueryRequest):
    query = request.query
    document_id = request.document_id
    session_id = request.session_id

    if not session_id:
        raise HTTPException(status_code=400, detail="Session ID is required")

    # Retrieve session memory
    memory_instance = get_session_memory(session_id)
    previous_context = memory_instance.load_memory_variables({}).get("history", [])
    if isinstance(previous_context, list):
        previous_context = "\n".join(
            [msg.content for msg in previous_context if hasattr(msg, "content")]
        )

    # 🔥 Hybrid Retrieval: Vector Similarity + Keyword Matching
    retrieved_docs, retrieved_metadata = vectordb.hybrid_query(query, document_id=document_id, top_k=5) 
    
    
    # Format metadata into context
    context = "\n".join([
        f"{doc}\n[Keywords: {', '.join(metadata.get('keywords', []))}]"  
        for doc, metadata in zip(retrieved_docs, retrieved_metadata or [{}])  
    ])
 

    # Generate LLM response
    full_prompt = construct_prompt(query, context, previous_context)
    response = get_together_meta_llama_response(full_prompt)
    logger.info(f"[Session {session_id}] LLM Response:\n{response}")

    # Update chat memory
    memory_instance.save_context({"input": query}, {"output": response})

    if not retrieved_docs:
        return {
            "query": query,
            "response": "No relevant documents found for this query.",
            "session_id": session_id,
            "chat_history": memory_instance.load_memory_variables({}).get("history", "")
        }

    return {
        "query": query,
        "response": response,
        "session_id": session_id,
        "chat_history": memory_instance.load_memory_variables({}).get("history", "")
    }
########################################################
class WebArticleRequest(BaseModel):
    url: str

@app.post("/upload_web_article/")
def upload_web_article(request: WebArticleRequest):
    document_id = str(uuid.uuid4())[:8]  # Generate unique ID for the web article
    
    result = vectordb.add_web_article(request.url, document_id)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result
#################################################################



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