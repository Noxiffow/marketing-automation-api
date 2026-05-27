from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models import Lead, LeadHistory, EstadoLead, TRANSICIONES_PERMITIDAS
from app.schemas import (
    LeadCreate, LeadUpdate, LeadEstado, LeadOut,
    LeadOutConHistorial, LeadHistoryOut,
)
from app.auth import get_current_user

router = APIRouter(
    prefix="/api/leads",
    tags=["Leads"],
    dependencies=[Depends(get_current_user)],
)


# ────────────────────────────────────────────────────────────────────────
#  GET /api/leads — listar con filtros avanzados combinables
# ────────────────────────────────────────────────────────────────────────
@router.get("/", response_model=List[LeadOut])
def listar_leads(
    # --- Filtro por estado (uno o varios) ---
    estado: Optional[List[EstadoLead]] = Query(
        None,
        description="Filtrar por uno o varios estados (ej: ?estado=nuevo&estado=contactado)",
    ),
    # --- Filtro por origen ---
    origen: Optional[str] = Query(
        None,
        description="Filtrar por origen del lead (web, WhatsApp, referido…)",
    ),
    # --- Filtro por responsable ---
    responsable: Optional[str] = Query(
        None,
        description="Filtrar por comercial/responsable asignado",
    ),
    # --- Filtro por rango de fecha de creación ---
    fecha_creacion_desde: Optional[datetime] = Query(
        None,
        description="Filtrar leads creados desde esta fecha (ISO 8601)",
    ),
    fecha_creacion_hasta: Optional[datetime] = Query(
        None,
        description="Filtrar leads creados hasta esta fecha (ISO 8601)",
    ),
    # --- Filtro por rango de último contacto ---
    ultimo_contacto_desde: Optional[datetime] = Query(
        None,
        description="Filtrar por último contacto desde fecha (ISO 8601)",
    ),
    ultimo_contacto_hasta: Optional[datetime] = Query(
        None,
        description="Filtrar por último contacto hasta fecha (ISO 8601)",
    ),
    # --- Búsqueda por texto en nombre / email / notas ---
    texto: Optional[str] = Query(
        None,
        description="Buscar texto en nombre, email y notas del lead",
    ),
    # --- Sesión de BD ---
    db: Session = Depends(get_db),
):
    """
    Lista los leads aplicando los filtros indicados.

    Todos los filtros son opcionales y combinables entre sí.
    Si no se envía ningún filtro se devuelven todos los leads (compatibilidad
    hacia atrás con la Fase 1).
    """
    query = db.query(Lead)

    # Filtro por estado (uno o varios)
    if estado:
        query = query.filter(Lead.estado.in_(estado))

    # Filtro por origen
    if origen is not None:
        query = query.filter(Lead.origen == origen)

    # Filtro por responsable
    if responsable is not None:
        query = query.filter(Lead.responsable == responsable)

    # Filtro por rango de fecha de creación
    if fecha_creacion_desde is not None:
        query = query.filter(Lead.fecha_creacion >= fecha_creacion_desde)
    if fecha_creacion_hasta is not None:
        query = query.filter(Lead.fecha_creacion <= fecha_creacion_hasta)

    # Filtro por rango de último contacto
    if ultimo_contacto_desde is not None:
        query = query.filter(Lead.ultimo_contacto >= ultimo_contacto_desde)
    if ultimo_contacto_hasta is not None:
        query = query.filter(Lead.ultimo_contacto <= ultimo_contacto_hasta)

    # Búsqueda por texto en nombre, email y notas
    if texto is not None and texto.strip():
        patron = f"%{texto.strip()}%"
        query = query.filter(
            or_(
                Lead.nombre.ilike(patron),
                Lead.email.ilike(patron),
                Lead.notas.ilike(patron),
            )
        )

    return query.all()


# ────────────────────────────────────────────────────────────────────────
#  POST /api/leads — crear nuevo lead
# ────────────────────────────────────────────────────────────────────────
@router.post("/", response_model=LeadOut, status_code=status.HTTP_201_CREATED)
def crear_lead(datos: LeadCreate, db: Session = Depends(get_db)):
    """Crea un lead nuevo en estado 'nuevo'."""
    lead = Lead(**datos.model_dump())
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


