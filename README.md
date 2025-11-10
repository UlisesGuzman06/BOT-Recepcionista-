# 🤖 Proyecto CrewAI – Jennifer (Recepcionista WhatsApp)

Este proyecto implementa una **IA tipo agente CrewAI** que actúa como recepcionista virtual ("Jennifer") para Houston Aesthetics, recibiendo y respondiendo mensajes de WhatsApp mediante **Twilio**, con soporte para texto, audios (mock) y simulación de agenda.

---

## 🧩 Estructura del Proyecto

```
DESAFIO/
│
├── src/
│   └── desafio/
│       ├── main.py
│       ├── crew.py
│       └── tools/
│           ├── TwilioReceiverTool.py
│           ├── TwilioSenderTool.py
│           ├── TranscribeAudioTool.py
│           └── CalendarSchedulerTool.py
│
├── config/
│   ├── agents.yaml
│   └── tasks.yaml
│
├── .env
└── README.md
```

---

## ⚙️ Instalación

1. **Clonar o descargar** este proyecto.
2. Crear entorno virtual (recomendado con Python 3.13 o 3.12):

```bash
python -m venv .venv
.\.venv\Scriptsctivate
```

## 🔐 Variables de Entorno (.env)

Crea un archivo llamado `.env` en la raíz del proyecto y completalo así:

```bash
# === OpenAI / CrewAI ===
OPENAI_API_KEY=tu_api_key_aqui
MODEL=gpt-4o-mini

# === Twilio WhatsApp ===
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
TWILIO_WHATSAPP_FROM=whatsapp:+549XXXXXXXXXX

# === Ngrok (opcional) ===
NGROK_AUTHTOKEN=tu_token_ngrok
```

---

## 🚀 Ejecución del Servidor Flask

Desde la carpeta raíz:

```bash
python -m src.desafio.main
```

Esto levantará un servidor Flask local en:

```
http://localhost:3500/webhooks/twilio/whatsapp
```

---

## 🌍 Conectar con Twilio usando Ngrok

1. Iniciar túnel:
   ```bash
   ngrok http 3500
   ```
2. Copiar la URL generada (ejemplo):
   ```
   https://4b3f-181-28-210-14.ngrok-free.app
   ```
3. En tu consola de **Twilio → Sandbox WhatsApp**, pegala en:
   ```
   WHEN A MESSAGE COMES IN:
   https://4b3f-181-28-210-14.ngrok-free.app/webhooks/twilio/whatsapp
   ```
4. Guardar cambios ✅

---

## 💬 Probar Jennifer

Desde tu WhatsApp, escribí al **número del sandbox** (por ejemplo, +1 415 523 8886).

Mensajes de prueba:
- “Hola Jennifer”
- “Quiero un turno mañana”
- “audio_transcrito Hola quiero saber precios”
- “Necesito un facial”

Jennifer te responderá automáticamente usando la lógica definida en `agents.yaml` y `tasks.yaml`.

---

## 🧠 Componentes Simulados

| Tool | Tipo | Descripción |
|------|------|-------------|
| `TwilioReceiverTool` | Real | Webhook Flask para recibir mensajes de Twilio |
| `TwilioSenderTool` | Real | Envía respuestas de WhatsApp usando Twilio API |
| `TranscribeAudioTool` | Mock | Simula transcripción de audio |
| `CalendarSchedulerTool` | Mock | Devuelve fechas y horas simuladas disponibles |

---
## 🧾 Licencia y Créditos

Desafío de agentes CrewAI 2025  
Autor: **Ulises Guzmán**  

