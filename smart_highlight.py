from backend.llm.models import get_groq_mistral_response
from backend.llm.prompts import smart_highlight_prompt 
from typing import Dict
import json

def smart_highlight(text: str) -> Dict:
    prompt = smart_highlight_prompt.format(text=text)
    response = get_groq_mistral_response(prompt)
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return {"error": "⚠️ Invalid JSON response from LLM.", "raw_output": response}
