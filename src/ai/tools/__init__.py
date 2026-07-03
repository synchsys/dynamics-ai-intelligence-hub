"""Function-calling tool layer (Epic 8, #61).

A registry of schema-described :class:`Tool`s, argument validation before
dispatch, and a bounded model-driven :func:`run_tools` loop. Epic 10's agents
reuse this layer for orchestration rather than duplicating tool plumbing
(ADR-0006).
"""

from ai.tools.base import Tool, ToolArgumentError, ToolError, UnknownToolError
from ai.tools.registry import ToolRegistry
from ai.tools.router import ToolCallRecord, ToolRunResult, run_tools
from ai.tools.samples import add_tool, record_count_tool

__all__ = [
    "Tool",
    "ToolError",
    "ToolArgumentError",
    "UnknownToolError",
    "ToolRegistry",
    "run_tools",
    "ToolRunResult",
    "ToolCallRecord",
    "add_tool",
    "record_count_tool",
]
