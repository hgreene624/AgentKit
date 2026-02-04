# AgentKit v0.3.0 Implementation Plan
## Auto-Orchestrated Workflow for Any Complex Project

---
project: AgentKit v0.3.0
type: implementation-plan
status: planning
date: 2026-02-04
spec: spec-v0.3.0.md

outcomes_addressed:
  - O1: Auto-Orchestrated Workflow (P1)
  - O2: Session Resumability (P2)
  - O3: Token-Efficient Architecture (P3)
  - O4: Backward Compatibility (P4)
---

## 1. Project Context

### Medium/Methods
- **Language**: Python 3.11+
- **Framework**: Click CLI (existing), Rich for output
- **Storage**: YAML files (workflow-state, config)
- **Validation**: pytest with tmp_path fixtures

### Resources Needed
- Existing AgentKit codebase (`src/agentkit_cli/`)
- SpecKit patterns for reference
- Test project for validation

### Constraints
- Phase instruction files: ≤500 tokens each
- Minimal AGENTS.md: ≤200 tokens
- Must work with: Claude, Copilot, Cursor, Gemini, Codex
- Backward compatible with v0.2.0 projects

## 2. Constitution Check

Verify alignment with AgentKit's principles:

| Principle | Status | Notes |
|-----------|--------|-------|
| Simplicity | ✅ | Modular files reduce complexity |
| Domain-agnostic | ✅ | No software-specific language in templates |
| Agent-agnostic | ✅ | Works with all supported agents |
| User-first | ✅ | Auto-orchestration reduces friction |

## 3. Implementation Strategy

### Approach
Incremental delivery organized by outcome. Each outcome can be validated independently.

### Guiding Principles
- **Working tool over perfect tool**: Get basic orchestration working, then refine
- **Test with real project**: Validate each milestone with non-software example (ceramics)
- **Preserve backward compatibility**: Existing commands must keep working
- **Domain-agnostic first**: All templates must work for any project type

## 4. Work Breakdown by Outcome

### Outcome 1: Auto-Orchestrated Workflow (P1) 🎯 MVP

**Goal**: Agent guides user through all phases without manual commands

| Task | Description | Output |
|------|-------------|--------|
| Create state.py module | Schema + read/write utilities | `src/agentkit_cli/state.py` |
| State detection fallback | Document existence check | Function in state.py |
| Minimal AGENTS.md router | ~200 token routing instructions | Template file |
| Phase: constitution.md | Phase-specific instructions | Template file |
| Phase: specify.md | Phase-specific instructions | Template file |
| Phase: plan.md | Phase-specific instructions | Template file |
| Phase: task.md | Phase-specific instructions | Template file |
| Phase: implement.md | Phase-specific instructions | Template file |
| Update init.py | Scaffold v0.3.0 structure | Modified init.py |
| /start command | Begin/resume auto workflow | Command template |

**Validation**: Run full workflow on ceramics project with zero slash commands

---

### Outcome 2: Session Resumability (P2)

**Goal**: Stop and continue from exact position

| Task | Description | Output |
|------|-------------|--------|
| State persistence | Save after each question batch | State write logic |
| Session tracking | docs_read, last_batch in state | State schema |
| State self-healing | Sync state to documents if mismatch | Fallback logic |
| /status command | Show current phase and progress | Command template |

**Validation**: Stop mid-specify, close session, reopen, continue from same question

---

### Outcome 3: Token-Efficient Architecture (P3)

**Goal**: 50% reduction in tokens per interaction

| Task | Description | Output |
|------|-------------|--------|
| Modular phase loading | Load only current phase file | AGENTS.md router |
| YAML frontmatter templates | Structured output docs | Template updates |
| Session read tracking | Skip re-reading docs | State tracking |
| Token measurement | Before/after comparison | Test results |

**Validation**: Measure token count v0.2 vs v0.3 - target 50% reduction

---

### Outcome 4: Backward Compatibility (P4)

**Goal**: All v0.2.0 commands work in v0.3.0

| Task | Description | Output |
|------|-------------|--------|
| Update existing commands | Sync state on manual invocation | Modified commands |
| /skip command | Skip phase with confirmation | Command template |
| Upgrade command | Migrate v0.2.0 → v0.3.0 | `src/agentkit_cli/upgrade.py` |
| Integration tests | Verify all commands work | Test suite |

**Validation**: Run all v0.2.0 commands on v0.3.0 project - all pass

---

## 5. Implementation Phases

### Phase 1: Setup

**Purpose**: Prepare development environment and foundational code

- [ ] T001 Create state.py with workflow-state schema → `src/agentkit_cli/state.py`
- [ ] T002 [P] Create minimal AGENTS.md router template → `templates/AGENTS-minimal.md`

**Checkpoint**: State module exists, can read/write YAML

---

### Phase 2: Foundation (Blocking)

**Purpose**: Core infrastructure that all outcomes depend on

⚠️ Complete before starting Outcome work

