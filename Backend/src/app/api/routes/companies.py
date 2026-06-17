"""Company listing and context switch (minimal)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies.deps import get_auth_service, get_company_repository, get_jwt_claims, JwtClaims
from app.models.requests.auth_requests import CreateCompanyRequest
from app.models.responses.common import AuthTokensResponse
from app.repositories.company_repository import CompanyRepository
from app.services.auth_service import AuthService

router = APIRouter(prefix="/api/v1", tags=["Companies"])


@router.post("/companies", status_code=201)
async def create_company(
    body: CreateCompanyRequest,
    claims: Annotated[JwtClaims, Depends(get_jwt_claims)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> dict:
    """Create an additional company for the authenticated user."""

    return await auth_service.create_company_for_user(user_id=claims.user_id, request=body)


@router.get("/companies")
async def list_my_companies(
    claims: Annotated[JwtClaims, Depends(get_jwt_claims)],
    company_repository: Annotated[CompanyRepository, Depends(get_company_repository)],
) -> dict:
    """List tenants for the authenticated user."""

    companies = await company_repository.list_companies_for_user(user_id=claims.user_id)
    return {
        "result": [
            {
                "id": c.id,
                "name": c.name,
                "createdAt": c.createdAt,
                "updatedAt": c.updatedAt,
            }
            for c in companies
        ]
    }


@router.post("/companies/{company_id}/switch", response_model=AuthTokensResponse)
async def switch_company(
    company_id: str,
    claims: Annotated[JwtClaims, Depends(get_jwt_claims)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> AuthTokensResponse:
    """Re-issue access token embedding the requested ``companyId``."""

    return await auth_service.switch_company(user_id=claims.user_id, company_id=company_id)
