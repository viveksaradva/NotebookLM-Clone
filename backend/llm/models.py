import os
from together import Together
from groq import Groq
from dotenv import load_dotenv

# load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
together_client = Together(api_key=os.getenv("TOGETHER_API_KEY"))

# Groq
def get_groq_mistral_response(prompt: str) -> str:
    
    try:
        response = groq_client.chat.completions.create(
            model="mistral-saba-24b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=1,
            max_completion_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,    
        )
    except Exception as e:
        print(f"Groq Error: {e}")
        return "Error from Groq/Mistral API."

    return response.choices[0].message.content

# Together
def get_together_meta_llama_response(prompt: str) -> str:
    try:
        response = together_client.chat.completions.create(
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
        print(f"Error in LLM response: {e}")
        return "Sorry, I encountered an error while processing your request."

###################################

# Making the LangChain BaseChatModel wrapper
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from typing import List, Optional, Any
from together import Together
from dotenv import load_dotenv
import os

load_dotenv()

class TogetherChatModel(BaseChatModel):
    api_key: str = os.getenv("TOGETHER_API_KEY")
    model: str = "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free"

    @property
    def _llm_type(self) -> str:
        return "together-chat"

    def _convert_messages(self, message):
        if isinstance(message, HumanMessage):
            return {"role": "user", "content": message.content}
        elif isinstance(message, AIMessage):
            return {"role": "assistant", "content": message.content}
        elif isinstance(message, SystemMessage):
            return {"role": "system", "content": message.content}
        else:
            raise ValueError(f"Unsupported message type: {type(message)}")

    def _convert_output(self, content: str):
        return AIMessage(content=content.strip())

    def _generate(self, messages: List[Any], stop: Optional[List[str]] = None, **kwargs) -> ChatResult:
        together_msgs = [self._convert_messages(msg) for msg in messages]

        try:
            client = Together(api_key=self.api_key)

            res = client.chat.completions.create(
                model=self.model,
                messages=together_msgs,
                max_tokens=None,
                temperature=0.5,
                top_p=0.9,
                top_k=40,
                repetition_penalty=1.03,
                stop=["<|end_of_sentence|>"],
                stream=False
            )
            response_content = res.choices[0].message.content
            return ChatResult(generations=[ChatGeneration(message=self._convert_output(response_content))])
        except Exception as e:
            print(f"Error in LLM response: {e}")
            return ChatResult(generations=[ChatGeneration(message=AIMessage(content="⚠️ Error: LLM failed."))])
