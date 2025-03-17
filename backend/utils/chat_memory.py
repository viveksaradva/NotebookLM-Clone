from langchain.memory import ConversationBufferWindowMemory

# In-memory storage for session memories
chat_memory = {}

def get_session_memory(session_id: str, k: int = 5):
    """
    Retrieve the memory instance for a given session.
    If it doesn't exist, create a new one with a window size k.
    """
    if session_id not in chat_memory:
        chat_memory[session_id] = ConversationBufferWindowMemory(k=k, return_messages=True)
    return chat_memory[session_id]

def reset_session_memory(session_id: str, k: int = 5):
    """
    Reset the conversation memory for a given session.
    """
    if session_id in chat_memory:
        chat_memory[session_id] = ConversationBufferWindowMemory(k=k, return_messages=True)
        return {"message": f"Chat history for session '{session_id}' cleared."}
    else:
        return {"message": f"No chat history found for session '{session_id}'."}
