# Marketing Automation API

API REST para automatización de marketing: gestión de clientes, seguimiento de leads y reglas de automatización comercial.

## Stack
- **Python 3.11+** · **FastAPI** · **SQLite** · **SQLAlchemy** · **APScheduler** · **Pydantic v2**

## Funcionalidades
- CRUD completo de clientes con validación de email duplicado
- Pipeline de leads con estados validados: `nuevo → contactado → interesado → propuesta → convertido / perdido`
- Historial automático de cambios de estado con fecha y notas
- Filtros avanzados combinables: estado, origen, responsable, fechas y búsqueda de texto libre
- Motor de reglas de automatización SI/ENTONCES con APScheduler (ejecución cada hora)
- Gestión de notificaciones generadas automáticamente por el motor
- Documentación interactiva automática (Swagger UI en `/docs`)

## Estructura
```
app/
├── main.py              ← arranque, lifespan y registro de routers
├── models.py            ← modelos: Cliente, Lead, LeadHistory, ReglaAutomatizacion, Notificacion
├── database.py          ← conexión SQLite + sesiones
├── schemas.py           ← validación Pydantic (Create / Update / Out)
├── scheduler.py         ← motor de automatización + APScheduler
└── routers/
    ├── clientes.py      ← CRUD clientes (5 endpoints)
    ├── leads.py         ← CRUD + pipeline + historial (7 endpoints)
    └── reglas.py        ← automatización, notificaciones (8 endpoints)
```

## Endpoints

### Clientes
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/clientes/` | Listar clientes |
| POST | `/api/clientes/` | Crear cliente |
| GET | `/api/clientes/{id}` | Obtener cliente |
| PUT | `/api/clientes/{id}` | Actualizar cliente |
| DELETE | `/api/clientes/{id}` | Eliminar cliente |

### Leads
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/leads/` | Listar leads (filtros: estado, origen, responsable, texto, fechas) |
| POST | `/api/leads/` | Crear lead |
| GET | `/api/leads/{id}` | Obtener lead con historial |
| PUT | `/api/leads/{id}` | Actualizar lead |
| PATCH | `/api/leads/{id}/estado` | Avanzar en el pipeline (con validación) |
| GET | `/api/leads/{id}/historial` | Historial completo de cambios de estado |
| DELETE | `/api/leads/{id}` | Eliminar lead |

### Automatización
| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | `/api/automatizacion/reglas` | Listar reglas |
| POST | `/api/automatizacion/reglas` | Crear regla |
| GET | `/api/automatizacion/reglas/{id}` | Obtener regla |
| PUT | `/api/automatizacion/reglas/{id}` | Actualizar regla |
| DELETE | `/api/automatizacion/reglas/{id}` | Eliminar regla |
| POST | `/api/automatizacion/ejecutar` | Lanzar el motor manualmente |
| GET | `/api/automatizacion/notificaciones` | Listar notificaciones |
| PATCH | `/api/automatizacion/notificaciones/{id}/leida` | Marcar notificación como leída |

## Arrancar en local
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```
Documentación interactiva: http://localhost:8001/docs

## Estado del proyecto
- ✅ Fase 1 — Base: modelos, schemas, CRUD de clientes, Swagger UI
- ✅ Fase 2 — Pipeline de leads con validación de transiciones, historial y filtros avanzados
- ✅ Fase 3 — Motor de reglas SI/ENTONCES, APScheduler cada hora, notificaciones
