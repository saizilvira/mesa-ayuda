# Mesa de Ayuda Inteligente

Prueba Técnica  
**Nivel objetivo declarado:** Ingeniero IA Middle I

## Etapa alcanzada

- [x] **Etapa 1 — Fundamentos** (Desarrollador IA Junior I)
- [x] **Etapa 2 — Autonomía e integración** (Desarrollador IA Junior II)
- [x] **Etapa 3 — Complejidad y calidad**
- [ ] Etapa 4 — Arquitectura y orquestación
- [ ] Etapa 5 — Estrategia técnica

---

## Cómo instalar

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Copia el archivo de variables de entorno:

```bash
cp .env.example .env
# Edita .env si necesitas cambiar tokens o URLs
```

---

## Cómo ejecutar

### Etapa 1

#### 1. Limpieza del histórico de tickets
```bash
python -m src.limpiar_tickets \
  data/tickets_historicos.csv \
  output/tickets_limpios.csv \
  output/resumen_area_prioridad.csv
```

#### 2. Consumo del servicio mock
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

#### 3. Consultas SQL
```bash
python -m src.consultas_sql
```

#### 4. Pruebas unitarias (Etapa 1)
```bash
pytest tests/test_limpiar_tickets.py -v
```

### Etapa 2

#### 1. Corrección del módulo legacy + pruebas
```bash
pytest tests/test_legacy_module.py -v
```

#### 2. API REST propia
```bash
uvicorn src.api.main:app --reload --port 8000
```

- Documentación interactiva: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

Ejemplos rápidos:

```bash
# Crear solicitud
curl -X POST http://127.0.0.1:8000/solicitudes \
  -H "Content-Type: application/json" \
  -d '{
    "asunto": "El portátil no enciende desde ayer",
    "area": "Operaciones",
    "solicitante": "armando.saiz@correo.com",
    "descripcion": "Necesito uno de reemplazo urgente"
  }'

# Listar
curl "http://127.0.0.1:8000/solicitudes?limit=5"

# Consultar por ID
curl http://127.0.0.1:8000/solicitudes/SOL-XXXXXXXX
```

### Etapa 3
```bash
# Ingesta de políticas (RAG)
python -m src.rag.ingest

# API (incluye endpoint RAG + métricas)
uvicorn src.api.main:app --reload --port 8000

# Consultar políticas
curl -X POST http://127.0.0.1:8000/consultar-politicas \
  -H "Content-Type: application/json" \
  -d '{"pregunta": "¿Cuántos días de vacaciones tengo?"}'

# Métricas
curl http://127.0.0.1:8000/metrics

# Prueba de abstención
pytest tests/test_rag_abstencion.py -v
```

---

## Qué hace cada etapa

### Etapa 1 — Fundamentos
- Lee el CSV histórico (2.000 registros con ruido real).
- Normaliza fechas (3 formatos), categorías y prioridades.
- Elimina duplicados por `id` y valida registros.
- Genera archivo limpio + resumen por área y prioridad.
- Consume el servicio mock (GET + POST) con timeout, reintentos y mensajes de error comprensibles.
- Ejecuta tres consultas SQL: agregación por área, join de tres tablas y tickets reabiertos.
- Pruebas unitarias de normalización y validación (incluye casos de borde).

### Etapa 2 — Autonomía e integración
- **API REST propia** con tres recursos:
  - `POST /solicitudes` → crear
  - `GET /solicitudes/{id}` → consultar estado
  - `GET /solicitudes` → listar con filtros
- Validación de entrada, códigos de estado correctos y formato uniforme de errores.
- **Módulo de IA desacoplado** para asignar categoría y prioridad:
  - Timeout y reintentos
  - Modo degradado (reglas locales) cuando el proveedor no responde
- Corrección de los 3 defectos de `legacy_module.py` con pruebas que fallan antes y pasan después + causa raíz documentada.
- Configuración por variables de entorno (cero secretos en el repositorio).
- Logging estructurado.
- Documentación funcional y contrato técnico de la API.

### Etapa 3 — Complejidad y calidad
- **RAG** sobre los 5 PDFs de políticas (ingesta, fragmentación, embeddings, ChromaDB).
- Endpoint `/consultar-politicas` que cita documento y página de origen.
- **Abstención** explícita cuando no hay evidencia + caso de prueba que lo demuestra.
- **Pipeline de CI** (ruff + pytest + ingesta) con evidencia de ejecución exitosa y fallida.
- **Informe de seguridad** con ≥ 3 hallazgos sobre código generado por IA y correcciones aplicadas.
- **Instrumentación**: latencia por petición, tokens consumidos y resumen agregado (`/metrics`).
- **Artefacto para el equipo**: guía de revisión de código generado por IA.

---

## Supuestos realizados

### Etapa 1
- Al encontrar `id` duplicados se conserva el primer registro.
- Fechas inválidas → `null`; el registro se descarta si no tiene `fecha_creacion` válida.
- Prioridades normalizadas a: Alta, Media, Baja, Crítica, Sin prioridad.
- Se utiliza SQLite para las consultas SQL.

### Etapa 2
- La persistencia de la API es en memoria (suficiente para la etapa).
- Si no hay proveedor de IA configurado, se activa automáticamente el modo degradado.
- El token del mock y las claves de IA se leen exclusivamente de variables de entorno.

### Etapa 3
- La persistencia de la API es en memoria (suficiente para las etapas implementadas).
- Clasificación de IA cae a modo degradado (reglas locales) cuando no hay proveedor configurado.
- Base vectorial generada localmente con `sentence-transformers` + ChromaDB.
- No se versionan secretos ni la carpeta `data/chroma_db/`.
---

## Qué se dejó fuera

**Etapa 2**  
- Pantalla Angular

**Etapa 3**  
- Conexión con LLM externo

---

## Documentación

| Documento | Ubicación |
|-----------|-----------|
| Funcional | [`docs/documentacion_funcional.md`](docs/documentacion_funcional.md) |
| Contrato de la API | [`docs/contrato_api.md`](docs/contrato_api.md) |
| Informe de seguridad | [`docs/informe_seguridad.md`](docs/informe_seguridad.md) |
| Guía de revisión de código IA | [`docs/guia_revision_codigo_ia.md`](docs/guia_revision_codigo_ia.md) |
| Demostración CI | [`docs/ci_ejecuciones.md`](docs/ci_ejecuciones.md) |

---

## Estructura del repositorio

```
mesa-ayuda-inteligente/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── data/
│   ├── tickets_historicos.csv
│   └── esquema.sql
│   └── politicas/
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── limpiar_tickets.py
│   ├── consumir_mock.py
│   ├── consultas_sql.py
│   └── legacy_module.py
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── clasificador.py
│   └── api/
│   │   ├── __init__.py
│   │   ├── schemas.py
│   │   └── main.py
│   └── observability/
│       ├── __init__.py
│       ├── metrics.py
├── tests/
│   ├── __init__.py
│   ├── test_limpiar_tickets.py
│   └── test_legacy_module.py
├── docs/
│   ├── documentacion_funcional.md
│   └── contrato_api.md
└── output/
```

---

## Declaración de uso de asistentes de IA

Se entregará el formato completo del numeral 6 del Anexo A junto con la entrega final del reto práctico.
