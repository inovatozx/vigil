from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime
from src.rag_manager import rag_manager

router = APIRouter()

class MemoryCreate(BaseModel):
    content: str
    metadata: Optional[Dict[str, Any]] = None

class MemoryResponse(BaseModel):
    id: str
    user_id: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: str
    updated_at: str

class MemorySearchQuery(BaseModel):
    query: str
    top_k: int = 5

class MemorySearchResult(BaseModel):
    type: str
    id: str
    content: str
    score: float

# In-memory store for memories (replace with DB in real app)
memories_db: Dict[str, Dict[str, Any]] = {}

# Placeholder for user dependency
async def get_current_user():
    return {"id": "test_user", "username": "testuser"}

@router.post("/memory", response_model=MemoryResponse)
async def create_memory(memory: MemoryCreate, current_user: dict = Depends(get_current_user)):
    memory_id = str(uuid4())
    new_memory = {
        "id": memory_id,
        "user_id": current_user["id"],
        "content": memory.content,
        "metadata": memory.metadata,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    memories_db[memory_id] = new_memory
    await rag_manager.add_memory(memory_id, memory.content, memory.metadata)
    return new_memory

@router.get("/memory", response_model=List[MemoryResponse])
async def list_memories(current_user: dict = Depends(get_current_user)):
    return [mem for mem in memories_db.values() if mem["user_id"] == current_user["id"]]

@router.get("/memory/{memory_id}", response_model=MemoryResponse)
async def get_memory(memory_id: str, current_user: dict = Depends(get_current_user)):
    memory = memories_db.get(memory_id)
    if not memory or memory["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Memory not found")
    return memory

@router.delete("/memory/{memory_id}", status_code=204)
async def delete_memory(memory_id: str, current_user: dict = Depends(get_current_user)):
    memory = memories_db.get(memory_id)
    if not memory or memory["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Memory not found")
    del memories_db[memory_id]
    # In a real app, also remove from RAG manager/vector DB
    return

@router.post("/memory/search", response_model=List[MemorySearchResult])
async def search_memories(search_query: MemorySearchQuery, current_user: dict = Depends(get_current_user)):
    # In a real app, filter by user_id in RAG manager
    results = await rag_manager.search_semantic(search_query.query, search_query.top_k)
    return results
