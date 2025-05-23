import os
from typing import Dict, Any, List, Optional
import json

from together import Together
from groq import Groq
from langchain_together import ChatTogether
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.outputs import ChatGeneration, ChatResult

from backend.core.config import settings
from backend.llm.prompts import (
    construct_prompt,
    chat_prompt,
    smart_highlight_prompt,
    semantic_summary_prompt
)

class LLMService:
    def __init__(self):
        # Initialize API clients
        self.together_client = Together(api_key=settings.TOGETHER_API_KEY)
        self.groq_client = Groq(api_key=settings.GROQ_API_KEY)

        # Initialize LangChain models
        self.together_chat = ChatTogether(
            model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
            temperature=0.5,
            top_p=0.9,
            together_api_key=settings.TOGETHER_API_KEY
        )

    def get_together_response(self, prompt: str) -> str:
        """Get a response from Together AI's Llama model."""
        try:
            response = self.together_client.chat.completions.create(
                model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=None,
                temperature=0.5,
                top_p=0.9,
                top_k=40,
                repetition_penalty=1.03,
                stop=["<|end_of_sentence|>"],
                stream=False
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error in Together LLM response: {e}")
            return "Sorry, I encountered an error while processing your request."

    def get_groq_response(self, prompt: str) -> str:
        """Get a response from Groq's Mistral model."""
        try:
            response = self.groq_client.chat.completions.create(
                model="mistral-saba-24b",
                messages=[{"role": "user", "content": prompt}],
                temperature=1,
                max_completion_tokens=1024,
                top_p=1,
                stream=False,
                stop=None,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error in Groq LLM response: {e}")
            return "Sorry, I encountered an error while processing your request."

    def generate_rag_response(self, query: str, context: str, previous_context: str = "") -> str:
        """Generate a RAG response using the Together AI model."""
        full_prompt = construct_prompt(query, context, previous_context)
        return self.get_together_response(full_prompt)

    def generate_smart_highlight(self, text: str) -> Dict[str, Any]:
        """Generate a smart highlight using the Groq model."""
        prompt = smart_highlight_prompt.format(text=text)
        response = self.get_groq_response(prompt)

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "highlight_type": "Unknown",
                "sentence_type": "Unknown",
                "short_note": "Failed to parse response"
            }

    def generate_semantic_summary(self, highlights: List[str]) -> Dict[str, Any]:
        """Generate a semantic summary using the Groq model."""
        formatted_prompt = semantic_summary_prompt.format(highlights="\n".join(highlights))
        response = self.get_groq_response(formatted_prompt)

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "compressed_study_memory": "Failed to generate summary"
            }

    def generate_study_guide(self, document_chunks: List[str]) -> Dict[str, Any]:
        """Generate a study guide using the Together AI model."""
        # Combine chunks into a single document, but limit to avoid token limits
        max_chunks = min(3, len(document_chunks))  # Limit to 3 chunks to avoid token limits
        document_text = "\n\n".join(document_chunks[:max_chunks])

        # Further limit text to avoid token limits
        document_text = document_text[:3000]  # Limit to 3000 characters

        # Create prompt
        prompt = f"""
        You are an expert educator and study guide creator. Create a concise study guide based on this document excerpt:

        {document_text}

        Include:
        1. A brief summary
        2. Key concepts
        3. Review questions

        Format in Markdown with clear sections.
        """

        # Generate study guide
        study_guide = self.get_together_response(prompt)

        # Extract key concepts and review questions with shorter prompts
        # Limit text to avoid token limits
        limited_text = document_text[:2000]  # Further limit for key concepts/questions
        key_concepts_prompt = f"""
        Based on this document excerpt, list 5 key concepts as a JSON array of strings:

        {limited_text}

        Return ONLY a valid JSON array of strings, nothing else.
        """

        review_questions_prompt = f"""
        Based on this document excerpt, create 5 review questions as a JSON array of strings:

        {limited_text}

        Return ONLY a valid JSON array of strings, nothing else.
        """

        # Get key concepts and review questions
        key_concepts_response = self.get_together_response(key_concepts_prompt)
        review_questions_response = self.get_together_response(review_questions_prompt)

        # Parse responses
        try:
            key_concepts = json.loads(key_concepts_response)
        except json.JSONDecodeError:
            try:
                # Try to extract JSON from the response if it contains other text
                import re
                json_match = re.search(r'\[.*\]', key_concepts_response, re.DOTALL)
                if json_match:
                    key_concepts = json.loads(json_match.group(0))
                else:
                    key_concepts = ["Failed to extract key concepts"]
            except:
                key_concepts = ["Failed to extract key concepts"]

        try:
            review_questions = json.loads(review_questions_response)
        except json.JSONDecodeError:
            try:
                # Try to extract JSON from the response if it contains other text
                import re
                json_match = re.search(r'\[.*\]', review_questions_response, re.DOTALL)
                if json_match:
                    review_questions = json.loads(json_match.group(0))
                else:
                    review_questions = ["Failed to extract review questions"]
            except:
                review_questions = ["Failed to extract review questions"]

        return {
            "study_guide": study_guide,
            "key_concepts": key_concepts,
            "review_questions": review_questions
        }
