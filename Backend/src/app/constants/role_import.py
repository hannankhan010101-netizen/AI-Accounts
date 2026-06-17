"""Role import tuning — P34."""

from __future__ import annotations

# Sync upload above this row count is auto-queued as a background job.
ROLE_IMPORT_ASYNC_THRESHOLD = 50
ROLE_IMPORT_JOB_TYPE = "roles"
