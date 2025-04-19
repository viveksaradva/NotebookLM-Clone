from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    username: str
    email: str
    password: str

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/api/v1/test")
def test_api():
    return {"message": "API is working"}

@app.post("/api/v1/auth/register")
def register(user: User):
    return {
        "id": 1,
        "username": user.username,
        "email": user.email,
        "is_active": True,
        "created_at": "2023-07-01T00:00:00"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=9000)
