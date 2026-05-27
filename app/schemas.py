from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from app.models import EstadoLead, TipoCondicion, TipoAccion


# ─────────────────────────────────────────
#  CLIENTES
# ─────────────────────────────────────────

class ClienteCreate(BaseModel):
    """Datos que hay que enviar para crear un cliente."""
    nombre:    str
    email:     EmailStr
    telefono:  Optional[str] = None
    empresa:   Optional[str] = None
    etiquetas: Optional[str] = None


class ClienteUpdate(BaseModel):
    """Todos los campos son opcionales — solo se actualiza lo que se envíe."""
    nombre:    Optional[str] = None
    email:     Optional[EmailStr] = None
    telefono:  Optional[str] = None
    empresa:   Optional[str] = None
    etiquetas: Optional[str] = None
    activo:    Optional[bool] = None


class ClienteOut(BaseModel):
    """Lo que devuelve la API al consultar un cliente."""
    id:         int
    nombre:     str
    email:      str
    telefono:   Optional[str]
    empresa:    Optional[str]
    etiquetas:  Optional[str]
    activo:     bool
    fecha_alta: Optional[datetime]

    class Config:
        from_attributes = True


# ─────────────────────────────────────────
#  LEADS
# ─────────────────────────────────────────

class LeadCreate(BaseModel):
    """Datos que hay que enviar para crear un lead."""
    nombre:      str
    email:       Optional[EmailStr] = None
    telefono:    Optional[str] = None
    origen:      Optional[str] = None
    responsable: Optional[str] = None
    notas:       Optional[str] = None


class LeadUpdate(BaseModel):
    """Actualización parcial de un lead."""
    nombre:          Optional[str] = None
    email:           Optional[EmailStr] = None
    telefono:        Optional[str] = None
    origen:          Optional[str] = None
    responsable:     Optional[str] = None
    notas:           Optional[str] = None
    ultimo_contacto: Optional[datetime] = None
    proxima_accion:  Optional[datetime] = None


class LeadEstado(BaseModel):
    """Para cambiar el estado en el pipeline, con nota opcional para el historial."""
    estado: EstadoLead
    notas: Optional[str] = None  # ← opcional: se guarda en LeadHistory


class LeadHistoryOut(BaseModel):
    """Entrada individual del historial de cambios de estado de un lead."""
    id:              int
    lead_id:         int
    estado_anterior: EstadoLead
    estado_nuevo:    EstadoLead
    fecha:           datetime
    notas:           Optional[str]

    class Config:
        from_attributes = True


class LeadOut(BaseModel):
    """Lo que devuelve la API al consultar un lead (versión sin historial)."""
    id:              int
    nombre:          str
    email:           Optional[str]
    telefono:        Optional[str]
    estado:          EstadoLead
    origen:          Optional[str]
    responsable:     Optional[str]
    notas:           Optional[str]
    ultimo_contacto: Optional[datetime]
    proxima_accion:  Optional[datetime]
    fecha_creacion:  Optional[datetime]

    class Config:
        from_attributes = True


class LeadOutConHistorial(LeadOut):
    """Lead con su historial completo de cambios de estado incluido."""
    historial: List[LeadHistoryOut] = []


# ─────────────────────────────────────────
#  REGLAS DE AUTOMATIZACIÓN
# ─────────────────────────────────────────

class ReglaCreate(BaseModel):
    """Datos para crear una regla de automatización."""
    nombre:          str
    condicion_tipo:  TipoCondicion
    condicion_valor: str
    accion_tipo:     TipoAccion
    accion_valor:    str
    activa:          bool = True


class ReglaUpdate(BaseModel):
    """Actualización parcial de una regla."""
    nombre:          Optional[str] = None
    condicion_tipo:  Optional[TipoCondicion] = None
    condicion_valor: Optional[str] = None
    accion_tipo:     Optional[TipoAccion] = None
    accion_valor:    Optional[str] = None
    activa:          Optional[bool] = None


class ReglaOut(BaseModel):
    """Lo que devuelve la API al consultar una regla."""
    id:              int
    nombre:          str
    condicion_tipo:  TipoCondicion
    condicion_valor: str
    accion_tipo:     TipoAccion
    accion_valor:    str
    activa:          bool
    fecha_creacion:  Optional[datetime]

    class Config:
        from_attributes = True


# ─────────────────────────────────────────
#  AUTENTICACIÓN / USUARIOS
# ─────────────────────────────────────────

class UserCreate(BaseModel):
    """Datos para registrar un nuevo usuario."""
    username: str
    email:    EmailStr
    password: str


class UserOut(BaseModel):
    """Datos públicos de un usuario (sin contraseña)."""
    id:             int
    username:       str
    email:          str
    activo:         bool
    fecha_creacion: Optional[datetime]

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Respuesta del endpoint de login."""
    access_token: str
    token_type:   str


# ─────────────────────────────────────────
#  NOTIFICACIONES
# ─────────────────────────────────────────

class NotificacionOut(BaseModel):
    id:       int
    lead_id:  int
    regla_id: Optional[int]
    mensaje:  str
    leida:    bool
    fecha:    datetime

    class Config:
        from_attributes = True
