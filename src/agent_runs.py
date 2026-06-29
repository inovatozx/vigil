from typing import Dict, List, Optional
from uuid import uuid4
from datetime import datetime

class AgentRunManager:
    def __init__(self):
        self.runs: Dict[str, Dict[str, Any]] = {}

    async def create_run(self, user_id: str, initial_prompt: str) -> Dict[str, Any]:
        run_id = str(uuid4())
        new_run = {
            "id": run_id,
            "user_id": user_id,
            "initial_prompt": initial_prompt,
            "status": "created",
            "current_step": 0,
            "history": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "approved_actions": [],
            "pending_approval": False,
        }
        self.runs[run_id] = new_run
        return new_run

    async def get_run(self, run_id: str) -> Optional[Dict[str, Any]]:
        return self.runs.get(run_id)

    async def list_runs(self, user_id: str) -> List[Dict[str, Any]]:
        return [run for run in self.runs.values() if run["user_id"] == user_id]

    async def update_run_status(self, run_id: str, status: str, current_step: int, history_entry: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        run = self.runs.get(run_id)
        if run:
            run["status"] = status
            run["current_step"] = current_step
            run["updated_at"] = datetime.now().isoformat()
            if history_entry:
                run["history"].append(history_entry)
            return run
        return None

    async def stop_run(self, run_id: str) -> bool:
        run = self.runs.get(run_id)
        if run:
            run["status"] = "stopped"
            run["updated_at"] = datetime.now().isoformat()
            return True
        return False

    async def request_approval(self, run_id: str, action: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        run = self.runs.get(run_id)
        if run:
            run["pending_approval"] = True
            run["action_to_approve"] = action
            run["updated_at"] = datetime.now().isoformat()
            return run
        return None

    async def approve_action(self, run_id: str, approved: bool) -> Optional[Dict[str, Any]]:
        run = self.runs.get(run_id)
        if run and run["pending_approval"]:
            run["pending_approval"] = False
            if approved:
                run["approved_actions"].append(run["action_to_approve"])
                run["status"] = "running" # Resume if approved
            else:
                run["status"] = "paused" # Stay paused if rejected
            run["action_to_approve"] = None
            run["updated_at"] = datetime.now().isoformat()
            return run
        return None


agent_run_manager = AgentRunManager() # Singleton instance
