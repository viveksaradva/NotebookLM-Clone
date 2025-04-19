import uuid
from typing import Dict, Any, List, Optional

from backend.services.vectordb_service import VectorDBService
from backend.services.llm_service import LLMService
from backend.utils.chat_memory import get_session_memory, reset_session_memory
from backend.schemas.chat import ChatMessage

class ChatService:
    def __init__(self):
        self.vectordb_service = VectorDBService()
        self.llm_service = LLMService()

    def create_session(self, document_id: str) -> Dict[str, Any]:
        """Create a new chat session."""
        session_id = f"session_{uuid.uuid4().hex[:8]}"

        # Initialize memory
        get_session_memory(session_id)

        return {
            "session_id": session_id,
            "document_id": document_id,
            "message": "Chat session created successfully."
        }

    def process_query(self, query: str, document_id: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Process a query and generate a response."""
        # Create session if not provided
        if not session_id:
            session_data = self.create_session(document_id)
            session_id = session_data["session_id"]

        # Get memory
        memory_instance = get_session_memory(session_id)
        previous_context = memory_instance.load_memory_variables({}).get("history", [])

        if isinstance(previous_context, list):
            previous_context = "\n".join(
                [msg.content for msg in previous_context if hasattr(msg, "content")]
            )

        # Retrieve relevant documents
        retrieved_docs, retrieved_metadata = self.vectordb_service.hybrid_query(
            query_text=query,
            document_id=document_id,
            top_k=5
        )

        # Format context
        context = "\n".join([
            f"{doc}\n[Keywords: {', '.join(metadata.get('keywords', []))}]"
            for doc, metadata in zip(retrieved_docs, retrieved_metadata or [{}])
        ])

        # Generate response
        response = self.llm_service.generate_rag_response(
            query=query,
            context=context,
            previous_context=previous_context
        )

        # Update memory
        memory_instance.save_context({"input": query}, {"output": response})

        # Get chat history and convert to the expected format
        chat_history = memory_instance.load_memory_variables({}).get("history", [])
        formatted_history = []

        # Convert LangChain message objects to ChatMessage objects
        for message in chat_history:
            if hasattr(message, "content") and message.content:
                if hasattr(message, "type") and message.type == "human":
                    formatted_history.append(ChatMessage(user=message.content))
                else:
                    formatted_history.append(ChatMessage(bot=message.content))

        # Return response with properly formatted chat history
        return {
            "query": query,
            "response": response,
            "session_id": session_id,
            "chat_history": formatted_history
        }

    def reset_session(self, session_id: str) -> Dict[str, Any]:
        """Reset a chat session."""
        return reset_session_memory(session_id)
