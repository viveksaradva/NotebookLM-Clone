import sys
import os

# Add the backend directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from app.services.ai_pipeline.retriever import DocumentRetriever

# Initialize the pipeline
retriever = DocumentRetriever()

# Path to the uploaded PDF file
document_path = "backend/app/services/ai_pipeline/disease-handbook-complete.pdf"

# Step 1: Process and store the document
retriever.process_and_store(document_path)

# Step 2: Query the stored documents
query = "What are the symptoms of Chickenpox?"
results = retriever.retrieve(query, top_k=3)

# Step 3: Display the results
print("\n🔍 Retrieved Documents:")
for idx, result in enumerate(results, start=1):
    print(f"{idx}. {result}")
