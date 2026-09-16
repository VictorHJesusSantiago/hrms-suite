from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def require_fields(payload: dict[str, Any], fields: tuple[str, ...]) -> None:
    missing = [name for name in fields if not str(payload.get(name, "")).strip()]
    if missing:
        raise ValueError("Campos obrigatórios: " + ", ".join(missing))


def normalize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {str(key): value for key, value in payload.items() if value is not None}


@dataclass
class DomainRecord:
    name: str
    status: str = "active"
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def activate(self) -> None:
        self.status = "active"

    def archive(self) -> None:
        self.status = "archived"
