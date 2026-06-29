from typing import AsyncGenerator, List, Dict, Any
from uuid import UUID

from sqlalchemy.orm import Session

from core.database import User
from src.chat_handler import ChatHandler
# from src.memory import MemoryManager
# from src.prompt_security import PromptSecurity

class ChatProcessor:
    def __init__(self, db: Session):
        self.db = db
        self.chat_handler = ChatHandler(db)
        # self.memory_manager = MemoryManager(db)
        # self.prompt_security = PromptSecurity()

    async def process_chat_request(
        self, 
        session_id: UUID, 
        user_message_content: str, 
        model_name: str,
        llm_provider_name: str,
        user: User
    ) -> AsyncGenerator[str, None]:
        # 1. Pre-processamento (e.g., segurança de prompt, extração de intenção)
        # if self.prompt_security.is_injection(user_message_content):
        #     yield "data: {\"error\": \"Prompt injection detected.\"}\n\n"
        #     return

        # 2. Recuperação de contexto/memória (RAG)
        # relevant_memories = await self.memory_manager.search_memories(user_message_content, user.id)
        # system_prompt = self.prompt_security.build_system_prompt(relevant_memories)

        # 3. Streaming da resposta do LLM
        async for chunk in self.chat_handler.stream_chat_response(
            session_id,
            user_message_content,
            model_name,
            llm_provider_name,
            user
        ):
            yield chunk

        # 4. Pós-processamento (e.g., extração de memória em background)
        # asyncio.create_task(self.memory_manager.extract_memories(full_response_content, user.id))
