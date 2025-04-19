from langsmith import traceable
from langchain.memory import ConversationBufferMemory
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, AIMessage
from typing import List, Dict, Any, Optional

# Create a mock LLM for development/testing
class MockChatModel(BaseChatModel):
    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        from langchain_core.outputs import ChatGeneration, ChatResult
        response = "This is a mock response for testing purposes."
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=response))])

    async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs):
        from langchain_core.outputs import ChatGeneration, ChatResult
        response = "This is a mock async response for testing purposes."
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=response))])

    @property
    def _llm_type(self) -> str:
        return "mock_chat_model"

# Initialize the mock model
llm = MockChatModel()

# In-memory storage for session memories
chat_memory = {}

@traceable(name="memory")
def get_session_memory(session_id: str):
    """
    Retrieve the memory instance for a given session.
    If it doesn't exist, create a new one.
    """
    if session_id not in chat_memory:
        chat_memory[session_id] = ConversationBufferMemory(return_messages=True)
    return chat_memory[session_id]

@traceable(name="memory")
def reset_session_memory(session_id: str):
    """
    Reset the conversation memory for a given session.
    """
    if session_id in chat_memory:
        chat_memory[session_id] = ConversationBufferMemory(return_messages=True)
        return {"message": f"Chat history for session '{session_id}' cleared."}
    else:
        return {"message": f"No chat history found for session '{session_id}'."}

@traceable(name="memory")
def store_chat_memory(session_id: str, user_message: str, ai_response: str):
    """
    Store user and AI responses in memory while ensuring session persistence.
    """
    memory = get_session_memory(session_id)
    memory.save_context({"input": user_message}, {"output": ai_response})
