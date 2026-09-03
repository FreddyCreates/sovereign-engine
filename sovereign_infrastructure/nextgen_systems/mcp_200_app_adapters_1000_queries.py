"""
SOVEREIGN OS MCP 200 APP ADAPTERS & 1000 QUERIES ENGINE (FACADE)
Re-exports MCP200AppAdaptersEngine from mcp_200_app_adapters_engine.py for complete backwards compatibility.
"""

import os
import sys

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from sovereign_infrastructure.nextgen_systems.mcp_200_app_adapters_engine import (
    MCP200AppAdaptersEngine,
    MCP200AppAdapterEngine,
    AppAdapter,
    MCPAction,
    MCPExecutionResult,
    FlexResult
)

__all__ = [
    "MCP200AppAdaptersEngine",
    "MCP200AppAdapterEngine",
    "AppAdapter",
    "MCPAction",
    "MCPExecutionResult",
    "FlexResult"
]
