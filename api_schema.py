from config import MODULE_LABELS


def openapi_schema() -> dict:
    resources = {module: "Use /api/records/{module}/{resource} para CRUD" for module in MODULE_LABELS}
    return {
        "openapi": "3.0.3",
        "info": {"title": "HRMS Suite API", "version": "1.0.0", "description": "API modular de gestão de pessoas."},
        "paths": {
            "/api/health": {"get": {"responses": {"200": {"description": "Serviço disponível"}}}},
            "/api/dashboard": {"get": {"responses": {"200": {"description": "Indicadores executivos"}}}},
            "/api/modules": {"get": {"responses": {"200": {"description": "Catálogo dos módulos"}}}},
            "/api/records/{module}/{resource}": {"get": {"responses": {"200": {"description": "Lista de registros"}}}, "post": {"responses": {"201": {"description": "Registro criado"}}}},
            "/api/records/{module}/{resource}/{id}": {"get": {"responses": {"200": {"description": "Registro"}}}, "patch": {"responses": {"200": {"description": "Registro atualizado"}}}, "delete": {"responses": {"200": {"description": "Registro arquivado"}}}},
            "/api/payroll/run": {"post": {"responses": {"201": {"description": "Folha processada"}}}},
            "/api/time/clock": {"post": {"responses": {"201": {"description": "Ponto registrado"}}}},
            "/api/feedback": {"post": {"responses": {"201": {"description": "Feedback registrado"}}}},
        },
        "x-modules": resources,
    }
