"""Access control routes — RBAC v2."""

from __future__ import annotations

import json
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.encoders import jsonable_encoder

from app.api.dependencies.deps import (
    JwtClaims,
    get_access_control_service,
    get_audit_log_service,
    get_company_bootstrap_repository,
    get_membership_repository,
    get_membership_role_repository,
    get_module_access_service,
    get_permission_service,
    get_role_repository,
    require_permission,
    resolve_tenant,
)
from app.constants.permission_registry import matrix_for_api
from app.constants.role_templates import ROLE_TEMPLATES, template_by_code
from app.models.requests.role_requests import (
    AssignUserRolesRequest,
    DataScopeReplaceRequest,
    FieldPolicyReplaceRequest,
    ModuleConfigReplaceRequest,
    RoleFromTemplateRequest,
)
from app.services.access_control_service import AccessControlService
from app.services.audit_log_service import AuditLogService
from app.services.module_access_service import ModuleAccessService
from app.services.permission_service import PermissionService
from app.repositories.company_bootstrap_repository import CompanyBootstrapRepository
from app.repositories.membership_repository import MembershipRepository
from app.repositories.membership_role_repository import MembershipRoleRepository
from app.repositories.role_repository import RoleRepository

router = APIRouter()


@router.get("/permissions/matrix")
async def get_permissions_matrix(
    _claims: Annotated[JwtClaims, Depends(resolve_tenant)],
) -> dict:
    return {"result": matrix_for_api()}


@router.get("/role-templates")
async def list_role_templates(
    _claims: Annotated[JwtClaims, Depends(resolve_tenant)],
) -> dict:
    return {"result": ROLE_TEMPLATES}


