import logging
import time
from typing import Optional

import requests

from src.ai.base import ClasificadorSolicitudes, ClasificacionResultado
from src.config import settings

logger = logging.getLogger("ai.clasificador")


# Categorías y prioridades
CATEGORIAS_VALIDAS = [
    "Hardware", "Software", "Accesos", "Red", "Viáticos",
    "Vacaciones", "Incidente", "Aplicaciones", "Otros",
]
PRIORIDADES_VALIDAS = ["Crítica", "Alta", "Media", "Baja"]


class ClasificadorIA(ClasificadorSolicitudes):
    # Clasificador que usa la IA
    def __init__(
        self,
        provider_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
    ):
        self.provider_url = provider_url or settings.ai_provider_url
        self.api_key = api_key or settings.ai_api_key
        self.timeout = timeout or settings.ai_timeout
        self.max_retries = max_retries or settings.ai_max_retries

    def clasificar(self, asunto: str, descripcion: str = "") -> ClasificacionResultado:
        texto = f"{asunto}. {descripcion}".strip()

        # Si no hay proveedor configurado: degradado inmediato
        if not self.provider_url or not self.api_key:
            logger.warning("Proveedor de IA no configurado. Activando modo degradado.")
            return self._modo_degradado(texto, motivo="Proveedor de IA no configurado")

        # Intentar con reintentos
        ultimo_error = None
        for intento in range(1, self.max_retries + 1):
            try:
                return self._llamar_proveedor(texto)
            except Exception as e:
                ultimo_error = e
                logger.warning(
                    "Intento %d/%d falló: %s", intento, self.max_retries, e
                )
                if intento < self.max_retries:
                    time.sleep(1.5 * intento)

        # Todos los reintentos fallaron: modo degradado
        logger.error("Proveedor de IA no disponible tras %d intentos. Modo degradado.", self.max_retries)
        return self._modo_degradado(
            texto,
            motivo=f"Proveedor no respondió: {ultimo_error}",
        )

    def _llamar_proveedor(self, texto: str) -> ClasificacionResultado:
        # Usar la IA para clasificar
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "gpt-4o-mini",          # ejemplo; se puede parametrizar
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Eres un clasificador de tickets de mesa de ayuda. "
                        "Responde ÚNICAMENTE con un JSON de la forma: "
                        '{"categoria": "...", "prioridad": "...", "confianza": 0.0-1.0}. '
                        f"Categorías permitidas: {', '.join(CATEGORIAS_VALIDAS)}. "
                        f"Prioridades permitidas: {', '.join(PRIORIDADES_VALIDAS)}."
                    ),
                },
                {"role": "user", "content": texto},
            ],
            "temperature": 0.0,
            "max_tokens": 100,
        }

        response = requests.post(
            self.provider_url,
            headers=headers,
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()
        data = response.json()

        # Adaptar según el formato de la IA
        contenido = data["choices"][0]["message"]["content"]
        import json
        resultado = json.loads(contenido)

        return ClasificacionResultado(
            categoria=resultado.get("categoria", "Otros"),
            prioridad=resultado.get("prioridad", "Media"),
            confianza=float(resultado.get("confianza", 0.5)),
            proveedor="openai",
            modo_degradado=False,
        )

    def _modo_degradado(self, texto: str, motivo: str) -> ClasificacionResultado:
        # Cuando la IA no esta disponible
        texto_lower = texto.lower()

        # Reglas básicas de categoría
        if any(p in texto_lower for p in ["vpn", "acceso", "permiso", "usuario", "login"]):
            categoria = "Accesos"
        elif any(p in texto_lower for p in ["portátil", "laptop", "teclado", "mouse", "pantalla", "hardware"]):
            categoria = "Hardware"
        elif any(p in texto_lower for p in ["software", "aplicación", "programa", "instalar"]):
            categoria = "Software"
        elif any(p in texto_lower for p in ["red", "internet", "wifi", "conectividad"]):
            categoria = "Red"
        elif any(p in texto_lower for p in ["vacaciones", "días libres", "permiso"]):
            categoria = "Vacaciones"
        elif any(p in texto_lower for p in ["viático", "viaje", "transporte"]):
            categoria = "Viáticos"
        else:
            categoria = "Otros"

        # Reglas de prioridad
        if any(p in texto_lower for p in ["urgente", "crítico", "caído", "no funciona", "producción"]):
            prioridad = "Alta"
        elif any(p in texto_lower for p in ["importante", "pronto"]):
            prioridad = "Media"
        else:
            prioridad = "Baja"

        return ClasificacionResultado(
            categoria=categoria,
            prioridad=prioridad,
            confianza=0.3,
            proveedor="reglas-locales",
            modo_degradado=True,
            motivo_degradado=motivo,
        )


# Ejecución
def obtener_clasificador() -> ClasificadorSolicitudes:
    """
    Punto único para obtener el clasificador.
    Facilita cambiar de implementación sin tocar la API.
    """
    return ClasificadorIA()