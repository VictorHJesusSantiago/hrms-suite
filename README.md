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
- `GET|POST /api/records/{module}/{resource}`
- `GET|PATCH|DELETE /api/records/{module}/{resource}/{id}`
- `GET /api/audit`
- `GET /api/openapi.json`
- `POST /api/payroll/preview`
- `POST /api/payroll/run`
- `POST /api/time/clock`
- `GET /api/time/entries`
- `POST /api/people`
- `POST /api/feedback`

## Módulos

Payroll, Time Tracking, Benefits, Recruiting/ATS, Onboarding, Talent, Performance, Learning/LMS, Compensation, Scheduling, Workforce Management e Employee Experience.

O catálogo de domínio contém mais de mil arquivos Python funcionais. Cada arquivo representa um recurso validável com criação e resumo de dados, e os recursos são descobertos automaticamente pela API.

Os registros dos doze módulos usam uma camada CRUD auditável, com validação específica, paginação, transição de status e trilha de auditoria. O contrato OpenAPI está disponível em `/api/openapi.json`.
