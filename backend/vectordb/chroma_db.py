# import chromadb
# from chromadb.utils import embedding_functions
# import sys
# import os
# from tqdm import tqdm  # For progress bar

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# from backend.embeddings.embedder import Embedder

# class ChromaDBManager:
#     def __init__(self, collection_name="notebooklm_data", persist_dir="data/chroma_db"):
#         self.client = chromadb.PersistentClient(path=persist_dir)
#         self.embedder = Embedder()

#     def add_pdf(self, pdf_path, document_id):
#         """Extracts text from a PDF, chunks it, embeds it, and stores it under a unique document_id."""
#         collection_name = f"doc_{document_id}"  # Unique collection for each PDF
#         collection = self.client.get_or_create_collection(name=collection_name)

#         pdf_chunks = self.embedder.load_pdf(pdf_path)

#         batch_size = 16  # Adjust based on performance
#         batch_docs, batch_ids, batch_embeddings = [], [], []

#         print(f"📘 Processing {len(pdf_chunks)} chunks from {pdf_path} (ID: {document_id})...")

#         for i, chunk in tqdm(enumerate(pdf_chunks), total=len(pdf_chunks), desc="Embedding Chunks"):
#             doc_id = f"{document_id}_chunk_{i}"
            
#             # Skip if already exists
#             existing = collection.get(ids=[doc_id])
#             if existing and existing["ids"]:
#                 continue
            
#             batch_docs.append(chunk)
#             batch_ids.append(doc_id)
#             batch_embeddings.append(self.embedder.get_embedding(chunk))

#             # Process in batches
#             if len(batch_docs) >= batch_size:
#                 collection.add(ids=batch_ids, embeddings=batch_embeddings, documents=batch_docs)
#                 batch_docs, batch_ids, batch_embeddings = [], [], []

#         # Insert remaining documents
#         if batch_docs:
#             collection.add(ids=batch_ids, embeddings=batch_embeddings, documents=batch_docs)

#         # print("✅ PDF successfully processed and stored!")
#         print(f"✅ PDF '{pdf_path}' stored as '{collection_name}' in ChromaDB!")

#     # def query(self, query_text, document_id=None, top_k=3):
#     #     """Retrieve the top-k most similar documents for a query. Searches a specific document or all documents."""
#     #     query_embedding = self.embedder.get_embedding(query_text)

#     #     if document_id:
#     #         # Query a specific document collection
#     #         collection_name = f"doc_{document_id}"
#     #         collection = self.client.get_collection(collection_name)
#     #         results = collection.query(query_embeddings=[query_embedding], n_results=top_k)

#     #     else:
#     #         # Query across all available documents
#     #         results = []
#     #         collection_names = self.client.list_collections()  
#     #         # collection_names = [col.name for col in self.client.list_collections()]  # ✅ Extract collection names
            
#     #         for collection_name in collection_names:
#     #             collection = self.client.get_collection(collection_name)
#     #             res = collection.query(query_embeddings=[query_embedding], n_results=top_k)
#     #             if res and "documents" in res:
#     #                 results.extend(res["documents"][0])  # ✅ Merge results from all documents

#     #     return results if results else []


#     def query(self, query_text, document_id=None, top_k=3):
#         """Retrieve the top-k most similar documents for a query, filtered by document_id if provided."""
#         query_embedding = self.embedder.get_embedding(query_text)

#         if document_id:
#             collection_name = f"doc_{document_id}"
#             try:
#                 collection = self.client.get_collection(name=collection_name)
#                 available_docs = collection.count()
#                 if available_docs == 0:
#                     print(f"⚠️ No documents found in {collection_name}")
#                     return []

#                 results = collection.query(query_embeddings=[query_embedding], n_results=min(top_k, available_docs))
#                 return results["documents"][0] if results and "documents" in results else []
#             except Exception as e:
#                 print(f"❌ Error fetching collection '{collection_name}': {e}")
#                 return []
        
#         # Query across all documents if no specific document is given
#         results = []
#         collection_names = self.client.list_collections()
        
#         for name in collection_names:
#             collection = self.client.get_collection(name=name)
#             available_docs = collection.count()
#             res = collection.query(query_embeddings=[query_embedding], n_results=min(top_k, available_docs))
            
#             if res and "documents" in res:
#                 results.extend(res["documents"][0])

#         return results if results else []



import chromadb
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from backend.embeddings.embedder import Embedder
from tqdm import tqdm

class ChromaDBManager:
    def __init__(self, persist_dir="data/chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.embedder = Embedder()

    def add_pdf(self, pdf_path, document_id):
        """Extracts text from a PDF, chunks it, embeds it, and stores it under a unique document_id."""
        collection_name = f"doc_{document_id}"  # Unique collection for each PDF
        collection = self.client.get_or_create_collection(name=collection_name)

        # Extract and embed text
        pdf_chunks = self.embedder.load_pdf(pdf_path)

        batch_size = 16
        batch_docs, batch_ids, batch_embeddings = [], [], []

        print(f"📘 Processing {len(pdf_chunks)} chunks from {pdf_path} (ID: {document_id})...")

        for i, chunk in tqdm(enumerate(pdf_chunks), total=len(pdf_chunks), desc="Embedding Chunks"):
            doc_id = f"{document_id}_chunk_{i}"

            # Skip if already exists
            existing = collection.get(ids=[doc_id])
            if existing and existing["ids"]:
                continue

            batch_docs.append(chunk)
            batch_ids.append(doc_id)
            batch_embeddings.append(self.embedder.get_embedding(chunk))

            # Process in batches
            if len(batch_docs) >= batch_size:
                collection.add(ids=batch_ids, embeddings=batch_embeddings, documents=batch_docs)
                batch_docs, batch_ids, batch_embeddings = [], [], []

        # Insert remaining documents
        if batch_docs:
            collection.add(ids=batch_ids, embeddings=batch_embeddings, documents=batch_docs)

        print(f"✅ PDF '{pdf_path}' stored as '{collection_name}' in ChromaDB!")

    def query(self, query_text, document_id=None, top_k=3):
        """Retrieve the top-k most similar documents for a query. Supports querying a specific document."""
        query_embedding = self.embedder.get_embedding(query_text)

        if document_id:
            # Query a specific document collection
            collection_name = f"doc_{document_id}"
            collection = self.client.get_collection(collection_name)  # ✅ Explicitly get the collection

            available_chunks = collection.count()
            print(f"📚 Querying document '{document_id}' with {available_chunks} chunks available.")

            if available_chunks == 0:
                return ["No documents found."]


            results = collection.query(query_embeddings=[query_embedding], n_results=min(top_k, available_chunks)) 
        
        else:
            # Query across all document collections
            results = []
            collection_names = self.client.list_collections()  # ✅ Extract collection names
            for collection_name in collection_names:
                collection = self.client.get_collection(collection_name)  # ✅ Explicitly fetch collection
                available_chunks = collection.count()
                # res = collection.query(query_embeddings=[query_embedding], n_results=top_k)
                # if res and "documents" in res:
                #     results.extend(res["documents"][0])  # Merge results
                print(f"📚 Querying collection '{collection_name}' with {available_chunks} chunks available.")

                if available_chunks > 0:
                    res = collection.query(query_embeddings=[query_embedding], n_results=min(top_k, available_chunks))
                    if res and "documents" in res:
                        results.extend(res["documents"][0])


        return results if results else []
















# collection_names = self.client.list_collections()
