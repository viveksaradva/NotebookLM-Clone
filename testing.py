from fastapi import FastAPI
from pydantic import BaseModel
from study_guide import generate_study_guide

app = FastAPI()

class StudyGuideRequest(BaseModel):
    chunk: str

@app.post("/generate-study-guide")
async def generate_guide(request: StudyGuideRequest):
    output = generate_study_guide(request.chunk)
    return output
