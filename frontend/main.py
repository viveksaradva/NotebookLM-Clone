import streamlit as st
import requests
import json
import os
import uuid
from dotenv import load_dotenv
import redis

# Load environment variables
load_dotenv()

# API URL
API_URL = "http://127.0.0.1:8005/api/v1"

# Redis connection for session management
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(redis_url)

# Page configuration
st.set_page_config(
    page_title="DocuMind",
    page_icon="📚",
    layout="wide"
)

# Initialize session state
if "session_id" not in st.session_state:
    # Generate a unique session ID if not already present
    st.session_state.session_id = f"session_{uuid.uuid4().hex}"

if "current_document_id" not in st.session_state:
    st.session_state.current_document_id = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Add a flag to track if we need to process a query
if "process_query" not in st.session_state:
    st.session_state.process_query = False

# Add a placeholder for the current query
if "current_query" not in st.session_state:
    st.session_state.current_query = ""

# API helpers
def api_request(method, endpoint, data=None, files=None):
    """Make an API request."""
    url = f"{API_URL}{endpoint}"

    # Add session ID to all requests
    if "?" in endpoint:
        url += f"&session_id={st.session_state.session_id}"
    else:
        url += f"?session_id={st.session_state.session_id}"

    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            if files:
                response = requests.post(url, files=files)
            else:
                response = requests.post(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)

        if response.status_code >= 400:
            st.error(f"Error: {response.status_code} - {response.text}")
            return None

        return response.json()
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None

# Session management functions
def reset_session():
    """Reset the session."""
    # Clear Redis data for this session
    redis_client.delete(f"chat_session:{st.session_state.session_id}")

    # Reset session state
    st.session_state.current_document_id = None
    st.session_state.chat_history = []

# Document functions
def upload_pdf(file):
    """Upload a PDF document."""
    files = {"file": file}
    response = api_request("POST", "/documents/upload-pdf", files=files)

    if response:
        st.session_state.current_document_id = response["document_id"]
        return response

    return None

def add_web_article(url):
    """Add a web article."""
    # Send URL as a query parameter instead of in the request body
    import urllib.parse
    encoded_url = urllib.parse.quote(url)
    response = api_request("POST", f"/documents/add-web-article?url={encoded_url}")

    if response:
        st.session_state.current_document_id = response["document_id"]
        return response

    return None

def get_user_documents():
    """Get all documents."""
    return api_request("GET", "/documents")

# Chat functions
def create_chat_session(document_id):
    """Create a new chat session."""
    response = api_request("POST", f"/chat/create-session?document_id={document_id}")

    if response:
        # Store the session ID in Redis
        redis_client.set(f"chat_session:{st.session_state.session_id}", response["session_id"])
        return response

    return None

def query_document(query, document_id, session_id=None):
    """Query a document and get a response."""
    # Get session ID from Redis if not provided
    if not session_id:
        stored_session_id = redis_client.get(f"chat_session:{st.session_state.session_id}")
        if stored_session_id:
            session_id = stored_session_id.decode('utf-8')

    data = {
        "query": query,
        "document_id": document_id,
        "session_id": session_id
    }

    response = api_request("POST", "/chat/query", data)

    if response:
        if "session_id" in response and not redis_client.get(f"chat_session:{st.session_state.session_id}"):
            # Store the session ID in Redis if not already stored
            redis_client.set(f"chat_session:{st.session_state.session_id}", response["session_id"])

        if "chat_history" in response:
            # Filter out any messages with None values
            filtered_history = []
            for msg in response["chat_history"]:
                if isinstance(msg, dict):
                    if ("user" in msg and msg["user"] is not None) or ("bot" in msg and msg["bot"] is not None):
                        filtered_history.append(msg)
                else:
                    filtered_history.append(msg)

            st.session_state.chat_history = filtered_history

        return response

    return None

def reset_chat_session():
    """Reset a chat session."""
    # Get session ID from Redis
    stored_session_id = redis_client.get(f"chat_session:{st.session_state.session_id}")
    if stored_session_id:
        session_id = stored_session_id.decode('utf-8')
        response = api_request("POST", f"/chat/reset-session?session_id={session_id}")

        if response:
            st.session_state.chat_history = []
            return response

    return None

