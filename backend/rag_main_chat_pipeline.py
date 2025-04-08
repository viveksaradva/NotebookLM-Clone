# from langchain.schema import AIMessage
# from langchain_core.runnables import Runnable
# from langchain.memory import ChatMessageHistory
# from langchain.schema import BaseMessage, HumanMessage, AIMessage
# from typing import Dict, List
# from backend.llm.prompts import construct_prompt
# from backend.llm.models import get_together_meta_llama_response
# from backend.vectordb.chroma_db import ChromaDBManager
# from backend.embeddings.embedder import Embedder

# db = ChromaDBManager()
# embedder = Embedder()

# class NotebookLMChain(Runnable):
#     def __init__(self, document_id: str):
#         self.document_id = document_id
#         self.history = ChatMessageHistory()  # keep this if managing memory internally

#     def invoke(self, inputs: Dict[str, List[BaseMessage]]) -> str:
#         messages = inputs["messages"]

#         # Load conversation into local history
#         self.history = ChatMessageHistory(messages=messages)

#         # Get latest user input
#         user_input = self.history.messages[-1].content if isinstance(self.history.messages[-1], HumanMessage) else ""

#         # Retrieve doc context
#         retrieved_docs = db.query(user_input, document_id=self.document_id, top_k=3)
#         context = "\n\n".join(retrieved_docs["documents"][0])

#         # Reconstruct previous conversation (excluding current user input)
#         previous_turns = self.history.messages[:-1] if isinstance(self.history.messages[-1], HumanMessage) else self.history.messages
#         previous_conversations = ""
#         for msg in previous_turns:
#             if isinstance(msg, HumanMessage):
#                 previous_conversations += f"User: {msg.content}\n"
#             elif isinstance(msg, AIMessage):
#                 previous_conversations += f"Assistant: {msg.content}\n"

#         # Prompt construction
#         final_prompt = construct_prompt(
#             query=user_input,
#             context=context,
#             previous_conversations=previous_conversations.strip()
#         )

#         # Get LLM response
#         response = get_together_meta_llama_response(final_prompt)

#         # Optional: Add response to memory
#         self.history.add_ai_message(response)

#         return response

# if __name__ == "__main__":
#     notebook_lm_chain = NotebookLMChain(document_id="f5c7da80")
#     response = notebook_lm_chain.invoke({"messages": [HumanMessage(content="What is this article about?")]})
#     print(f"Response: {response}")
#     print(f"History: {notebook_lm_chain.history.messages}")





from langchain_core.runnables import RunnableLambda, RunnableMap, RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory


# === Imports from my custom stack ===
from backend.llm.models import TogetherChatModel
from backend.vectordb.chroma_db import ChromaDBManager
from backend.llm.prompts import chat_prompt

# === Initialize components ===
llm = TogetherChatModel()
db = ChromaDBManager()

# === Retrieval logic (you can switch to db.hybrid_query if desired) ===
retriever = RunnableLambda(lambda inputs: db.query(inputs["query"], document_id=inputs.get("document_id")))

# === Chain with memory ===
def create_chain_with_memory(session_id: str):
    def get_memory(session_id: str) -> BaseChatMessageHistory:
        return RedisChatMessageHistory(
            session_id=session_id,
            url="redis://localhost:6379",
            ttl=3600 * 24 * 7  # 1 week expiration
        )

    rag_chain = (
        RunnableMap({
            "context": retriever,
            "query": lambda x: x["query"]
        })
        | chat_prompt
        | llm
    )

    return RunnableWithMessageHistory(
        rag_chain,
        get_memory,
        input_messages_key="query",
        history_messages_key="history",
    )

# === Example call ===
session_id = "user_123"
rag_with_memory = create_chain_with_memory(session_id)

response = rag_with_memory.invoke({
    "query": "Who created this article?",
    "document_id": "49b35b85"
})

print("AI Response:\n", response.content)
