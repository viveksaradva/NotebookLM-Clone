import streamlit as st
import uuid
import os
from dotenv import load_dotenv
from backend.vectordb.chroma_db import ChromaDBManager
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.runnables import RunnableMap
from langchain_core.runnables.history import RunnableWithMessageHistory
from backend.llm.prompts import chat_prompt
from langchain_together import ChatTogether

load_dotenv()

# Initialize components
chroma_manager = ChromaDBManager(persist_dir="data/chroma_db")
redis_url = os.getenv("REDIS_URL")

def get_message_history(session_id: str):
    return RedisChatMessageHistory(session_id=session_id, url=redis_url)

llm = ChatTogether(
    model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
    temperature=0.5,
    top_p=0.9,
    together_api_key=os.getenv("TOGETHER_API_KEY")
)

rag_chain = (
    RunnableMap({
        "query": lambda x: x["query"],
        "context": lambda x: x["context"],
        "history": lambda x: x["history"]
    })
    | chat_prompt
    | llm
)

rag_with_memory = RunnableWithMessageHistory(
    rag_chain,
    get_message_history,
    input_messages_key="query",
    history_messages_key="history"
)

st.set_page_config(page_title="DocuMind 📘💬", layout="wide")
st.title("📘 DocuMind - Your Document Chatbot")

# Sidebar for Upload
with st.sidebar:
    st.header("📄 Upload your document")
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])
    if uploaded_file:
        document_id = str(uuid.uuid4())[:8]
        save_path = f"./data/{document_id}_{uploaded_file.name}"
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        chroma_manager.add_pdf(save_path, document_id)
        st.success(f"✅ Document uploaded! ID: `{document_id}`")

# Chat state
if "document_id" not in st.session_state:
    st.session_state.document_id = None

if uploaded_file:
    st.session_state.document_id = document_id

if st.session_state.document_id:
    session_id = f"user_{st.session_state.document_id}"
    st.subheader("💬 Chat with your document")

    for msg in st.session_state.get("chat_history", []):
        st.markdown(f"**You:** {msg['user']}")
        st.markdown(f"**AI:** {msg['bot']}")

    query = st.text_input("Ask your question:")

    if query:
        # Using hybrid_query instead of query
        retrieved_docs, retrieved_metadata = chroma_manager.hybrid_query(
            query_text=query,
            document_id=st.session_state.document_id,
            top_k=5
        )

        # Handle the different return format from hybrid_query
        flat_docs = retrieved_docs if retrieved_docs else []
        context = "\n\n".join(flat_docs) if flat_docs else "No relevant context found."

        response = rag_with_memory.invoke(
            {"query": query, "context": context},
            config={"configurable": {"session_id": session_id}}
        )

        user_message = query
        bot_reply = response.content

        # Save chat history
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        st.session_state.chat_history.append({"user": user_message, "bot": bot_reply})

        st.rerun()
else:
    st.info("Upload a PDF document to start chatting.")

