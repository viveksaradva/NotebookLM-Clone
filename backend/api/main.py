from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import settings
from backend.api.routes import documents, chat, highlights, summaries, study_guides

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    debug=settings.DEBUG
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents.router, prefix=settings.API_PREFIX)
app.include_router(chat.router, prefix=settings.API_PREFIX)
app.include_router(highlights.router, prefix=settings.API_PREFIX)
app.include_router(summaries.router, prefix=settings.API_PREFIX)
app.include_router(study_guides.router, prefix=settings.API_PREFIX)

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": settings.APP_DESCRIPTION
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
