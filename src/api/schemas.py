from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field, field_validator

# Formato uniforme de error para toda la API

class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[Any] = None


class ErrorResponse(BaseModel):
    error: ErrorDetail

# Recursos de la API

class SolicitudCreate(BaseModel):
    asunto: str = Field(..., min_length=5, max_length=200)
    descripcion: str = Field(default="", max_length=4000)
    area: str = Field(..., min_length=2, max_length=80)
    solicitante: str = Field(..., min_length=5, max_length=120)
    canal: str = Field(default="api", max_length=30)

    @field_validator("asunto", "area", "solicitante")
    @classmethod
    def no_solo_espacios(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("No puede estar vacío o contener solo espacios")
        return v.strip()


class SolicitudResponse(BaseModel):
    id: str
    asunto: str
    descripcion: str
    area: str
    solicitante: str
    canal: str
    estado: str
    categoria: Optional[str] = None
    prioridad: Optional[str] = None
    fecha_creacion: datetime
    fecha_actualizacion: datetime


class SolicitudListResponse(BaseModel):
    total: int
    items: list[SolicitudResponse]