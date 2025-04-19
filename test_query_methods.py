from backend.vectordb.chroma_db import ChromaDBManager

# Initialize ChromaDB manager
chroma_manager = ChromaDBManager(persist_dir="data/chroma_db")

# List all available collections
print("\n===== Available Collections =====")
collection_names = chroma_manager.client.list_collections()
for collection_name in collection_names:
    print(f"Collection: {collection_name}")

# Use the first collection if available
document_id = None
if collection_names:
    document_id = collection_names[0].replace("doc_", "")
    print(f"\nUsing document_id: {document_id}")
else:
    print("\nNo collections found. Please upload a document first.")
    exit(1)

# Test query
query = "Summarize this article for me!"

print("\n===== Testing query method =====")
query_results = chroma_manager.query(query_text=query, document_id=document_id, top_k=5)
print(f"query results type: {type(query_results)}")
print(f"query results: {query_results}")

print("\n===== Testing hybrid_query method =====")
hybrid_results, hybrid_metadata = chroma_manager.hybrid_query(query_text=query, document_id=document_id, top_k=5)
print(f"hybrid_results type: {type(hybrid_results)}")
print(f"hybrid_results: {hybrid_results}")
print(f"hybrid_metadata: {hybrid_metadata}")
