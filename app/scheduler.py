from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging

from app.database import SessionLocal
from app.models import (
    Lead, ReglaAutomatizacion, Notificacion, LeadHistory,
    TipoCondicion, TipoAccion, TRANSICIONES_PERMITIDAS, EstadoLead
)

logger = logging.getLogger("scheduler")

# ─────────────────────────────────────────────────────────────────
#  EVALUADOR DE CONDICIONES
#  Dado una regla y un lead, devuelve True si el lead cumple
#  la condición de la regla.
# ─────────────────────────────────────────────────────────────────

def evaluar_condicion(lead: Lead, regla: ReglaAutomatizacion) -> bool:
    ahora = datetime.utcnow()

    if regla.condicion_tipo == TipoCondicion.dias_sin_contacto:
        dias = int(regla.condicion_valor)
        if lead.ultimo_contacto is None:
            # Nunca contactado — usar fecha de creación como referencia
            referencia = lead.fecha_creacion or ahora
        else:
            referencia = lead.ultimo_contacto
        return (ahora - referencia) >= timedelta(days=dias)

    elif regla.condicion_tipo == TipoCondicion.proxima_accion_vencida:
        if lead.proxima_accion is None:
            return False
        return lead.proxima_accion < ahora

    elif regla.condicion_tipo == TipoCondicion.estado_es:
        return lead.estado.value == regla.condicion_valor

    return False


# ─────────────────────────────────────────────────────────────────
#  EJECUTOR DE ACCIONES
#  Aplica la acción de la regla sobre el lead.
#  Devuelve True si se ejecutó algo.
# ─────────────────────────────────────────────────────────────────

def ejecutar_accion(lead: Lead, regla: ReglaAutomatizacion, db: Session) -> bool:

    if regla.accion_tipo == TipoAccion.cambiar_estado:
        nuevo_estado = EstadoLead(regla.accion_valor)
        estados_validos = TRANSICIONES_PERMITIDAS.get(lead.estado)

        if not estados_validos or nuevo_estado not in estados_validos:
            logger.warning(
                f"[Regla {regla.id}] Transición inválida para lead {lead.id}: "
                f"{lead.estado} → {nuevo_estado}. Saltando."
            )
            return False

        estado_anterior = lead.estado
        lead.estado = nuevo_estado

        # Registrar en historial
        entrada = LeadHistory(
            lead_id=lead.id,
            estado_anterior=estado_anterior,
            estado_nuevo=nuevo_estado,
            notas=f"Automatización: {regla.nombre}",
        )
        db.add(entrada)
        logger.info(f"[Regla {regla.id}] Lead {lead.id}: {estado_anterior} → {nuevo_estado}")
        return True

    elif regla.accion_tipo == TipoAccion.notificar:
        mensaje = regla.accion_valor.replace("{nombre}", lead.nombre).replace("{estado}", lead.estado.value)
        notif = Notificacion(
            lead_id=lead.id,
            regla_id=regla.id,
            mensaje=mensaje,
        )
        db.add(notif)
        logger.info(f"[Regla {regla.id}] Notificación para lead {lead.id}: {mensaje}")
        return True

    return False


# ─────────────────────────────────────────────────────────────────
#  MOTOR PRINCIPAL
#  Evalúa todas las reglas activas contra todos los leads.
#  Devuelve el número de acciones ejecutadas.
# ─────────────────────────────────────────────────────────────────

def evaluar_reglas(db: Session) -> int:
    reglas = db.query(ReglaAutomatizacion).filter(ReglaAutomatizacion.activa == True).all()
    leads  = db.query(Lead).all()
    acciones = 0

    for regla in reglas:
        for lead in leads:
            try:
                if evaluar_condicion(lead, regla):
                    if ejecutar_accion(lead, regla, db):
                        acciones += 1
            except Exception as e:
                logger.error(f"[Regla {regla.id}] Error en lead {lead.id}: {e}")

    if acciones:
        db.commit()
        logger.info(f"Motor ejecutado: {acciones} acción(es) aplicada(s).")
    else:
        logger.info("Motor ejecutado: sin acciones necesarias.")

    return acciones


# ─────────────────────────────────────────────────────────────────
#  SCHEDULER — se ejecuta automáticamente cada hora
# ─────────────────────────────────────────────────────────────────

def job_automatizacion():
    """Función que llama el scheduler: abre sesión, ejecuta el motor y cierra."""
    db = SessionLocal()
    try:
        evaluar_reglas(db)
    finally:
        db.close()


def iniciar_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        job_automatizacion,
        trigger="interval",
        hours=1,
        id="motor_automatizacion",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler iniciado — motor se ejecutará cada hora.")
    return scheduler
