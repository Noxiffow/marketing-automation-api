from fastapi import FastAPI
from app.database import engine, Base
from app.routers import clientes, leads

# Crea todas las tablas en la BD si no existen todavía
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Automatización de Marketing",
    description="Gestión de clientes, seguimiento de leads y automatización comercial — WinoWin",
    version="1.0.0"
)

# Registrar los routers
app.include_router(clientes.router)
app.include_router(leads.router)


# Ruta raíz — comprobación rápida de que la API está viva
@app.get("/")
def root():
    return {"status": "ok", "mensaje": "API de Marketing WinoWin funcionando ✅"}
