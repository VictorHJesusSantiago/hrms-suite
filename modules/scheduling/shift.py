"""Recurso de escalas: Shift."""
from dataclasses import dataclass, field
from typing import Any

from domain.shared import normalize_payload, require_fields, utc_now

RESOURCE = "Shift"
FIELDS = ('employee_id', 'starts_at', 'ends_at')
DEFAULT_STATUS = "active"

@dataclass
class ShiftRecord:
    data: dict[str, Any]
    created_at: str = field(default_factory=utc_now)

    def validate(self) -> None:
        require_fields(self.data, FIELDS[:1])

    def to_dict(self) -> dict[str, Any]:
        return {**self.data, "resource": RESOURCE, "status": self.data.get("status", DEFAULT_STATUS), "created_at": self.created_at}

    def transition(self, status: str) -> dict[str, Any]:
        if status not in {"active", "pending", "completed", "archived"}:
            raise ValueError("Status inválido")
        self.data["status"] = status
        return self.to_dict()

def validate(payload: dict[str, Any]) -> dict[str, Any]:
    record = ShiftRecord(normalize_payload(payload))
    record.validate()
    return record.to_dict()

def create(payload: dict[str, Any]) -> ShiftRecord:
    record = ShiftRecord(normalize_payload(payload))
    record.validate()
    return record
