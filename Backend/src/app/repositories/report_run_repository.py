"""Persisted report execution rows."""



from __future__ import annotations



from datetime import datetime, timezone

from typing import Any



from prisma_generated import Prisma

from prisma_generated.fields import Json

from prisma_generated.models import ReportRun



from app.services.report_blob_store import get_report_blob_store





class ReportRunRepository:

    def __init__(self, prisma_client: Prisma) -> None:

        self._db = prisma_client



    async def create_pending(

        self,

        *,

        company_id: str,

        report_id: str,

        criteria: dict[str, Any],

    ) -> ReportRun:

        return await self._db.reportrun.create(

            data={

                "companyId": company_id,

                "reportId": report_id,

                "status": "pending",

                "criteria": Json(criteria),

            }

        )



    async def get_run(self, *, company_id: str, run_id: str) -> ReportRun | None:

        row = await self._db.reportrun.find_unique(where={"id": run_id})

        if row is None or row.companyId != company_id:

            return None

        return row



    async def load_rows_for_run(self, run: ReportRun) -> list[dict[str, Any]]:

        storage_key = getattr(run, "storageKey", None) or getattr(run, "storage_key", None)

        if storage_key:

            return await get_report_blob_store().load_rows(storage_key=str(storage_key))

        raw = run.rows if isinstance(run.rows, list) else []

        return [r for r in raw if isinstance(r, dict)]



    async def complete_run(

        self,

        *,

        run_id: str,

        company_id: str,

        rows: list[dict[str, Any]],

        status: str = "completed",

        error_message: str | None = None,

    ) -> ReportRun:

        data_rows = [r for r in rows if isinstance(r, dict) and "_meta" not in r]

        storage_key = await get_report_blob_store().save_rows(

            company_id=company_id,

            run_id=run_id,

            rows=data_rows,

        )

        return await self._db.reportrun.update(

            where={"id": run_id},

            data={

                "status": status,

                "rows": Json([]),

                "storageKey": storage_key,

                "rowCount": len(data_rows),

                "errorMessage": error_message,

                "completedAt": datetime.now(timezone.utc),

            },

        )
