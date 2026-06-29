from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from src.task_scheduler import task_scheduler

router = APIRouter()

class TaskCreate(BaseModel):
    name: str
    cron_expression: str
    agent_run_params: Dict[str, Any] = {}

class TaskUpdate(BaseModel):
    name: Optional[str] = None
    cron_expression: Optional[str] = None
    agent_run_params: Optional[Dict[str, Any]] = None

class TaskResponse(BaseModel):
    id: str
    user_id: str
    name: str
    cron_expression: str
    agent_run_params: Dict[str, Any]
    status: str
    created_at: str
    next_run_at: str

# Placeholder for user dependency
async def get_current_user():
    return {"id": "test_user", "username": "testuser"}

@router.post("/tasks", response_model=TaskResponse)
async def create_task(task: TaskCreate, current_user: dict = Depends(get_current_user)):
    new_task = await task_scheduler.schedule_task(
        user_id=current_user["id"],
        name=task.name,
        cron_expression=task.cron_expression,
        agent_run_params=task.agent_run_params
    )
    return new_task

@router.get("/tasks", response_model=List[TaskResponse])
async def list_tasks(current_user: dict = Depends(get_current_user)):
    return await task_scheduler.list_tasks(current_user["id"])

@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, current_user: dict = Depends(get_current_user)):
    task = await task_scheduler.get_task(task_id)
    if not task or task["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.delete("/tasks/{task_id}", status_code=204)
async def delete_task(task_id: str, current_user: dict = Depends(get_current_user)):
    task = await task_scheduler.get_task(task_id)
    if not task or task["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Task not found")
    if not await task_scheduler.cancel_task(task_id):
        raise HTTPException(status_code=500, detail="Failed to cancel task")
    return

# Note: Update functionality for scheduled tasks can be complex if the task is already running.
# For simplicity, we'll omit a direct PUT for cron_expression/agent_run_params for now,
# suggesting cancellation and re-creation for changes to scheduling logic.
# A simple update for 'name' could be added if needed.
