import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Any

from core.config import get_settings
from core.constants import CHROMA_DATA_PATH

settings = get_settings()

class ChromaVectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=CHROMA_DATA_PATH)
        # Using a default embedding function for now, will integrate FastEmbed later
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        self.collection = self.client.get_or_create_collection(
            name="vigil_memories",
            embedding_function=self.embedding_function
        )

    def add_memory(self, id: str, content: str, metadata: Optional[Dict] = None):
        self.collection.add(
            documents=[content],
            metadatas=[metadata if metadata else {}],
            ids=[id]
        )

    def delete_memory(self, id: str):
        self.collection.delete(ids=[id])

    def search(self, query_text: str, user_id: int, n_results: int = 5) -> List[Dict]:
        # Filter by user_id if metadata is properly set during add_memory
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results,
            # where={"user_id": user_id} # Uncomment if user_id is added to metadata
        )
        # Format results to be consistent with what MemoryManager expects
        formatted_results = []
        if results and results["ids"]:
            for i in range(len(results["ids"][0])):
                formatted_results.append({
                    "id": results["ids"][0][i],
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i]
                })
        return formatted_results
