# src/desafio/crew.py
# -*- coding: utf-8 -*-
from typing import List
from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, task, crew

from src.desafio.tools.TranscribeAudioTool import TranscribeAudioTool
from src.desafio.tools.CalendarSchedulerTool import CalendarSchedulerTool

@CrewBase
class CrewProject:
    agents: List[Agent]
    tasks: List[Task]

    @agent
    def transcriptor(self) -> Agent:
        return Agent(
            config=self.agents_config["transcriptor"],
            tools=[TranscribeAudioTool()],
            verbose=self.agents_config["transcriptor"].get("verbose", False),
        )

    @agent
    def jennifer(self) -> Agent:
        return Agent(
            config=self.agents_config["jennifer"],
            tools=[CalendarSchedulerTool()],
            verbose=self.agents_config["jennifer"].get("verbose", False),
        )

    @task
    def transcribir_audio(self) -> Task:
        return Task(
            config=self.tasks_config["transcribir_audio"],
            agent=self.transcriptor(),
            output_key="texto_limpio",
        )

    @task
    def responder(self) -> Task:
        return Task(
            config=self.tasks_config["responder"],
            agent=self.jennifer(),
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.transcriptor(), self.jennifer()],
            tasks=[self.transcribir_audio(), self.responder()],
            process=Process.sequential,
            verbose=False,
        )
