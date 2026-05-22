# Marketing Automation API

API REST para automatización de marketing: gestión de clientes, seguimiento de leads y reglas de automatización comercial.

## Stack
- **Python 3.11+** · **FastAPI** · **SQLite** · **SQLAlchemy** · **APScheduler** · **Pydantic**

## Funcionalidades
- CRUD completo de clientes con validación de email duplicado
- Pipeline de leads con estados: `nuevo → contactado → interesado → propuesta → convertido → perdido`
- Documentación interactiva automática (Swagger UI)
- Motor de reglas de automatización con scheduler (Fase 3)

## Estructura
```
app/
├── main.py              ← arranque y configuración
├── models.py            ← modelos de base de datos (Cliente, Lead)
├── database.py          ← conexión SQLite + sesiones
├── schemas.py           ← validación Pydantic
└── routers/
    ├── clientes.py      ← CRUD clientes (5 endpoints)
    ├── leads.py         ← CRUD + pipeline de leads (6 endpoints)
    └── automatizacion.py ← reglas y scheduler
```

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/clientes/` | Listar clientes |
| POST | `/api/clientes/` | Crear cliente |
| GET | `/api/clientes/{id}` | Obtener cliente |
| PUT | `/api/clientes/{id}` | Actualizar cliente |
| DELETE | `/api/clientes/{id}` | Eliminar cliente |
| GET | `/api/leads/` | Listar leads (filtro por estado) |
| POST | `/api/leads/` | Crear lead |
| GET | `/api/leads/{id}` | Obtener lead |
| PUT | `/api/leads/{id}` | Actualizar lead |
| PATCH | `/api/leads/{id}/estado` | Avanzar en el pipeline |
| DELETE | `/api/leads/{id}` | Eliminar lead |

## Arrancar en local
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```
Documentación interactiva: http://localhost:8001/docs

## Estado del proyecto
- ✅ Fase 1 — Base: modelos, schemas, endpoints CRUD, Swagger UI
- 🔄 Fase 2 — Pipeline avanzado y filtros de búsqueda
- ⏳ Fase 3 — Motor de reglas de automatización con APScheduler

---

<p align="right">Built by <a href="https://noxiffow.github.io/nozu">Nozu</a></p>
