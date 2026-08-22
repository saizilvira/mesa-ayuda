import pytest
from datetime import date

from src.legacy_module import (
    filtrar_por_periodo,
    resumir_por_area,
    contar_reaperturas,
    tasa_reapertura,
    informe_mensual,
    parsear_fecha,
)

# S1 — El informe mensual pierde tickets de los extremos del periodo

def test_s1_filtrar_periodo_incluye_extremos():

    tickets = [
        {"fecha_creacion": "2025-03-01", "area": "Operaciones"},  # primer día
        {"fecha_creacion": "2025-03-15", "area": "Operaciones"},
        {"fecha_creacion": "2025-03-31", "area": "Operaciones"},  # último día
        {"fecha_creacion": "2025-04-01", "area": "Operaciones"},  # fuera
    ]
    inicio = date(2025, 3, 1)
    fin = date(2025, 3, 31)

    resultado = filtrar_por_periodo(tickets, inicio, fin)

    assert len(resultado) == 3, (
        "Debe incluir los tickets del 1 y del 31 de marzo (extremos inclusivos)"
    )

# S2 — Cifras infladas cuando se llama varias veces seguidas

def test_s2_resumir_por_area_no_comparte_estado():

    tickets_a = [
        {"area": "Operaciones"},
        {"area": "Operaciones"},
        {"area": "Compras"},
    ]
    tickets_b = [
        {"area": "Talento Humano"},
    ]

    resumen_a = resumir_por_area(tickets_a)
    resumen_b = resumir_por_area(tickets_b)

    # resumen_b NO debe contener las áreas de la llamada anterior
    assert "Operaciones" not in resumen_b
    assert "Compras" not in resumen_b
    assert resumen_b.get("Talento Humano") == 1
    assert resumen_a.get("Operaciones") == 2

# S3 — Reaperturas subcontadas

def test_s3_contar_reaperturas_case_insensitive_y_campo_numerico():

    tickets = [
        {"estado": "reabierto", "reaperturas": 0},
        {"estado": "Reabierto", "reaperturas": 0},
        {"estado": "REABIERTO", "reaperturas": 0},
        {"estado": "Cerrado", "reaperturas": 2},
        {"estado": "Abierto", "reaperturas": 0},
    ]

    total = contar_reaperturas(tickets)

    assert total == 4, (
        "Debe contar los 3 estados 'reabierto' (cualquier capitalización) "
        "más el que tiene reaperturas > 0"
    )