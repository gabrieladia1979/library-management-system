# Integración Continua (CI/CD)

El proyecto utiliza **GitHub Actions** para implementar un pipeline básico y efectivo de integración continua.

## Pipeline Definido

El archivo de configuración reside en `.github/workflows/ci.yml`.

### Triggers (Desencadenadores)
- `push` en la rama `main`.
- `pull_request` hacia la rama `main`.

### Jobs

1. **Linting (ruff):**
   - Garantiza que todo el código Python siga las convenciones PEP-8 y las mejores prácticas de codificación.
   - Detecta errores de sintaxis o de estilo temprano.

2. **Testing (pytest):**
   - Configura un entorno con Python (ej. 3.10 o superior).
   - Instala las dependencias declaradas en `requirements.txt`.
   - Ejecuta la suite de pruebas unitarias, de integración y de sistema.
   - Verifica que ninguna confirmación rompa la funcionalidad existente.

## Flujo de Trabajo Recomendado

1. Todo el desarrollo se realiza en ramas de características (`feature/nueva-funcionalidad`).
2. Se abre un Pull Request hacia `main`.
3. GitHub Actions ejecuta automáticamente el Linting y el Testing.
4. Si (y solo si) los checks pasan en verde, se permite realizar el *merge* a `main`.
