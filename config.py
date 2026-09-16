from pathlib import Path

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
DB_PATH = DATA_DIR / "hrms.sqlite3"
HOST = "127.0.0.1"
PORT = 8080

MODULE_LABELS = {
    "payroll": "Folha de pagamento",
    "time_tracking": "Controle de ponto",
    "benefits": "Benefícios",
    "recruiting": "Recrutamento / ATS",
    "onboarding": "Onboarding",
    "talent": "Gestão de talentos",
    "performance": "Desempenho",
    "learning": "Treinamento / LMS",
    "compensation": "Remuneração",
    "scheduling": "Escalas",
    "wfm": "Workforce Management",
    "employee_experience": "Employee Experience",
}
