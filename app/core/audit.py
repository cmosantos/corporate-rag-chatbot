import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from fastapi import Depends

from app.core.config import Settings, get_settings


class AuditLogger:
    def __init__(self, path: Path) -> None:
        self.path = path

    def write(
        self,
        event: str,
        *,
        user_id: str,
        conversation_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        route: str | None = None,
    ) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "timestamp": datetime.now(UTC).isoformat(),
            "event": event,
            "user_id": user_id,
            "conversation_id": conversation_id,
            "route": route,
            "metadata": metadata or {},
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")


def get_audit_logger(settings: Settings = Depends(get_settings)) -> AuditLogger:
    return AuditLogger(settings.audit_log_path)

