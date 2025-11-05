# src/crew_project/tools/TwilioReceiverTool.py
import os
from typing import Callable, Optional
from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse

class TwilioReceiverTool:
    """
    Webhook Flask para recibir WhatsApp desde Twilio (SIN validar firma).
    Úsalo solo en desarrollo. En producción, activa la validación.
    """

    def __init__(
        self,
        path: str = "/webhooks/twilio/whatsapp",
        on_message: Optional[Callable[[str, dict], str]] = None,

    ):
        self.path = path
        self.on_message = on_message
        self.app = Flask(__name__)
        self._configure_routes()

    def _configure_routes(self):
        @self.app.post(self.path)
        def whatsapp_webhook():
            from_number = request.form.get("From", "")
            to_number   = request.form.get("To", "")
            body        = request.form.get("Body", "")
            wa_id       = request.form.get("WaId", "")
            msg_sid     = request.form.get("MessageSid", "")
            num_media   = int(request.form.get("NumMedia", "0"))

            media = []
            for i in range(num_media):
                media.append({
                    "url": request.form.get(f"MediaUrl{i}", ""),
                    "content_type": request.form.get(f"MediaContentType{i}", "")
                })

            datos = {
                "from": from_number,
                "to": to_number,
                "wa_id": wa_id,
                "message_sid": msg_sid,
                "body": body,
                "media": media,
                "raw_form": request.form.to_dict(flat=True),
            }

            if self.on_message is not None:
                try:
                    respuesta_texto = self.on_message(body, datos)
                    if not isinstance(respuesta_texto, str):
                        respuesta_texto = "Recibido."
                except Exception as e:
                    respuesta_texto = f"Problema procesando tu mensaje. ({e})"
            else:
                respuesta_texto = "¡Recibido! (Webhook sin validación) ✅"

            twiml = MessagingResponse()
            twiml.message(respuesta_texto)
            return Response(str(twiml), mimetype="text/xml")

    def run(self, host: str = "0.0.0.0", port: int = 3500, debug: bool = True):
        self.app.run(host=host, port=port, debug=debug)

    def get_app(self):
        return self.app
