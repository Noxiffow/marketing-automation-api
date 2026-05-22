from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Ruta del archivo de base de datos SQLite
DATABASE_URL = "sqlite:///./marketing.db"

# Motor de base de datos
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # necesario para SQLite con FastAPI
)

# Fábrica de sesiones — cada petición a la API abre y cierra una sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Clase base de la que heredarán todos los modelos
Base = declarative_base()


# Función auxiliar — nos da una sesión de BD y la cierra al terminar
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
