# test_twilio_sender.py
import os
from dotenv import load_dotenv

from src.desafio.tools.TwilioSenderTool import TwilioSenderTool

load_dotenv()

# tu número personal con whatsapp: delante
TO = "whatsapp:+5492615983376"  # poné tu número real acá

resp = TwilioSenderTool().run(to=TO, body="Mensaje de prueba desde TwilioSenderTool")
print("RESPUESTA TOOL:", resp)
