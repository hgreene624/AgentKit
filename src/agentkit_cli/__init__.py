"""
AgentKit - Creative Idea Development with AI Agents

A toolkit for transforming fuzzy ideas into concrete realities through
structured workflows with AI coding agents.
"""

__version__ = "0.2.0"
__author__ = "AgentKit Maintainers"
__license__ = "MIT"

from .config import (
    AgentKitConfig,
    ProjectPaths,
    AGENT_CONFIG,
    SCRIPT_CONFIG,
    is_agentkit_project,
    find_agentkit_root,
)

__all__ = [
    "AgentKitConfig",
    "ProjectPaths",
    "AGENT_CONFIG",
    "SCRIPT_CONFIG",
    "is_agentkit_project",
    "find_agentkit_root",
    "__version__",
]
