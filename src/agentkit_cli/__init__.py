"""
AgentKit - Creative Idea Development with AI Agents

A toolkit for transforming fuzzy ideas into concrete realities through
structured workflows with AI coding agents.

v0.3.0: Auto-Orchestrated Workflow
- Agent automatically guides through all phases
- Session resumability with workflow state
- Modular phase instructions for token efficiency
"""

__version__ = "0.3.0"
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

from .state import (
    WorkflowState,
    read_state,
    write_state,
    detect_phase_from_documents,
    sync_state_to_documents,
    update_phase_status,
    create_initial_state,
    PHASE_ORDER,
)

__all__ = [
    "AgentKitConfig",
    "ProjectPaths",
    "AGENT_CONFIG",
    "SCRIPT_CONFIG",
    "is_agentkit_project",
    "find_agentkit_root",
    "WorkflowState",
    "read_state",
    "write_state",
    "detect_phase_from_documents",
    "sync_state_to_documents",
    "update_phase_status",
    "create_initial_state",
    "PHASE_ORDER",
    "__version__",
]
