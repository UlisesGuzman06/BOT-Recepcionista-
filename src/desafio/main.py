# src/desafio/main.py
# -*- coding: utf-8 -*-
import re
from datetime import datetime, timedelta
from dotenv import load_dotenv

from src.desafio.crew import CrewProject
from src.desafio.tools.TwilioReceiverTool import TwilioReceiverTool
from src.desafio.tools.TwilioSenderTool import TwilioSenderTool

load_dotenv()

SESSIONS = {}

YES_WORDS = {
    "si", "sí", "ok", "dale", "confirmo", "confirmar", "listo",
    "perfecto", "de acuerdo", "sí,", "si,", "sí.", "si."
}
NO_WORDS = {
    "no", "otra", "otro", "cambiar", "mas tarde", "más tarde",
    "no puedo", "no me sirve", "no me queda", "otro horario"
}

MONTHS = {
    "enero":1,"febrero":2,"marzo":3,"abril":4,"mayo":5,"junio":6,
    "julio":7,"agosto":8,"septiembre":9,"setiembre":9,"octubre":10,"noviembre":11,"diciembre":12
}

def _norm(s: str) -> str:
    return (s or "").strip().lower()

def _get_session(wa_id: str):
    if wa_id not in SESSIONS:
        SESSIONS[wa_id] = {}
    return SESSIONS[wa_id]

def generar_slot_sugerido() -> str:
    ahora = datetime.now()
    hoy_16 = ahora.replace(hour=16, minute=0, second=0, microsecond=0)
    if (hoy_16 - ahora).total_seconds() > 7200:
        return hoy_16.strftime("%d/%m %H:%M")
    manana_10 = (ahora + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)
    return manana_10.strftime("%d/%m %H:%M")

def _mk_slot(dt: datetime) -> str:
    return dt.strftime("%d/%m %H:%M")

def try_parse_slot_es(text: str, default_hour: int | None = None) -> tuple[str|None, str|None]:
    t = (text or "").lower()

    # HORA (evitar confundir '13' del día como hora)
    h = None; m = 0
    mh = re.search(r"\b(\d{1,2}):(\d{2})\b", t)
    if mh:
        h = int(mh.group(1)); m = int(mh.group(2))
    else:
        mh = re.search(r"\ba\s*las\s*(\d{1,2})(?::(\d{2}))?\b", t)
        if mh:
            h = int(mh.group(1)); m = int(mh.group(2) or 0)
        else:
            mh = re.search(r"\b(\d{1,2})\s*(?:hs|horas|h)\b", t)
            if mh:
                h = int(mh.group(1)); m = 0
    if h is not None:
        if h == 24: h = 0
        if not (0 <= h <= 23): h = None

    # FECHA
    d = mo = None
    m1 = re.search(r"\b(\d{1,2})[/-](\d{1,2})\b", t)
    if m1:
        d = int(m1.group(1)); mo = int(m1.group(2))
    if d is None:
        m2 = re.search(
            r"\b(\d{1,2})\s*(?:de\s+)?(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre|octubre|noviembre|diciembre)\b",
            t
        )
        if m2:
            d = int(m2.group(1)); mo = MONTHS[m2.group(2)]

    now = datetime.now()
    if d and mo:
        year = now.year
        try_dt = datetime(year, mo, d, h if h is not None else (default_hour or 16), m, 0)
        if try_dt < now:
            try_dt = datetime(year + 1, mo, d, try_dt.hour, try_dt.minute, 0)
        if h is None:
            return (_mk_slot(try_dt), "hora")
        return (_mk_slot(try_dt), None)

    if h is not None:
        candidate = now.replace(hour=h, minute=m, second=0, microsecond=0)
        if (candidate - now).total_seconds() <= 2*3600:
            candidate = (now + timedelta(days=1)).replace(hour=h, minute=m, second=0, microsecond=0)
        return (_mk_slot(candidate), "fecha")

    return (None, None)

def on_message_callback(texto: str, datos: dict) -> str:
    try:
        incoming_text = (texto or "").strip()
        to = datos.get("from") or ""  # whatsapp:+549...
        wa_id = datos.get("wa_id") or datos.get("from") or ""
        ses = _get_session(wa_id)
        norm = _norm(incoming_text)

        # Etiqueta simulada: [AUDIO_TRANSCRITO: ...]
        tag = re.search(r"\[AUDIO_TRANSCRITO:\s*(.+?)\s*\]", incoming_text, flags=re.I)
        if tag:
            incoming_text = tag.group(1).strip()

        # Confirmación / rechazo con pendiente
        if ses.get("pending_slot") and any(w in norm for w in YES_WORDS):
            slot = ses.pop("pending_slot")
            TwilioSenderTool().run(to=to, body=f"¡Genial! Confirmo tu turno para el {slot}. Te esperamos unos minutos antes.")
            return ""
        if ses.get("pending_slot") and any(w in norm for w in NO_WORDS):
            parsed, falta = try_parse_slot_es(incoming_text)
            if parsed and not falta:
                ses["pending_slot"] = parsed
                TwilioSenderTool().run(to=to, body=f"Gracias. ¿Confirmo {parsed}? Respondé 'SI' para agendar.")
                return ""
            ses.pop("pending_slot")
            TwilioSenderTool().run(to=to, body="Sin problema. Decime día y hora exactos y te lo reservo.")
            return ""

        # Propuesta libre (fecha/hora en texto)
        parsed, falta = try_parse_slot_es(incoming_text)
        if parsed:
            if falta == "hora":
                ses["pending_slot"] = parsed
                TwilioSenderTool().run(to=to, body=f"Perfecto. Indicá la hora (ej: 18:00) para el {parsed.split()[0]}.")
                return ""
            if falta == "fecha":
                ses["pending_slot"] = parsed
                TwilioSenderTool().run(to=to, body=f"¿Te parece bien {parsed}? Si sí, respondé 'SI' y lo agendo.")
                return ""
            ses["pending_slot"] = parsed
            TwilioSenderTool().run(to=to, body=f"¿Confirmo {parsed}? Decime 'SI' para reservar.")
            return ""

        # Flujo normal con Crew (sin audio real)
        slot = generar_slot_sugerido()
        ses["pending_slot"] = slot

        crew = CrewProject().crew()
        result = crew.kickoff(inputs={
            "incoming_text": incoming_text,
            "audio_url": "",               # siempre vacío (no audio real)
            "slot_sugerido": slot,
            "texto_limpio": incoming_text
        })

        respuesta = getattr(result, "raw", None) or str(result)
        respuesta = " ".join(respuesta.splitlines()).strip()

        TwilioSenderTool().run(to=to, body=respuesta)
        return ""

    except Exception as e:
        TwilioSenderTool().run(
            to=datos.get("from") or "",
            body=f"Tu mensaje llegó perfecto. Estoy con un problema técnico ({e}). ¿Podés confirmarme en una línea qué necesitás?"
        )
        return ""

if __name__ == "__main__":
    receiver = TwilioReceiverTool(
        path="/webhooks/twilio/whatsapp",
        on_message=on_message_callback,
    )
    receiver.run(port=3500, debug=True)
