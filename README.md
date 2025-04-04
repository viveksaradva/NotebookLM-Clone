# **DocuMind: AI-Powered Knowledge Management**  

DocuMind is an advanced note-taking and document understanding system designed to help users efficiently summarize, organize, and retrieve key information from their documents. It leverages state-of-the-art AI models, hybrid search, and interactive UI components to enhance productivity and knowledge retention. Most of the reference is taken from [Google NotebookLM](https://notebooklm.google/).  

---

## **Key Features**  

### **1. Multi-Format Document Support**  
DocuMind can process various document formats, including plain text (`.txt`), Microsoft Word (`.docx`), and web articles.  
- Automatically chunks large documents into smaller, structured sections for better retrieval and summarization.  
- Supports efficient searching and categorization of document contents.  

### **2. Hybrid Search (Vector + Keyword)**  
The system integrates **semantic vector search** with **keyword-based search** to provide highly relevant retrieval results.  
- **Vector search**: Uses embeddings to retrieve conceptually similar text even if exact words do not match.  
- **Keyword-based search**: Retrieves content using traditional exact-term matching.  
- **Hybrid approach**: Combines both methods to enhance precision and recall.  

### **3. Smart Highlights & Custom Notes**  
Users can highlight sections of text and attach custom notes for future reference. This feature includes:  
- **Undo/Redo actions** for modifying highlights and notes.  
- **Rich text formatting** with support for:  
  - **Bold, italic, and headings** for structuring notes.  
  - **Numbered lists and bullet points** for organizing content.  
  - **Code blocks (`<>`)** for technical documentation.  
  - **Hyperlink support** to reference external resources.  

### **4. AI-Powered Semantic Summaries**  
DocuMind generates **context-aware summaries** tailored to user needs.  
- Uses **Large Language Models (LLMs)** to extract the most relevant insights.  
- Provides multiple summarization options, including **brief overviews** and **detailed study guides**.  

### **5. Study Guide Generator**  
Automatically generates structured study guides from documents.  
- Extracts **key topics, explanations, and Q&A-style insights** to facilitate learning.  
- Unlike Google’s NotebookLM, which merely combines excerpts, DocuMind **integrates and synthesizes** information for a more coherent output.  

### **6. Briefing Document Creator**  
Generates high-level briefings based on document content. The briefing documents include:  
- **Core themes and key ideas** extracted from the text.  
- **Chapter-wise breakdowns** summarizing different sections.  
- **Concise reports** designed for decision-makers who need quick insights.  

### **7. Conversational Memory & Multi-Turn Conversations**  
DocuMind enables **context-aware, multi-turn conversations** by integrating a memory mechanism.  
- Utilizes **LangGraph** to maintain conversation history.  
- Allows users to ask follow-up questions without losing context.  

### **8. Audio Interaction (Podcast-Style Conversations)**  
Transforms document discussions into an **interactive audio experience**.  
- The system generates **natural language discussions** from document content.  
- Future iterations will support **real-time user participation** in AI-generated conversations.  

---

## **Project Structure**  

```
NotebookLM-Clone
 ├── backend
 │   ├── app.py                # FastAPI backend
 │   ├── auth.py               # User authentication (JWT-based)
 │   ├── retrieval.py          # Hybrid search and document retrieval
 │   ├── summarization.py      # AI-powered summarization and study guides
 │   ├── embeddings.py         # SentenceTransformer-based embeddings
 │   ├── topic_modeling.py     # BERTopic for document categorization
 │   ├── metadata_extraction.py# Metadata parsing and enrichment
 ├── frontend
 │   ├── ui.py                 # Streamlit/Gradio-based UI
 │   ├── interaction.py        # Conversational memory & user interaction
 │   ├── highlights.py         # Smart highlight & custom note handling
 ├── data
 │   ├── sample_notes.txt      # Sample input notes for testing
 ├── requirements.txt          # Dependencies
 ├── docker-compose.yml        # PostgreSQL setup with Docker
 ├── README.md                 # Project documentation
```

---

## **Tested Functionalities**  

- **Custom Notes (Smart Highlights)**: Users can highlight and annotate text with formatting options.  
- **Semantic Summaries (LLM-powered)**: AI-generated document summaries tailored for quick reference.  
- **Study Guide Generator**: Automatically creates structured learning materials from documents.  
- **Briefing Document Creator**: Generates high-level summaries and key insights from documents.  
- **Conversational Memory with LangGraph**: Multi-turn conversations with contextual awareness.  
- **Multi-Turn QA for Document Retrieval**: Users can ask follow-up questions with improved contextual relevance.  

---

## **Installation and Setup**  

### **1. Install Dependencies**  
Ensure you have Python 3.9+ installed. Then, install the required dependencies using:  
```bash
pip install -r requirements.txt
```

### **2. Run the Backend**  
Start the FastAPI backend server:  
```bash
uvicorn backend.api:app --reload
```

### **3. Start the Frontend(yet to implement)**  
Launch the Streamlit-based UI:  
```bash
streamlit run frontend/ui.py
```
