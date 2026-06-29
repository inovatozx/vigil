import asyncio
from typing import Dict, Any, List, Optional
from uuid import uuid4
from datetime import datetime
import croniter

class TaskScheduler:
    def __init__(self):
        self.scheduled_tasks: Dict[str, Dict[str, Any]] = {}
        self._task_runners: Dict[str, asyncio.Task] = {}

    async def _run_task_agent(self, task_id: str, agent_run_params: Dict[str, Any]):
        """
        Simulates running an agent for a scheduled task.
        In a real implementation, this would trigger an agent run.
        """
        print(f"[TaskScheduler] Running agent for task {task_id} with params: {agent_run_params}")
        # Placeholder for actual agent execution logic
        await asyncio.sleep(5) # Simulate agent work
        print(f"[TaskScheduler] Agent finished for task {task_id}.")
        # Update task status in self.scheduled_tasks if needed

    async def _schedule_loop(self, task_id: str):
        task_info = self.scheduled_tasks.get(task_id)
        if not task_info:
            return

        cron_expression = task_info["cron_expression"]
        agent_run_params = task_info["agent_run_params"]

        cron = croniter.croniter(cron_expression, datetime.now())

        while True:
            next_run_time = cron.get_next(datetime)
            delay = (next_run_time - datetime.now()).total_seconds()

            if delay > 0:
                print(f"[TaskScheduler] Task {task_id} next run in {delay:.2f} seconds at {next_run_time}")
                await asyncio.sleep(delay)

            if task_id not in self.scheduled_tasks: # Check if task was cancelled during sleep
                print(f"[TaskScheduler] Task {task_id} cancelled during sleep.")
                break

            print(f"[TaskScheduler] Executing scheduled task {task_id} at {datetime.now()}")
            # Execute the agent for the task
            await self._run_task_agent(task_id, agent_run_params)

            # Update cron iterator for the next run
            cron = croniter.croniter(cron_expression, datetime.now())

    async def schedule_task(self, user_id: str, name: str, cron_expression: str, agent_run_params: Dict[str, Any]) -> Dict[str, Any]:
        task_id = str(uuid4())
        new_task = {
            "id": task_id,
            "user_id": user_id,
            "name": name,
            "cron_expression": cron_expression,
            "agent_run_params": agent_run_params,
            "status": "scheduled",
            "created_at": datetime.now().isoformat(),
            "next_run_at": croniter.croniter(cron_expression, datetime.now()).get_next(datetime).isoformat()
        }
        self.scheduled_tasks[task_id] = new_task

        # Start the background task for scheduling
        self._task_runners[task_id] = asyncio.create_task(self._schedule_loop(task_id))

        print(f"Task {name} ({task_id}) scheduled with cron: {cron_expression}")
        return new_task

    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        return self.scheduled_tasks.get(task_id)

    async def list_tasks(self, user_id: str) -> List[Dict[str, Any]]:
        return [task for task in self.scheduled_tasks.values() if task["user_id"] == user_id]

    async def cancel_task(self, task_id: str) -> bool:
        if task_id in self.scheduled_tasks:
            if task_id in self._task_runners:
                self._task_runners[task_id].cancel()
                try:
                    await self._task_runners[task_id]
                except asyncio.CancelledError:
                    print(f"[TaskScheduler] Background task for {task_id} cancelled.")
                del self._task_runners[task_id]

            del self.scheduled_tasks[task_id]
            print(f"Task {task_id} cancelled.")
            return True
        return False

task_scheduler = TaskScheduler() # Singleton instance
