import csv
import logging
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Optional

# Configuración
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

# Para pasar los meses en español a inglés (formato DD-Mon-YYYY)
MESES_ES = {
    "ene": "Jan", "feb": "Feb", "mar": "Mar", "abr": "Apr",
    "may": "May", "jun": "Jun", "jul": "Jul", "ago": "Aug",
    "sep": "Sep", "oct": "Oct", "nov": "Nov", "dic": "Dec",
}

# Formatos de fecha que están en el CSV
FORMATOS_FECHA = (
    "%Y-%m-%d",      # 2025-03-08
    "%d/%m/%Y",      # 03/06/2025
    "%d-%b-%Y",      # 30-Jun-2025
)

# Normlizar las prioridades
PRIORIDAD_NORMALIZADA = {
    "alta": "Alta",
    "1-alta": "Alta",
    "media": "Media",
    "2-media": "Media",
    "baja": "Baja",
    "3-baja": "Baja",
    "critica": "Crítica",
    "crítica": "Crítica",
}

# Funciones para normalizar

def normalizar_fecha(valor: Optional[str]) -> Optional[str]:

    # Convierte las fechas a formato ISO YYYY-MM-DD.

    if valor is None:
        return None

    valor = str(valor).strip()
    if not valor:
        return None

    # Traducir mes si viene en formato DD-Mon-YYYY
    partes = valor.split("-")
    if len(partes) == 3 and partes[1].lower() in MESES_ES:
        valor = f"{partes[0]}-{MESES_ES[partes[1].lower()]}-{partes[2]}"

    for fmt in FORMATOS_FECHA:
        try:
            fecha = datetime.strptime(valor, fmt)
            return fecha.strftime("%Y-%m-%d")
        except ValueError:
            continue

    # Si ningún formato funcionó
    logger.warning("Fecha no reconocida: %r", valor)
    return None


def normalizar_categoria(valor: Optional[str]) -> str:

    # Deja la primera letra en mayúscula y el resto en minúscula.

    if valor is None:
        return "Sin clasificar"

    valor = str(valor).strip()
    if not valor:
        return "Sin clasificar"

    return valor.capitalize()


def normalizar_prioridad(valor: Optional[str]) -> str:

    # Convierte las distintas formas escritas de prioridad

    if valor is None:
        return "Sin prioridad"

    clave = str(valor).strip().lower()
    if not clave:
        return "Sin prioridad"

    return PRIORIDAD_NORMALIZADA.get(clave, "Sin prioridad")


def normalizar_estado(valor: Optional[str]) -> str:

    if valor is None:
        return "Desconocido"
    valor = str(valor).strip()
    if not valor:
        return "Desconocido"
    return valor.capitalize()


# ---------------------------------------------------------------------------
# Validación y limpieza principal
# ---------------------------------------------------------------------------

def es_registro_valido(fila: dict) -> bool:

    # Valida que las filas tengan id y una fecha de creación válida.

    if not fila.get("id") or not str(fila["id"]).strip():
        return False
    if not fila.get("fecha_creacion"):
        return False
    return True


def limpiar_tickets(ruta_entrada: str, ruta_salida: str, ruta_resumen: str) -> dict:
    
    # Lee el CSV, normaliza campos, elimina duplicados, descarta registros inválidos, 
    # escribe archivo limpio y genera resumen por área y prioridad.

    ruta_entrada = Path(ruta_entrada)
    if not ruta_entrada.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_entrada}")

    registros_limpios = []
    ids_vistos = set()
    descartados = 0
    duplicados = 0

    with open(ruta_entrada, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        # Valida que el archivo no este vacío y tenga cabeceras
        if reader.fieldnames is None:
            logger.warning("El archivo no tiene cabeceras")
            return {"total_leidos": 0, "limpios": 0, "duplicados": 0, "descartados": 0}

        for fila in reader:
            # Normalización
            fila_norm = {
                "id": str(fila.get("id", "")).strip(),
                "fecha_creacion": normalizar_fecha(fila.get("fecha_creacion")),
                "fecha_cierre": normalizar_fecha(fila.get("fecha_cierre")),
                "area": str(fila.get("area", "")).strip() or "Sin área",
                "categoria": normalizar_categoria(fila.get("categoria")),
                "prioridad": normalizar_prioridad(fila.get("prioridad")),
                "canal": str(fila.get("canal", "")).strip(),
                "solicitante": str(fila.get("solicitante", "")).strip(),
                "asunto": str(fila.get("asunto", "")).strip(),
                "descripcion": str(fila.get("descripcion", "")).strip(),
                "estado": normalizar_estado(fila.get("estado")),
                "reaperturas": fila.get("reaperturas", "0"),
            }

            # Validación
            if not es_registro_valido(fila_norm):
                descartados += 1
                continue

            # Deduplicación por id
            if fila_norm["id"] in ids_vistos:
                duplicados += 1
                continue

            ids_vistos.add(fila_norm["id"])
            registros_limpios.append(fila_norm)

    # Escribir archivo limpio
    Path(ruta_salida).parent.mkdir(parents=True, exist_ok=True)
    if registros_limpios:
        with open(ruta_salida, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=registros_limpios[0].keys())
            writer.writeheader()
            writer.writerows(registros_limpios)
    else:
        # Caso de borde: ningún registro válido
        with open(ruta_salida, "w", encoding="utf-8", newline="") as f:
            f.write("")

    # Resumen por área y prioridad
    resumen = defaultdict(Counter)
    for r in registros_limpios:
        resumen[r["area"]][r["prioridad"]] += 1

    # Escribir resumen
    with open(ruta_resumen, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["area", "prioridad", "cantidad"])
        for area in sorted(resumen.keys()):
            for prioridad, cantidad in sorted(resumen[area].items()):
                writer.writerow([area, prioridad, cantidad])

    stats = {
        "total_leidos": len(ids_vistos) + duplicados + descartados,
        "limpios": len(registros_limpios),
        "duplicados": duplicados,
        "descartados": descartados,
    }
    logger.info("Limpieza terminada: %s", stats)
    return stats

# Ejecución

if __name__ == "__main__":
    import sys

    entrada = sys.argv[1] if len(sys.argv) > 1 else "data/tickets_historicos.csv"
    salida = sys.argv[2] if len(sys.argv) > 2 else "output/tickets_limpios.csv"
    resumen = sys.argv[3] if len(sys.argv) > 3 else "output/resumen_area_prioridad.csv"

    limpiar_tickets(entrada, salida, resumen)
    print(f"Archivo limpio → {salida}")
    print(f"Resumen        → {resumen}")