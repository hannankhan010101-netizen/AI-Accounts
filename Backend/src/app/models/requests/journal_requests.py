"""General journal request bodies."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class JournalLineRequest(BaseModel):
    """One debit/credit line on a manual journal."""

    model_config = {"populate_by_name": True}

    nominal_code: str = Field(..., alias="nominalCode")
    debit: str | float = Field(default=0, alias="debit")
    credit: str | float = Field(default=0, alias="credit")
    project_code: str | None = Field(default=None, alias="projectCode")


class JournalCreateRequest(BaseModel):
    """Create journal voucher with line grid."""

    model_config = {"populate_by_name": True}

    journal_date: datetime = Field(..., alias="journalDate")
    ref_no: str | None = Field(default=None, alias="refNo")
    lines: list[JournalLineRequest] = Field(..., min_length=2, alias="lines")
    status: Literal["draft", "posted"] = "posted"

    def to_prisma_lines(self) -> list[dict[str, Any]]:
        """Convert validated lines into Prisma nested create payloads."""

        from decimal import Decimal

        out: list[dict[str, Any]] = []
        for line in self.lines:
            out.append(
                {
                    "nominalCode": line.nominal_code,
                    "debit": Decimal(str(line.debit)),
                    "credit": Decimal(str(line.credit)),
                    "projectCode": line.project_code,
                }
            )
        return out


class JournalUpdateRequest(BaseModel):
    """Replace a draft journal header and line grid."""

    model_config = {"populate_by_name": True}

    journal_date: datetime | None = Field(default=None, alias="journalDate")
    ref_no: str | None = Field(default=None, alias="refNo")
    lines: list[JournalLineRequest] | None = None

    def to_prisma_lines(self) -> list[dict[str, Any]] | None:
        if self.lines is None:
            return None
        from decimal import Decimal

        out: list[dict[str, Any]] = []
        for line in self.lines:
            out.append(
                {
                    "nominalCode": line.nominal_code,
                    "debit": Decimal(str(line.debit)),
                    "credit": Decimal(str(line.credit)),
                    "projectCode": line.project_code,
                }
            )
        return out
