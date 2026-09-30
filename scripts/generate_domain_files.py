from pathlib import Path
import re

ROOT = Path(__file__).parents[1]
MODULES = {
    "payroll": "folha",
    "time_tracking": "ponto",
    "benefits": "beneficios",
    "recruiting": "ats",
    "onboarding": "onboarding",
    "talent": "talentos",
    "performance": "desempenho",
    "learning": "lms",
    "compensation": "remuneracao",
    "scheduling": "escalas",
    "wfm": "wfm",
    "employee_experience": "experiencia",
}

SHARED = [
    "approval_request", "audit_entry", "automation_rule", "calendar_event", "comment", "configuration", "cost_center", "custom_field", "document", "eligibility_rule", "escalation", "event_subscription", "goal", "integration", "notification", "policy", "questionnaire", "report", "review_cycle", "workflow", "assignment", "attachment", "budget", "checklist", "compliance_item", "dashboard_widget", "decision", "directory_entry", "exception_case", "export_job", "form_template", "import_job", "insight", "kpi", "milestone", "outcome", "permission", "queue_item", "reminder", "risk", "scorecard", "segment", "service_request", "survey", "tag", "task", "template", "threshold", "timeline_event", "training_plan", "user_preference", "webhook", "workspace", "activity_log", "agreement", "approver", "availability", "capacity_plan", "change_request", "channel", "check_in", "classification", "coverage", "data_quality_rule", "delegation", "engagement", "handoff", "incident", "intake", "job_level", "location", "metric", "operating_hour", "ownership", "priority_rule", "recognition", "resource_pool", "retention_rule", "role_assignment", "service_level", "status_history", "team", "time_window", "value_driver", "version", "visibility_rule", "work_item", "year_plan",
]

SPECIFIC = {
    "payroll": ["payroll_run", "payroll_item", "salary_component", "tax_bracket", "deduction", "earning", "advance_payment", "bonus_policy", "termination_calculation", "vacation_calculation", "thirteenth_salary", "social_security", "income_tax", "bank_file", "payslip", "payroll_calendar", "payroll_closure", "retroactive_adjustment", "cost_allocation", "payroll_validation"],
    "time_tracking": ["time_entry", "attendance_policy", "overtime_request", "break_rule", "absence", "leave_request", "holiday", "timesheet", "geofence", "device", "clock_correction", "schedule_exception", "bank_of_hours", "attendance_alert", "workday", "rest_period", "remote_workday", "attendance_closure", "presence_status", "time_balance"],
    "benefits": ["benefit_plan", "enrollment", "dependent", "provider", "allowance", "meal_card", "health_plan", "dental_plan", "life_insurance", "transport_voucher", "wellness_credit", "benefit_invoice", "eligibility_snapshot", "benefit_claim", "benefit_budget", "open_enrollment", "benefit_comparison", "benefit_portability", "benefit_usage", "benefit_statement"],
    "recruiting": ["job_opening", "candidate", "application", "interview", "interview_panel", "candidate_score", "resume", "talent_pool", "offer", "offer_approval", "requisition", "sourcing_campaign", "referral", "recruiter", "candidate_message", "pipeline_stage", "assessment", "background_check", "hiring_decision", "recruiting_metric"],
    "onboarding": ["onboarding_plan", "onboarding_task", "new_hire", "document_request", "equipment_request", "access_request", "welcome_event", "buddy_assignment", "probation_checkin", "onboarding_form", "policy_acknowledgement", "first_week_plan", "orientation", "onboarding_survey", "offboarding_plan", "exit_task", "knowledge_handoff", "departure_reason", "exit_interview", "offboarding_checklist"],
    "talent": ["talent_profile", "skill", "skill_assessment", "career_path", "succession_plan", "talent_review", "potential_rating", "nine_box", "mentorship", "mentor_match", "development_plan", "mobility_request", "internal_opportunity", "high_potential", "critical_role", "talent_pool", "readiness_level", "career_conversation", "growth_action", "talent_metric"],
    "performance": ["performance_review", "objective", "key_result", "feedback_request", "one_on_one", "checkin", "rating", "calibration", "review_comment", "competency", "competency_rating", "performance_plan", "recognition_event", "review_goal", "review_signoff", "review_template", "review_question", "performance_cycle", "manager_summary", "performance_metric"],
    "learning": ["course", "learning_path", "lesson", "enrollment", "learning_assignment", "certificate", "quiz", "quiz_attempt", "learning_provider", "content_item", "classroom_session", "instructor", "lms_catalog", "learning_budget", "learning_request", "mandatory_training", "skill_badge", "learning_transcript", "course_feedback", "learning_metric"],
    "compensation": ["compensation_cycle", "salary_review", "pay_band", "market_benchmark", "merit_budget", "bonus_plan", "bonus_award", "equity_grant", "promotion_case", "compensation_statement", "total_rewards", "compa_ratio", "salary_history", "pay_equity_analysis", "compensation_approval", "commission_plan", "commission_result", "retention_offer", "reward_preference", "compensation_metric"],
    "scheduling": ["shift", "shift_template", "rota", "schedule_rule", "schedule_assignment", "shift_swap", "shift_bid", "availability_window", "schedule_publish", "coverage_request", "schedule_conflict", "shift_note", "break_schedule", "shift_demand", "roster", "rotation", "schedule_exception", "shift_cost", "schedule_approval", "schedule_metric"],
    "wfm": ["workforce_plan", "demand_forecast", "capacity_model", "staffing_requirement", "queue_forecast", "intraday_action", "service_level_target", "occupancy_metric", "shrinkage_plan", "agent_state", "workload", "forecast_version", "scenario", "scenario_assumption", "workforce_alert", "productivity_metric", "contact_volume", "response_time", "wfm_dashboard", "wfm_metric"],
    "employee_experience": ["experience_survey", "pulse_check", "employee_feedback", "listening_campaign", "recognition", "wellbeing_check", "culture_signal", "engagement_score", "employee_story", "community", "event", "internal_communication", "idea", "idea_vote", "mood_checkin", "journey_stage", "experience_action", "belonging_indicator", "ex_index", "experience_metric"],
}


