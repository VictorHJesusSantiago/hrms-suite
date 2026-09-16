class DomainError(Exception):
    """Erro esperado de validação ou regra de negócio."""


class NotFoundError(DomainError):
    """Recurso solicitado não encontrado."""


def error_payload(message: str, status: int = 400) -> tuple[dict, int]:
    return {"error": message, "status": status}, status