- [ ] T003 Implement state detection fallback → function in state.py
- [ ] T004 Implement state self-healing sync → function in state.py
- [ ] T005 Unit tests for state management → `tests/test_state.py`

**Checkpoint**: State detection works with missing/corrupted state file

---

### Phase 3: Outcome 1 - Auto-Orchestrated Workflow (P1) 🎯

**Goal**: Complete workflow without slash commands
**Validation**: Ceramics project runs constitution → implement with zero commands

- [ ] T006 [O1] Create phases/constitution.md → `templates/phases/constitution.md`
- [ ] T007 [P] [O1] Create phases/specify.md → `templates/phases/specify.md`
- [ ] T008 [P] [O1] Create phases/plan.md → `templates/phases/plan.md`
- [ ] T009 [P] [O1] Create phases/task.md → `templates/phases/task.md`
- [ ] T010 [P] [O1] Create phases/implement.md → `templates/phases/implement.md`
- [ ] T011 [O1] Update init.py for .agentkit/phases/ → modified `init.py`
- [ ] T012 [O1] Update init.py for workflow-state.yaml → modified `init.py`
- [ ] T013 [O1] Update init.py for minimal AGENTS.md → modified `init.py`
- [ ] T014 [O1] Create /start command template → `templates/commands/start.md`

**Checkpoint**: `agentkit init` creates v0.3.0 structure, workflow runs

---

### Phase 4: Outcome 2 - Session Resumability (P2)

**Goal**: Stop and resume from exact position
**Validation**: Stop mid-phase, return next day, continue exactly

- [ ] T015 [O2] Create /status command template → `templates/commands/status.md`
- [ ] T016 [O2] Add session tracking to state schema → updated state.py
- [ ] T017 [O2] Test session resume scenarios → `tests/test_resume.py`

**Checkpoint**: Session resume works across multiple test scenarios

---

### Phase 5: Outcome 3 - Token Efficiency (P3)

**Goal**: 50% token reduction
**Validation**: Measure before/after token counts

- [ ] T018 [O3] Implement YAML frontmatter templates → updated output templates
- [ ] T019 [O3] Add docs_read tracking to state → updated state logic
- [ ] T020 [O3] Measure token counts → test results document

**Checkpoint**: Token measurement shows ≥50% reduction

---

### Phase 6: Outcome 4 - Backward Compatibility (P4)

**Goal**: All v0.2.0 commands work
**Validation**: Run all existing commands - all pass

- [ ] T021 [O4] Update existing commands for state sync → modified command templates
- [ ] T022 [O4] Create /skip command template → `templates/commands/skip.md`
- [ ] T023 [O4] Create agentkit upgrade command → `src/agentkit_cli/upgrade.py`
- [ ] T024 [O4] Integration tests for all commands → `tests/test_integration.py`

**Checkpoint**: All v0.2.0 commands pass, upgrade works

---

### Final Phase: Polish

**Purpose**: Documentation, final testing, release prep

- [ ] T025 Update README.md → documented new features
- [ ] T026 [P] Update QUICKSTART.md → updated workflow guide
- [ ] T027 [P] Update CHANGELOG.md → version history
- [ ] T028 Bump version to 0.3.0 → updated `pyproject.toml`
- [ ] T029 End-to-end test full workflow → test results
- [ ] T030 Test with non-software project (ceramics) → validation complete

**Checkpoint**: Ready for release

---

## 6. Phase Instruction File Design

Each phase file follows this structure (~400-500 tokens):

```markdown
# {Phase} Phase

## Purpose
One-line description of this phase's goal.

## Prerequisites
- Required files that must exist
- Required state conditions

## Adaptive Questioning

### Clarity Assessment
How to assess user's clarity level for this phase.

### Question Bank (prioritized)
1. [Most important question]
2. [Second priority]
...

### Presentation Rules
- Recommend answers with reasoning
- Maximum 3 clarifications per phase
- Make informed guesses for rest

## Completion Criteria
How to know when this phase is done.

## Output Document
- Filename and location
- YAML frontmatter schema
- Required sections

## Transition
Update state, announce completion, begin next phase.
```

## 7. File Changes Summary

### New Files
| File | Purpose |
|------|---------|
| `src/agentkit_cli/state.py` | Workflow state management |
| `src/agentkit_cli/upgrade.py` | v0.2.0 → v0.3.0 migration |
| `templates/phases/constitution.md` | Phase instructions |
| `templates/phases/specify.md` | Phase instructions |
| `templates/phases/plan.md` | Phase instructions |
| `templates/phases/task.md` | Phase instructions |
| `templates/phases/implement.md` | Phase instructions |
| `templates/commands/start.md` | /start command |
| `templates/commands/status.md` | /status command |
| `templates/commands/skip.md` | /skip command |
| `templates/workflow-state.yaml` | State file template |
| `templates/AGENTS-minimal.md` | Minimal router |
| `tests/test_state.py` | State unit tests |
| `tests/test_integration.py` | Integration tests |
| `tests/test_resume.py` | Resume scenario tests |

