# Guía de Revisión de Código Generado por IA  
**Equipo de Aplicaciones**  
**Versión:** 1.0 · Etapa 3

---

## 1. Objetivo

Establecer un estándar mínimo y práctico para que el código asistido por IA entre al repositorio con la misma calidad y seguridad que el código escrito a mano.

---

## 2. Qué se permite generar con IA

| Permitido | No permitido sin revisión extra |
|-----------|---------------------------------|
| Estructura de carpetas y esqueletos | Lógica de negocio crítica (idempotencia, cálculos financieros, permisos) |
| Pruebas unitarias y de borde | Manejo de secretos o autenticación |
| Documentación y comentarios | Consultas SQL complejas o migraciones |
| Código de infraestructura (Docker, CI) | Cualquier cosa que toque datos reales de producción |

---

## 3. Checklist obligatorio antes de hacer commit

Todo código generado o muy asistido por IA debe pasar por esta lista:

- [ ] **Secretos**: no hay tokens, claves, contraseñas ni URLs internas hardcodeadas.
- [ ] **Validación de entrada**: todo dato externo se valida (longitud, tipo, contenido vacío).
- [ ] **Casos de borde**: al menos un test que demuestre el comportamiento con datos inválidos o vacíos.
- [ ] **Manejo de errores**: no se tragan excepciones; se registran y se devuelve mensaje controlado.
- [ ] **Desacoplamiento**: la lógica de negocio no llama directamente al proveedor de IA.
- [ ] **Prueba que falla antes / pasa después** cuando se corrige un defecto.
- [ ] **README o docstring** explica supuestos y limitaciones.

Si algún ítem no se cumple → no se hace merge.

---

## 4. Estándar de prompts (recomendado)

Cuando se pida código a un asistente de IA, el prompt debe incluir:

1. **Contexto**: “Estamos en una API FastAPI de mesa de ayuda…”
2. **Restricciones**: “No hardcodees secretos. Usa variables de entorno. Incluye manejo de timeout.”
3. **Formato de salida**: “Devuelve solo el código del archivo X, sin explicaciones largas.”
4. **Casos de borde**: “Debe manejar entrada vacía, None y valores con solo espacios.”

Ejemplo de prompt bueno:

> “Escribe una función `normalizar_fecha` en Python que acepte tres formatos (YYYY-MM-DD, DD/MM/YYYY, DD-Mon-YYYY con meses en español). Debe devolver None si la fecha es inválida o vacía. No uses librerías externas. Incluye docstring.”

---

## 5. Estándar de commits

- Un commit = una intención clara.
- Prefijo convencional: `feat`, `fix`, `test`, `docs`, `chore`, `ci`, `refactor`.
- Mensaje en español o inglés, pero consistente.
- Nunca un commit “fix stuff” o “cambios varios”.

Ejemplos correctos:
```
feat(etapa3): endpoint RAG con abstención
fix(etapa2): corregir acumulador mutable en resumir_por_area
test(etapa3): demostrar abstención cuando no hay evidencia
```

---

## 6. Qué nunca se acepta sin prueba

- Cualquier cambio en lógica de clasificación, permisos o dinero.
- Cambios en el manejo de secretos o autenticación.
- Modificaciones al pipeline de CI que debiliten los controles.
- Código que “funciona en el escenario feliz” pero no tiene caso de borde.

---

## 7. Resumen en una frase

> **La IA escribe, el humano responde.**  
> Si no puedes explicar y modificar el código en vivo, no debe entrar al repositorio.
