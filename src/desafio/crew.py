# src/desafio/crew.py (fragmento)
from typing import List
from crewai import Agent, Task, Crew, Process
from crewai.project import CrewBase, agent, task, crew

from src.desafio.tools.TwilioSenderTool import TwilioSenderTool  # <-- importar la tool

@CrewBase
class CrewProject:
    agents: List[Agent]
    tasks: List[Task]

    @agent
    def jennifer(self) -> Agent:
        return Agent(
            config=self.agents_config["jennifer"],
            tools=[TwilioSenderTool()],  # <-- ahora sí es una BaseTool válida
            verbose=self.agents_config["jennifer"].get("verbose", False),
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
            agents=[self.jennifer()],
            tasks=[self.responder()],
            process=Process.sequential,
            verbose=False,
        )
