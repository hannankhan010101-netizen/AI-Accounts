"""Outbox worker claim SQL (Phase 1 concurrency)."""

from __future__ import annotations

CLAIM_PENDING_SQL = """
UPDATE outbox_events
SET
  status = 'processing',
  attempts = attempts + 1,
  locked_at = NOW()
WHERE id IN (
  SELECT id
  FROM outbox_events
  WHERE status = 'pending'
    AND (next_attempt_at IS NULL OR next_attempt_at <= NOW())
  ORDER BY created_at ASC
  FOR UPDATE SKIP LOCKED
  LIMIT $1
)
RETURNING id
"""
