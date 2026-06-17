"""Pytest configuration."""

from __future__ import annotations

import os

os.environ.setdefault("SKIP_PRISMA", "1")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-at-least-32-characters-long")
