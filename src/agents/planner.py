"""Planner agent — turns a goal into an ordered plan (#76).

Contract: ``plan(client, goal) -> Plan`` where ``Plan.steps`` is a short ordered
list of concrete steps. Uses structured output (#60) so the plan is schema-valid,
not free text. No tools — planning is pure reasoning.
"""

from dataclasses import dataclass

from pydantic import BaseModel, Field

from ai.client import AIClient
from ai.structured import structured_output

_INSTRUCTIONS = (
    "You are the planner. Break the user's goal into a short, ordered list of "
    "concrete, self-contained research steps. Prefer {max_steps} steps or fewer; "
    "each step should be actionable on its own."
)


class Plan(BaseModel):
    """An ordered research plan."""

    steps: list[str] = Field(default_factory=list, description="Ordered, concrete steps")


@dataclass
class Planner:
    """Goal → ordered plan."""

    instructions: str = _INSTRUCTIONS
    max_steps: int = 5

    def plan(self, client: AIClient, goal: str) -> Plan:
        messages = [
            {"role": "system", "content": self.instructions.format(max_steps=self.max_steps)},
            {"role": "user", "content": f"Goal: {goal}"},
        ]
        return structured_output(client, messages, Plan)
