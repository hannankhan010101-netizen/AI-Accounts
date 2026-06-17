"""ASGI entry (``uvicorn main:app --app-dir src``)."""

from app.main import app

__all__ = ["app"]
