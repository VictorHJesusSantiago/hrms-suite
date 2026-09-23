"""Recurso de folha: Checklist."""
from dataclasses import dataclass, field
from typing import Any

from domain.shared import normalize_payload, require_fields, utc_now

RESOURCE = "Checklist"
FIELDS = ('employee_id', 'period', 'amount')
DEFAULT_STATUS = "active"

@dataclass
class ChecklistRecord:
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
    record = ChecklistRecord(normalize_payload(payload))
    record.validate()
    return record.to_dict()

def create(payload: dict[str, Any]) -> ChecklistRecord:
    record = ChecklistRecord(normalize_payload(payload))
    record.validate()
    return record
