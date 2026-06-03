# Plan de Pruebas

Este proyecto implementa una estrategia de validación, verificación y automatización exhaustiva utilizando `pytest` y `FastAPI TestClient`.

## 1. Niveles de Prueba

### Pruebas Unitarias (Unit Tests)
- **Objetivo:** Verificar el correcto funcionamiento de la lógica de negocio aislada de la capa de transporte (HTTP).
- **Alcance:** Archivos en `app/services/` (ej. validaciones de disponibilidad de copias, conflictos de ISBN).
- **Ubicación:** Directorio `tests/unit/`.

### Pruebas de Integración (Integration Tests)
- **Objetivo:** Asegurar que los endpoints HTTP de la API interactúan correctamente con los servicios y la base de datos en memoria.
- **Alcance:** Rutas en `app/api/v1/endpoints/`.
- **Ubicación:** Directorio `tests/integration/`.

### Pruebas de Sistema / End-to-End (System Tests)
- **Objetivo:** Probar flujos completos del usuario imitando un comportamiento real (ej. Registrar usuario -> Registrar Libro -> Pedir Préstamo -> Validar Stock -> Devolver).
- **Alcance:** Flujos combinados.
- **Ubicación:** Directorio `tests/system/`.

## 2. Automatización

Todas las pruebas están automatizadas. Se utiliza una base de datos `SQLite` en memoria (`sqlite://`) que se limpia tras cada prueba mediante el uso de "fixtures" (`tests/conftest.py`).

**Comando de ejecución:**
\`\`\`bash
pytest tests/ -v
\`\`\`

## 3. Cobertura (Coverage)
Se integra `pytest-cov` para garantizar que todo el código nuevo esté testeado.

**Generar reporte:**
\`\`\`bash
pytest --cov=app tests/
\`\`\`
