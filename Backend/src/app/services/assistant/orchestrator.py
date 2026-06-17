"""Assistant orchestration — Groq streaming, tools, memory."""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator
from typing import Any

from groq.types.chat import ChatCompletionMessageParam

from app.core.config import get_settings
from app.integrations.groq_client import GroqClient
from app.repositories.assistant_conversation_repository import AssistantConversationRepository
from app.services.assistant.prompt_builder import build_system_prompt, infer_mode
from app.services.assistant.prompt_sanitize import sanitize_user_message
from app.services.assistant.session_store import PendingAssistantSession, pop_session, store_session
from app.services.assistant.tool_handlers import AssistantToolHandlers
from app.services.assistant.tool_registry import (
    is_client_tool,
    sanitize_tool_calls,
    tools_for_mode,
)
from app.services.audit_log_service import AuditLogService

logger = logging.getLogger(__name__)


class AssistantOrchestrator:
    def __init__(
        self,
        *,
        groq_client: GroqClient,
        conversation_repository: AssistantConversationRepository,
        tool_handlers: AssistantToolHandlers,
        audit_log_service: AuditLogService,
    ) -> None:
        self._groq = groq_client
        self._repo = conversation_repository
        self._tools = tool_handlers
        self._audit = audit_log_service

    async def ensure_thread(
        self,
        *,
        thread_id: str | None,
        company_id: str,
        user_id: str,
        locale: str,
    ) -> str:
        if thread_id:
            ok = await self._repo.get_thread(
                thread_id=thread_id, company_id=company_id, user_id=user_id
            )
            if ok:
                return thread_id
        return await self._repo.create_thread(
            company_id=company_id, user_id=user_id, locale=locale
        )

    async def stream_chat(
        self,
        *,
        message: str,
        pathname: str,
        company_id: str,
        user_id: str,
        permissions: list[str],
        thread_id: str | None,
        locale: str | None,
        mode: str | None,
        entity_context: dict[str, Any] | None,
        onboarding_progress: dict[str, Any] | None,
    ) -> AsyncIterator[dict[str, Any]]:
        settings = get_settings()
        if not self._groq.enabled:
            yield {
                "type": "error",
                "message": "AI assistant is not configured. Set GROQ_API_KEY on the server.",
            }
            return

        safe_message = sanitize_user_message(
            message, max_chars=settings.assistant_max_message_chars
        )
        resolved_mode = infer_mode(pathname, mode)
        tid = await self.ensure_thread(
            thread_id=thread_id,
            company_id=company_id,
            user_id=user_id,
            locale=locale or "en",
        )

        await self._repo.append_message(
            thread_id=tid, role="user", content=safe_message
        )
        await self._audit.record(
            company_id=company_id,
            user_id=user_id,
            transaction_type="assistant.query",
            transaction_id=tid,
            status="ok",
            details=safe_message[:200],
        )

        history = await self._repo.recent_turns_for_llm(
            thread_id=tid, max_turns=settings.assistant_memory_turns
        )
        system = build_system_prompt(
            mode=resolved_mode,
            pathname=pathname,
            permissions=permissions,
            locale=locale,
            screen_context=entity_context,
            onboarding_progress=onboarding_progress,
        )
        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": system},
            *[{"role": m["role"], "content": m["content"]} for m in history[:-1]],
            {"role": "user", "content": safe_message},
        ]
        tools = tools_for_mode(resolved_mode, pathname)

        yield {"type": "thread", "threadId": tid}

        full_content = ""
        tool_calls: list[dict[str, Any]] = []

        async for event in self._stream_groq_turn(
            messages=messages, tools=tools, allow_text_fallback=True
        ):
            if event["type"] == "token":
                full_content += event.get("content", "")
                yield {"type": "token", "content": event.get("content", "")}
            elif event["type"] == "tool_calls":
                tool_calls = sanitize_tool_calls(event.get("tool_calls", []))
            elif event["type"] == "error":
                yield event
                return
            elif event["type"] == "done":
                break

        if not tool_calls:
            if full_content:
                await self._repo.append_message(
                    thread_id=tid, role="assistant", content=full_content
                )
            yield {"type": "done", "threadId": tid, "engine": "groq"}
            return

        async for out in self._handle_tool_calls(
            tool_calls=tool_calls,
            messages=messages,
            tools=tools,
            tid=tid,
            resolved_mode=resolved_mode,
            pathname=pathname,
            company_id=company_id,
            user_id=user_id,
            permissions=permissions,
            locale=locale,
            full_content=full_content,
        ):
            yield out

    async def _handle_tool_calls(
        self,
        *,
        tool_calls: list[dict[str, Any]],
        messages: list[ChatCompletionMessageParam],
        tools: list[dict[str, Any]],
        tid: str,
        resolved_mode: str,
        pathname: str,
        company_id: str,
        user_id: str,
        permissions: list[str],
        locale: str | None,
        full_content: str,
    ) -> AsyncIterator[dict[str, Any]]:
        assistant_msg: dict[str, Any] = {
            "role": "assistant",
            "content": full_content or None,
            "tool_calls": [
                {
                    "id": tc["id"],
                    "type": "function",
                    "function": {
                        "name": tc["name"],
                        "arguments": json.dumps(tc.get("arguments") or {}),
                    },
                }
                for tc in tool_calls
            ],
        }
        messages = [*messages, assistant_msg]  # type: ignore[arg-type]

        for tc in tool_calls:
            name = tc.get("name") or ""
            args = tc.get("arguments") or {}
            tc_id = tc.get("id") or ""

            await self._audit.record(
                company_id=company_id,
                user_id=user_id,
                transaction_type=f"assistant.tool.{name}",
                transaction_id=tid,
                status="ok",
                details=json.dumps(args, default=str)[:300],
            )

            if is_client_tool(name):
                key = f"{tid}:{tc_id}"
                await store_session(
                    key,
                    PendingAssistantSession(
                        messages=list(messages),
                        mode=resolved_mode,
                        pathname=pathname,
                        company_id=company_id,
                        user_id=user_id,
                        permissions=permissions,
                        locale=locale,
                        tool_call_id=tc_id,
                        tool_name=name,
                    ),
                )
                yield {
                    "type": "tool_call",
                    "threadId": tid,
                    "toolCallId": tc_id,
                    "name": name,
                    "arguments": args,
                }
                return

            result = await self._tools.execute(
                name=name,
                arguments=args,
                company_id=company_id,
                user_id=user_id,
                pathname=pathname,
            )
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc_id,
                    "content": json.dumps(result, default=str)[:8000],
                }
            )

        async for event in self._continue_after_tools(
            messages=messages,
            tools=tools,
            tid=tid,
            company_id=company_id,
            user_id=user_id,
            resolved_mode=resolved_mode,
            pathname=pathname,
            permissions=permissions,
            locale=locale,
        ):
            yield event

    async def continue_with_tool_result(
        self,
        *,
        thread_id: str,
        tool_call_id: str,
        result: dict[str, Any],
        company_id: str,
        user_id: str,
    ) -> AsyncIterator[dict[str, Any]]:
        key = f"{thread_id}:{tool_call_id}"
        session = await pop_session(key)
        if not session:
            yield {"type": "error", "message": "Tool session expired. Send a new message."}
            return

        messages = list(session.messages)
        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": json.dumps(result, default=str)[:8000],
            }
        )
        tools = tools_for_mode(session.mode, session.pathname)

        async for event in self._continue_after_tools(
            messages=messages,
            tools=tools,
            tid=thread_id,
            company_id=company_id,
            user_id=user_id,
            resolved_mode=session.mode,
            pathname=session.pathname,
            permissions=session.permissions,
            locale=session.locale,
        ):
            yield event

    async def _continue_after_tools(
        self,
        *,
        messages: list[ChatCompletionMessageParam],
        tools: list[dict[str, Any]],
        tid: str,
        company_id: str,
        user_id: str,
        resolved_mode: str = "erp_help",
        pathname: str = "/",
        permissions: list[str] | None = None,
        locale: str | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        full_content = ""
        tool_calls: list[dict[str, Any]] = []

        async for event in self._stream_groq_turn(
            messages=messages, tools=tools, allow_text_fallback=True
        ):
            if event["type"] == "token":
                full_content += event.get("content", "")
                yield {"type": "token", "content": event.get("content", "")}
            elif event["type"] == "tool_calls":
                tool_calls = sanitize_tool_calls(event.get("tool_calls", []))
            elif event["type"] == "error":
                yield event
                return
            elif event["type"] == "done":
                break

        if tool_calls:
            async for out in self._handle_tool_calls(
                tool_calls=tool_calls,
                messages=messages,
                tools=tools,
                tid=tid,
                resolved_mode=resolved_mode,
                pathname=pathname,
                company_id=company_id,
                user_id=user_id,
                permissions=permissions or [],
                locale=locale,
                full_content=full_content,
            ):
                yield out
            return

        if full_content:
            await self._repo.append_message(
                thread_id=tid, role="assistant", content=full_content
            )
        yield {"type": "done", "threadId": tid, "engine": "groq"}

    async def _stream_groq_turn(
        self,
        *,
        messages: list[ChatCompletionMessageParam],
        tools: list[dict[str, Any]] | None,
        allow_text_fallback: bool,
    ) -> AsyncIterator[dict[str, Any]]:
        """Stream one Groq turn; on tool-generation failure retry once without tools."""

        saw_tool_error = False
        async for event in self._groq.stream_chat(messages=messages, tools=tools):
            if event["type"] == "error":
                if (
                    allow_text_fallback
                    and tools
                    and event.get("code") == "GROQ_TOOL_FAILED"
                ):
                    saw_tool_error = True
                    break
                yield event
                return
            yield event

        if not saw_tool_error:
            return

        logger.info("Groq tool generation failed; retrying assistant turn without tools")
        async for event in self._groq.stream_chat(messages=messages, tools=None):
            if event["type"] == "error":
                yield event
                return
            yield event

    async def simple_reply(
        self,
        *,
        message: str,
        pathname: str,
        permissions: list[str],
        mode: str = "onboarding",
        onboarding_progress: dict[str, Any] | None = None,
    ) -> tuple[str, str]:
        """Non-streaming reply for onboarding backward compatibility."""

        if not self._groq.enabled:
            return (
                "AI assistant is not configured on this server. Use guided tours from the compass button.",
                "rules",
            )
        settings = get_settings()
        safe = sanitize_user_message(message, max_chars=settings.assistant_max_message_chars)
        system = build_system_prompt(
            mode=mode,
            pathname=pathname,
            permissions=permissions,
            locale=None,
            screen_context=None,
            onboarding_progress=onboarding_progress,
        )
        messages: list[ChatCompletionMessageParam] = [
            {"role": "system", "content": system},
            {"role": "user", "content": safe},
        ]
        try:
            content, _ = await self._groq.chat_completion(messages=messages, tools=None)
            return (content.strip() or "I could not generate a reply.", "groq")
        except Exception as exc:
            logger.warning("simple_reply failed: %s", exc)
            return (
                "I could not reach the AI service. Try a guided tour from the list below.",
                "rules",
            )
