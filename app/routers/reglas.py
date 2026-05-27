from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import ReglaAutomatizacion, Notificacion
from app.schemas import ReglaCreate, ReglaUpdate, ReglaOut, NotificacionOut

router = APIRouter(prefix="/api/automatizacion", tags=["Automatización"])


# GET /api/automatizacion/reglas — listar reglas
@router.get("/reglas", response_model=List[ReglaOut])
def listar_reglas(db: Session = Depends(get_db)):
    return db.query(ReglaAutomatizacion).all()


# POST /api/automatizacion/reglas — crear regla
@router.post("/reglas", response_model=ReglaOut, status_code=status.HTTP_201_CREATED)
def crear_regla(datos: ReglaCreate, db: Session = Depends(get_db)):
    regla = ReglaAutomatizacion(**datos.model_dump())
    db.add(regla)
    db.commit()
    db.refresh(regla)
    return regla


# GET /api/automatizacion/reglas/{id} — ver una regla
@router.get("/reglas/{regla_id}", response_model=ReglaOut)
def obtener_regla(regla_id: int, db: Session = Depends(get_db)):
    regla = db.query(ReglaAutomatizacion).filter(ReglaAutomatizacion.id == regla_id).first()
    if not regla:
        raise HTTPException(status_code=404, detail="Regla no encontrada.")
    return regla


# PUT /api/automatizacion/reglas/{id} — actualizar regla
@router.put("/reglas/{regla_id}", response_model=ReglaOut)
def actualizar_regla(regla_id: int, datos: ReglaUpdate, db: Session = Depends(get_db)):
    regla = db.query(ReglaAutomatizacion).filter(ReglaAutomatizacion.id == regla_id).first()
    if not regla:
        raise HTTPException(status_code=404, detail="Regla no encontrada.")
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(regla, campo, valor)
    db.commit()
    db.refresh(regla)
    return regla


# DELETE /api/automatizacion/reglas/{id} — eliminar regla
@router.delete("/reglas/{regla_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_regla(regla_id: int, db: Session = Depends(get_db)):
    regla = db.query(ReglaAutomatizacion).filter(ReglaAutomatizacion.id == regla_id).first()
    if not regla:
        raise HTTPException(status_code=404, detail="Regla no encontrada.")
    db.delete(regla)
    db.commit()


# POST /api/automatizacion/ejecutar — lanzar el motor manualmente
@router.post("/ejecutar")
def ejecutar_motor(db: Session = Depends(get_db)):
    from app.scheduler import evaluar_reglas
    resultado = evaluar_reglas(db)
    return {"status": "ok", "acciones_ejecutadas": resultado}


# GET /api/automatizacion/notificaciones — ver notificaciones
@router.get("/notificaciones", response_model=List[NotificacionOut])
def listar_notificaciones(solo_no_leidas: bool = False, db: Session = Depends(get_db)):
    query = db.query(Notificacion)
    if solo_no_leidas:
        query = query.filter(Notificacion.leida == False)
    return query.order_by(Notificacion.fecha.desc()).all()


# PATCH /api/automatizacion/notificaciones/{id}/leida — marcar como leída
@router.patch("/notificaciones/{notif_id}/leida", response_model=NotificacionOut)
def marcar_leida(notif_id: int, db: Session = Depends(get_db)):
    notif = db.query(Notificacion).filter(Notificacion.id == notif_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notificación no encontrada.")
    notif.leida = True
    db.commit()
    db.refresh(notif)
    return notif
