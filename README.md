<p align="center">
  <img src="https://img.icons8.com/fluency/96/library.png" alt="BiblioTech Logo" width="96" height="96"/>
</p>

<h1 align="center">📚 BiblioTech — Sistema de Gestión de Biblioteca</h1>

<p align="center">
  <em>Sistema integral de gestión bibliotecaria desarrollado como proyecto académico para la cátedra de <strong>Calidad de Software</strong>.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.11"/>
  <img src="https://img.shields.io/badge/FastAPI-0.104-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/PyTest-7.4-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white" alt="PyTest"/>
  <img src="https://img.shields.io/badge/Licencia-MIT-green?style=for-the-badge" alt="License MIT"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/build-passing-brightgreen?style=flat-square" alt="Build Status"/>
  <img src="https://img.shields.io/badge/coverage-95%25-brightgreen?style=flat-square" alt="Coverage"/>
  <img src="https://img.shields.io/badge/code%20style-ruff-000000?style=flat-square" alt="Code Style"/>
</p>

---

## 📋 Tabla de Contenidos

- [Descripción](#-descripción)
- [Características](#-características)
- [Tecnologías](#-tecnologías)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Testing](#-testing)
- [CI/CD](#-cicd)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [API Endpoints](#-api-endpoints)
- [Documentación](#-documentación)
- [Equipo](#-equipo)
- [Licencia](#-licencia)

---

## 📖 Descripción

**BiblioTech** es un sistema de gestión de biblioteca diseñado para administrar de forma eficiente el catálogo de libros, el registro de usuarios y el control de préstamos de una biblioteca universitaria. El proyecto fue desarrollado siguiendo las mejores prácticas de **ingeniería de software** y **aseguramiento de la calidad**, aplicando metodologías de testing a múltiples niveles (unitario, integración y sistema).

El sistema expone una **API RESTful** construida con FastAPI que permite realizar todas las operaciones CRUD necesarias, con documentación interactiva autogenerada y validación robusta de datos mediante Pydantic.

### 🎯 Objetivos del Proyecto

- Aplicar conceptos de **calidad de software** en un proyecto real.
- Implementar una suite de pruebas completa con cobertura superior al 90%.
- Configurar un pipeline de **integración continua** con GitHub Actions.
- Documentar exhaustivamente el proceso de desarrollo y testing.

---

## ✨ Características

| Característica | Descripción |
|---|---|
| 📚 **Gestión de Libros** | CRUD completo para el catálogo de libros (título, autor, ISBN, género, año de publicación). |
| 👥 **Gestión de Usuarios** | Registro, actualización y administración de usuarios de la biblioteca. |
| 📖 **Control de Préstamos** | Sistema de préstamos y devoluciones con control de fechas y estados. |
| 🔍 **Búsqueda Avanzada** | Búsqueda de libros por título, autor, ISBN o género con filtros combinados. |
| 📊 **Disponibilidad en Tiempo Real** | Consulta del estado de disponibilidad de cada ejemplar en el catálogo. |
| ✅ **Suite de Pruebas Completa** | Tests unitarios, de integración y de sistema con cobertura ≥ 95%. |
| 🔄 **Pipeline CI/CD** | Integración continua con GitHub Actions: linting, testing y reporte de cobertura. |
| 📋 **Documentación Interactiva** | Documentación automática de la API con Swagger UI y ReDoc. |

---

## 🛠 Tecnologías

| Categoría | Tecnología | Versión |
|---|---|---|
| **Lenguaje** | Python | 3.11+ |
| **Framework Web** | FastAPI | 0.104+ |
| **ORM** | SQLAlchemy | 2.0+ |
| **Base de Datos** | SQLite | 3.x |
| **Validación** | Pydantic | 2.5+ |
| **Servidor ASGI** | Uvicorn | 0.24+ |
| **Testing** | PyTest | 7.4+ |
| **Linter / Formatter** | Ruff | 0.1+ |
| **CI/CD** | GitHub Actions | — |

---

## 📌 Requisitos Previos

Antes de comenzar, asegúrate de tener instaladas las siguientes herramientas:

- ✅ **Python 3.11** o superior — [Descargar aquí](https://www.python.org/downloads/)
- ✅ **pip** — Gestor de paquetes de Python (incluido con Python 3.11+)
- ✅ **Git** — Sistema de control de versiones — [Descargar aquí](https://git-scm.com/downloads)

Puedes verificar las versiones instaladas ejecutando:

```bash
python --version    # Python 3.11.x
pip --version       # pip 23.x+
git --version       # git 2.x+
```

---

## 🚀 Instalación

Sigue estos pasos para configurar el proyecto en tu entorno local:

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/bibliotech.git
cd bibliotech
```

### 2. Crear y activar el entorno virtual

```bash
# Crear el entorno virtual
python -m venv venv

# Activar el entorno virtual
# En Windows:
venv\Scripts\activate

# En macOS/Linux:
source venv/bin/activate
```

### 3. Instalar las dependencias

```bash
pip install -r requirements.txt
```

### 4. Inicializar la base de datos con datos de prueba

```bash
python -m app.db.seed
```

> **Nota:** Este comando crea la base de datos SQLite y la puebla con datos de ejemplo para facilitar las pruebas iniciales.

### 5. Iniciar el servidor de desarrollo

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

✅ El servidor estará disponible en `http://localhost:8000`

---

## 💻 Uso

Una vez que el servidor esté en ejecución, puedes interactuar con la API de las siguientes formas:

| Recurso | URL | Descripción |
|---|---|---|
| **API Base** | `http://localhost:8000` | Punto de entrada principal de la API. |
| **Swagger UI** | `http://localhost:8000/docs` | Documentación interactiva con interfaz Swagger. |
| **ReDoc** | `http://localhost:8000/redoc` | Documentación alternativa con interfaz ReDoc. |

### Ejemplo rápido con `curl`

```bash
# Obtener todos los libros
curl -X GET http://localhost:8000/api/v1/books

# Crear un nuevo libro
curl -X POST http://localhost:8000/api/v1/books \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Cien años de soledad",
    "author": "Gabriel García Márquez",
    "isbn": "978-0-06-088328-7",
    "genre": "Realismo mágico",
    "published_year": 1967,
    "quantity": 4
  }'

# Buscar libros por autor
curl -X GET "http://localhost:8000/api/v1/books?search=García%20Márquez"
```

---

## 🧪 Testing

El proyecto cuenta con una suite de pruebas exhaustiva organizada en tres niveles. Todas las pruebas se ejecutan con **PyTest**.

### Ejecutar todas las pruebas

```bash
pytest
```

### Ejecutar por nivel de prueba

```bash
# Pruebas unitarias
pytest -m unit

# Pruebas de integración
pytest -m integration

# Pruebas de sistema
pytest -m system
```

### Ejecutar con reporte de cobertura

```bash
pytest --cov=app --cov-report=html --cov-report=term-missing
```

> El reporte HTML de cobertura se genera en el directorio `htmlcov/`. Ábrelo en tu navegador para explorar la cobertura línea por línea.

### Resumen de la estrategia de testing

| Nivel | Marcador | Descripción | Cantidad |
|---|---|---|---|
| **Unitario** | `@pytest.mark.unit` | Pruebas de funciones y métodos aislados con mocks. | ~30 tests |
| **Integración** | `@pytest.mark.integration` | Pruebas de interacción entre módulos y la base de datos. | ~20 tests |
| **Sistema** | `@pytest.mark.system` | Pruebas end-to-end sobre la API REST completa. | ~15 tests |

---

## 🔄 CI/CD

El proyecto utiliza **GitHub Actions** para la integración y entrega continua. El pipeline se ejecuta automáticamente en cada `push` y `pull request` sobre la rama `main`.

### Pipeline de CI/CD

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Checkout   │───▶│   Linting   │───▶│   Testing   │───▶│  Coverage   │
│   del código │    │   (Ruff)    │    │  (PyTest)   │    │  Report     │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

### Etapas del pipeline

1. **Checkout** — Descarga del código fuente del repositorio.
2. **Configuración del entorno** — Instalación de Python 3.11 y las dependencias del proyecto.
3. **Linting** — Análisis estático del código con Ruff para garantizar el cumplimiento de estándares de estilo.
4. **Testing** — Ejecución de la suite completa de pruebas (unitarias, integración y sistema).
5. **Cobertura** — Generación y publicación del reporte de cobertura de código.

> El archivo de configuración se encuentra en `.github/workflows/ci.yml`.

---

## 🗂 Estructura del Proyecto

```
bibliotech/
├── .github/
│   └── workflows/
│       └── ci.yml                  # Pipeline de CI/CD
├── app/
│   ├── __init__.py
│   ├── main.py                     # Punto de entrada de la aplicación
│   ├── api/
│   │   └── v1/
│   │       ├── router.py           # Enrutador principal de la API
│   │       └── endpoints/
│   │           ├── books.py        # Endpoints de Libros
│   │           ├── loans.py        # Endpoints de Préstamos
│   │           └── users.py        # Endpoints de Usuarios
│   ├── core/
│   │   └── config.py               # Configuración general
│   ├── db/
│   │   ├── database.py             # Configuración de la base de datos
│   │   └── seed.py                 # Script de carga de datos iniciales
│   ├── models/
│   │   ├── book.py                 # Modelo ORM de Libro
│   │   ├── loan.py                 # Modelo ORM de Préstamo
│   │   └── user.py                 # Modelo ORM de Usuario
│   ├── schemas/
│   │   ├── book.py                 # Esquemas Pydantic de Libro
│   │   ├── loan.py                 # Esquemas Pydantic de Préstamo
│   │   └── user.py                 # Esquemas Pydantic de Usuario
│   └── services/
│       ├── book_service.py         # Lógica de negocio de Libros
│       ├── loan_service.py         # Lógica de negocio de Préstamos
│       └── user_service.py         # Lógica de negocio de Usuarios
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # Fixtures compartidos
│   ├── unit/                       # Pruebas unitarias
│   ├── integration/                # Pruebas de integración
│   └── system/                     # Pruebas de sistema
├── docs/
│   ├── plan_de_pruebas.md          # Plan de pruebas del proyecto
│   └── ...                         # Otros documentos de calidad
├── requirements.txt                # Dependencias del proyecto
├── pyproject.toml                  # Configuración de herramientas
└── README.md                       # Este archivo
```

---

## 🌐 API Endpoints

### 📚 Libros

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/api/v1/books` | Obtener todos los libros (con filtros opcionales). |
| `GET` | `/api/v1/books/{id}` | Obtener un libro por su ID. |
| `POST` | `/api/v1/books` | Crear un nuevo libro. |
| `PUT` | `/api/v1/books/{id}` | Actualizar un libro existente. |
| `DELETE` | `/api/v1/books/{id}` | Eliminar un libro del catálogo. |

### 👥 Usuarios

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/api/v1/users` | Obtener todos los usuarios registrados. |
| `GET` | `/api/v1/users/{id}` | Obtener un usuario por su ID. |
| `POST` | `/api/v1/users` | Registrar un nuevo usuario. |
| `PUT` | `/api/v1/users/{id}` | Actualizar la información de un usuario. |
| `DELETE` | `/api/v1/users/{id}` | Eliminar un usuario del sistema. |

### 📖 Préstamos

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/api/v1/loans` | Obtener todos los préstamos. |
| `GET` | `/api/v1/loans/{id}` | Obtener un préstamo por su ID. |
| `POST` | `/api/v1/loans` | Registrar un nuevo préstamo. |
| `PUT` | `/api/v1/loans/{id}` | Actualizar un préstamo (ej: marcar devolución). |
| `DELETE` | `/api/v1/loans/{id}` | Eliminar un registro de préstamo. |

---

## 📄 Documentación

El directorio `docs/` contiene toda la documentación del proyecto relacionada con la cátedra de Calidad de Software:

| Documento | Descripción |
|---|---|
| [`plan_de_pruebas.md`](docs/plan_de_pruebas.md) | Plan maestro de pruebas: estrategia, alcance, criterios de entrada/salida y cronograma. |
| [`casos_de_prueba.md`](docs/casos_de_prueba.md) | Casos de prueba detallados con precondiciones, pasos, datos de prueba y resultados esperados. |
| [`reporte_calidad.md`](docs/reporte_calidad.md) | Reporte de calidad del software: métricas, cobertura, defectos encontrados y análisis. |
| [`arquitectura.md`](docs/arquitectura.md) | Documentación de la arquitectura del sistema: diagramas, decisiones de diseño y patrones. |

---

## 👨‍💻 Equipo

| Nombre | Rol | Contacto |
|---|---|---|
| **Gabriel Adia** | Developer | [gadia@uade.edu.ar](mailto:gadia@uade.edu.ar) |
| **Tomas Basualdo** | Developer | [tbasualdo@uade.edu.ar](mailto:tbasualdo@uade.edu.ar) |
| **Lucas Bustamante** | Developer / PM | [lucabustamante@uade.edu.ar](mailto:lucabustamante@uade.edu.ar) |
| **Lautaro Casalini** | Developer | [lcasalini@uade.edu.ar](mailto:lcasalini@uade.edu.ar) |

> 📧 Para consultas sobre el proyecto, contactar al equipo a través de los correos institucionales.

---

## 📝 Licencia

Este proyecto está licenciado bajo la **Licencia MIT**. Consulta el archivo [`LICENSE`](LICENSE) para más detalles.

```
MIT License

Copyright (c) 2026 BiblioTech

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

<p align="center">
  Hecho con ❤️ para la materia <strong>Calidad de Software</strong> — UADE 2026
</p>
