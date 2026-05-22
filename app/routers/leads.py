from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import Lead, EstadoLead
from app.schemas import LeadCreate, LeadUpdate, LeadEstado, LeadOut

router = APIRouter(prefix="/api/leads", tags=["Leads"])


# GET /api/leads — listar todos (con filtro opcional por estado)
@router.get("/", response_model=List[LeadOut])
def listar_leads(estado: Optional[EstadoLead] = None, db: Session = Depends(get_db)):
    query = db.query(Lead)
    if estado:
        query = query.filter(Lead.estado == estado)
    return query.all()


# POST /api/leads — crear nuevo
@router.post("/", response_model=LeadOut, status_code=status.HTTP_201_CREATED)
def crear_lead(datos: LeadCreate, db: Session = Depends(get_db)):
    lead = Lead(**datos.model_dump())
    db.add(lead)
    db.commit()
    db.refresh(lead)
    return lead


# GET /api/leads/{id} — ver uno
@router.get("/{lead_id}", response_model=LeadOut)
def obtener_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado.")
    return lead


# PUT /api/leads/{id} — actualizar datos generales
@router.put("/{lead_id}", response_model=LeadOut)
def actualizar_lead(lead_id: int, datos: LeadUpdate, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado.")

    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(lead, campo, valor)

    db.commit()
    db.refresh(lead)
    return lead


# PATCH /api/leads/{id}/estado — avanzar en el pipeline
@router.patch("/{lead_id}/estado", response_model=LeadOut)
def cambiar_estado(lead_id: int, datos: LeadEstado, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado.")

    lead.estado = datos.estado
    db.commit()
    db.refresh(lead)
    return lead


# DELETE /api/leads/{id} — eliminar
@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead no encontrado.")

    db.delete(lead)
    db.commit()
