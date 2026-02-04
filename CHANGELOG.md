# AgentKit Changelog

## [0.3.0] - 2026-02-04

### Major Changes

#### Auto-Orchestrated Workflow
- **NEW**: Agent automatically guides through all workflow phases
- No need to invoke `/specify`, `/plan`, `/task` manually - just say "start a project"
- Agent handles phase transitions automatically
- Adaptive questioning based on clarity level (1-5 questions per batch)

#### Session Resumability
- **NEW**: `workflow-state.yaml` tracks progress across sessions
- Stop mid-phase, close session, return later and continue exactly where you left off
- Self-healing: if state file is corrupted, detects phase from existing documents

#### Modular Phase Instructions
- **NEW**: Phase-specific instruction files in `.agentkit/phases/`
- Each phase file is ~400-500 tokens (vs 2000+ for monolithic approach)
- ~50% reduction in token usage per interaction
- Phases: constitution.md, specify.md, plan.md, task.md, implement.md

#### New Commands
- **NEW**: `/start` or `/continue` - Begin/resume auto-orchestrated workflow
- **NEW**: `/status` - Show current phase and progress
- **NEW**: `/skip` - Skip current phase (with confirmation)

#### Domain-Agnostic Design
- Templates work for ANY project type (ceramics, marketing, software, events)
- "Outcomes" instead of "User Stories"
- Task format: `- [ ] T001 [P?] [O1?] Description → artifact`
- Examples across multiple domains in templates

#### Agent Recommendations
- Agent recommends answers with brief reasoning
- Maximum 3 clarifications per phase - makes informed guesses for rest
- References constitution values when suggesting approaches

### New Files
- `src/agentkit_cli/state.py` - Workflow state management
- `.agentkit/phases/` - Phase instruction files
- `.agentkit/workflow-state.yaml` - Session state tracking
- `AGENTS.md` - Minimal router for auto-orchestration

### Breaking Changes
- `AGENTS.md` is now a minimal router (old content moved to phase files)
- New `.agentkit/phases/` directory structure
- Workflow state file format is new

### Migration Guide

For existing v0.2.0 projects, run `agentkit upgrade` (coming soon) or manually:
1. Create `.agentkit/phases/` directory
2. Copy phase instruction files from templates
3. Create `workflow-state.yaml` based on existing documents
4. Replace `AGENTS.md` with minimal router

### Dependencies
- Added: `pyyaml>=6.0.0`

---

## [0.2.0] - 2025-10-16

### Major Changes

#### Streamlined Constitution
- **Removed** Articles V (Tools & Methods) and VI (Collaboration Style) - these belong in planning, not constitution
- Constitution now focuses on strategic principles, not tactical implementation
- Added YAML frontmatter for structured metadata
- Constitution is now 5 articles instead of 7

#### Visible Project Structure
- **NEW**: Workflow documents now live in visible project directory
  - `constitution.md` - Created at project init (blank template)
  - `spec.md` - Created after `/specify` completes
  - `plan.md` - Created after `/plan` completes
  - `tasks.md` - Created after `/task` completes
- **NEW**: `deliverables/` directory for actual project outputs
- **NEW**: `notes/` directory for additional documentation
- No more hidden `.agentkit` directory for user-facing files

#### Task Management Improvements
- **NEW**: SpeckKit-style task IDs (T001, T002, T003...)
- **NEW**: Multi-phase support (T001, T101, T201...)
- **NEW**: Checkbox format `[ ] T001` → `[x] T001` for easy tracking
- Tasks use markdown checkboxes with proper spacing (blank lines between)

#### YAML Frontmatter
- All workflow documents now use YAML frontmatter + minimal markdown
- Structured data for: project name, date, status, team, decisions, timeline
- More token-efficient for AI parsing
- Maintains human readability

#### Interactive Question Flow
- Agent asks questions one-by-one with numbered options
- Agent provides best guess based on context
- "Other (please specify)" option always available
- Batches logically related questions (2-4 together)
- Reduces cognitive load while maintaining efficiency

#### Token Efficiency
- Strategic file reading - avoid re-reading unchanged files
- Batch related questions to reduce round-trips
- YAML frontmatter reduces parsing overhead
- Minimal prose in workflow docs

### Breaking Changes

- Constitution template structure changed (removed 2 articles)
- Project directory structure changed (visible files instead of hidden)
- Task format changed to checkbox style
- Templates now include YAML frontmatter

### Migration Guide

For existing v0.1.0 projects:

1. **Constitution**: Remove Articles V and VI if present
2. **Files**: Move workflow documents from `.agentkit/ideas/` to project root
3. **Tasks**: Convert task format to checkbox style with task IDs
4. **Structure**: Create `deliverables/` and `notes/` directories

---

## [0.1.0] - Initial Release

### Features

- Project initialization with `agentkit init`
- Support for multiple AI agents (Claude, Copilot, Cursor, Gemini)
- Constitution-based workflow
- Slash commands: /constitution, /specify, /clarify, /plan, /task, /implement
- Template system for specifications, plans, and tasks
- Hidden `.agentkit` directory structure
- Bash and PowerShell script support
