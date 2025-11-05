# src/desafio/main.py
# -*- coding: utf-8 -*-
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Tu Crew (usa @CrewBase y toma agents/tasks del YAML)
from src.desafio.crew import CrewProject

# Tu webhook (la versión SIN validación que venimos usando)
from src.desafio.tools.TwilioReceiverTool import TwilioReceiverTool
# o, si tu paquete raíz es "src":
# from src.desafio.tools.TwilioReceiverTool import TwilioReceiverTool

load_dotenv()

# --- util: generar un slot sugerido simple ---
def generar_slot_sugerido() -> str:
    """
    Sugerimos un horario básico:
    - Si faltan > 2 horas para las 16:00 de HOY, ofrecer hoy 16:00.
    - Si no, ofrecer mañana 10:00.
    Ajustá a tu lógica real cuando conectes agenda.
    """
    ahora = datetime.now()
    hoy_16 = ahora.replace(hour=16, minute=0, second=0, microsecond=0)
    if hoy_16 - ahora > timedelta(hours=2):
        return hoy_16.strftime("%d/%m %H:%M")
    manana_10 = (ahora + timedelta(days=1)).replace(hour=10, minute=0, second=0, microsecond=0)
    return manana_10.strftime("%d/%m %H:%M")


def on_message_callback(texto: str, datos: dict) -> str:
    """
    1) Calcula un slot sugerido
    2) Ejecuta tu Crew con inputs que tu tasks.yaml espera:
       - incoming_text
       - slot_sugerido
    3) Devuelve UNA línea para responder por TwiML
    """
    try:
        slot = generar_slot_sugerido()

        # Tu CrewProject (carga agents.yaml y tasks.yaml automáticamente por @CrewBase)
        crew = CrewProject().crew()
        result = crew.kickoff(inputs={
            "incoming_text": texto,
            "slot_sugerido": slot
        })

        # CrewAI suele devolver un objeto con .raw; si no, casteamos a str
        respuesta = getattr(result, "raw", None) or str(result)
        # Forzar una sola línea (WhatsApp breve)
        return " ".join(respuesta.splitlines()).strip()
    except Exception as e:
        # Fallback amable si algo falla
        return f"Tu mensaje llegó perfecto. Estoy con un problema técnico ({e}). ¿Podés confirmarme en una línea qué necesitás?"

if __name__ == "__main__":
    receiver = TwilioReceiverTool(
        path="/webhooks/twilio/whatsapp",
        on_message=on_message_callback,
     
    )
    receiver.run(port=3500, debug=True)
