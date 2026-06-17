"""Enterprise AI assistant routes — SSE streaming under tenant scope."""

from __future__ import annotations

import json
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.api.dependencies.deps import (
    JwtClaims,
    get_assistant_orchestrator,
    get_membership_repository,
    get_onboarding_repository,
    get_permission_service,
    resolve_tenant,
    get_assistant_conversation_repository,
)
from app.core.rate_limit import check_rate_limit
from app.models.requests.assistant_requests import (
    AssistantChatStreamRequest,
    AssistantToolResultRequest,
)
from app.repositories.assistant_conversation_repository import AssistantConversationRepository
from app.repositories.onboarding_repository import OnboardingRepository
from app.repositories.membership_repository import MembershipRepository
from app.services.assistant.orchestrator import AssistantOrchestrator
from app.services.onboarding_llm_service import learning_suggestions
from app.services.permission_service import PermissionService

router = APIRouter()


def _sse_event(payload: dict[str, Any]) -> str:
    return f"data: {json.dumps(payload, default=str)}\n\n"


async def _stream_orchestrator(
    orchestrator: AssistantOrchestrator,
    *,
    gen,
) -> StreamingResponse:
    async def event_generator():
        try:
            async for item in gen:
                yield _sse_event(item)
        except Exception as exc:
            yield _sse_event({"type": "error", "message": str(exc)})

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/me/assistant/chat/stream")
async def post_assistant_chat_stream(
    company_id: str,
    body: AssistantChatStreamRequest,
    request: Request,
    claims: Annotated[JwtClaims, Depends(resolve_tenant)],
    orchestrator: Annotated[AssistantOrchestrator, Depends(get_assistant_orchestrator)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
    onboarding_repo: Annotated[OnboardingRepository, Depends(get_onboarding_repository)],
) -> StreamingResponse:
    try:
        check_rate_limit(request, group="assistant", subject=claims.user_id)
    except PermissionError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc

    perms = await permission_service.permissions_for(
        company_id=company_id, user_id=claims.user_id
    )
    progress_payload = await onboarding_repo.get_payload(
        company_id=company_id, user_id=claims.user_id
    )

    gen = orchestrator.stream_chat(
        message=body.message,
        pathname=body.pathname,
        company_id=company_id,
        user_id=claims.user_id,
        permissions=perms,
        thread_id=body.thread_id,
        locale=body.locale,
        mode=body.mode,
        entity_context=body.entity_context,
        onboarding_progress=progress_payload,
    )
    return await _stream_orchestrator(orchestrator, gen=gen)


@router.post("/me/assistant/chat/tool-result")
async def post_assistant_tool_result(
    company_id: str,
    body: AssistantToolResultRequest,
    request: Request,
    claims: Annotated[JwtClaims, Depends(resolve_tenant)],
    orchestrator: Annotated[AssistantOrchestrator, Depends(get_assistant_orchestrator)],
    conversation_repo: Annotated[
        AssistantConversationRepository, Depends(get_assistant_conversation_repository)
    ],
) -> StreamingResponse:
    try:
        check_rate_limit(request, group="assistant", subject=claims.user_id)
    except PermissionError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc

    ok = await conversation_repo.get_thread(
        thread_id=body.thread_id, company_id=company_id, user_id=claims.user_id
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Thread not found")

    gen = orchestrator.continue_with_tool_result(
        thread_id=body.thread_id,
        tool_call_id=body.tool_call_id,
        result=body.result,
        company_id=company_id,
        user_id=claims.user_id,
    )
    return await _stream_orchestrator(orchestrator, gen=gen)


@router.get("/me/assistant/threads/{thread_id}/messages")
async def get_assistant_thread_messages(
    company_id: str,
    thread_id: str,
    claims: Annotated[JwtClaims, Depends(resolve_tenant)],
    conversation_repo: Annotated[
        AssistantConversationRepository, Depends(get_assistant_conversation_repository)
    ],
) -> dict:
    ok = await conversation_repo.get_thread(
        thread_id=thread_id, company_id=company_id, user_id=claims.user_id
    )
    if not ok:
        raise HTTPException(status_code=404, detail="Thread not found")
    messages = await conversation_repo.list_messages(thread_id=thread_id)
    return {"result": {"threadId": thread_id, "messages": messages}}


@router.delete("/me/assistant/threads/{thread_id}")
async def delete_assistant_thread(
    company_id: str,
    thread_id: str,
    claims: Annotated[JwtClaims, Depends(resolve_tenant)],
    conversation_repo: Annotated[
        AssistantConversationRepository, Depends(get_assistant_conversation_repository)
    ],
) -> dict:
    deleted = await conversation_repo.delete_thread(
        thread_id=thread_id, company_id=company_id, user_id=claims.user_id
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Thread not found")
    return {"result": {"deleted": True}}


@router.get("/me/assistant/suggestions")
async def get_assistant_suggestions(
    company_id: str,
    pathname: str,
    claims: Annotated[JwtClaims, Depends(resolve_tenant)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
    onboarding_repo: Annotated[OnboardingRepository, Depends(get_onboarding_repository)],
    membership_repo: Annotated[MembershipRepository, Depends(get_membership_repository)],
) -> dict:
    perms = await permission_service.permissions_for(
        company_id=company_id, user_id=claims.user_id
    )
    payload = await onboarding_repo.get_payload(
        company_id=company_id, user_id=claims.user_id
    )
    membership = await membership_repo.get_membership(
        company_id=company_id, user_id=claims.user_id
    )
    progress = {
        "tours": payload.get("tours", {}),
        "maturityScore": payload.get("maturityScore", 0),
        "dismissedHints": payload.get("dismissedHints", []),
    }
    releases: list[dict[str, Any]] = []
    suggestions, engine = await learning_suggestions(
        pathname=pathname,
        user_perms=perms,
        progress=progress,
        persona=membership.get("roleName") if membership else None,
        releases=releases,
    )
    return {"result": {"suggestions": suggestions, "pathname": pathname, "engine": engine}}
