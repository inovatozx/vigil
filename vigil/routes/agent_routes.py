from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
from src.agent_runs import agent_run_manager
from src.agent_loop import AgentLoop, ProgressEmitter, LLMCore, ToolExecutor
from src.tool_implementations import tool_implementations

router = APIRouter()

class AgentRunRequest(BaseModel):
    initial_prompt: str

class AgentRunResponse(BaseModel):
    id: str
    user_id: str
    initial_prompt: str
    status: str
    current_step: int
    created_at: str
    updated_at: str

class AgentActionApproval(BaseModel):
    approved: bool

# Placeholder for user dependency
async def get_current_user():
    # In a real app, this would validate a token and return a user object
    return {"id": "test_user", "username": "testuser"}

@router.post("/agent/run", response_model=AgentRunResponse)
async def start_agent_run(run_request: AgentRunRequest, current_user: dict = Depends(get_current_user)):
    new_run = await agent_run_manager.create_run(current_user["id"], run_request.initial_prompt)

    # Initialize agent components (these would be properly injected in a larger app)
    llm_core = LLMCore() # Placeholder
    tool_executor = ToolExecutor(tool_implementations)
    progress_emitter = ProgressEmitter() # Placeholder for WebSocket/SSE

    agent_loop = AgentLoop(
        agent_run_id=new_run["id"],
        llm_core=llm_core,
        tool_executor=tool_executor,
        progress_emitter=progress_emitter
    )

    # Run the agent loop in the background
    # In a real application, this might be offloaded to a worker queue
    import asyncio
    asyncio.create_task(agent_loop.run(run_request.initial_prompt))

    return new_run

@router.get("/agent/runs", response_model=List[AgentRunResponse])
async def list_agent_runs(current_user: dict = Depends(get_current_user)):
    return await agent_run_manager.list_runs(current_user["id"])

@router.get("/agent/runs/{run_id}", response_model=AgentRunResponse)
async def get_agent_run_status(run_id: str, current_user: dict = Depends(get_current_user)):
    run = await agent_run_manager.get_run(run_id)
    if not run or run["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Agent run not found")
    return run

@router.post("/agent/runs/{run_id}/stop", response_model=AgentRunResponse)
async def stop_agent_run(run_id: str, current_user: dict = Depends(get_current_user)):
    run = await agent_run_manager.get_run(run_id)
    if not run or run["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Agent run not found")
    if not await agent_run_manager.stop_run(run_id):
        raise HTTPException(status_code=500, detail="Failed to stop agent run")
    return await agent_run_manager.get_run(run_id) # Return updated run status

@router.post("/agent/runs/{run_id}/approve", response_model=AgentRunResponse)
async def approve_agent_action(run_id: str, approval: AgentActionApproval, current_user: dict = Depends(get_current_user)):
    run = await agent_run_manager.get_run(run_id)
    if not run or run["user_id"] != current_user["id"]:
        raise HTTPException(status_code=404, detail="Agent run not found")
    if not run["pending_approval"]:
        raise HTTPException(status_code=400, detail="No pending action for approval")

    updated_run = await agent_run_manager.approve_action(run_id, approval.approved)
    if not updated_run:
        raise HTTPException(status_code=500, detail="Failed to process approval")
    return updated_run
