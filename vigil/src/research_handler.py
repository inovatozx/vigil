from typing import Dict, Any, Optional, List
from uuid import uuid4
from datetime import datetime
from src.deep_research import deep_research_engine

class ResearchManager:
    def __init__(self):
        self.researches: Dict[str, Dict[str, Any]] = {}

    async def create_research(self, user_id: str, query: str) -> Dict[str, Any]:
        research_id = str(uuid4())
        new_research = {
            "id": research_id,
            "user_id": user_id,
            "query": query,
            "status": "pending",
            "report_html": None,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        self.researches[research_id] = new_research
        return new_research

    async def get_research(self, research_id: str) -> Optional[Dict[str, Any]]:
        return self.researches.get(research_id)

    async def list_researches(self, user_id: str) -> List[Dict[str, Any]]:
        return [r for r in self.researches.values() if r["user_id"] == user_id]

    async def update_research_status(self, research_id: str, status: str, report_html: Optional[str] = None) -> Optional[Dict[str, Any]]:
        research = self.researches.get(research_id)
        if research:
            research["status"] = status
            if report_html:
                research["report_html"] = report_html
            research["updated_at"] = datetime.now().isoformat()
            return research
        return None

    async def delete_research(self, research_id: str) -> bool:
        if research_id in self.researches:
            del self.researches[research_id]
            return True
        return False

    async def start_research_task(self, research_id: str, query: str):
        research = await self.update_research_status(research_id, "running")
        if not research:
            print(f"Research {research_id} not found to start.")
            return

        try:
            result = await deep_research_engine.perform_research(query)
            await self.update_research_status(research_id, "completed", result["report_html"])
        except Exception as e:
            print(f"Error during deep research for {research_id}: {e}")
            await self.update_research_status(research_id, "failed")

research_manager = ResearchManager() # Singleton instance
