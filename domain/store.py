"""Persistência CRUD para qualquer recurso dos módulos HRMS."""

import json
from typing import Any

from db import connection
from domain.registry import load_resource
from domain.shared import utc_now


def _resource(module: str, resource: str):
    loaded = load_resource(module, resource)
    if not hasattr(loaded, "validate"):
        raise ValueError(f"Recurso sem validador: {module}/{resource}")
    return loaded


def _audit(conn, module: str, resource: str, record_id: int | None, action: str, details: dict[str, Any]) -> None:
    conn.execute(
        "INSERT INTO audit_events (module, resource, record_id, action, details, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (module, resource, record_id, action, json.dumps(details, ensure_ascii=False), utc_now()),
    )


def create_record(module: str, resource: str, payload: dict[str, Any], actor: str = "system") -> dict[str, Any]:
    definition = _resource(module, resource)
    clean = definition.validate(dict(payload))
    now = utc_now()
    status = str(clean.get("status", "active"))
    with connection() as conn:
        cursor = conn.execute(
            "INSERT INTO domain_records (module, resource, payload, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (module, resource, json.dumps(clean, ensure_ascii=False), status, now, now),
        )
        record_id = cursor.lastrowid
        _audit(conn, module, resource, record_id, "created", {"actor": actor, "payload": clean})
    return get_record(module, resource, record_id)


def list_records(module: str, resource: str, limit: int = 100, offset: int = 0, status: str | None = None) -> list[dict[str, Any]]:
    _resource(module, resource)
    limit = max(1, min(int(limit), 500))
    offset = max(0, int(offset))
    query = "SELECT * FROM domain_records WHERE module = ? AND resource = ?"
    params: list[Any] = [module, resource]
    if status:
        query += " AND status = ?"
        params.append(status)
    query += " ORDER BY id DESC LIMIT ? OFFSET ?"
    params.extend((limit, offset))
    with connection() as conn:
        records = conn.execute(query, tuple(params)).fetchall()
    return [_row_to_record(row) for row in records]


def get_record(module: str, resource: str, record_id: int) -> dict[str, Any]:
    _resource(module, resource)
    with connection() as conn:
        row = conn.execute(
            "SELECT * FROM domain_records WHERE module = ? AND resource = ? AND id = ?",
            (module, resource, int(record_id)),
        ).fetchone()
    if row is None:
        raise ValueError("Registro não encontrado")
    return _row_to_record(row)


def update_record(module: str, resource: str, record_id: int, changes: dict[str, Any], actor: str = "system") -> dict[str, Any]:
    current = get_record(module, resource, record_id)
    merged = {**current["payload"], **changes}
    definition = _resource(module, resource)
    clean = definition.validate(merged)
    now = utc_now()
    status = str(clean.get("status", current["status"]))
    with connection() as conn:
        cursor = conn.execute(
            "UPDATE domain_records SET payload = ?, status = ?, updated_at = ? WHERE module = ? AND resource = ? AND id = ?",
            (json.dumps(clean, ensure_ascii=False), status, now, module, resource, int(record_id)),
        )
        if cursor.rowcount != 1:
            raise ValueError("Registro não encontrado")
        _audit(conn, module, resource, int(record_id), "updated", {"actor": actor, "changes": changes})
    return get_record(module, resource, record_id)


def archive_record(module: str, resource: str, record_id: int, actor: str = "system") -> dict[str, Any]:
    return update_record(module, resource, record_id, {"status": "archived"}, actor)


def audit_events(limit: int = 100) -> list[dict[str, Any]]:
    with connection() as conn:
        rows = conn.execute("SELECT * FROM audit_events ORDER BY id DESC LIMIT ?", (max(1, min(int(limit), 500)),)).fetchall()
    return [dict(row) | {"details": json.loads(row["details"])} for row in rows]


def _row_to_record(row) -> dict[str, Any]:
    return {
        "id": row["id"], "module": row["module"], "resource": row["resource"], "payload": json.loads(row["payload"]),
        "status": row["status"], "created_at": row["created_at"], "updated_at": row["updated_at"],
    }
