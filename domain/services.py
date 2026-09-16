from datetime import datetime

from db import insert, rows
from domain.shared import utc_now


def seed_demo() -> None:
    if rows("SELECT id FROM employees LIMIT 1"):
        return
    employees = [
        ("Ana Souza", "ana@acme.test", "Produto", "Product Manager", 12500),
        ("Bruno Lima", "bruno@acme.test", "Engenharia", "Software Engineer", 9800),
        ("Carla Mendes", "carla@acme.test", "Pessoas", "People Partner", 8600),
    ]
    for name, email, department, role, salary in employees:
        insert("employees", {"name": name, "email": email, "department": department, "role": role, "salary": salary})
    for title, hours, rate in [("Liderança inclusiva", 6, 68), ("LGPD para RH", 3, 82), ("Gestão ágil", 8, 41)]:
        insert("courses", {"title": title, "duration_hours": hours, "completion_rate": rate})
    insert("candidates", {"name": "Diego Rocha", "email": "diego@candidate.test", "job_title": "UX Designer", "stage": "interview", "score": 87})


def dashboard() -> dict:
    counts = {
        "employees": rows("SELECT COUNT(*) AS value FROM employees")[0]["value"],
        "open_candidates": rows("SELECT COUNT(*) AS value FROM candidates WHERE stage NOT IN ('hired', 'rejected')")[0]["value"],
        "active_benefits": rows("SELECT COUNT(*) AS value FROM benefits WHERE active = 1")[0]["value"],
        "learning_courses": rows("SELECT COUNT(*) AS value FROM courses")[0]["value"],
    }
    payroll = rows("SELECT * FROM payroll_runs ORDER BY id DESC LIMIT 5")
    return {"counts": counts, "payroll": payroll, "generated_at": utc_now()}


def preview_payroll(employee_id: int, bonus: float = 0) -> dict:
    employee = rows("SELECT * FROM employees WHERE id = ?", (employee_id,))
    if not employee:
        raise ValueError("Colaborador não encontrado")
    gross = round(float(employee[0]["salary"]) + float(bonus), 2)
    deductions = round(gross * 0.11, 2)
    benefits = rows("SELECT COALESCE(SUM(value), 0) AS value FROM benefits WHERE employee_id = ? AND active = 1", (employee_id,))[0]["value"]
    return {"employee": employee[0], "gross": gross, "deductions": deductions, "benefits": benefits, "net": round(gross - deductions, 2)}


def clock(employee_id: int, event: str, note: str = "") -> dict:
    if event not in {"in", "out", "break_start", "break_end"}:
        raise ValueError("Evento de ponto inválido")
    if not rows("SELECT id FROM employees WHERE id = ?", (employee_id,)):
        raise ValueError("Colaborador não encontrado")
    return insert("time_entries", {"employee_id": employee_id, "event": event, "occurred_at": utc_now(), "note": note})


def submit_feedback(employee_id: int | None, category: str, message: str) -> dict:
    if not message.strip():
        raise ValueError("A mensagem é obrigatória")
    sentiment = "positive" if any(word in message.lower() for word in ("obrigado", "ótimo", "gosto", "bom")) else "neutral"
    return insert("feedback", {"employee_id": employee_id, "category": category, "message": message.strip(), "sentiment": sentiment, "created_at": utc_now()})
