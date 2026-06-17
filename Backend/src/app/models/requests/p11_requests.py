"""P11 — module entitlements, custom fields, product UOM."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


class ModuleEntitlementItem(BaseModel):
    module_code: str = Field(alias="moduleCode")
    enabled: bool = True

    model_config = {"populate_by_name": True}


class ModuleEntitlementsReplaceRequest(BaseModel):
    entitlements: list[ModuleEntitlementItem]


class CustomFieldDefinitionCreateRequest(BaseModel):
    entity_type: str = Field(alias="entityType")
    field_key: str = Field(alias="fieldKey")
    label: str
    field_type: str = Field(default="text", alias="fieldType")
    is_required: bool = Field(default=False, alias="isRequired")
    picklist_options: list[str] | None = Field(default=None, alias="picklistOptions")

    model_config = {"populate_by_name": True}


class DocumentVoidRequest(BaseModel):
    reversal_date: datetime | None = Field(default=None, alias="reversalDate")

    model_config = {"populate_by_name": True}


class GoodsIssueLineVoidRequest(BaseModel):
    reversal_date: datetime | None = Field(default=None, alias="reversalDate")

    model_config = {"populate_by_name": True}


class PortalSessionRequest(BaseModel):
    return_url: str | None = Field(default=None, alias="returnUrl")

    model_config = {"populate_by_name": True}


class CheckoutSessionRequest(BaseModel):
    plan_code: str = Field(default="starter", alias="planCode")
    success_url: str | None = Field(default=None, alias="successUrl")
    cancel_url: str | None = Field(default=None, alias="cancelUrl")

    model_config = {"populate_by_name": True}


class BillingWebhookRequest(BaseModel):
    company_id: str = Field(alias="companyId")
    event_type: str = Field(alias="eventType")
    plan_code: str | None = Field(default=None, alias="planCode")
    external_customer_id: str | None = Field(default=None, alias="externalCustomerId")

    model_config = {"populate_by_name": True}


class CustomFieldsPatchRequest(BaseModel):
    custom_fields: dict[str, Any] = Field(alias="customFields")

    model_config = {"populate_by_name": True}


class ProductUomUpsertRequest(BaseModel):
    unit_code: str = Field(alias="unitCode")
    conversion_factor: Decimal = Field(default=Decimal("1"), alias="conversionFactor")
    sale_price: Decimal = Field(default=Decimal("0"), alias="salePrice")
    is_default: bool = Field(default=False, alias="isDefault")

    model_config = {"populate_by_name": True}
