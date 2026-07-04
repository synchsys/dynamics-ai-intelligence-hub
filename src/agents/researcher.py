"""Researcher agent — investigates a task using tools / RAG (#76).

Contract: ``research(client, task, context=?) -> str`` (concise findings). Wraps
the :class:`~agents.agent.Agent` primitive over a tool registry, so the
researcher reuses the #61 tool layer (e.g. Dataverse reads, or a RAG-backed
tool). The only agent that calls tools.
"""

from dataclasses import dataclass, field

from agents.agent import Agent
from ai.client import AIClient
from ai.tools.registry import ToolRegistry

_INSTRUCTIONS = (
    "You are the researcher. Investigate the task using your available tools and "
    "report concise, factual findings grounded strictly in the tool results. If "
    "the tools cannot answer, say what is missing rather than guessing."
)


@dataclass
class Researcher:
    """Task → findings, using tools."""

    registry: ToolRegistry = field(default_factory=ToolRegistry)
    instructions: str = _INSTRUCTIONS
    max_iterations: int = 6

    def research(self, client: AIClient, task: str, *, context: str | None = None) -> str:
        agent = Agent(
            name="researcher",
            instructions=self.instructions,
            registry=self.registry,
            max_iterations=self.max_iterations,
        )
        return agent.run(client, task, context=context).content
