from fastembed import TextEmbedding
from typing import List

class EmbeddingManager:
    def __init__(self):
        # Initialize FastEmbed with a default model
        # The model will be downloaded on first use if not present
        self.model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        embeddings: List[List[float]] = self.model.embed(texts)
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        embedding: List[List[float]] = self.model.embed([text])
        return embedding[0]
