# Administración de la Configuración

Para garantizar la trazabilidad y gestionar los cambios adecuadamente, BiblioTech implementa las siguientes prácticas:

## 1. Gestión de Variables de Entorno
El sistema utiliza `pydantic-settings` para cargar la configuración desde un archivo `.env`.
- Existe un archivo `.env.example` en el repositorio para que los desarrolladores conozcan qué variables se necesitan (ej. `DATABASE_URL`).
- Esto evita que credenciales sensibles o configuraciones de entorno específicas se suban al repositorio.

## 2. Control de Versiones
Todo el proyecto está gestionado en Git.
- **.gitignore:** Configurado de manera estricta para ignorar carpetas de cache (`__pycache__`), bases de datos locales (`*.db`), y entornos virtuales (`.venv`).

## 3. Trazabilidad de Cambios
- Las modificaciones deben seguir un ciclo de commits pequeños y atómicos.
- Cada commit describe claramente el propósito del cambio.
- Las funciones críticas de la base de datos (por ejemplo, el modelo `Book` y `Loan`) cuentan con campos de auditoría básicos como `created_at` (o `loan_date`) gestionados automáticamente por SQLAlchemy.

## 4. Gestión de Dependencias
- Se utiliza `requirements.txt` fijando las versiones (ej. `fastapi==0.115.6`) para evitar que el código deje de funcionar en caso de que alguna dependencia actualice y rompa la retrocompatibilidad.
