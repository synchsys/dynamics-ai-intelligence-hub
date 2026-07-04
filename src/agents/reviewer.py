"""Reviewer agent — checks an output for soundness (#76).

Contract: ``review(client, content, goal=?) -> Review`` with ``approved`` +
``issues`` + ``summary``. Uses structured output (#60) so the verdict is
machine-actionable by the workflow (#124). No tools.
"""

from dataclasses import dataclass

from pydantic import BaseModel, Field

from ai.client import AIClient
from ai.structured import structured_output

_INSTRUCTIONS = (
    "You are the reviewer. Check the content for correctness, completeness, and "
    "whether claims are grounded. Approve only if it is sound; otherwise list "
    "specific issues. Be concise and specific."
)


class Review(BaseModel):
    """A structured review verdict."""

    approved: bool = Field(description="True only if the content is sound")
    issues: list[str] = Field(default_factory=list, description="Specific problems, if any")
    summary: str = Field(description="One-line assessment")


@dataclass
class Reviewer:
    """Content → structured verdict."""

    instructions: str = _INSTRUCTIONS

    def review(self, client: AIClient, content: str, *, goal: str | None = None) -> Review:
        task = content if goal is None else f"Goal: {goal}\n\nContent to review:\n{content}"
        messages = [
            {"role": "system", "content": self.instructions},
            {"role": "user", "content": task},
        ]
        return structured_output(client, messages, Review)