# Highlight functions
def create_smart_highlight(text):
    """Generate a smart highlight."""
    data = {"text": text}
    return api_request("POST", "/highlights/smart", data)

def create_highlight(text, document_id, highlight_type=None, sentence_type=None, note=None):
    """Create a new highlight."""
    data = {
        "text": text,
        "document_id": document_id,
        "highlight_type": highlight_type,
        "sentence_type": sentence_type,
        "note": note
    }

    return api_request("POST", "/highlights", data)

def get_document_highlights(document_id):
    """Get all highlights for a document."""
    return api_request("GET", f"/highlights/document/{document_id}")

# Summary functions
def generate_document_summary(document_id, max_length=500):
    """Generate a summary for a document."""
    data = {
        "document_id": document_id,
        "max_length": max_length
    }

    return api_request("POST", "/summaries/document", data)

def generate_semantic_summary(highlights):
    """Generate a semantic summary from highlights."""
    data = {"highlights": highlights}
    return api_request("POST", "/summaries/semantic", data)

# Study guide functions
def generate_study_guide(document_id, format="markdown"):
    """Generate a study guide for a document."""
    data = {
        "document_id": document_id,
        "format": format
    }

    return api_request("POST", "/study-guides/generate", data)

# Sidebar
with st.sidebar:
    st.title("📚 DocuMind")
    st.write(f"Session ID: {st.session_state.session_id[:8]}...")

    st.subheader("📄 Documents")

    # Upload document
    with st.expander("Upload Document", expanded=False):
        uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

        if uploaded_file:
            if st.button("Process PDF"):
                with st.spinner("Processing PDF..."):
                    result = upload_pdf(uploaded_file)

                    if result:
                        st.success(f"PDF uploaded! Document ID: {result['document_id']}")

    # Add web article
    with st.expander("Add Web Article", expanded=False):
        url = st.text_input("Web Article URL")

        if url:
            if st.button("Process URL"):
                with st.spinner("Processing URL..."):
                    result = add_web_article(url)

                    if result:
                        st.success(f"Web article added! Document ID: {result['document_id']}")

    # Document list
    st.subheader("My Documents")
    documents = get_user_documents()

    if documents:
        for doc in documents:
            if st.button(f"📄 {doc['title']}", key=f"doc_{doc['document_id']}"):
                st.session_state.current_document_id = doc['document_id']
                st.rerun()

    # Reset session
    if st.button("Reset Session"):
        reset_session()
        st.rerun()

# Main content
st.write(f"Debug - Current Document ID: {st.session_state.current_document_id}")

# Force update document ID if needed (temporary fix)
if st.session_state.current_document_id and st.session_state.current_document_id not in [doc['document_id'] for doc in documents if documents]:
    if documents:
        st.session_state.current_document_id = documents[0]['document_id']
        st.info(f"Updated document ID to: {st.session_state.current_document_id}")