# ────────────────────────────────────────────────────────────────────────
#  GET /api/leads/{id} — ver un lead (sin historial, Fase 1 compatible)
# ────────────────────────────────────────────────────────────────────────
@router.get("/{lead_id}", response_model=LeadOutConHistorial)
def obtener_lead(lead_id: int, db: Session = Depends(get_db)):
    """
    Obtiene un lead por ID incluyendo su historial completo de cambios
    de estado.
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado.")
    return lead


# ────────────────────────────────────────────────────────────────────────
#  PUT /api/leads/{id} — actualizar datos generales
# ────────────────────────────────────────────────────────────────────────
@router.put("/{lead_id}", response_model=LeadOut)
def actualizar_lead(lead_id: int, datos: LeadUpdate, db: Session = Depends(get_db)):
    """Actualiza los campos generales del lead (no el estado del pipeline)."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado.")

    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(lead, campo, valor)

    db.commit()
    db.refresh(lead)
    return lead


# ────────────────────────────────────────────────────────────────────────
#  PATCH /api/leads/{id}/estado — avanzar en el pipeline con validación
# ────────────────────────────────────────────────────────────────────────
@router.patch("/{lead_id}/estado", response_model=LeadOutConHistorial)
def cambiar_estado(lead_id: int, datos: LeadEstado, db: Session = Depends(get_db)):
    """
    Cambia el estado de un lead en el pipeline, validando que la transición
    sea válida según las reglas de negocio.

    Reglas:
      - nuevo → contactado
      - contactado → interesado | perdido
      - interesado → propuesta | perdido
      - propuesta → convertido | perdido
      - convertido → (final, no admite más cambios)
      - perdido → nuevo (recuperación)

    Se registra automáticamente en LeadHistory.
    Si se envía el campo opcional 'notas', se guarda en el historial.
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado.")

    estado_actual = lead.estado
    estado_nuevo = datos.estado

    # Si no hay cambio, no hacemos nada (idempotente)
    if estado_actual == estado_nuevo:
        return lead

    # Validar que la transición está permitida
    estados_destino = TRANSICIONES_PERMITIDAS.get(estado_actual)

    if estados_destino is None:
        raise HTTPException(
            status_code=400,
            detail=(
                f"No se puede cambiar desde el estado '{estado_actual.value}'. "
                f"Es un estado final que no admite más transiciones."
            ),
        )

    if estado_nuevo not in estados_destino:
        permitidos = ", ".join(e.value for e in estados_destino)
        raise HTTPException(
            status_code=400,
            detail=(
                f"Transición inválida: de '{estado_actual.value}' a "
                f"'{estado_nuevo.value}'. Transiciones permitidas: {permitidos}."
            ),
        )

    # Aplicar el cambio de estado
    lead.estado = estado_nuevo

    # Registrar en el historial
    entrada = LeadHistory(
        lead_id=lead.id,
        estado_anterior=estado_actual,
        estado_nuevo=estado_nuevo,
        notas=datos.notas or "",
    )
    db.add(entrada)
    db.commit()
    db.refresh(lead)
    return lead


# ────────────────────────────────────────────────────────────────────────
#  GET /api/leads/{id}/historial — consultar el historial de cambios
# ────────────────────────────────────────────────────────────────────────
@router.get(
    "/{lead_id}/historial",
    response_model=List[LeadHistoryOut],
)
def obtener_historial(lead_id: int, db: Session = Depends(get_db)):
    """
    Devuelve el historial completo de cambios de estado de un lead,
    ordenado cronológicamente.
    """
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado.")

    historial = (
        db.query(LeadHistory)
        .filter(LeadHistory.lead_id == lead_id)
        .order_by(LeadHistory.fecha)
        .all()
    )
    return historial


# ────────────────────────────────────────────────────────────────────────
#  DELETE /api/leads/{id} — eliminar lead
# ────────────────────────────────────────────────────────────────────────
@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_lead(lead_id: int, db: Session = Depends(get_db)):
    """Elimina un lead y todo su historial asociado (CASCADE)."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado.")

    db.delete(lead)
    db.commit()
