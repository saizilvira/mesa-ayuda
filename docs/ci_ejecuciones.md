# Demostración del Pipeline de CI — Etapa 3

## Ejecución exitosa
- **Fecha:** 23-Ago-2026
- **Commit:** 5dc6024
- **Resultado:** Todas las pruebas unitarias pasaron.
- **Enlace / evidencia:** https://github.com/saizilvira/mesa-ayuda/actions/runs/32652269853

## Ejecución fallida (demostración controlada)
- **Fecha:** 23-Ago-2026
- **Commit:** 8bb2b83
- **Resultado:** No se ejecuto el comando para ingestar la info de los PDF a chromaDB
- **Enlace / evidencia:** https://github.com/saizilvira/mesa-ayuda/actions/runs/32651034338
- **Corrección:** Se agrego la instruccion para agregar la info de los PDF a chromaDB 

## Qué ejecuta el pipeline
1. Checkout del código
2. Configuración de Python 3.11
3. Instalación de dependencias
4. Ejecución de **pytest** sobre toda la carpeta `tests/`