### Modified Files
| File | Changes |
|------|---------|
| `src/agentkit_cli/__main__.py` | Add `upgrade` subcommand |
| `src/agentkit_cli/init.py` | Scaffold v0.3.0 structure |
| `pyproject.toml` | Version bump to 0.3.0 |
| `README.md` | Document new features |
| `QUICKSTART.md` | Update workflow instructions |
| `CHANGELOG.md` | Document v0.3.0 changes |
| Existing command templates | Add state sync logic |

## 8. Dependencies

```
Phase 1 (Setup) ──────────────────┐
                                  │
Phase 2 (Foundation) ─────────────┼──→ Phase 3 (O1: Auto-Workflow)
                                  │            │
                                  │            ├──→ Phase 4 (O2: Resumability)
                                  │            │
                                  │            ├──→ Phase 5 (O3: Token Efficiency)
                                  │            │
                                  │            └──→ Phase 6 (O4: Backward Compat)
                                  │                         │
                                  └─────────────────────────┴──→ Final (Polish)
```

**Critical Path**: Setup → Foundation → O1 → Polish

**Parallel Opportunities**:
- Phase instruction files (T006-T010) can be created in parallel
- Documentation updates (T025-T027) can be done in parallel
- O2, O3, O4 can proceed in parallel after O1

## 9. Risk Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Phase instructions exceed 500 tokens | Medium | Low | Ruthless editing, test with counter |
| State file corruption | Low | Medium | Self-healing fallback to documents |
| Backward compat breaks | Medium | High | Integration tests for all commands |
| Domain-specific language creeps in | Medium | Medium | Review templates with non-software lens |
| Upgrade edge cases | Medium | Medium | Conservative approach - preserve, don't delete |

## 10. Validation Strategy

### Unit Tests
- State file read/write
- State detection fallback
- Self-healing sync logic

### Integration Tests
- `agentkit init` creates correct structure
- `agentkit upgrade` preserves existing work
- All commands update state correctly
- Manual commands still work

### End-to-End Tests
- Full workflow: init → constitution → specify → plan → task → implement
- Session resume: stop mid-phase, continue later
- Non-software project: ceramics workflow from start to finish

### Domain Validation
Test all templates and examples work for:
- Ceramics/physical product
- Marketing campaign
- Event planning
- Software project (for comparison)

## 11. Implementation Order (Tasks)

Organized by outcome with dependencies:

```markdown
## Setup
- [ ] T001 Create state.py module
- [ ] T002 [P] Create minimal AGENTS.md router

## Foundation (Blocking)
- [ ] T003 State detection fallback [blocked by T001]
- [ ] T004 State self-healing sync [blocked by T001]
- [ ] T005 Unit tests for state [blocked by T001, T003, T004]

## Outcome 1: Auto-Workflow (P1)
- [ ] T006 phases/constitution.md [blocked by T002]
- [ ] T007 [P] phases/specify.md [blocked by T002]
- [ ] T008 [P] phases/plan.md [blocked by T002]
- [ ] T009 [P] phases/task.md [blocked by T002]
- [ ] T010 [P] phases/implement.md [blocked by T002]
- [ ] T011 Update init.py for phases [blocked by T006-T010]
- [ ] T012 Update init.py for state [blocked by T001]
- [ ] T013 Update init.py for AGENTS.md [blocked by T002]
- [ ] T014 /start command [blocked by T001, T003]

## Outcome 2: Resumability (P2)
- [ ] T015 /status command [blocked by T001]
- [ ] T016 Session tracking in state [blocked by T001]
- [ ] T017 Resume scenario tests [blocked by T014, T015, T016]

## Outcome 3: Token Efficiency (P3)
- [ ] T018 YAML frontmatter templates [blocked by T011]
- [ ] T019 docs_read tracking [blocked by T001]
- [ ] T020 Token measurement [blocked by T018, T019]

## Outcome 4: Backward Compat (P4)
- [ ] T021 Update existing commands [blocked by T001]
- [ ] T022 /skip command [blocked by T001]
- [ ] T023 Upgrade command [blocked by T011, T012, T013]
- [ ] T024 Integration tests [blocked by T021, T022, T023]

## Polish
- [ ] T025 Update README [blocked by T014, T015, T022]
- [ ] T026 [P] Update QUICKSTART [blocked by T014]
- [ ] T027 [P] Update CHANGELOG [blocked by all]
- [ ] T028 Bump version [blocked by T027]
- [ ] T029 End-to-end test [blocked by T011-T024]
- [ ] T030 Non-software project test [blocked by T029]
```

## 12. Ready for Implementation

With this plan approved, implementation begins with:

1. **T001**: Create `state.py` with workflow state schema
2. **T002**: Create minimal AGENTS.md router template (parallel)
3. **T006-T010**: Create phase instruction files (parallel after T002)

**MVP Milestone**: After T014 (/start command), Outcome 1 is complete and can be validated with a real project.

**Full Release**: After T030 (non-software test), v0.3.0 is ready for release.
