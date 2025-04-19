from backend.vectordb.chroma_db import ChromaDBManager
import streamlit as st

# Initialize ChromaDB manager
chroma_manager = ChromaDBManager()

def add_note_to_chroma(note_text):
    """Encodes the note and adds it to ChromaDB under 'notes_collection'."""
    collection_name = "notes_collection"
    collection = chroma_manager.client.get_or_create_collection(name=collection_name)
    
    # Generate embedding for the note
    note_embedding = chroma_manager.embedder.get_embedding(note_text)
    
    if note_embedding:
        # Insert the note into the collection
        note_id = f"note_{hash(note_text)}"
        metadata = {"keywords": ", ".join(note_text.split())}
        collection.add(
            ids=[note_id],
            embeddings=[note_embedding],
            documents=[note_text],
            metadatas=[metadata]
        )
        st.success("Note added successfully!")
    else:
        st.error("Note is too short to add!")

def get_cross_referenced_notes(query_text):
    """Retrieve cross-referenced notes based on similarity to the query."""
    collection_name = "notes_collection"
    collection = chroma_manager.client.get_collection(collection_name)
    
    if collection.count() > 0:
        results = collection.query(query_embeddings=[chroma_manager.embedder.get_embedding(query_text)], n_results=5)
        return results
    else:
        st.warning("No notes found in the database.")
        return []