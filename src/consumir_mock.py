import logging
import time
from typing import Any, Optional

import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

# Configuración

BASE_URL = "http://127.0.0.1:8080"
TOKEN = "demo-token-prueba-2026"
TIMEOUT = 5
MAX_REINTENTOS = 3
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json",
}


class ServicioMockError(Exception):
    pass

# Manejar respuestas

def _manejar_respuesta(response: requests.Response) -> dict:
    # De acuerdo al codigo de estado se devuelve la respuesta

    if response.status_code == 200 or response.status_code == 201:
        return response.json()

    
    if response.status_code == 401:
        raise ServicioMockError(
            "No autorizado: falta el token o es inválido."
        )

    if response.status_code == 429:
        retry_after = response.headers.get("Retry-After", "desconocido")
        raise ServicioMockError(
            f"Muchas peticiones: Reintentar después de {retry_after} segundos."
        )

    if response.status_code >= 500:
        raise ServicioMockError(
            f"Error interno: ({response.status_code}). "
        )

    raise ServicioMockError(
        f"Respuesta inesperada: {response.status_code} - {response.text[:200]}"
    )

# Obtener solicitudes

def get_solicitudes(
    area: Optional[str] = None,
    estado: Optional[str] = None,
    limite: int = 10,
) -> list[dict]:
    
    params = {"limite": limite}
    if area:
        params["area"] = area
    if estado:
        params["estado"] = estado

    # Petición GET a /solicitudes
    url = f"{BASE_URL}/solicitudes"
    logger.info("GET %s params=%s", url, params)

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            params=params,
            timeout=TIMEOUT,
        )
        data = _manejar_respuesta(response)
        logger.info("GET: Se recibieron %d solicitudes.", len(data) if isinstance(data, list) else 1)
        return data if isinstance(data, list) else [data]

    except requests.exceptions.Timeout:
        raise ServicioMockError(
            f"Timeout: el servicio no respondió en {TIMEOUT} segundos."
        )
    except requests.exceptions.ConnectionError:
        raise ServicioMockError(
            "No se pudo conectar con el servicio."
        )

# Crear solicitud

def post_solicitud(
    asunto: str,
    area: str,
    solicitante: str,
    descripcion: str = "",
    canal: str = "api",
    idempotency_key: Optional[str] = None,
) -> dict:

    payload = {
        "asunto": asunto,
        "area": area,
        "solicitante": solicitante,
        "descripcion": descripcion,
        "canal": canal,
    }

    headers = HEADERS.copy()
    if idempotency_key:
        headers["Idempotency-Key"] = idempotency_key

    # Petición POST a /solicitudes
    url = f"{BASE_URL}/solicitudes"
    logger.info("POST %s payload=%s", url, payload)

    try:
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=TIMEOUT,
        )
        data = _manejar_respuesta(response)
        logger.info("POST: Solicitud creada: %s", data.get("id", data))
        return data

    except requests.exceptions.Timeout:
        raise ServicioMockError(
            f"Timeout: el servicio no respondió en {TIMEOUT} segundos."
        )
    except requests.exceptions.ConnectionError:
        raise ServicioMockError(
            "No se pudo conectar con el servicio"
        )

# Reintentar peticiones 

def consumir_con_reintento(funcion, *args, **kwargs) -> Any:

    ultimo_error = None
    for intento in range(1, MAX_REINTENTOS + 1):
        try:
            return funcion(*args, **kwargs)
        except ServicioMockError as e:
            ultimo_error = e
            logger.warning("Intento %d/%d falló: %s", intento, MAX_REINTENTOS, e)
            if intento < MAX_REINTENTOS:
                time.sleep(1.5 * intento)
    raise ServicioMockError(
        f"Se agotaron los {MAX_REINTENTOS} reintentos. Último error: {ultimo_error}"
    )


# Ejecución 

if __name__ == "__main__":
    print("=== Consumo del servicio (Etapa 1) ===\n")

    # 1. GET
    try:
        print("Realizando petición GET...")
        solicitudes = consumir_con_reintento(get_solicitudes, limite=5)
        print(f"   OK — se recibieron {len(solicitudes)} solicitudes")
        if solicitudes:
            print(f"   Solicitud: {solicitudes[0]}")
    except ServicioMockError as e:
        print(f"   ERROR: {e}")

    print()

    # 2. POST
    try:
        print("Realizando petción POST...")
        nueva = consumir_con_reintento(
            post_solicitud,
            asunto="Prueba técnica: Acceso VPN",
            area="Infraestructura",
            solicitante="armando.saiz@correo.com",
            descripcion="Solicitud para la prueba técnica Ing. IA Middle I.",
            idempotency_key="prueba-etapa1-001",
        )
        print(f"   Solicitud creada: {nueva}")
    except ServicioMockError as e:
        print(f"   ERROR: {e}")

    print("\n=== Fin de la demostración ===")