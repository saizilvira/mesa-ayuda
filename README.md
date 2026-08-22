# Mesa de Ayuda

Prueba Técnica  
**Nivel objetivo declarado:** Ingeniero IA Middle I

## Etapa alcanzada

- [x] **Etapa 1 — Fundamentos** (Desarrollador IA Junior I)
- [ ] Etapa 2 — Autonomía e integración
- [ ] Etapa 3 — Complejidad y calidad
- [ ] Etapa 4 — Arquitectura y orquestación
- [ ] Etapa 5 — Estrategia técnica

---

## Cómo instalar

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## Cómo ejecutar (Etapa 1)

### 1. Limpieza del histórico de tickets
```bash
python -m src.limpiar_tickets \
  data/tickets_historicos.csv \
  output/tickets_limpios.csv \
  output/resumen_area_prioridad.csv
```

### 2. Consumo del servicio mock
Primero levanta el mock en otra terminal:
```bash
cd materiales/servicio_mock          # o la ruta donde esté
pip install -r requirements.txt
uvicorn app:app --port 8080
```

Luego ejecuta el cliente:
```bash
python -m src.consumir_mock
```

### 3. Consultas SQL
```bash
python -m src.consultas_sql
```

### 4. Pruebas unitarias
```bash
pytest tests/test_limpiar_tickets.py -v
```

---

## Qué hace la Etapa 1

- Lee el CSV histórico (2.000 registros con ruido real: tres formatos de fecha, categorías y prioridades inconsistentes, duplicados y campos vacíos).
- Normaliza fechas a formato ISO (`YYYY-MM-DD`), categorías y prioridades a un conjunto controlado.
- Elimina duplicados por `id` (se conserva el primer registro encontrado).
- Valida registros mínimos (descarta los que no tienen `id` o `fecha_creacion` válida).
- Genera:
  - `output/tickets_limpios.csv`
  - `output/resumen_area_prioridad.csv`
- Consume el servicio mock externo (GET + POST) con timeout, reintentos y mensajes de error comprensibles.
- Ejecuta tres consultas SQL sobre el esquema relacional:
  1. Agregación por área (conteo + promedio de reaperturas)
  2. Join de tres tablas (tickets + usuarios + áreas)
  3. Tickets reabiertos (`estado = 'Reabierto'` o `reaperturas > 0`)
- Incluye pruebas unitarias de las funciones de normalización y validación, con casos de borde.

---

## Supuestos realizados

- Al encontrar `id` duplicados se conserva el **primer** registro y se descartan los siguientes.
- Las fechas que no coinciden con ninguno de los tres formatos conocidos se convierten a `null` y el registro se descarta si no tiene `fecha_creacion` válida.
- Las prioridades se normalizan al conjunto: `Alta`, `Media`, `Baja`, `Crítica`, `Sin prioridad`.
- Las categorías se normalizan con `.capitalize()` (primera letra mayúscula).
- Se utiliza SQLite para las consultas SQL (el esquema original es compatible).
- El token del servicio mock (`demo-token-prueba-2026`) se mantiene en el código solo para la prueba; en etapas posteriores se moverá a variables de entorno.