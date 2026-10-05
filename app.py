import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from api_schema import openapi_schema
from config import HOST, PORT, MODULE_LABELS
from db import initialize, insert, rows
from domain.registry import load_resource, resource_catalog
from domain.services import add_employee, clock, dashboard, preview_payroll, run_payroll, seed_demo, submit_feedback
from domain.store import archive_record, audit_events, create_record, get_record, list_records, update_record

ROOT = Path(__file__).parent


class HRMSHandler(BaseHTTPRequestHandler):
    def send_json(self, payload: dict | list, status: int = 200) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)

    def read_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        return json.loads((self.rfile.read(length) or b"{}").decode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PATCH, DELETE, OPTIONS")
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        try:
            if path == "/api/health":
                return self.send_json({"status": "ok", "service": "hrms-suite", "database": "sqlite", "version": "1.0.0"})
            if path == "/api/openapi.json":
                return self.send_json(openapi_schema())
            if path == "/api/dashboard":
                return self.send_json(dashboard())
            if path == "/api/modules":
                return self.send_json({"modules": resource_catalog()})
            if path == "/api/people":
                return self.send_json(rows("SELECT * FROM employees ORDER BY name"))
            if path == "/api/candidates":
                return self.send_json(rows("SELECT * FROM candidates ORDER BY id DESC"))
            if path == "/api/time/entries":
                employee_id = parse_qs(urlparse(self.path).query).get("employee_id", [None])[0]
                query = "SELECT * FROM time_entries ORDER BY id DESC" if employee_id is None else "SELECT * FROM time_entries WHERE employee_id = ? ORDER BY id DESC"
                return self.send_json(rows(query, () if employee_id is None else (int(employee_id),)))
            if path == "/api/audit":
                limit = parse_qs(urlparse(self.path).query).get("limit", [100])[0]
                return self.send_json(audit_events(int(limit)))
            if path.startswith("/api/records/"):
                pieces = path.strip("/").split("/")
                module = pieces[2]
                if module not in MODULE_LABELS:
                    return self.send_json({"error": "Módulo desconhecido"}, 404)
                if len(pieces) == 3:
                    return self.send_json({"module": module, "resources": resource_catalog_for(module)})
                resource = pieces[3]
                if len(pieces) == 4:
                    query = parse_qs(urlparse(self.path).query)
                    return self.send_json(list_records(module, resource, int(query.get("limit", [100])[0]), int(query.get("offset", [0])[0]), query.get("status", [None])[0]))
                return self.send_json(get_record(module, resource, int(pieces[4])))
            if path == "/":
                return self.serve_static("index.html")
            if path.startswith("/static/"):
                return self.serve_static(path.removeprefix("/static/"))
            self.send_json({"error": "Rota não encontrada"}, 404)
        except Exception as exc:
            self.send_json({"error": str(exc)}, 500)

    def do_POST(self):
        path = urlparse(self.path).path
        try:
            body = self.read_body()
            if path == "/api/payroll/preview":
                return self.send_json(preview_payroll(int(body["employee_id"]), float(body.get("bonus", 0))))
            if path == "/api/time/clock":
                return self.send_json(clock(int(body["employee_id"]), body["event"], body.get("note", "")), 201)
            if path == "/api/feedback":
                return self.send_json(submit_feedback(body.get("employee_id"), body["category"], body["message"]), 201)
            if path == "/api/people":
                return self.send_json(add_employee(body), 201)
            if path == "/api/payroll/run":
                return self.send_json(run_payroll(body["period"], float(body.get("bonus", 0))), 201)
            if path == "/api/candidates":
                required = ("name", "email", "job_title")
                if any(not body.get(item) for item in required):
                    return self.send_json({"error": "name, email e job_title são obrigatórios"}, 400)
                return self.send_json(insert("candidates", {**body, "stage": body.get("stage", "applied"), "score": float(body.get("score", 0))}), 201)
            if path.startswith("/api/records/"):
                pieces = path.strip("/").split("/")
                if len(pieces) != 4:
                    return self.send_json({"error": "Use /api/records/{module}/{resource}"}, 400)
                return self.send_json(create_record(pieces[2], pieces[3], body, body.get("actor", "system")), 201)
            self.send_json({"error": "Rota não encontrada"}, 404)
        except (KeyError, ValueError, json.JSONDecodeError) as exc:
            self.send_json({"error": str(exc)}, 400)
        except Exception as exc:
            self.send_json({"error": str(exc)}, 500)

    def do_PATCH(self):
        try:
            path = urlparse(self.path).path
            pieces = path.strip("/").split("/")
            if len(pieces) != 5 or pieces[:2] != ["api", "records"]:
                return self.send_json({"error": "Rota não encontrada"}, 404)
            body = self.read_body()
            return self.send_json(update_record(pieces[2], pieces[3], int(pieces[4]), body, body.get("actor", "system")))
        except (KeyError, ValueError, json.JSONDecodeError) as exc:
            self.send_json({"error": str(exc)}, 400)
        except Exception as exc:
            self.send_json({"error": str(exc)}, 500)

    def do_DELETE(self):
        try:
            pieces = urlparse(self.path).path.strip("/").split("/")
            if len(pieces) != 5 or pieces[:2] != ["api", "records"]:
                return self.send_json({"error": "Rota não encontrada"}, 404)
            return self.send_json(archive_record(pieces[2], pieces[3], int(pieces[4])))
        except (KeyError, ValueError) as exc:
            self.send_json({"error": str(exc)}, 400)
        except Exception as exc:
            self.send_json({"error": str(exc)}, 500)

    def serve_static(self, name: str) -> None:
        path = (ROOT / "static" / name).resolve()
        if not path.is_file() or ROOT not in path.parents:
            return self.send_json({"error": "Arquivo não encontrado"}, 404)
        content_type = "text/html; charset=utf-8" if path.suffix == ".html" else "text/css; charset=utf-8" if path.suffix == ".css" else "application/javascript; charset=utf-8"
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def resource_catalog_for(module: str) -> list[dict]:
    result = []
    for item in resource_catalog():
        if item["key"] != module:
            continue
        for resource in item["resources"]:
            loaded = load_resource(module, resource)
            result.append({"resource": resource, "label": loaded.RESOURCE, "fields": list(loaded.FIELDS)})
    return result


if __name__ == "__main__":
    initialize()
    seed_demo()
    server = ThreadingHTTPServer((HOST, PORT), HRMSHandler)
    print(f"HRMS Suite em http://{HOST}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
