from __future__ import annotations

from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.exceptions import HTTPException as StarletteHTTPException


FIELD_LABELS = {
    "area_ha": "Área a preparar",
    "start_date": "Data inicial",
    "end_date": "Data final",
    "hours_per_day": "Horas por dia",
    "message": "Mensagem",
}


class FieldError(BaseModel):
    field: str
    message: str
    type: str


class ErrorResponse(BaseModel):
    code: str
    message: str
    fields: list[FieldError] = Field(default_factory=list)


def _clean_message(message: str) -> str:
    cleaned = message.removeprefix("Value error, ").strip()
    translations = {
        "Field required": "Este campo é obrigatório.",
        "Input should be a valid date or datetime, input is too short": "Informe uma data válida.",
        "Input should be greater than 0": "O valor deve ser maior que zero.",
        "Input should be less than or equal to 24": "O valor deve ser de no máximo 24 horas.",
    }
    return translations.get(cleaned, cleaned)


def _field_name(location: tuple[Any, ...]) -> str:
    parts = [str(part) for part in location if part not in {"body", "query", "path"}]
    return parts[-1] if parts else "request"


async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    fields = []
    for error in exc.errors():
        field = _field_name(tuple(error.get("loc", ())))
        message = _clean_message(str(error.get("msg", "Valor inválido.")))
        fields.append({"field": field, "message": message, "type": str(error.get("type", "value_error"))})

    if len(fields) == 1:
        label = FIELD_LABELS.get(fields[0]["field"])
        message = f"{label}: {fields[0]['message']}" if label else fields[0]["message"]
    else:
        message = "Revise os campos destacados e tente novamente."

    payload = ErrorResponse(code="VALIDATION_ERROR", message=message, fields=fields)
    return JSONResponse(status_code=422, content=payload.model_dump())


async def http_exception_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
    codes = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
    }
    message = exc.detail if isinstance(exc.detail, str) else "Não foi possível concluir a solicitação."
    payload = ErrorResponse(code=codes.get(exc.status_code, "HTTP_ERROR"), message=message)
    return JSONResponse(status_code=exc.status_code, content=payload.model_dump(), headers=exc.headers)
