# -*- coding: utf-8 -*-
# src/desafio/tools/TranscribeAudioTool.py
from typing import Optional, Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

class TranscribeAudioInput(BaseModel):
    audio_url: Optional[str] = Field(
        None, description="URL del audio (MediaUrl de Twilio). Ignorada en MOCK."
    )
    language: Optional[str] = Field(
        "es", description="Idioma esperado. Ignorado en MOCK."
    )
    hint: Optional[str] = Field(
        None, description="Texto a devolver en modo MOCK; si no hay, usa un default."
    )

class TranscribeAudioTool(BaseTool):
    """
    MOCK-UP: simula la transcripción. No llama a servicios externos.
    Devuelve 'hint' si viene; si no, 'Transcripción simulada del audio'.
    """
    name: str = "TranscribeAudioTool"
    description: str = "Transcribe (MOCK). Devuelve hint o un texto simulado."
    args_schema: Type[BaseModel] = TranscribeAudioInput

    def _run(self, audio_url: Optional[str] = None, language: str = "es", hint: Optional[str] = None) -> str:
        return (hint or "Transcripción simulada del audio").strip()
