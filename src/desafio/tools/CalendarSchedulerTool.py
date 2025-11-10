# -*- coding: utf-8 -*-
from typing import Optional, Type, Literal, List
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import os, json

BUS_START, BUS_END, DURATION = 10, 18, 30  # 10–18h, 30'

def _fmt(dt: datetime) -> str: return dt.strftime("%d/%m %H:%M")
def _parse(s: str) -> datetime: return datetime.strptime(s, "%Y-%m-%d %H:%M")
def _over(a,b,c,d): return not (b<=c or d<=a)

def _path()->str: return os.getenv("CALENDAR_STORE_PATH", ".calendar_store/data.json")
def _load()->List[dict]:
    p=_path()
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        return json.load(open(p,"r",encoding="utf-8"))
    except: return []
def _save(evs:List[dict]): json.dump(evs, open(_path(),"w",encoding="utf-8"), ensure_ascii=False, indent=2)

class _Input(BaseModel):
    action: Literal["find","book","cancel","list"] = Field(..., description="find/book/cancel/list")
    start_time: Optional[str] = Field(None, description="YYYY-MM-DD HH:MM (book/cancel)")
    count: int = 2
    start_from_minutes: int = 120
    duration_minutes: int = DURATION
    client_name: Optional[str] = None
    days_ahead: int = 7

class CalendarSchedulerTool(BaseTool):
    name: str = "CalendarSchedulerTool"
    description: str = "Agenda mock con find/book/cancel/list."
    args_schema: Type[BaseModel] = _Input

    def _run(self, action: str, start_time: Optional[str] = None, count: int = 2,
             start_from_minutes: int = 120, duration_minutes: int = DURATION,
             client_name: Optional[str] = None, days_ahead: int = 7) -> str:
        evs = _load()
        now = datetime.now()

        if action == "find":
            found, cur = [], now + timedelta(minutes=start_from_minutes)
            cur = cur.replace(minute=0, second=0, microsecond=0)
            while len(found) < max(1, count) and cur < now + timedelta(days=30):
                if cur.hour < BUS_START: cur = cur.replace(hour=BUS_START)
                if cur.hour >= BUS_END:  cur = (cur + timedelta(days=1)).replace(hour=BUS_START)
                s, e = cur, cur + timedelta(minutes=duration_minutes)
                busy = any(_over(s,e,_parse(x["start"]),_parse(x["end"])) for x in evs)
                if not busy: found.append(f"{_fmt(s)} ({duration_minutes} min)")
                cur += timedelta(minutes=duration_minutes)
            return "Opciones: " + "; ".join(found) if found else "Sin disponibilidad próxima."

        if action == "book":
            if not start_time: return "Error: falta start_time (YYYY-MM-DD HH:MM)."
            s = _parse(start_time); e = s + timedelta(minutes=duration_minutes)
            if any(_over(s,e,_parse(x["start"]),_parse(x["end"])) for x in evs):
                return f"No disponible: {_fmt(s)} ya ocupado."
            evs.append({"start": s.strftime("%Y-%m-%d %H:%M"), "end": e.strftime("%Y-%m-%d %H:%M"),
                        "title": "Turno", "client": client_name or "Cliente"})
            _save(evs); return f"Reservado: {s.strftime('%A, %Y-%m-%d %H:%M')}."

        if action == "cancel":
            if not start_time: return "Error: falta start_time."
            s = _parse(start_time); n = len(evs)
            evs = [x for x in evs if _parse(x["start"]) != s]; _save(evs)
            return "Cancelado." if len(evs) < n else "No existía ese turno."

        if action == "list":
            end = now + timedelta(days=days_ahead)
            lst = [f"{_fmt(_parse(x['start']))}–{_fmt(_parse(x['end']))} {x.get('title','')}"
                   for x in evs if now <= _parse(x["start"]) <= end]
            return "Próximos: " + "; ".join(lst) if lst else "Sin turnos próximos."

        return "Acción inválida."
