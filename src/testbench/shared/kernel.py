"""
Shared Kernel — value objects and types used across all bounded contexts.
"""

from __future__ import annotations
import uuid
from datetime import datetime, timezone

# ─── Identifiers ───────────────────────────────────────────────


def generate_id() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
