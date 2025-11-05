# -*- coding: utf-8 -*-
# src/desafio/tools/TwilioSenderTool.py
from typing import Type, Optional
from pydantic import BaseModel, Field, validator
from crewai.tools import BaseTool
from twilio.rest import Client
import os


class TwilioSenderInput(BaseModel):
    to: str = Field(..., description="Destino WhatsApp, ej: 'whatsapp:+549261000000'")
    body: str = Field(..., description="Texto a enviar por WhatsApp (1–2 líneas)")
    media_url: Optional[str] = Field(
        None,
        description="URL pública de una imagen/video/documento para adjuntar (opcional). Debe ser accesible por Twilio."
    )

    @validator("to")
    def ensure_whatsapp_prefix(cls, v: str) -> str:
        v = v.strip()
        if not v.startswith("whatsapp:"):
            raise ValueError("El campo 'to' debe comenzar con 'whatsapp:'. Ej: whatsapp:+549261000000")
        return v

    @validator("body")
    def non_empty_body(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("El 'body' no puede estar vacío.")
        return v


class TwilioSenderTool(BaseTool):
    """
    Tool REAL para enviar mensajes de WhatsApp vía Twilio.
    Requiere TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN y TWILIO_WHATSAPP_NUMBER
    en el entorno (o .env).
    """
    name: str = "TwilioSenderTool"
    description: str = (
        "Envía un mensaje de WhatsApp usando Twilio. "
        "Parámetros: to (whatsapp:+NN...), body (texto), media_url (opcional). "
        "Devuelve 'OK <MessageSid>' o 'Error ...'."
    )
    args_schema: Type[BaseModel] = TwilioSenderInput

    def _run(self, to: str, body: str, media_url: Optional[str] = None) -> str:
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        from_whatsapp = os.getenv("TWILIO_WHATSAPP_NUMBER")

        if not account_sid or not auth_token or not from_whatsapp:
            return (
                "Error: faltan variables de entorno. "
                "Requeridas: TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_NUMBER."
            )

        try:
            client = Client(account_sid, auth_token)

            create_kwargs = {
                "from_": from_whatsapp,
                "to": to,
                "body": body,
            }
            # Adjuntar media si viene
            if media_url:
                create_kwargs["media_url"] = [media_url]

            msg = client.messages.create(**create_kwargs)
            return f"OK {msg.sid}"
        except Exception as e:
            return f"Error enviando WhatsApp: {e}"
