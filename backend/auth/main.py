from fastapi import FastAPI
from backend.auth import routes

app = FastAPI(
    title="DocuMind Auth API 🧠🔐",
    debug=True
    )

app.include_router(routes.router, prefix="/auth", tags=["auth"])