# HRMS Suite

Suíte modular de RH para operações de pessoas, folha, ponto, benefícios, recrutamento, onboarding, talentos, desempenho, aprendizagem, remuneração, escalas, WFM e Employee Experience.

## Executar

```powershell
python app.py
```

Abra `http://127.0.0.1:8080`. A aplicação usa somente a biblioteca padrão do Python e cria `data/hrms.sqlite3` automaticamente.

## API principal

- `GET /api/health`
- `GET /api/dashboard`
- `GET /api/modules`
- `GET /api/records/{module}`
- `POST /api/records/{module}`
- `POST /api/payroll/preview`
- `POST /api/time/clock`
- `POST /api/feedback`

## Módulos

Payroll, Time Tracking, Benefits, Recruiting/ATS, Onboarding, Talent, Performance, Learning/LMS, Compensation, Scheduling, Workforce Management e Employee Experience.

O catálogo de domínio contém mais de mil arquivos Python funcionais. Cada arquivo representa um recurso validável com criação e resumo de dados, e os recursos são descobertos automaticamente pela API.
