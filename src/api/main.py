import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.responses import JSONResponse

from src.api.schemas import (
    ErrorResponse,
    ErrorDetail,
    SolicitudCreate,
    SolicitudResponse,
    SolicitudListResponse,
)
from src.config import settings

from src.ai.clasificador import obtener_clasificador

from src.rag.retriever import RetrieverPoliticas
from src.api.schemas import ConsultaRAGRequest, ConsultaRAGResponse, CitaResponse

_retriever: Optional[RetrieverPoliticas] = None

def get_retriever() -> RetrieverPoliticas:
    global _retriever
    if _retriever is None:
        _retriever = RetrieverPoliticas()
    return _retriever

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("api")

# Base de datos en memoria
_db: dict[str, dict] = {}

# App
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="API de la Mesa de Ayuda",
)

# Manejador uniforme de errores
@app.exception_handler(Exception)
async def unhandled_exception_handler(request, exc):
    logger.exception("Error no controlado: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error=ErrorDetail(
                code="internal_error",
                message="Error interno del servidor",
                details=str(exc) if settings.environment == "development" else None,
            )
        ).model_dump(),
    )

# Endpoints
@app.post(
    "/solicitudes",
    response_model=SolicitudResponse,
    status_code=status.HTTP_201_CREATED,
    responses={422: {"model": ErrorResponse}},
    summary="Crear una nueva solicitud",
)
def crear_solicitud(payload: SolicitudCreate):
    #La categoría y prioridad quedan en null, la idea es asignarlas con el módulo de IA
    now = datetime.now(timezone.utc)
    solicitud_id = f"SOL-{uuid.uuid4().hex[:8].upper()}"

    clasificador = obtener_clasificador()
    clasificacion = clasificador.clasificar(payload.asunto, payload.descripcion)

    registro = {
        "id": solicitud_id,
        "asunto": payload.asunto,
        "descripcion": payload.descripcion,
        "area": payload.area,
        "solicitante": payload.solicitante,
        "canal": payload.canal,
        "estado": "Abierto",
        "categoria": None,
        "prioridad": None,
        "fecha_creacion": now,
        "fecha_actualizacion": now,
    }

    registro["categoria"] = clasificacion.categoria
    registro["prioridad"] = clasificacion.prioridad

    if clasificacion.modo_degradado:
        logger.warning(
            "clasificacion_degradada",
            extra={
                "solicitud_id": solicitud_id,
                "motivo": clasificacion.motivo_degradado,
            },
        )
    else:
        logger.info(
            "clasificacion_ok",
            extra={
                "solicitud_id": solicitud_id,
                "categoria": clasificacion.categoria,
                "prioridad": clasificacion.prioridad,
                "confianza": clasificacion.confianza,
            },
        )

    _db[solicitud_id] = registro

    logger.info(
        "solicitud_creada",
        extra={"solicitud_id": solicitud_id, "area": payload.area},
    )
    return SolicitudResponse(**registro)


@app.get(
    "/solicitudes/{solicitud_id}",
    response_model=SolicitudResponse,
    responses={
        404: {"model": ErrorResponse},
    },
    summary="Consultar estado de una solicitud",
)
def obtener_solicitud(solicitud_id: str):
    registro = _db.get(solicitud_id)
    if not registro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=ErrorDetail(
                code="not_found",
                message=f"No existe la solicitud {solicitud_id}",
            ).model_dump(),
        )
    return SolicitudResponse(**registro)


@app.get(
    "/solicitudes",
    response_model=SolicitudListResponse,
    summary="Listar solicitudes con filtros",
)
def listar_solicitudes(
    area: Optional[str] = Query(None, description="Filtrar por área"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    limit: int = Query(20, ge=1, le=100, description="Máximo de resultados"),
    offset: int = Query(0, ge=0, description="Desplazamiento"),
):
    items = list(_db.values())

    if area:
        items = [s for s in items if s["area"].lower() == area.lower()]
    if estado:
        items = [s for s in items if s["estado"].lower() == estado.lower()]

    total = len(items)
    items = items[offset : offset + limit]

    return SolicitudListResponse(
        total=total,
        items=[SolicitudResponse(**s) for s in items],
    )


@app.get("/health", summary="Health check")
def health():
    return {"status": "ok", "version": settings.app_version}

# RAG
@app.post(
    "/consultar-politicas",
    response_model=ConsultaRAGResponse,
    summary="Consultar políticas internas (RAG)",
)
def consultar_politicas(payload: ConsultaRAGRequest):
    # Responde preguntas sobre las políticas internas.
    retriever = get_retriever()
    resultado = retriever.consultar(payload.pregunta)

    return ConsultaRAGResponse(
        respuesta=resultado.respuesta,
        tiene_evidencia=resultado.tiene_evidencia,
        citas=[
            CitaResponse(
                documento=c.documento,
                pagina=c.pagina,
                fragmento=c.fragmento,
                score=c.score,
            )
            for c in resultado.citas
        ],
        mensaje_abstencion=resultado.mensaje_abstencion,
    )