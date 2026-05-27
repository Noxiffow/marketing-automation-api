import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import engine, Base
from app.routers import clientes, leads, reglas, auth
from app.scheduler import iniciar_scheduler

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")

# Ciclo de vida: arranca el scheduler al iniciar y lo para al cerrar
@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = iniciar_scheduler()
    yield
    scheduler.shutdown()

# Crea todas las tablas en la BD si no existen todavía
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Automatización de Marketing",
    description="Gestión de clientes, seguimiento de leads y automatización comercial — WinoWin",
    version="1.0.0",
    lifespan=lifespan,
)

# Registrar los routers
app.include_router(auth.router)
app.include_router(clientes.router)
app.include_router(leads.router)
app.include_router(reglas.router)


# Ruta raíz — comprobación rápida de que la API está viva
@app.get("/")
def root():
    return {"status": "ok", "mensaje": "API de Marketing WinoWin funcionando ✅"}
