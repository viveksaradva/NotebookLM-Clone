# **DocuMind: AI-Powered Knowledge Management**

DocuMind is an advanced note-taking and document understanding system designed to help users efficiently summarize, organize, and retrieve key information from their documents. It leverages state-of-the-art AI models, hybrid search, and interactive UI components to enhance productivity and knowledge retention. Inspired by [Google NotebookLM](https://notebooklm.google/).

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
DocuMind/
├── backend/
│   ├── api/
│   │   ├── main.py                  # Main FastAPI application
│   │   └── routes/                  # API route handlers
│   ├── core/
│   │   ├── config.py                # Configuration settings
│   │   └── security.py              # Security utilities
│   ├── db/
│   │   ├── database.py              # Database connection
│   │   └── models.py                # SQLAlchemy models
│   ├── services/
│   │   ├── auth_service.py          # Authentication service
│   │   ├── document_service.py      # Document processing service
│   │   ├── vectordb_service.py      # Vector database service
│   │   ├── llm_service.py           # LLM integration service
│   │   ├── chat_service.py          # Chat service
│   │   ├── highlight_service.py     # Smart highlighting service
│   │   ├── summary_service.py       # Summarization service
│   │   └── study_guide_service.py   # Study guide generation service
│   ├── schemas/                     # Pydantic models
│   └── utils/
│       ├── embeddings.py            # Embedding utilities
│       └── chat_memory.py           # Chat memory utilities
├── frontend/
│   └── main.py                      # Streamlit application
├── data/                            # Data storage directory
├── docker/
│   ├── Dockerfile                   # API Dockerfile
│   ├── Dockerfile.frontend          # Frontend Dockerfile
│   └── docker-compose.yml           # Docker Compose configuration
├── requirements.txt                 # Python dependencies
├── .env                             # Environment variables
└── run.py                           # Script to run the application
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

### **1. Clone the Repository**
```bash
git clone https://github.com/yourusername/documind.git
cd documind
```

### **2. Set Up Environment Variables**
Copy the example environment file and update it with your settings:
```bash
cp docker/.env.example .env
# Edit .env with your configuration
```

### **3. Install Dependencies**
Ensure you have Python 3.10+ installed. Then, install the required dependencies:
```bash
pip install -r requirements.txt
```

### **4. Set Up the Database**
Run the PostgreSQL database using Docker:
```bash
docker-compose -f docker/docker-compose.yml up -d db
```

### **5. Initialize the Database**
Create the database tables:
```bash
python -c "from backend.db.database import engine; from backend.db.models import Base; Base.metadata.create_all(bind=engine)"
```

## **Running the Application**

### **1. Run with Docker Compose**
The easiest way to run the entire application:
```bash
docker-compose -f docker/docker-compose.yml up -d
```

### **2. Run Locally**
Alternatively, you can run the components separately:

**Backend API:**
```bash
python run.py --component backend
# Or: uvicorn backend.api.main:app --reload
```

**Frontend:**
```bash
python run.py --component frontend
# Or: streamlit run frontend/main.py
```

**Both Components:**
```bash
python run.py
```

## **API Documentation**

Once the backend is running, you can access the API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## **Testing**

To run the tests:

```bash
python -m pytest tests/
```

## **Features**

### **Document Management**
- Upload PDF documents
- Add web articles by URL
- View and manage your document library

### **Intelligent Chat**
- Chat with your documents using RAG (Retrieval-Augmented Generation)
- Persistent chat history
- Context-aware responses

### **Smart Highlighting**
- Highlight important text
- AI-powered classification of highlights
- Automatic note generation

### **Summarization**
- Generate document summaries
- Create semantic summaries from highlights
- Customizable summary length

### **Study Guides**
- Generate comprehensive study guides
- Extract key concepts
- Create review questions

## **Contributing**

Contributions are welcome! Please feel free to submit a Pull Request.

## **License**

This project is licensed under the MIT License - see the LICENSE file for details.
