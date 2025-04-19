# DocuMind Project Structure

```
NotebookLM-Clone/
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py                  # Main FastAPI application
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py              # Authentication routes
│   │   │   ├── documents.py         # Document upload/retrieval routes
│   │   │   ├── chat.py              # RAG chat routes
│   │   │   ├── highlights.py        # Smart highlighting routes
│   │   │   ├── summaries.py         # Summarization routes
│   │   │   └── study_guides.py      # Study guide generation routes
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                # Configuration settings
│   │   ├── security.py              # Security utilities
│   │   └── exceptions.py            # Custom exceptions
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py              # Database connection
│   │   ├── models.py                # SQLAlchemy models
│   │   └── repositories/
│   │       ├── __init__.py
│   │       ├── users.py             # User repository
│   │       └── documents.py         # Document repository
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py          # Authentication service
│   │   ├── document_service.py      # Document processing service
│   │   ├── vectordb_service.py      # Vector database service
│   │   ├── llm_service.py           # LLM integration service
│   │   ├── chat_service.py          # Chat service
│   │   ├── highlight_service.py     # Smart highlighting service
│   │   ├── summary_service.py       # Summarization service
│   │   └── study_guide_service.py   # Study guide generation service
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py                  # Auth-related schemas
│   │   ├── documents.py             # Document-related schemas
│   │   ├── chat.py                  # Chat-related schemas
│   │   ├── highlights.py            # Highlight-related schemas
│   │   ├── summaries.py             # Summary-related schemas
│   │   └── study_guides.py          # Study guide-related schemas
│   └── utils/
│       ├── __init__.py
│       ├── embeddings.py            # Embedding utilities
│       ├── text_processing.py       # Text processing utilities
│       └── chat_memory.py           # Chat memory utilities
├── frontend/
│   ├── __init__.py
│   ├── main.py                      # Main Streamlit application
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── auth.py                  # Authentication pages
│   │   ├── chat.py                  # Chat interface
│   │   ├── highlights.py            # Smart highlighting interface
│   │   ├── summaries.py             # Summarization interface
│   │   └── study_guides.py          # Study guide interface
│   ├── components/
│   │   ├── __init__.py
│   │   ├── sidebar.py               # Sidebar component
│   │   ├── document_uploader.py     # Document uploader component
│   │   └── chat_interface.py        # Chat interface component
│   └── utils/
│       ├── __init__.py
│       ├── api.py                   # API client
│       └── session.py               # Session management
├── data/
│   ├── .gitkeep                     # Placeholder for data directory
│   └── chroma_db/                   # ChromaDB storage (gitignored)
├── tests/
│   ├── __init__.py
│   ├── conftest.py                  # Test configuration
│   ├── backend/
│   │   ├── __init__.py
│   │   ├── test_auth.py             # Auth tests
│   │   ├── test_documents.py        # Document tests
│   │   ├── test_chat.py             # Chat tests
│   │   ├── test_highlights.py       # Highlight tests
│   │   ├── test_summaries.py        # Summary tests
│   │   └── test_study_guides.py     # Study guide tests
│   └── frontend/
│       ├── __init__.py
│       └── test_pages.py            # Frontend page tests
├── docker/
│   ├── Dockerfile                   # Application Dockerfile
│   ├── docker-compose.yml           # Docker Compose configuration
│   └── .env.example                 # Example environment variables
├── .env                             # Environment variables (gitignored)
├── .gitignore                       # Git ignore file
├── README.md                        # Project documentation
├── requirements.txt                 # Python dependencies
└── run.py                           # Script to run the application
```
