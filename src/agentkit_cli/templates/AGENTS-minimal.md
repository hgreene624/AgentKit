# AgentKit Auto-Orchestrated Project

This project uses AgentKit's auto-orchestrated workflow. The agent guides you through each phase automatically.

## Workflow Instructions

1. **Sync state with documents** - Always verify state matches actual documents before proceeding
2. Read `.agentkit/workflow-state.yaml` to determine current phase
3. Load phase instructions from `.agentkit/phases/{current_phase}.md`
4. Follow phase instructions to guide user through conversation
5. When phase completes (document exists with content), update state and transition

## State Detection & Self-Healing

If state file is missing, corrupted, or inconsistent with documents:
- No constitution.md → constitution phase
- No spec.md → specify phase
- No plan.md → plan phase
- No tasks.md → task phase
- All exist → implement phase

**Trust documents over state file.** If state claims to be ahead of documents, roll back.

## Available Commands

- `/start` or `/continue` - Resume auto-orchestrated workflow
- `/status` - Show current phase and progress
- `/skip` - Skip current phase (requires confirmation)
- `/specify`, `/plan`, `/task`, `/implement` - Manual phase jump

## Conversation Style

- **Technical scoping first**: Understand concrete details (inputs, users, constraints) before abstract values
- **Open-ended for scope**: Let user describe technical reality in their own words
- **Numbered options for values/decisions**: Propose guiding principles based on what you learned
- Have a back-and-forth dialogue, not an interrogation
- Summarize and confirm before creating documents
- Update workflow state after each phase completes
