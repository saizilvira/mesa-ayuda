from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class ClasificacionResultado:
    categoria: str
    prioridad: str
    confianza: float
    proveedor: str
    modo_degradado: bool = False
    motivo_degradado: Optional[str] = None


class ClasificadorSolicitudes(ABC):
    @abstractmethod
    def clasificar(self, asunto: str, descripcion: str = "") -> ClasificacionResultado:
        pass