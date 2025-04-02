from fastapi import FastAPI
from auth import routes

app = FastAPI()

app.include_router(routes.router, prefix="/auth", tags=["auth"])

print("done")