def class_name(resource: str) -> str:
    return "".join(part.title() for part in resource.split("_")) + "Record"


def make_file(module: str, resource: str) -> str:
    title = resource.replace("_", " ").title()
    cls = class_name(resource)
    field_sets = {
        "payroll": ("employee_id", "period", "amount"), "time_tracking": ("employee_id", "occurred_at", "event"), "benefits": ("employee_id", "provider", "value"),
        "recruiting": ("candidate_id", "job_title", "stage"), "onboarding": ("employee_id", "due_date", "owner"), "talent": ("employee_id", "skill", "level"),
        "performance": ("employee_id", "cycle", "score"), "learning": ("employee_id", "course_id", "progress"), "compensation": ("employee_id", "cycle", "value"),
        "scheduling": ("employee_id", "starts_at", "ends_at"), "wfm": ("period", "team", "capacity"), "employee_experience": ("employee_id", "category", "score"),
    }
    fields = field_sets[module]
    return f'''"""Recurso de {MODULES[module]}: {title}."""
from dataclasses import dataclass, field
from typing import Any

from domain.shared import normalize_payload, require_fields, utc_now

RESOURCE = "{title}"
FIELDS = {fields!r}
DEFAULT_STATUS = "active"

@dataclass
class {cls}:
    data: dict[str, Any]
    created_at: str = field(default_factory=utc_now)

    def validate(self) -> None:
        require_fields(self.data, FIELDS[:1])

    def to_dict(self) -> dict[str, Any]:
        return {{**self.data, "resource": RESOURCE, "status": self.data.get("status", DEFAULT_STATUS), "created_at": self.created_at}}

    def transition(self, status: str) -> dict[str, Any]:
        if status not in {{"active", "pending", "completed", "archived"}}:
            raise ValueError("Status inválido")
        self.data["status"] = status
        return self.to_dict()

def validate(payload: dict[str, Any]) -> dict[str, Any]:
    record = {cls}(normalize_payload(payload))
    record.validate()
    return record.to_dict()

def create(payload: dict[str, Any]) -> {cls}:
    record = {cls}(normalize_payload(payload))
    record.validate()
    return record
'''


def main() -> None:
    for module, label in MODULES.items():
        package = ROOT / "modules" / module
        package.mkdir(parents=True, exist_ok=True)
        (package / "__init__.py").write_text(f'"""Recursos funcionais de {label}."""\n', encoding="utf-8")
        resources = list(dict.fromkeys(SPECIFIC[module] + SHARED))
        for resource in resources:
            (package / f"{resource}.py").write_text(make_file(module, resource), encoding="utf-8")
        if len(resources) < 100:
            raise RuntimeError(f"Esperados pelo menos 100 recursos em {module}, encontrados {len(resources)}")


if __name__ == "__main__":
    main()
