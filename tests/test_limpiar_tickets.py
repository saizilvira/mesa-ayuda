import pytest
from src.limpiar_tickets import (
    normalizar_fecha,
    normalizar_categoria,
    normalizar_prioridad,
    es_registro_valido,
)

# 1. normalizar_fecha

def test_normalizar_fecha_formato_iso():
    assert normalizar_fecha("2025-03-08") == "2025-03-08"

def test_normalizar_fecha_formato_slash():
    assert normalizar_fecha("03/06/2025") == "2025-06-03"

def test_normalizar_fecha_formato_mes_espanol():
    assert normalizar_fecha("30-Jun-2025") == "2025-06-30"
    assert normalizar_fecha("20-Ene-2026") == "2026-01-20"

def test_normalizar_fecha_vacia_o_none():
    # Caso de borde: valor vacío o None
    assert normalizar_fecha(None) is None
    assert normalizar_fecha("") is None
    assert normalizar_fecha("   ") is None

def test_normalizar_fecha_invalida():
    # Caso de borde: fecha que no coincide con ningún formato
    assert normalizar_fecha("fecha-invalida") is None
    assert normalizar_fecha("32/13/2025") is None

# 2. normalizar_categoria

def test_normalizar_categoria_mayusculas():
    assert normalizar_categoria("HARDWARE") == "Hardware"
    assert normalizar_categoria("software") == "Software"


def test_normalizar_categoria_vacia():
    #Caso de borde
    assert normalizar_categoria(None) == "Sin clasificar"
    assert normalizar_categoria("") == "Sin clasificar"
    assert normalizar_categoria("   ") == "Sin clasificar"

# 3. normalizar_prioridad

def test_normalizar_prioridad_variantes():
    assert normalizar_prioridad("alta") == "Alta"
    assert normalizar_prioridad("1-Alta") == "Alta"
    assert normalizar_prioridad("ALTA") == "Alta"
    assert normalizar_prioridad("2-Media") == "Media"
    assert normalizar_prioridad("Critica") == "Crítica"
    assert normalizar_prioridad("crítica") == "Crítica"


def test_normalizar_prioridad_desconocida():
    # Caso de borde
    assert normalizar_prioridad(None) == "Sin prioridad"
    assert normalizar_prioridad("") == "Sin prioridad"
    assert normalizar_prioridad("urgentisimo") == "Sin prioridad"

# 4. es_registro_valido

def test_es_registro_valido_ok():
    fila = {"id": "TK-001", "fecha_creacion": "2025-03-08"}
    assert es_registro_valido(fila) is True


def test_es_registro_valido_sin_id():
    # Caso de borde
    fila = {"id": "", "fecha_creacion": "2025-03-08"}
    assert es_registro_valido(fila) is False


def test_es_registro_valido_sin_fecha():
    # Caso de borde
    fila = {"id": "TK-001", "fecha_creacion": None}
    assert es_registro_valido(fila) is False