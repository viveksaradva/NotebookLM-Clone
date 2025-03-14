import os
import uuid
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.vectordb.chroma_db import ChromaDBManager
from backend.llm.meta_llama import ask_meta_llama_rag
from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel

app = FastAPI()
vectordb = ChromaDBManager()

#################################
# Doc retrieving and processing #
#################################

@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    """Uploads a PDF, assigns a document ID, extracts text, embeds it, and stores it in ChromaDB."""
    document_id = str(uuid.uuid4())[:8]  # Generate a short unique document ID
    file_path = f"./data/{document_id}_{file.filename}"

    try:
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        # Store the PDF in ChromaDB under its unique document ID
        vectordb.add_pdf(file_path, document_id)

        return {
            "message": f"PDF '{file.filename}' uploaded successfully!",
            "document_id": document_id
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")


class QueryRequest(BaseModel):
    query: str
    document_id: str = None

#################
# RAG operation #
#################

@app.post("/rag")
def rag_query(request: QueryRequest):
    """Handles retrieval-augmented generation (RAG). Supports querying a specific document."""
    query = request.query
    document_id = request.document_id  # If provided, only query this document

    print(f"📝 Received query: '{query}' for document_id: {document_id}") # For debugging

    retrieved_docs = vectordb.query(query, document_id=document_id, top_k=3)

    print(f"🔍 Retrieved Docs: {retrieved_docs}") # For debugging

    if retrieved_docs and any(len(doc.strip()) > 10 for doc in retrieved_docs):
        response = ask_meta_llama_rag(query)
    else:
        response = ask_meta_llama_rag(f"(No relevant docs found) {query}")

    print(f"📝 Final Response: {response}")

    return {
        "query": query,
        "response": {
            "summary": response.split("\n\n")[0] if response else "No response",
            "detailed_response": response,
            "format": "markdown"
        }
    }


# Run the FastAPI server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


