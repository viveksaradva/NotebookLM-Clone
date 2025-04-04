from langsmith import traceable
from langchain_together import ChatTogether
from langchain.memory import ConversationBufferMemory

# Initialize the ChatTogether model
llm = ChatTogether(model="meta-llama/Llama-3-8B-Instruct")

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