if st.session_state.current_document_id:
    # Document tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Chat", "Highlights", "Summary", "Study Guide"])

    with tab1:
        st.header("💬 Chat with your Document")

        # Chat interface
        if "chat_history" in st.session_state and st.session_state.chat_history:
            # Create a container for the chat messages
            chat_container = st.container()

            with chat_container:
                for message in st.session_state.chat_history:
                    if hasattr(message, "content"):
                        if hasattr(message, "type") and message.type == "human":
                            st.markdown(f"**You:** {message.content}")
                        else:
                            st.markdown(f"**AI:** {message.content}")
                    elif isinstance(message, dict):
                        if "user" in message and message["user"] is not None:
                            st.markdown(f"**You:** {message['user']}")
                        if "bot" in message and message["bot"] is not None:
                            st.markdown(f"**AI:** {message['bot']}")

        # Define a callback function for the query submission
        def submit_query():
            if st.session_state.query_input and st.session_state.query_input != st.session_state.current_query:
                st.session_state.current_query = st.session_state.query_input
                st.session_state.process_query = True

        # Query input with callback
        query = st.text_input("Ask a question about your document:", key="query_input", on_change=submit_query)

        # Process the query if the flag is set
        if st.session_state.process_query:
            with st.spinner("Generating response..."):
                # Get session ID from Redis
                stored_session_id = redis_client.get(f"chat_session:{st.session_state.session_id}")
                session_id = None
                if stored_session_id:
                    session_id = stored_session_id.decode('utf-8')

                response = query_document(
                    query=st.session_state.current_query,
                    document_id=st.session_state.current_document_id,
                    session_id=session_id
                )

                # Reset the flag
                st.session_state.process_query = False

                # Force a rerun to update the chat display
                if response and "chat_history" in response and response["chat_history"]:
                    st.rerun()

        # Define a callback function for resetting the chat
        def reset_chat():
            st.session_state.process_query = False
            st.session_state.current_query = ""
            st.session_state.query_input = ""
            reset_chat_session()

        # Reset chat button
        if redis_client.get(f"chat_session:{st.session_state.session_id}"):
            st.button("Reset Chat", on_click=reset_chat)

    with tab2:
        st.header("✨ Smart Highlights")

        # Create highlight
        with st.expander("Create Highlight", expanded=True):
            highlight_text = st.text_area("Text to highlight:")

            if highlight_text:
                if st.button("Generate Smart Highlight"):
                    with st.spinner("Analyzing text..."):
                        smart_highlight = create_smart_highlight(highlight_text)

                        if smart_highlight:
                            st.success("Smart highlight generated!")
                            st.json(smart_highlight)

                            if st.button("Save Highlight"):
                                result = create_highlight(
                                    text=highlight_text,
                                    document_id=st.session_state.current_document_id,
                                    highlight_type=smart_highlight.get("highlight_type"),
                                    sentence_type=smart_highlight.get("sentence_type"),
                                    note=smart_highlight.get("short_note")
                                )

                                if result:
                                    st.success("Highlight saved!")
                                    st.rerun()

        # Display highlights
        st.subheader("Document Highlights")
        highlights = get_document_highlights(st.session_state.current_document_id)

        if highlights:
            for highlight in highlights:
                with st.expander(f"{highlight['highlight_type']}: {highlight['text'][:50]}...", expanded=False):
                    st.write(f"**Text:** {highlight['text']}")
                    st.write(f"**Type:** {highlight['highlight_type']}")
                    st.write(f"**Sentence Type:** {highlight['sentence_type']}")
                    st.write(f"**Note:** {highlight['note']}")
        else:
            st.info("No highlights found for this document.")

    with tab3:
        st.header("📝 Document Summary")

        if st.button("Generate Summary"):
            with st.spinner("Generating summary..."):
                summary = generate_document_summary(st.session_state.current_document_id)

                if summary:
                    st.success("Summary generated!")
                    st.markdown(summary["summary"])

    with tab4:
        st.header("📚 Study Guide")

        if st.button("Generate Study Guide"):
            with st.spinner("Generating study guide..."):
                study_guide = generate_study_guide(st.session_state.current_document_id)

                if study_guide:
                    st.success("Study guide generated!")

                    # Display study guide
                    st.markdown(study_guide["study_guide"])

                    # Display key concepts
                    with st.expander("Key Concepts", expanded=False):
                        for concept in study_guide["key_concepts"]:
                            st.markdown(f"- {concept}")

                    # Display review questions
                    with st.expander("Review Questions", expanded=False):
                        for i, question in enumerate(study_guide["review_questions"], 1):
                            st.markdown(f"{i}. {question}")
else:
    st.title("📚 DocuMind - AI-Powered Knowledge Management")
    st.write("Please select or upload a document from the sidebar to get started.")

    # Welcome message
    st.markdown("""
    ## Welcome to DocuMind!

    DocuMind is an AI-powered knowledge management system inspired by Google's NotebookLM.

    ### Features:
    - 📝 Upload and process documents
    - 💬 Chat with your documents using RAG
    - ✨ Create smart highlights with AI-powered analysis
    - 📚 Generate comprehensive study guides
    - 🧠 Create semantic summaries from your highlights

    Get started by uploading a document or adding a web article from the sidebar.
    """)
