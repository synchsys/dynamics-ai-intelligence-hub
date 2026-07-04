"""The Agent primitive — a role + tools over the #61 tool layer (ADR-0007).

An :class:`Agent` pairs a name and role instructions with a
:class:`~ai.tools.registry.ToolRegistry`, and runs a task by delegating to
``run_tools`` (#61) — so agents reuse the single tool layer (ADR-0006) rather
than re-abstracting it. This is the seed the four core agents (#76) and the
multi-agent workflow (#124) build on; it is deliberately thin.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

from ai.client import AIClient
from ai.tools.registry import ToolRegistry
from ai.tools.router import ToolRunResult, run_tools
from shared.logging import get_logger

_logger = get_logger("agents.agent")


@dataclass
class Agent:
    """A named agent with role instructions and its own tool registry."""

    name: str
    instructions: str
    registry: ToolRegistry = field(default_factory=ToolRegistry)
    max_iterations: int = 6

    def run(self, client: AIClient, task: str, *, context: str | None = None) -> ToolRunResult:
        """Run ``task`` as this agent, using its tools; returns the tool-run result."""
        messages: list[Mapping[str, object]] = [{"role": "system", "content": self._system()}]
        if context:
            messages.append({"role": "user", "content": f"Context from prior steps:\n{context}"})
        messages.append({"role": "user", "content": task})
        _logger.info("agent %r running task (%d tool[s])", self.name, len(self.registry))
        return run_tools(client, messages, self.registry, max_iterations=self.max_iterations)

    def _system(self) -> str:
        return f"You are the {self.name} agent.\n{self.instructions}"


def agent_with_tools(name: str, instructions: str, tools: Sequence[object]) -> Agent:
    """Build an :class:`Agent` with a registry pre-populated from ``tools``."""
    registry = ToolRegistry()
    for tool in tools:
        registry.register(tool)  # type: ignore[arg-type]
    return Agent(name=name, instructions=instructions, registry=registry)
