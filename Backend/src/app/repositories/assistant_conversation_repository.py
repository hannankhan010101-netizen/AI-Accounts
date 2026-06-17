"""AI assistant conversation threads and messages."""

from __future__ import annotations

from typing import Any

from prisma_generated import Prisma

from app.core.prisma_data import omit_none, optional_json


class AssistantConversationRepository:
    def __init__(self, prisma_client: Prisma) -> None:
        self._db = prisma_client

    async def create_thread(
        self, *, company_id: str, user_id: str, locale: str = "en"
    ) -> str:
        row = await self._db.assistantthread.create(
            data={
                "companyId": company_id,
                "userId": user_id,
                "locale": locale,
            }
        )
        return row.id

    async def get_thread(
        self, *, thread_id: str, company_id: str, user_id: str
    ) -> bool:
        row = await self._db.assistantthread.find_unique(where={"id": thread_id})
        if row is None:
            return False
        return row.companyId == company_id and row.userId == user_id

    async def delete_thread(
        self, *, thread_id: str, company_id: str, user_id: str
    ) -> bool:
        row = await self._db.assistantthread.find_unique(where={"id": thread_id})
        if row is None or row.companyId != company_id or row.userId != user_id:
            return False
        await self._db.assistantmessage.delete_many(where={"threadId": thread_id})
        await self._db.assistantthread.delete(where={"id": thread_id})
        return True

    async def append_message(
        self,
        *,
        thread_id: str,
        role: str,
        content: str,
        tool_name: str | None = None,
        tool_payload: dict[str, Any] | None = None,
    ) -> str:
        payload = optional_json(tool_payload)
        data = omit_none(
            {
                "role": role,
                "content": content,
                "thread": {"connect": {"id": thread_id}},
                "toolName": tool_name,
                "toolPayload": payload,
            }
        )
        row = await self._db.assistantmessage.create(data=data)
        return row.id

    async def list_messages(
        self, *, thread_id: str, take: int = 40
    ) -> list[dict[str, Any]]:
        rows = await self._db.assistantmessage.find_many(
            where={"threadId": thread_id},
            order={"createdAt": "asc"},
            take=take,
        )
        return [
            {
                "id": r.id,
                "role": r.role,
                "content": r.content,
                "toolName": r.toolName,
                "toolPayload": r.toolPayload,
                "createdAt": r.createdAt.isoformat() if r.createdAt else None,
            }
            for r in rows
        ]

    async def recent_turns_for_llm(
        self, *, thread_id: str, max_turns: int
    ) -> list[dict[str, str]]:
        """Load last N messages as OpenAI-style role/content pairs."""

        rows = await self._db.assistantmessage.find_many(
            where={"threadId": thread_id},
            order={"createdAt": "desc"},
            take=max_turns * 2,
        )
        rows = list(reversed(rows))
        out: list[dict[str, str]] = []
        for r in rows:
            if r.role in ("user", "assistant") and r.content:
                out.append({"role": r.role, "content": r.content[:8000]})
        return out[-max_turns * 2 :]