@router.post("/roles/from-template/{template_code}", status_code=201)
async def create_role_from_template(
    company_id: str,
    template_code: str,
    body: RoleFromTemplateRequest,
    repo: Annotated[RoleRepository, Depends(get_role_repository)],
    audit: Annotated[AuditLogService, Depends(get_audit_log_service)],
    claims: Annotated[JwtClaims, Depends(require_permission("settings.roles.manage"))],
) -> dict:
    tpl = template_by_code(template_code)
    if tpl is None:
        raise HTTPException(status_code=404, detail="Template not found")
    try:
        row = await repo.create_from_template(
            company_id=company_id,
            template=tpl,
            name=body.name,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    payload = await repo.get_role_payload(company_id=company_id, role_id=row.id)
    await audit.record(
        company_id=company_id,
        user_id=claims.user_id,
        transaction_type="ROLE_CREATE",
        transaction_id=row.id,
        status="ok",
        details=json.dumps({"source": "template", "templateCode": template_code}),
    )
    return {"result": payload}


@router.post("/roles/seed-missing-templates")
async def seed_missing_role_templates(
    company_id: str,
    bootstrap: Annotated[CompanyBootstrapRepository, Depends(get_company_bootstrap_repository)],
    audit: Annotated[AuditLogService, Depends(get_audit_log_service)],
    claims: Annotated[JwtClaims, Depends(require_permission("settings.roles.manage"))],
) -> dict:
    created = await bootstrap.seed_missing_template_roles(company_id=company_id)
    await audit.record(
        company_id=company_id,
        user_id=claims.user_id,
        transaction_type="ROLE_CREATE",
        transaction_id=None,
        status="ok",
        details=json.dumps({"source": "seed_missing_templates", "created": created}),
    )
    return {"result": created}


@router.put("/users/{user_id}/roles")
async def assign_user_roles(
    company_id: str,
    user_id: str,
    body: AssignUserRolesRequest,
    membership_repo: Annotated[MembershipRepository, Depends(get_membership_repository)],
    membership_roles: Annotated[
        MembershipRoleRepository, Depends(get_membership_role_repository)
    ],
    role_repo: Annotated[RoleRepository, Depends(get_role_repository)],
    audit: Annotated[AuditLogService, Depends(get_audit_log_service)],
    claims: Annotated[JwtClaims, Depends(require_permission("settings.roles.manage"))],
) -> dict:
    membership = await membership_repo.get_membership(company_id=company_id, user_id=user_id)
    if membership is None:
        raise HTTPException(status_code=404, detail="User is not a member of this company")
    for role_id in body.role_ids:
        role = await role_repo.get_role(company_id=company_id, role_id=role_id)
        if role is None:
            raise HTTPException(status_code=400, detail=f"Invalid role: {role_id}")
    before = membership.get("roleIds", [])
    try:
        await membership_roles.replace_roles(
            membership_id=membership["id"],
            role_ids=body.role_ids,
            primary_role_id=body.primary_role_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    updated = await membership_repo.get_membership(company_id=company_id, user_id=user_id)
    await audit.record(
        company_id=company_id,
        user_id=claims.user_id,
        transaction_type="USER_ROLE_ASSIGN",
        transaction_id=user_id,
        status="ok",
        details=json.dumps({"before": before, "after": body.role_ids}),
    )
    return {"result": updated}


@router.get("/access-control/modules")
async def get_access_control_modules(
    company_id: str,
    service: Annotated[AccessControlService, Depends(get_access_control_service)],
    _claims: Annotated[JwtClaims, Depends(resolve_tenant)],
) -> dict:
    return {"result": await service.list_module_config(company_id=company_id)}


@router.put("/access-control/modules")
async def put_access_control_modules(
    company_id: str,
    body: ModuleConfigReplaceRequest,
    service: Annotated[AccessControlService, Depends(get_access_control_service)],
    audit: Annotated[AuditLogService, Depends(get_audit_log_service)],
    claims: Annotated[
        JwtClaims,
        Depends(require_permission("settings.access_control.manage")),
    ],
) -> dict:
    before = await service.list_module_config(company_id=company_id)
    result = await service.replace_module_config(
        company_id=company_id,
        modules=[m.model_dump(by_alias=True) for m in body.modules],
    )
    await audit.record(
        company_id=company_id,
        user_id=claims.user_id,
        transaction_type="MODULE_CONFIG_CHANGE",
        transaction_id=None,
        status="ok",
        details=json.dumps({"before": before, "after": result}),
    )
    return {"result": result}


@router.get("/access-control/effective")
async def get_access_control_effective(
    company_id: str,
    claims: Annotated[JwtClaims, Depends(resolve_tenant)],
    permission_service: Annotated[PermissionService, Depends(get_permission_service)],
    module_access: Annotated[ModuleAccessService, Depends(get_module_access_service)],
    membership_repo: Annotated[MembershipRepository, Depends(get_membership_repository)],
) -> dict:
    membership = await membership_repo.get_membership(
        company_id=company_id, user_id=claims.user_id
    )
    perms = await permission_service.permissions_for(
        company_id=company_id, user_id=claims.user_id
    )
    matrix = await module_access.matrix_for_user(
        company_id=company_id, user_id=claims.user_id
    )
    return {
        "result": {
            "membership": membership,
            "permissions": perms,
            "modules": matrix,
        }
    }


@router.get("/access-control/field-security")
async def get_field_security(
    company_id: str,
    service: Annotated[AccessControlService, Depends(get_access_control_service)],
    _claims: Annotated[JwtClaims, Depends(resolve_tenant)],
    role_id: str | None = Query(default=None, alias="roleId"),
) -> dict:
    return {
        "result": await service.list_field_policies(
            company_id=company_id, role_id=role_id
        )
    }


@router.put("/access-control/field-security")
async def put_field_security(
    company_id: str,
    body: FieldPolicyReplaceRequest,
    service: Annotated[AccessControlService, Depends(get_access_control_service)],
    audit: Annotated[AuditLogService, Depends(get_audit_log_service)],
    claims: Annotated[
        JwtClaims,
        Depends(require_permission("settings.access_control.manage")),
    ],
) -> dict:
    result = await service.replace_field_policies(
        company_id=company_id,
        role_id=body.role_id,
        policies=[p.model_dump(by_alias=True) for p in body.policies],
    )
    await audit.record(
        company_id=company_id,
        user_id=claims.user_id,
        transaction_type="FIELD_POLICY_CHANGE",
        transaction_id=body.role_id,
        status="ok",
        details=json.dumps({"policies": result}),
    )
    return {"result": result}


@router.get("/access-control/data-scope/{membership_id}")
async def get_data_scope(
    company_id: str,
    membership_id: str,
    service: Annotated[AccessControlService, Depends(get_access_control_service)],
    _claims: Annotated[JwtClaims, Depends(resolve_tenant)],
) -> dict:
    return {
        "result": await service.list_data_scope(
            company_id=company_id, membership_id=membership_id
        )
    }


@router.put("/access-control/data-scope/{membership_id}")
async def put_data_scope(
    company_id: str,
    membership_id: str,
    body: DataScopeReplaceRequest,
    service: Annotated[AccessControlService, Depends(get_access_control_service)],
    audit: Annotated[AuditLogService, Depends(get_audit_log_service)],
    claims: Annotated[
        JwtClaims,
        Depends(require_permission("settings.access_control.manage")),
    ],
) -> dict:
    result = await service.replace_data_scope(
        company_id=company_id,
        membership_id=membership_id,
        assignments=[a.model_dump(by_alias=True) for a in body.assignments],
    )
    await audit.record(
        company_id=company_id,
        user_id=claims.user_id,
        transaction_type="DATA_SCOPE_CHANGE",
        transaction_id=membership_id,
        status="ok",
        details=json.dumps({"assignments": result}),
    )
    return {"result": result}
