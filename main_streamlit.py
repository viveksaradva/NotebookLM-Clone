import streamlit as st
import requests
from smart_highlight import smart_highlight
from semantic_summary import semantic_summary
from cross_referencing_in_notes import add_note_to_chroma, get_cross_referenced_notes

# --- Page Configuration ---
st.set_page_config(
    page_title="DocuMind",
    page_icon="🧠",
    layout="wide"
)

API_URL = "http://127.0.0.1:8000/auth"

# --- Initialize Session ---
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None

# --- Sidebar Navigation ---
with st.sidebar:
    st.markdown("""
        ## 🧠 DocuMind
        Unlock your AI-powered study space.
    """)
    if st.session_state.token:
        page = st.radio("🔧 Navigation", ["🏠 Dashboard", "🚪 Logout"])
    else:
        page = st.radio("👋 Welcome", ["📝 Register", "🔑 Login"])

# --- API Helpers ---
def api_register(username, email, password):
    return requests.post(f"{API_URL}/register", json={
        "username": username, "email": email, "password": password
    })

def api_login(username, password):
    return requests.post(f"{API_URL}/login", json={
        "username": username, "password": password
    })

def api_protected(token):
    return requests.get(f"{API_URL}/protected", headers={
        "Authorization": f"Bearer {token}"
    })

# --- Registration Page ---
if page == "📝 Register":
    st.header("📝 Create Your DocuMind Account")
    with st.form("register_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        register = st.form_submit_button("Register")

    if register:
        response = api_register(username, email, password)
        if response.status_code == 200:
            st.success("🎉 Registered successfully! You can now log in.")
            st.rerun()
        else:
            st.error(response.json().get("detail", "Registration failed."))

# --- Login Page ---
elif page == "🔑 Login":
    st.header("🔑 Log In to DocuMind")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login = st.form_submit_button("Login")

    if login:
        response = api_login(username, password)
        if response.status_code == 200:
            st.session_state.token = response.json().get("access_token")
            st.session_state.user = username
            st.success("✅ Login successful! Welcome aboard.")
            st.rerun()
        else:
            st.error("❌ Invalid credentials. Please try again.")

# --- Protected Dashboard ---
elif page == "🏠 Dashboard" and st.session_state.token:
    st.header(f"🎯 Welcome, {st.session_state.user}!")
    st.markdown("### Select a core functionality to explore:")

    feature = st.selectbox("Core Functionalities", [
        "📌 Smart Highlighting",
        "🧠 Semantic Summarization",
        "🏷️ Auto-Tagging",
        "🔗 Cross-Referencing",
        "📚 Study Guide Generator",
        "🎤 Voice-Based Learning (coming soon)",
        "🤖 RAG Chatbot"
    ])

    st.divider()

    if feature == "📌 Smart Highlighting":
        st.info("Highlight and annotate key sentences from your documents.")

        highlight_text = st.text_area(
            "Paste or write your highlighted sentence here:",
            placeholder="e.g. Reinforcement learning uses reward feedback to teach agents how to act."
        )

        if st.button("🔍 Analyze Highlight"):
            if not highlight_text.strip():
                st.warning("⚠️ Please enter a sentence to analyze.")
            else:
                with st.spinner("Analyzing with LLM..."):
                    result = smart_highlight(highlight_text)

                if "error" in result:
                    st.error(result["error"])
                    st.text(result["raw_output"])
                else:
                    st.success("✅ Highlight Analyzed!")
                    st.json(result)

    elif feature == "🧠 Semantic Summarization":
        st.info("Takes a list of highlighted notes and summarizes them into one polished study paragraph.")

        highlights_input = st.text_area(
            "Paste multiple highlighted sentences (one per line):",
            placeholder="e.g.\nReinforcement learning uses reward feedback to teach agents how to act.\nAI safety research focuses on alignment problems to ensure AI systems behave as intended."
        )

        if st.button("🧠 Generate Summary"):
            highlights = [line.strip() for line in highlights_input.strip().split("\n") if line.strip()]

            if not highlights:
                st.warning("⚠️ Please enter at least one highlighted sentence.")
            else:
                with st.spinner("Generating summary with LLM..."):
                    result = semantic_summary(highlights)

                if isinstance(result, dict) and "error" in result:
                    st.error(result["error"])
                    st.text(result["raw_output"])
                else:
                    st.success("✅ Semantic Summary Generated!")
                    st.json(result)

    elif feature == "🏷️ Auto-Tagging":
        st.info("Automatically detect topics, tasks, and custom entities.")
    
    elif feature == "🔗 Cross-Referencing":
        st.info("Find related notes via vector similarity in ChromaDB.")
        st.title("Note-Taking and Cross-Referencing App")

    # Feature selection for navigation
    feature = st.sidebar.radio("Choose a feature", ["📝 Add Note", "🔗 Cross-Referencing"])

    if feature == "📝 Add Note":
        st.subheader("Add your note")
        note_text = st.text_area("Enter your note here:", height=150)

        if st.button("Add Note"):
            if note_text.strip():
                add_note_to_chroma(note_text.strip())  # Add the note to ChromaDB
            else:
                st.warning("Please enter a valid note.")

    elif feature == "🔗 Cross-Referencing":
        st.info("Find related notes via vector similarity in ChromaDB.")
        
        query_text = st.text_input("Enter a query to find related notes:")

        if st.button("Get Cross-Referenced Notes"):
            if query_text.strip():
                results = get_cross_referenced_notes(query_text.strip())  # Query for cross-referenced notes
                
                if results:
                    st.subheader("Cross-Referenced Notes:")
                    for idx, doc in enumerate(results["documents"][0]):
                        st.write(f"Related Note {idx + 1}: {doc}")
                else:
                    st.warning("No cross-referenced notes found.")
            else:
                st.warning("Please enter a valid query.")
    elif feature == "📚 Study Guide Generator":
        st.info("Generate layered study guides: summary, concepts, FAQs, questions, and analogies.")
    elif feature == "🎤 Voice-Based Learning (coming soon)":
        st.warning("🚧 Voice-based interactive study mode is under development.")
    elif feature == "🤖 RAG Chatbot":
        st.info("Chat with your documents using Retrieval-Augmented Generation.")

# --- Logout ---
elif page == "🚪 Logout" and st.session_state.token:
    st.header("👋 Logout")
    if st.button("Confirm Logout"):
        st.session_state.token = None
        st.session_state.user = None
        st.success("✅ You have been logged out.")
        st.rerun()
