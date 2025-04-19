from backend.llm.models import get_groq_mistral_response
from backend.llm.prompts import semantic_summary_prompt
import json

def semantic_summary(highlights: list) -> dict:
    formatted_prompt = semantic_summary_prompt.format(highlights="\n".join(highlights))
    response = get_groq_mistral_response(formatted_prompt)

    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return {"error": "⚠️ Invalid JSON response from LLM.", "raw_output": response}
