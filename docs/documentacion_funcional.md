# Documentación Funcional — Mesa de Ayuda

**Versión:** 0.0.1 (Etapa 2)  
**Nivel objetivo:** Ingeniero IA Middle I

## 1. ¿Qué resuelve?

El área de Aplicaciones recibe solicitudes internas en texto libre correo y formulario.  
Actualmente el proceso es manual: un analista lee el texto, asigna categoría y prioridad, y crea el ticket.

Esta solución automatiza la primera parte del flujo:

1. Recibe la solicitud por API.
2. Asigna automáticamente **categoría** y **prioridad** (usando IA o, si no está disponible, reglas de respaldo).
3. Permite consultar el estado de cualquier solicitud.
4. Permite listar solicitudes con filtros.

## 2. ¿Para quién?

| Rol | Beneficio |
|-----|-----------|
| **Analista de Mesa de Ayuda** | Reduce el tiempo de clasificación manual. |
| **Usuario interno** | Puede crear y consultar sus solicitudes de forma inmediata. |
| **Coordinación de Aplicaciones** | Tiene trazabilidad y un punto único de entrada. |
| **Equipo de IA / Desarrollo** | Base desacoplada para evolucionar a RAG y orquestación (etapas 3 y 4). |

## 3. Flujos principales

### 3.1 Crear solicitud
1. El cliente envía `asunto`, `área`, `solicitante` y opcionalmente `descripción`.
2. El sistema valida los datos.
3. El clasificador de IA (o el modo degradado) asigna categoría y prioridad.
4. Se devuelve la solicitud creada con su identificador.

### 3.2 Consultar estado
El cliente consulta por el identificador de la solicitud y recibe el estado actual, categoría, prioridad y fechas.

### 3.3 Listar con filtros
Se pueden filtrar por `área` y `estado`, con paginación básica (`limit` / `offset`).

## 4. Comportamiento ante fallos del proveedor de IA

Si el proveedor de IA no está configurado, no responde o falla:

- El sistema **no se detiene**.
- Se activa el **modo degradado** (reglas locales).
- Se registra un warning en los logs.
- La solicitud se crea igual, con categoría y prioridad asignadas por reglas.

Este comportamiento es intencional y forma parte del diseño de resiliencia.

## 5. Alcance actual (Etapa 2)

Incluido:
- API REST propia
- Clasificación automática desacoplada
- Corrección de defectos del módulo heredado
- Configuración por variables de entorno
- Logging estructurado

Fuera de alcance (se aborda en etapas posteriores):
- RAG sobre políticas
- Orquestación multi-paso
- Persistencia en base de datos real
- Interfaz de usuario (Angular es opcional)