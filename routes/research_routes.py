from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List
from pydantic import BaseModel
from src.research_handler import research_manager

router = APIRouter()

class ResearchQuery(BaseModel):
    query: str

class ResearchResponse(BaseModel):
    id: str
    user_id: str
    query: str
    status: str
    report_html: Optional[str] = None
    created_at: str
    updated_at: str

# Placeholder for user dependency
async def get_current_user():
    # In a real app, this would validate a token and return a user object
    return {"id": "test_user", "username": "testuser"}

@router.post("/research", response_model=ResearchResponse)
async def create_research_task(research_query: ResearchQuery, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    new_research = await research_manager.create_research(current_user["id"], research_query.query)
    background_tasks.add_task(research_manager.start_research_task, new_research["id"], new_research["query"])
    return new_research

@router.get("/research", response_model=List[ResearchResponse])
async def list_researches(current_user: dict = Depends(get_current_user)):
    return await research_manager.list_researches(current_user["id"])

@router.get("/research/{research_id}", response_model=ResearchResponse)
async def get_research_status(research_id: str, current_user: dict = Depends(get_current_user)):
    research = await research_manager.get_research(research_id)
    if not research or research["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Research not found")
    return research

@router.delete("/research/{research_id}", status_code=204)
async def delete_research_task(research_id: str, current_user: dict = Depends(get_current_user)):
    research = await research_manager.get_research(research_id)
    if not research or research["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Research not found")
    if not await research_manager.delete_research(research_id):
        raise HTTPException(status_code=500, detail="Failed to delete research")
    return
