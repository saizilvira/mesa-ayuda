import sqlite3
from pathlib import Path


def crear_base_datos(ruta_esquema: str = "data/esquema.sql", ruta_db: str = "data/mesa_ayuda.db") -> sqlite3.Connection:

    # Crear la BD a partir del esquema proporcionado
    ruta_db = Path(ruta_db)
    if ruta_db.exists():
        ruta_db.unlink()

    conn = sqlite3.connect(ruta_db)
    conn.row_factory = sqlite3.Row

    with open(ruta_esquema, encoding="utf-8") as f:
        script = f.read()

    conn.executescript(script)
    conn.commit()
    return conn

# Consultas

def consulta_1_agregacion_por_area(conn: sqlite3.Connection) -> list[dict]:
    # Cuenta cuántos tickets hay por cada área y calcula el promedio de reaperturas.
    sql = """
    SELECT
        a.nombre AS area,
        COUNT(t.id_ticket) AS total_tickets,
        ROUND(AVG(t.reaperturas), 2) AS promedio_reaperturas
    FROM tickets t
    JOIN areas a ON t.id_area = a.id_area
    GROUP BY a.nombre
    ORDER BY total_tickets DESC;
    """
    cursor = conn.execute(sql)
    return [dict(row) for row in cursor.fetchall()]


def consulta_2_join_tres_tablas(conn: sqlite3.Connection) -> list[dict]:
    # Muestra el código del ticket, el nombre del solicitante y el área.
    sql = """
    SELECT
        t.codigo,
        u.nombre AS solicitante,
        u.correo,
        a.nombre AS area,
        t.categoria,
        t.prioridad,
        t.estado,
        t.fecha_creacion
    FROM tickets t
    JOIN usuarios u ON t.id_usuario = u.id_usuario
    JOIN areas a    ON t.id_area    = a.id_area
    ORDER BY t.fecha_creacion DESC
    LIMIT 10;
    """
    cursor = conn.execute(sql)
    return [dict(row) for row in cursor.fetchall()]


def consulta_3_tickets_reabiertos(conn: sqlite3.Connection) -> list[dict]:
    # Muestra los que tienen estado 'Reabierto' o reaperturas > 0.
    sql = """
    SELECT
        t.codigo,
        t.estado,
        t.reaperturas,
        t.categoria,
        t.prioridad,
        a.nombre AS area,
        t.fecha_creacion,
        t.fecha_cierre
    FROM tickets t
    JOIN areas a ON t.id_area = a.id_area
    WHERE t.estado = 'Reabierto'
       OR t.reaperturas > 0
    ORDER BY t.reaperturas DESC, t.fecha_creacion;
    """
    cursor = conn.execute(sql)
    return [dict(row) for row in cursor.fetchall()]


def ejecutar_todas():

    print("=== Creando base de datos desde esquema.sql ===")
    conn = crear_base_datos()

    print("\n--- Consulta 1: Agregación por área ---")
    for fila in consulta_1_agregacion_por_area(conn):
        print(dict(fila))

    print("\n--- Consulta 2: Join de tres tablas (tickets, usuarios y areas) ---")
    for fila in consulta_2_join_tres_tablas(conn):
        print(dict(fila))

    print("\n--- Consulta 3: Tickets reabiertos ---")
    resultados = consulta_3_tickets_reabiertos(conn)
    print(f"Total de tickets reabiertos encontrados: {len(resultados)}")
    for fila in resultados[:10]:
        print(dict(fila))
    if len(resultados) > 10:
        print(f"... y {len(resultados) - 10} más")

    conn.close()
    print("\n=== Consultas finalizadas ===")

# Ejecución

if __name__ == "__main__":
    ejecutar_todas()