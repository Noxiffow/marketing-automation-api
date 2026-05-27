from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


# --- ENUMs para el motor de automatización ---
class TipoCondicion(str, enum.Enum):
    dias_sin_contacto    = "dias_sin_contacto"     # ultimo_contacto >= X días atrás o nunca
    proxima_accion_vencida = "proxima_accion_vencida"  # proxima_accion < ahora
    estado_es            = "estado_es"             # lead.estado == valor


class TipoAccion(str, enum.Enum):
    cambiar_estado = "cambiar_estado"  # cambia el estado del lead (si transición válida)
    notificar      = "notificar"       # registra una notificación en la tabla


# --- ENUM: estados posibles de un Lead ---
class EstadoLead(str, enum.Enum):
    nuevo = "nuevo"
    contactado = "contactado"
    interesado = "interesado"
    propuesta = "propuesta"
    convertido = "convertido"
    perdido = "perdido"


# --- Reglas de transición del pipeline ---
# Define qué transiciones están permitidas entre estados.
# convertido y perdido como origen no aparecen aquí porque:
#   - convertido → no admite más cambios
#   - perdido → solo puede volver a "nuevo" (recuperación)
TRANSICIONES_PERMITIDAS: dict[EstadoLead, set[EstadoLead]] = {
    EstadoLead.nuevo:      {EstadoLead.contactado},
    EstadoLead.contactado: {EstadoLead.interesado, EstadoLead.perdido},
    EstadoLead.interesado: {EstadoLead.propuesta, EstadoLead.perdido},
    EstadoLead.propuesta:  {EstadoLead.convertido, EstadoLead.perdido},
    EstadoLead.perdido:    {EstadoLead.nuevo},
}


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

    # Relación con el historial de cambios de estado
    historial = relationship("LeadHistory", back_populates="lead", order_by="LeadHistory.fecha")


# --- TABLA: historial de cambios de estado de leads ---
class LeadHistory(Base):
    """Registra cada cambio de estado en el pipeline para trazabilidad completa."""
    __tablename__ = "lead_history"

    id              = Column(Integer, primary_key=True, index=True)
    lead_id         = Column(Integer, ForeignKey("leads.id", ondelete="CASCADE"), nullable=False)
    estado_anterior = Column(Enum(EstadoLead), nullable=False)
    estado_nuevo    = Column(Enum(EstadoLead), nullable=False)
    fecha           = Column(DateTime, server_default=func.now(), nullable=False)
    notas           = Column(Text, default="")

    # Relación inversa hacia el lead
    lead = relationship("Lead", back_populates="historial")


# --- TABLA: reglas de automatización ---
class ReglaAutomatizacion(Base):
    """Define una regla del tipo: SI <condicion> ENTONCES <accion>."""
    __tablename__ = "reglas_automatizacion"

    id               = Column(Integer, primary_key=True, index=True)
    nombre           = Column(String(150), nullable=False)
    condicion_tipo   = Column(Enum(TipoCondicion), nullable=False)
    condicion_valor  = Column(String(100), nullable=False)  # ej: "3" (días) o "nuevo" (estado)
    accion_tipo      = Column(Enum(TipoAccion), nullable=False)
    accion_valor     = Column(String(100), nullable=False)  # ej: "contactado" o mensaje
    activa           = Column(Boolean, default=True)
    fecha_creacion   = Column(DateTime, server_default=func.now())


# --- TABLA: notificaciones generadas por el motor ---
class Notificacion(Base):
    """Registro de notificaciones disparadas por el motor de automatización."""
    __tablename__ = "notificaciones"

    id          = Column(Integer, primary_key=True, index=True)
    lead_id     = Column(Integer, ForeignKey("leads.id", ondelete="CASCADE"), nullable=False)
    regla_id    = Column(Integer, ForeignKey("reglas_automatizacion.id", ondelete="SET NULL"), nullable=True)
    mensaje     = Column(Text, nullable=False)
    leida       = Column(Boolean, default=False)
    fecha       = Column(DateTime, server_default=func.now(), nullable=False)
