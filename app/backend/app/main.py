from __future__ import annotations

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import get_settings
from app.core.errors import http_exception_handler, validation_exception_handler
from app.modules.auth.controller import router as auth_router
from app.modules.chat.controller import router as chat_router
from app.modules.implements.controller import router as implements_router
from app.modules.ml.controller import router as ml_router
from app.modules.operation_planning.controller import router as operation_planning_router
from app.modules.recommendations.controller import router as recommendations_router
from app.modules.tractors.controller import router as tractors_router


app = FastAPI(
    title="Chatbot de Regulagem de Implementos",
    description="API tecnico-cientifica para recomendacao de arados, grades e tratores.",
    version="0.2.0",
)
settings = get_settings()
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(implements_router, prefix="/api")
app.include_router(tractors_router, prefix="/api")
app.include_router(recommendations_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(ml_router, prefix="/api")
app.include_router(operation_planning_router, prefix="/api")


@app.get("/api/health", tags=["health"])
def health_check():
    return {"status": "ok", "service": "regulagem-implementos-api"}
