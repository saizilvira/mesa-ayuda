# Informe de Seguridad — Código generado por IA  
**Proyecto:** Mesa de Ayuda  
**Etapa:** 3 — Complejidad y calidad  
**Fecha:** Agosto 2026  
**Alcance:** Revisión de código generado o asistido por IA en las etapas 1 y 2

---

## Resumen

Se revisó el código producido con asistencia de IA. Se identificaron **3 hallazgos** de seguridad/calidad.  
Todos fueron **corregidos** antes de este informe. Ninguno permanece abierto.

| # | Hallazgo | Severidad | Estado |
|---|----------|-----------|--------|
| 1 | Posible exposición de token/credencial en código fuente | Alta | Corregido |
| 2 | Falta de validación estricta de entrada en endpoint de creación | Media | Corregido |
| 3 | Uso de valor por defecto mutable (anti-patrón) en módulo legacy | Media | Corregido |

---

## Hallazgo 1 — Posible exposición de token en código

**Severidad:** Alta  
**Evidencia:**  
En versiones tempranas del cliente del servicio mock (`src/consumir_mock.py`) el token `demo-token-prueba-2026` estaba hardcodeado directamente en el archivo fuente.  
Aunque es un token de prueba, el patrón es peligroso: cualquier clave real podría haber seguido el mismo camino.

**Riesgo:** Si se hubiera usado una clave real, habría quedado versionada en Git.

**Corrección aplicada:**  
- Se movió toda configuración sensible a variables de entorno (`src/config.py` + `.env`).  
- Se creó `.env.example` sin valores secretos.  
- `.env` está en `.gitignore`.  
- El código ahora lee `settings.mock_token` y `settings.ai_api_key`.

**Estado:** Corregido y verificado.

---

## Hallazgo 2 — Validación de entrada insuficiente

**Severidad:** Media  
**Evidencia:**  
Las primeras versiones del endpoint `POST /solicitudes` aceptaban cadenas vacías o solo espacios en campos obligatorios (`asunto`, `area`, `solicitante`) porque solo se validaba la longitud mínima de Pydantic, no el contenido real.

**Riesgo:** Creación de solicitudes basura o con datos no utilizables.

**Corrección aplicada:**  
Se añadió un `field_validator` en `SolicitudCreate` (`src/api/schemas.py`) que rechaza valores que, después de `strip()`, quedan vacíos.  
Ahora se devuelve error 422 de forma uniforme.

**Estado:** Corregido y verificado.

---

## Hallazgo 3 — Valor por defecto mutable en función

**Severidad:** Media  
**Evidencia:**  
El módulo heredado `legacy_module.py` contenía:

```python
def resumir_por_area(tickets, acumulador={}):
```

Este es un anti-patrón clásico de Python. El diccionario se crea una sola vez y se comparte entre llamadas, provocando el síntoma S2 (cifras infladas).

**Riesgo:** Comportamiento incorrecto y difícil de depurar en producción (datos contaminados entre peticiones).

**Corrección aplicada:**  
Se cambió a:

```python
def resumir_por_area(tickets, acumulador=None):
    if acumulador is None:
        acumulador = {}
```

Se dejó la prueba que falla antes y pasa después (`tests/test_legacy_module.py`).

**Estado:** Corregido y verificado.

---

## Conclusión

Los tres hallazgos fueron detectados mediante revisión manual del código generado/asistido por IA y corregidos en la misma etapa en que se introdujeron.  
No quedan hallazgos abiertos de severidad Alta o Media relacionados con el código revisado.

**Recomendación para el equipo:**  
Todo código generado por IA debe pasar por:
1. Revisión de secretos (búsqueda de tokens, claves, URLs internas).
2. Validación estricta de entradas.
3. Pruebas que demuestren el comportamiento antes/después de correcciones.
