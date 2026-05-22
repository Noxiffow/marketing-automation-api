from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum


# --- ENUM: estados posibles de un Lead ---
class EstadoLead(str, enum.Enum):
    nuevo = "nuevo"
    contactado = "contactado"
    interesado = "interesado"
    propuesta = "propuesta"
    convertido = "convertido"
    perdido = "perdido"


# --- TABLA: clientes ---
class Cliente(Base):
    __tablename__ = "clientes"

    id          = Column(Integer, primary_key=True, index=True)
    nombre      = Column(String(100), nullable=False)
    email       = Column(String(150), unique=True, index=True, nullable=False)
    telefono    = Column(String(20))
    empresa     = Column(String(100))
    etiquetas   = Column(String(200))           # ej: "VIP, recurrente"
    activo      = Column(Boolean, default=True)
    fecha_alta  = Column(DateTime, server_default=func.now())


# --- TABLA: leads ---
class Lead(Base):
    __tablename__ = "leads"

    id               = Column(Integer, primary_key=True, index=True)
    nombre           = Column(String(100), nullable=False)
    email            = Column(String(150), index=True)
    telefono         = Column(String(20))
    estado           = Column(Enum(EstadoLead), default=EstadoLead.nuevo, nullable=False)
    origen           = Column(String(50))       # web, WhatsApp, referido...
    responsable      = Column(String(100))      # comercial asignado
    notas            = Column(Text)
    ultimo_contacto  = Column(DateTime)
    proxima_accion   = Column(DateTime)
    fecha_creacion   = Column(DateTime, server_default=func.now())
