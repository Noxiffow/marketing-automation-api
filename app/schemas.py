from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models import EstadoLead


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
    nombre:         Optional[str] = None
    email:          Optional[EmailStr] = None
    telefono:       Optional[str] = None
    origen:         Optional[str] = None
    responsable:    Optional[str] = None
    notas:          Optional[str] = None
    ultimo_contacto: Optional[datetime] = None
    proxima_accion:  Optional[datetime] = None


class LeadEstado(BaseModel):
    """Para cambiar solo el estado en el pipeline."""
    estado: EstadoLead


class LeadOut(BaseModel):
    """Lo que devuelve la API al consultar un lead."""
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
