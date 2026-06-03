# Análisis de Atributos de Calidad (ISO 25010)

Para el proyecto BiblioTech (Sistema de Gestión de Biblioteca), se seleccionaron los siguientes 5 atributos de calidad principales según la norma ISO 25010:

## 1. Adecuación Funcional (Functional Suitability)
- **Definición:** El grado en que el software proporciona funciones que satisfacen las necesidades explícitas e implícitas al utilizarse bajo condiciones específicas.
- **Justificación:** El sistema debe gestionar correctamente el catálogo de libros, préstamos, devoluciones y usuarios. Es crítico que las validaciones (ej. evitar prestar un libro sin stock) funcionen a la perfección.

## 2. Fiabilidad (Reliability)
- **Definición:** El grado en que el sistema desempeña funciones específicas bajo condiciones dadas por un tiempo determinado.
- **Justificación:** Se incluye tolerancia a fallos en la conexión de la base de datos (SQLite local) y manejo adecuado de excepciones (ej. HTTP 404, HTTP 409) para no interrumpir el flujo de uso.

## 3. Eficiencia de Desempeño (Performance Efficiency)
- **Definición:** El desempeño en relación con la cantidad de recursos utilizados.
- **Justificación:** Al ser una SPA (Single Page Application) servida con Vanilla JS y un backend FastAPI (asíncrono/rápido), la carga de la interfaz y la respuesta de los endpoints se mantiene en pocos milisegundos.

## 4. Usabilidad (Usability)
- **Definición:** El grado en que el producto puede ser usado por usuarios especificados para lograr sus objetivos con eficacia, eficiencia y satisfacción.
- **Justificación:** Se implementó una interfaz de usuario en modo oscuro con diseño moderno (Glassmorphism), fuentes legibles (Inter/Outfit) y retroalimentación inmediata mediante notificaciones tipo *Toast* y modales.

## 5. Mantenibilidad (Maintainability)
- **Definición:** El grado de efectividad y eficiencia con la cual un producto puede ser modificado.
- **Justificación:** El proyecto adopta una arquitectura multicapa clara (Endpoints -> Services -> Models) con código testeado (>90% coverage), tipado estático parcial mediante Pydantic y reglas estrictas de linting (Ruff).
