from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from uuid import uuid4
from datetime import datetime

router = APIRouter()

class NoteCreate(BaseModel):
    title: str
    content: str
    tags: Optional[List[str]] = None

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None

class NoteResponse(BaseModel):
    id: str
    user_id: str
    title: str
    content: str
    tags: Optional[List[str]] = None
    created_at: str
    updated_at: str

# In-memory store for notes (replace with DB in real app)
notes_db: Dict[str, Dict[str, Any]] = {}

# Placeholder for user dependency
async def get_current_user():
    return {"id": "test_user", "username": "testuser"}

@router.post("/notes", response_model=NoteResponse)
async def create_note(note: NoteCreate, current_user: dict = Depends(get_current_user)):
    note_id = str(uuid4())
    new_note = {
        "id": note_id,
        "user_id": current_user["id"],
        "title": note.title,
        "content": note.content,
        "tags": note.tags,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    notes_db[note_id] = new_note
    return new_note

@router.get("/notes", response_model=List[NoteResponse])
async def list_notes(current_user: dict = Depends(get_current_user)):
    return [note for note in notes_db.values() if note["user_id"] == current_user["id"]]

@router.get("/notes/{note_id}", response_model=NoteResponse)
async def get_note(note_id: str, current_user: dict = Depends(get_current_user)):
    note = notes_db.get(note_id)
    if not note or note["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@router.put("/notes/{note_id}", response_model=NoteResponse)
async def update_note(note_id: str, note_update: NoteUpdate, current_user: dict = Depends(get_current_user)):
    note = notes_db.get(note_id)
    if not note or note["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Note not found")

    update_data = note_update.model_dump(exclude_unset=True)
    note.update(update_data)
    note["updated_at"] = datetime.now().isoformat()
    return note

@router.delete("/notes/{note_id}", status_code=204)
async def delete_note(note_id: str, current_user: dict = Depends(get_current_user)):
    note = notes_db.get(note_id)
    if not note or note["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Note not found")
    del notes_db[note_id]
    return
