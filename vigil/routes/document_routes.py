from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime

router = APIRouter()

class DocumentCreate(BaseModel):
    title: str
    content: str
    tags: Optional[List[str]] = None

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None

class DocumentResponse(BaseModel):
    id: str
    user_id: str
    title: str
    content: str
    tags: Optional[List[str]] = None
    created_at: str
    updated_at: str

class DocumentAIEditRequest(BaseModel):
    prompt: str

# In-memory store for documents (replace with DB in real app)
documents_db: Dict[str, Dict[str, Any]] = {}

# Placeholder for user dependency
async def get_current_user():
    return {"id": "test_user", "username": "testuser"}

@router.post("/documents", response_model=DocumentResponse)
async def create_document(doc: DocumentCreate, current_user: dict = Depends(get_current_user)):
    doc_id = str(uuid4())
    new_doc = {
        "id": doc_id,
        "user_id": current_user["id"],
        "title": doc.title,
        "content": doc.content,
        "tags": doc.tags,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    documents_db[doc_id] = new_doc
    return new_doc

@router.get("/documents", response_model=List[DocumentResponse])
async def list_documents(current_user: dict = Depends(get_current_user)):
    return [doc for doc in documents_db.values() if doc["user_id"] == current_user["id"]]

@router.get("/documents/{doc_id}", response_model=DocumentResponse)
async def get_document(doc_id: str, current_user: dict = Depends(get_current_user)):
    doc = documents_db.get(doc_id)
    if not doc or doc["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.put("/documents/{doc_id}", response_model=DocumentResponse)
async def update_document(doc_id: str, doc_update: DocumentUpdate, current_user: dict = Depends(get_current_user)):
    doc = documents_db.get(doc_id)
    if not doc or doc["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Document not found")

    update_data = doc_update.model_dump(exclude_unset=True)
    doc.update(update_data)
    doc["updated_at"] = datetime.now().isoformat()
    return doc

@router.delete("/documents/{doc_id}", status_code=204)
async def delete_document(doc_id: str, current_user: dict = Depends(get_current_user)):
    doc = documents_db.get(doc_id)
    if not doc or doc["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Document not found")
    del documents_db[doc_id]
    return

@router.post("/documents/{doc_id}/ai", response_model=DocumentResponse)
async def ai_edit_document(doc_id: str, ai_edit_request: DocumentAIEditRequest, current_user: dict = Depends(get_current_user)):
    doc = documents_db.get(doc_id)
    if not doc or doc["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Document not found")

    # Placeholder for AI editing logic
    # In a real scenario, this would call an LLM to modify the document content
    original_content = doc["content"]
    edited_content = f"[AI Edited based on \'{ai_edit_request.prompt}\']\n\n{original_content}\n\n[End AI Edit]"

    doc["content"] = edited_content
    doc["updated_at"] = datetime.now().isoformat()
    return doc
