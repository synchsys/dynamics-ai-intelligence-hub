"""Reporter agent — writes the final report (#76).

Contract: ``report(client, material) -> str`` — a clear, well-structured report
composed from the material gathered by the other agents. Plain generation (no
tools, no schema): the output is prose for a human.
"""

from collections.abc import Mapping
from dataclasses import dataclass

from ai.client import AIClient

_INSTRUCTIONS = (
    "You are the reporter. Write a clear, well-structured final report from the "
    "material provided (the goal, findings, and review). Use only that material — "
    "do not invent facts — and note any open issues the reviewer raised."
)


@dataclass
class Reporter:
    """Material → final report."""

    instructions: str = _INSTRUCTIONS

    def report(self, client: AIClient, material: str) -> str:
        messages: list[Mapping[str, object]] = [
            {"role": "system", "content": self.instructions},
            {"role": "user", "content": material},
        ]
        return client.chat(messages)
