import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.embeddings.embedder import Embedder
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class QueryRewriter:
    def __init__(self):
        self.embedder = Embedder()

    def rewrite_query(self, query):
        """Rewrites a user query into a more detailed and structured format."""

        query_embedding = self.embedder.get_embedding(query)

        # Define sample refined query structures (we can expand this dynamically later)
        templates = [
            f"Provide a structured explanation about: {query}",
            f"Explain in detail: {query}",
            f"List key points regarding: {query}",
            f"Retrieve relevant information about: {query}",
            f"Expand on the topic: {query}",
        ]

        # Embed all rewritten queries
        template_embeddings = [self.embedder.get_embedding(t) for t in templates]

        # Find the most similar refined query to the original
        similarities = cosine_similarity([query_embedding], template_embeddings)[0]
        best_rewritten_query = templates[np.argmax(similarities)]  # Select best-matching reformulated query

        return best_rewritten_query