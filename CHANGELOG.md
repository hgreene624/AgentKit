# AgentKit Changelog

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
