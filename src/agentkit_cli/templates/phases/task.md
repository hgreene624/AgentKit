# Task Phase

## Purpose
Break the plan into actionable, trackable tasks organized by outcome.

## Prerequisites
- plan.md must exist

## Process

Unlike other phases, Task phase is more collaborative:
1. Agent proposes task breakdown based on plan and outcomes
2. User reviews and adjusts
3. Agent finalizes tasks.md

### Task Generation Rules

**Format**: `- [ ] T001 [P?] [O1?] Description → artifact`
- `T001`: Sequential task ID
- `[P]`: Parallelizable (can run alongside other [P] tasks)
- `[O1]`: Belongs to Outcome 1
- `→ artifact`: What this task produces

**Organization by Phase**:
1. **Setup** - Gather resources, prepare workspace
2. **Foundation** - Blocking work that enables all outcomes (⚠️ must complete first)
3. **Outcome phases** - One section per outcome (P1, P2, P3...)
4. **Polish** - Final quality checks and refinements

### Proposing Tasks
- Read outcomes from spec.md
- Read approach and timeline from plan.md
- Generate tasks that achieve each outcome
- Mark parallel opportunities with [P]
- Include checkpoint after each outcome phase

### Confirming with User
Present proposed tasks and ask:
- "Does this task breakdown look right?"
- "Any tasks to add, remove, or modify?"
- "Are the parallel [P] markers correct?"

## Completion Criteria
- Every outcome has associated tasks
- Tasks have clear artifacts/outputs
- Dependencies are logical (setup → foundation → outcomes → polish)
- User has confirmed the breakdown

## Output Document

Create `tasks.md` in project root:

```markdown
# Tasks: [PROJECT NAME]

**Spec**: spec.md | **Plan**: plan.md | **Date**: [DATE]

## Format
`- [ ] T001 [P?] [O1?] Description → artifact`

---

## Phase 1: Setup

- [ ] T001 [Description] → [artifact]
- [ ] T002 [P] [Description] → [artifact]

---

## Phase 2: Foundation (Blocking)

⚠️ Complete before starting any Outcome work

- [ ] T003 [Description] → [artifact]

---

## Phase 3: Outcome 1 - [Title] (P1) 🎯

**Goal**: [What this delivers]
**Validation**: [How to verify]

- [ ] T004 [O1] [Description] → [artifact]
- [ ] T005 [P] [O1] [Description] → [artifact]

**Checkpoint**: Outcome 1 complete

---

## Final Phase: Polish

- [ ] TXXX Quality review → [reviewed deliverables]

---

## Dependencies
- Setup → Foundation → Outcomes (can parallel) → Polish
```

## Transition
1. Save tasks.md
2. Update workflow-state.yaml: task=completed, current_phase=implement, tasks_total=[count]
3. Announce: "✓ Tasks defined! Ready to implement..."
4. Begin implement phase
