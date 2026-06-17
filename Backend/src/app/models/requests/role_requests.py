"""Role CRUD request bodies — P25 / RBAC v2."""

from __future__ import annotations

from pydantic import BaseModel, Field


class RoleCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    permissions: list[str] = Field(default_factory=list)
    description: str | None = Field(default=None, max_length=500)
    parent_role_id: str | None = Field(default=None, alias="parentRoleId")
    code: str | None = Field(default=None, max_length=64)

    model_config = {"populate_by_name": True}


class RoleUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    permissions: list[str] | None = None
    description: str | None = Field(default=None, max_length=500)
    parent_role_id: str | None = Field(default=None, alias="parentRoleId")

    model_config = {"populate_by_name": True}


class AssignUserRoleRequest(BaseModel):
    role_id: str = Field(..., alias="roleId")

    model_config = {"populate_by_name": True}


class AssignUserRolesRequest(BaseModel):
    role_ids: list[str] = Field(..., min_length=1, alias="roleIds")
    primary_role_id: str | None = Field(default=None, alias="primaryRoleId")

    model_config = {"populate_by_name": True}


class RoleFromTemplateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)


class ReinviteUserRequest(BaseModel):
    role_id: str = Field(..., alias="roleId")

    model_config = {"populate_by_name": True}


class ReinviteByEmailRequest(BaseModel):
    """Reinvite a revoked user by email — P42."""

    email: str = Field(..., min_length=3, max_length=254)
    role_id: str = Field(..., alias="roleId")

    model_config = {"populate_by_name": True}


class RoleCloneRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)


class RoleCloneBatchRequest(BaseModel):
    role_ids: list[str] = Field(..., min_length=1, max_length=50, alias="roleIds")
    name_suffix: str | None = Field(default=None, max_length=40, alias="nameSuffix")

    model_config = {"populate_by_name": True}


class RoleImportEntry(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    permissions: list[str] = Field(default_factory=list)
    description: str | None = None


class RoleImportRequest(BaseModel):
    roles: list[RoleImportEntry] = Field(..., min_length=1, max_length=100)
    skip_existing: bool = Field(default=True, alias="skipExisting")

    model_config = {"populate_by_name": True}


class InviteUserRequest(BaseModel):
    email: str = Field(..., min_length=3, max_length=254)
    first_name: str = Field(..., min_length=1, max_length=120, alias="firstName")
    last_name: str = Field(..., min_length=1, max_length=120, alias="lastName")
    role_id: str = Field(..., alias="roleId")
    role_ids: list[str] | None = Field(default=None, alias="roleIds")

    model_config = {"populate_by_name": True}


class BulkUserIdsRequest(BaseModel):
    user_ids: list[str] = Field(..., min_length=1, max_length=100, alias="userIds")

    model_config = {"populate_by_name": True}


class BulkAssignRoleRequest(BaseModel):
    user_ids: list[str] = Field(..., min_length=1, max_length=100, alias="userIds")
    role_id: str = Field(..., alias="roleId")

    model_config = {"populate_by_name": True}


class UpdateIpAllowlistRequest(BaseModel):
    ip_allowlist: str | None = Field(default=None, alias="ipAllowlist")

    model_config = {"populate_by_name": True}


class ModuleConfigEntry(BaseModel):
    module_code: str = Field(..., alias="moduleCode")
    enabled: bool = True
    sidebar_visible: bool = Field(default=True, alias="sidebarVisible")
    routes_enabled: bool = Field(default=True, alias="routesEnabled")
    api_enabled: bool = Field(default=True, alias="apiEnabled")
    reports_enabled: bool = Field(default=True, alias="reportsEnabled")
    widgets_enabled: bool = Field(default=True, alias="widgetsEnabled")

    model_config = {"populate_by_name": True}


class ModuleConfigReplaceRequest(BaseModel):
    modules: list[ModuleConfigEntry]


class FieldPolicyEntry(BaseModel):
    field_key: str = Field(..., alias="fieldKey")
    access_level: str = Field(..., alias="accessLevel")

    model_config = {"populate_by_name": True}


class FieldPolicyReplaceRequest(BaseModel):
    role_id: str = Field(..., alias="roleId")
    policies: list[FieldPolicyEntry] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


class DataScopeEntry(BaseModel):
    scope_type: str = Field(..., alias="scopeType")
    scope_id: str = Field(..., alias="scopeId")

    model_config = {"populate_by_name": True}


class DataScopeReplaceRequest(BaseModel):
    assignments: list[DataScopeEntry] = Field(default_factory=list)
