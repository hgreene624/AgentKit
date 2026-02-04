# AgentKit Auto-Orchestrated Project

This project uses AgentKit's auto-orchestrated workflow. The agent guides you through each phase automatically.

## Workflow Instructions

1. Read `.agentkit/workflow-state.yaml` to determine current phase
2. Load phase instructions from `.agentkit/phases/{current_phase}.md`
3. Follow phase instructions to guide user through questions
4. When phase completes, update state and transition to next phase

## State Detection Fallback

If state file is missing or corrupted, detect phase from documents:
- No constitution.md → constitution phase
- No spec.md → specify phase
- No plan.md → plan phase
- No tasks.md → task phase
- All exist → implement phase

## Available Commands

- `/start` or `/continue` - Resume auto-orchestrated workflow
- `/status` - Show current phase and progress
- `/skip` - Skip current phase (requires confirmation)
- `/specify`, `/plan`, `/task`, `/implement` - Manual phase jump

## Core Rules

- Ask questions adaptively (more if unclear, fewer if well-defined)
- Recommend answers with brief reasoning
- Maximum 3 clarifications per phase - make informed guesses for rest
- Update workflow state after each interaction
- Announce phase transitions clearly
