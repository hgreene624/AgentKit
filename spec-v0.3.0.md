# AgentKit v0.3.0 Specification
## Auto-Orchestrated Workflow for Any Complex Project

---
project: AgentKit v0.3.0
type: cli-tool-enhancement
status: specified
date: 2026-02-04
authors: [holden, claude]

problem: |
  Users must manually invoke workflow commands (/specify, /plan, /task, /implement)
  in correct order. This creates friction and relies on user discipline.

solution: |
  Agent automatically orchestrates the full workflow, prompting users through each
  phase conversationally. User just answers questions; agent handles transitions.

key_changes:
  - from: "User invokes commands → Agent executes"
  - to: "User starts project → Agent drives entire workflow"

success_criteria:
  - SC-001: User completes full workflow without invoking slash commands
  - SC-002: Sessions are resumable - can stop and continue later
  - SC-003: 50% reduction in token usage via modular loading
  - SC-004: 100% backward compatibility - manual commands still work
---

## 1. Problem Statement

### Current State (v0.2.0)
- User must know and invoke `/specify`, `/clarify`, `/plan`, `/task`, `/implement` in order
- No enforcement beyond prerequisite scripts (which require user to run them)
- Agent dumps all questions at once (overwhelming)
- No session state - can't resume mid-phase
- Single large AGENTS.md loads on every interaction

### Pain Points
1. **Cognitive load**: User must remember workflow sequence
2. **No guidance**: User doesn't know when to transition phases
3. **Question overwhelm**: All questions presented at once
4. **No resumability**: Starting new session loses progress
5. **Token waste**: Full instructions loaded regardless of phase

## 2. Outcomes (Prioritized Deliverables)

### Outcome 1 - Auto-Orchestrated Workflow (Priority: P1) 🎯 MVP

Agent automatically guides user through all workflow phases without requiring manual command invocation.

**Why this priority**: Core value proposition - eliminates the main pain point of manual orchestration.

**Independent Validation**: User says "start a project about X" and completes constitution → specify → plan → task → implement with zero slash commands.

**Success Scenarios**:
1. **When** user says "start a project", **then** agent begins constitution phase automatically
2. **When** a phase completes, **then** agent transitions to next phase without user command
3. **When** user provides vague input, **then** agent asks more clarifying questions adaptively

---

### Outcome 2 - Session Resumability (Priority: P2)

Users can stop mid-workflow and resume later from exactly where they left off.

**Why this priority**: Critical for real-world usage where projects span multiple sessions.

**Independent Validation**: User stops mid-specify phase, closes session, returns next day, and continues from the exact question they left off.

**Success Scenarios**:
1. **When** user returns to project, **then** agent reads state and continues from last position
2. **When** state file is corrupted, **then** agent detects phase from existing documents (self-healing)
3. **When** user asks "where was I?", **then** agent shows current phase and progress

---

### Outcome 3 - Token-Efficient Architecture (Priority: P3)

Modular instruction loading reduces token usage by 50%+ compared to monolithic approach.

**Why this priority**: Improves performance and reduces costs for users.

**Independent Validation**: Measure tokens loaded per interaction - should be ~500-700 vs ~2000+ in v0.2.0.

**Success Scenarios**:
1. **When** agent starts, **then** only minimal router + current phase instructions load
2. **When** phase changes, **then** previous phase instructions unload, new phase loads
3. **When** documents already read in session, **then** agent skips re-reading them

---

### Outcome 4 - Backward Compatibility (Priority: P4)

All existing manual commands continue to work for power users.

**Why this priority**: Don't break existing workflows; provide migration path.

**Independent Validation**: Run all v0.2.0 commands (`/specify`, `/plan`, etc.) on v0.3.0 project - all work correctly.

**Success Scenarios**:
1. **When** user invokes `/specify` manually, **then** that phase runs and updates state
2. **When** user invokes `/plan` without spec.md, **then** error with helpful message
3. **When** user mixes manual and auto modes, **then** state stays consistent

---

## 3. Requirements

### Functional Requirements

- **R-001**: System MUST detect current workflow phase from state file or document existence
- **R-002**: System MUST auto-transition between phases when completion criteria met
- **R-003**: System MUST persist workflow state across sessions
- **R-004**: System MUST adapt question quantity based on clarity level (1-5 questions per batch)
- **R-005**: System MUST support manual phase override via existing commands
- **R-006**: System MUST self-heal state if state file and documents disagree
- **R-007**: System MUST load only current phase instructions (not all phases)
- **R-008**: System MUST track which documents have been read in current session
- **R-009**: Agent MUST recommend answers with reasoning when asking questions
- **R-010**: Agent MUST limit clarifications to maximum 3 per phase (make informed guesses for rest)

### Key Elements

- **Workflow State**: Tracks current phase, progress within phase, session info
- **Phase Instructions**: Modular files containing phase-specific guidance
- **Project Documents**: constitution.md, spec.md, plan.md, tasks.md, deliverables/
- **Router**: Minimal AGENTS.md that loads appropriate phase instructions

## 4. Architecture Overview

```
project/
├── AGENTS.md                      # Minimal router (~200 tokens)
├── constitution.md                # Project principles (Phase 1 output)
├── spec.md                        # What & why (Phase 2 output)
├── plan.md                        # How & when (Phase 3 output)
├── tasks.md                       # Actionable items (Phase 4 output)
├── deliverables/                  # Final outputs (Phase 5 outputs)
└── .agentkit/
    ├── workflow-state.yaml        # Session state + progress tracking
    ├── config.json                # Agent type, preferences (existing)
    └── phases/                    # Phase-specific instructions
        ├── constitution.md
        ├── specify.md
        ├── plan.md
        ├── task.md
        └── implement.md
```

## 5. Workflow State Management

### State File Schema
```yaml
# .agentkit/workflow-state.yaml
version: "0.3.0"
project:
  name: "project-name"
  created: 2026-02-04T10:00:00Z
  domain: "ceramics"  # or "software", "marketing", "event", etc.

current_phase: specify  # constitution | specify | plan | task | implement

session:
  last_active: 2026-02-04T14:30:00Z
  docs_read: [constitution]  # Skip re-reading these

phases:
  constitution:
    status: completed        # pending | in_progress | completed
    completed_at: 2026-02-04T10:15:00Z
  specify:
    status: in_progress
    questions_total: 8
    questions_answered: 3
    last_batch: 1
  plan:
    status: pending
  task:
    status: pending
  implement:
    status: pending
    tasks_total: 0
    tasks_completed: 0
```

### State Detection Logic (Self-Healing)

Agent uses dual verification:

1. **Primary**: Read `workflow-state.yaml`
2. **Fallback**: Check document existence
3. **Self-healing**: If mismatch, trust documents over state file

```
Document Existence → Implied Phase:
- No constitution.md     → constitution
- No spec.md            → specify
- No plan.md            → plan
- No tasks.md           → task
- All exist             → implement
```

## 6. Phase Definitions

### Phase 1: Constitution
**Purpose**: Establish project principles, constraints, definition of done

**Adaptive Questions** (clarity-based):
- Core principles and values guiding this project
- Aesthetic/style preferences and standards
- Budget, timeline, and resource constraints
- Decision-making framework when trade-offs arise
- What does "done" look like?

**Output**: `constitution.md` with YAML frontmatter

**Completion Criteria**: All core principles documented
**Transition**: Auto-advance to Specify

---

### Phase 2: Specify
**Purpose**: Capture WHAT will be created and WHY it matters

**Adaptive Questions** (clarity-based):
- What problem or opportunity does this address?
- Who benefits from this? (audience/users/recipients)
- What are the concrete deliverables/outputs?
- What's in scope vs explicitly out of scope?
- What are the must-have requirements?

**Output**: `spec.md` with YAML frontmatter + prioritized outcomes

**Gate**: Requires constitution.md
**Completion Criteria**: All outcomes defined with success scenarios
**Transition**: Auto-advance to Plan

---

### Phase 3: Plan
**Purpose**: Define HOW work will be done and WHEN

**Adaptive Questions** (clarity-based):
- What approach/method will you use?
- What resources, tools, or materials are needed?
- What are the dependencies and blockers?
- What's the timeline and key milestones?
- What could go wrong? (risks and contingencies)

**Output**: `plan.md` with YAML frontmatter

**Gate**: Requires spec.md
**Completion Criteria**: Approach defined, resources identified, timeline set
**Transition**: Auto-advance to Task

---

### Phase 4: Task
**Purpose**: Break plan into actionable, trackable items

**Process**:
- Agent proposes task breakdown organized by outcome
- User confirms/adjusts tasks
- Tasks formatted: `- [ ] T001 [P?] [O1?] Description → artifact`

**Output**: `tasks.md` with checkbox format, organized by outcome

**Gate**: Requires plan.md
**Completion Criteria**: All outcomes have tasks, dependencies clear
**Transition**: Auto-advance to Implement

---

### Phase 5: Implement
**Purpose**: Execute tasks, create deliverables

**Process**:
- Agent assists with tasks sequentially (or parallel where marked)
- Updates task checkboxes as completed
- Creates outputs in `deliverables/` folder

**Gate**: Requires tasks.md
**Completion Criteria**: All tasks checked off

## 7. Adaptive Question Design

### Clarity Assessment

| Clarity Level | Questions Per Batch | Signals |
|---------------|--------------------| --------|
| **Low** | 3-5 questions | Vague idea, many unknowns, broad scope, few details provided |
| **Medium** | 2-3 questions | Some definition, specific unknowns to resolve |
| **High** | 1-2 questions | Well-defined scope, just confirming details |

### Question Presentation Pattern

Agent MUST:
1. **Assess clarity** from user input and existing context
2. **Recommend an answer** with brief reasoning
3. **Provide options** as table or lettered list
4. **Include "Other"** for custom responses
5. **Limit to 3 clarifications** per phase - make informed guesses for rest

**Example - Low Clarity:**
```markdown
Let's explore what you're creating:

1. **What's the core problem or opportunity?**
   (Describe in your own words)

2. **Who is this for?**
   a) Yourself  b) A client  c) A specific audience  d) Other

3. **What type of output?**
   a) Physical product  b) Digital artifact  c) Service/experience  d) Document/plan  e) Other

4. **What's your timeline?**
   a) Flexible  b) Weeks  c) Months  d) Specific deadline

**Recommended for Q2**: Based on your mention of "restaurant," I'd suggest (c) A specific audience
```

**Example - High Clarity:**
```markdown
Based on your detailed brief, I just need to confirm:

1. **The 3-month timeline - is that firm or flexible?**
   a) Firm deadline  b) Flexible  c) Other

**Recommended**: Given the restaurant opening date you mentioned, I'd suggest (a) Firm deadline
```

### Clarify Taxonomy (Domain-Agnostic)

When scanning for ambiguities, assess these categories:

| Category | What to Check |
|----------|---------------|
| **Core Elements** | What's being created? Clear definition of outputs? |
| **Audience & Value** | Who benefits? Why does this matter to them? |
| **Scope & Boundaries** | What's included/excluded? Where does this end? |
| **Quality Standards** | What level of quality? How will we know it's good? |
| **Resources & Constraints** | Budget, time, materials, skills available? |
| **Dependencies** | What must happen first? What are we waiting on? |
| **Risks & Contingencies** | What could go wrong? What's the backup plan? |
| **Success Criteria** | How do we know when it's done? What does success look like? |

## 8. Token Efficiency Design

### 8.1 Tiered Instruction Loading

**Minimal AGENTS.md** (~200 tokens):
```markdown
# AgentKit Project

Read `.agentkit/workflow-state.yaml` for current phase.
Load instructions from `.agentkit/phases/{phase}.md`.

Fallback state detection:
- No constitution.md → constitution phase
- No spec.md → specify phase
- No plan.md → plan phase
- No tasks.md → task phase
- Otherwise → implement phase
```

**Phase files**: ~300-500 tokens each, loaded only when needed

**Per-message cost**: ~500-700 tokens vs ~2000+ monolithic

### 8.2 YAML-Heavy Documents

All workflow documents use structured frontmatter:
```yaml
---
project: Ceramics Collection
phase: specify
status: complete
outcomes:
  - id: O1
    title: "Serving bowl collection"
    priority: P1
requirements:
  - id: R-001
    text: "All pieces must be food-safe"
---

## Context
Minimal prose only where structure can't capture nuance.
```

**Savings**: ~40% vs full prose

### 8.3 Session Read Tracking

State file tracks `docs_read` - agent skips re-reading unless:
- Document was modified
- User explicitly asks about content
- Entering new phase that needs the context

## 9. Task Format (Domain-Agnostic)

### Format
```
- [ ] T001 [P?] [O1?] Description → artifact/output
```

| Component | Meaning |
|-----------|---------|
| `- [ ]` | Checkbox (incomplete) |
| `T001` | Task ID (sequential) |
| `[P]` | Parallelizable (optional) |
| `[O1]` | Belongs to Outcome 1 (optional) |
| `→ artifact` | What this task produces |

### Examples Across Domains

**Ceramics Project:**
```markdown
- [ ] T001 [O1] Source clay and glazes → materials inventory
- [ ] T002 [P] [O1] Throw prototype bowl → 8" bowl bisqueware
- [ ] T003 [P] [O1] Throw prototype plate → 10" plate bisqueware
- [ ] T004 [O1] Test glaze combinations → glaze test tiles
- [ ] T005 [O1] Fire final pieces → finished serving set
```

**Marketing Campaign:**
```markdown
- [ ] T001 [O1] Define target audience personas → persona document
- [ ] T002 [P] [O1] Draft social media copy → Instagram post series
- [ ] T003 [P] [O1] Design visual assets → campaign graphics folder
- [ ] T004 [O1] Schedule content calendar → publishing schedule
- [ ] T005 [O1] Launch campaign → live posts
```

**Event Planning:**
```markdown
- [ ] T001 [O1] Confirm venue and date → signed venue contract
- [ ] T002 [P] [O1] Create guest list → guest spreadsheet
- [ ] T003 [P] [O1] Design invitations → invitation PDF
- [ ] T004 [O1] Send invitations → sent confirmations
- [ ] T005 [O1] Coordinate catering → catering contract
```

**Software Project:**
```markdown
- [ ] T001 [O1] Set up project structure → initialized repo
- [ ] T002 [P] [O1] Create User model → src/models/user.py
- [ ] T003 [P] [O1] Create Auth service → src/services/auth.py
- [ ] T004 [O1] Implement login endpoint → src/api/login.py
- [ ] T005 [O1] Write integration tests → tests/test_auth.py
```

### Task Organization

**Phase Structure:**
1. **Setup** - Gather resources, prepare workspace
2. **Foundation** - Work that enables all outcomes (MUST complete first)
3. **Outcome Phases** - One phase per outcome (P1, P2, P3...)
4. **Polish** - Refinement, quality checks, final touches

## 10. User Experience

### Starting a Project
```
User: I want to start a ceramics project for a restaurant

Agent: Great! I'll guide you through the full workflow. Let's start with
       your project's constitution - the principles that will guide decisions.

       Based on "restaurant," I'm guessing this is client work with quality standards.

       1. **What are the core values for this project?**
          a) Quality craftsmanship over speed
          b) Innovation and uniqueness
          c) Budget-conscious practicality
          d) Other

          **Recommended**: (a) - restaurant tableware typically prioritizes durability and quality

       2. **What's your timeline constraint?**
          a) Flexible / no deadline
          b) 1-3 months
          c) 3-6 months
          d) Specific date: ___
```

### Resuming a Session
```
User: Let's continue the ceramics project

Agent: [Reads workflow-state.yaml]

       Welcome back! You're in the Specify phase (3/8 questions answered).

       Last time we established:
       - Core value: Quality craftsmanship
       - Timeline: 3 months (restaurant opening)
       - Budget: $5,000

       Continuing with:

       4. **What specific pieces are needed?**
          a) Full dinnerware set (plates, bowls, cups)
          b) Serving pieces only (bowls, platters)
          c) Accent pieces (vases, decorative)
          d) Custom mix: ___
```

### Phase Transitions
```
Agent: ✓ Specification complete! I've saved spec.md.

       Summary of what we're building:
       - 12 serving bowls (3 sizes)
       - 8 platters (2 sizes)
       - Food-safe, dishwasher-safe
       - Earth-tone glazes matching restaurant aesthetic

       Moving to Planning phase...

       Now let's figure out the approach:

       1. **What's your production method?**
          a) Wheel throwing (traditional)
          b) Slip casting (efficient for multiples)
          c) Hand building (organic shapes)
          d) Combination

          **Recommended**: (a) for serving pieces - better structural integrity
```

## 11. Backward Compatibility

Manual commands still work for power users:

| Command | Behavior in v0.3.0 |
|---------|-------------------|
| `/specify` | Jumps to Specify phase, runs that phase only |
| `/plan` | Jumps to Plan phase (requires spec.md) |
| `/task` | Jumps to Task phase (requires plan.md) |
| `/implement` | Jumps to Implement phase (requires tasks.md) |
| `/status` | Shows current workflow state |
| `/reset` | Resets to beginning (with confirmation) |

New commands:
| Command | Behavior |
|---------|----------|
| `/start` | Begins auto-orchestrated workflow from current state |
| `/continue` | Alias for `/start` |
| `/skip` | Skip current phase (with confirmation + warning) |

## 12. Implementation Scope

### In Scope
- [ ] Workflow state file schema and management
- [ ] Minimal AGENTS.md router
- [ ] Phase-specific instruction files (5 files)
- [ ] Auto-transition logic between phases
- [ ] Adaptive question batching with recommendations
- [ ] Session resumability
- [ ] YAML frontmatter templates for output docs
- [ ] `/start`, `/continue`, `/skip`, `/status` commands
- [ ] Update `agentkit init` to scaffold new structure
- [ ] `agentkit upgrade` for existing projects

### Out of Scope (Future)
- Multi-idea workspace orchestration
- Parallel phase execution
- Team/collaboration features
- Web UI
- Phase customization/plugin system
- Domain-specific templates (ceramics, marketing, etc.)

## 13. Migration Path

### For New Projects
`agentkit init` creates v0.3.0 structure automatically

### For Existing Projects
`agentkit upgrade` command:
1. Creates `.agentkit/phases/` directory
2. Generates phase instruction files
3. Creates workflow-state.yaml from existing documents
4. Updates AGENTS.md to minimal router
5. Preserves existing constitution.md, spec.md, etc.

## 14. Success Criteria (Measurable)

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Commands for full workflow | 1 ("start") vs 5+ | Count commands in test session |
| Token usage per session | 50% reduction | Compare token counts v0.2 vs v0.3 |
| Session resumability | 100% success | Test stop/resume 10 times |
| Time to first deliverable | Same or faster | Time from start to tasks.md |
| Backward compatibility | 100% | All v0.2 commands pass tests |
| User completes without help | 80%+ | User testing sessions |

## 15. Exceptions & Constraints

### What Could Go Wrong
- **State file corruption**: Mitigated by document-existence fallback
- **User skips phases**: `/skip` requires confirmation + warning about implications
- **Ambiguous domain**: Agent asks clarifying questions; defaults to general approach
- **Very large projects**: May need to break into sub-projects (future scope)

### Constraints
- Phase instructions must stay under 500 tokens each
- Maximum 3 clarification questions per phase
- State file must be human-readable YAML
- Must work with all supported agents (Claude, Copilot, Cursor, Gemini)

## 16. Open Questions

1. ~~**Question batching size**~~ **RESOLVED**: Adaptive based on clarity (1-5)
2. **State file location**: `.agentkit/` or root? → `.agentkit/` (keeps root clean)
3. **Phase skipping**: Allow? → Yes, with `/skip` + confirmation
4. **Undo support**: Go back a phase? → Not in v0.3.0 (future consideration)
5. **Domain detection**: Auto-detect project type? → Not in v0.3.0 (future)

---

## Appendix A: File Templates

### workflow-state.yaml (initial)
```yaml
version: "0.3.0"
project:
  name: ""
  created: null
  domain: null
current_phase: constitution
session:
  last_active: null
  docs_read: []
phases:
  constitution: {status: pending}
  specify: {status: pending}
  plan: {status: pending}
  task: {status: pending}
  implement: {status: pending}
```

### Minimal AGENTS.md
```markdown
# AgentKit Auto-Orchestrated Project

## Workflow
This project uses AgentKit's auto-orchestrated workflow.
Read `.agentkit/workflow-state.yaml` for current phase.
Load phase instructions from `.agentkit/phases/{current_phase}.md`.

## State Detection Fallback
If state file missing or corrupted:
- No constitution.md → constitution phase
- No spec.md → specify phase
- No plan.md → plan phase
- No tasks.md → task phase
- All exist → implement phase

## Commands
- `/start` or `/continue` - Resume auto-orchestrated workflow
- `/status` - Show current phase and progress
- `/skip` - Skip current phase (with confirmation)
- `/specify`, `/plan`, `/task`, `/implement` - Manual phase jump
```

### spec.md Template (Output)
```yaml
---
project: "[PROJECT NAME]"
phase: specify
status: complete
date: YYYY-MM-DD

outcomes:
  - id: O1
    title: "[Outcome title]"
    priority: P1
    validation: "[How to verify independently]"
  - id: O2
    title: "[Outcome title]"
    priority: P2
    validation: "[How to verify independently]"

requirements:
  - id: R-001
    text: "[Thing] MUST [requirement]"
  - id: R-002
    text: "[Thing] MUST [requirement]"

constraints:
  budget: "[if applicable]"
  timeline: "[deadline or duration]"
  other: "[any other constraints]"
---

## Context
[Brief prose describing the project vision and any nuance not captured above]

## Success Scenarios
[Key scenarios in When/Then format]
```

### tasks.md Template (Output)
```markdown
# Tasks: [PROJECT NAME]

**Spec**: spec.md | **Plan**: plan.md | **Date**: YYYY-MM-DD

## Format
`- [ ] T001 [P?] [O1?] Description → artifact`
- **[P]**: Can run in parallel
- **[O1]**: Belongs to Outcome 1

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
**Validation**: [How to verify independently]

- [ ] T004 [O1] [Description] → [artifact]
- [ ] T005 [P] [O1] [Description] → [artifact]

**Checkpoint**: Outcome 1 complete and validated

---

## Phase 4: Outcome 2 - [Title] (P2)

...

---

## Final Phase: Polish

- [ ] TXXX Quality review → [reviewed deliverables]
- [ ] TXXX Final adjustments → [polished outputs]

---

## Dependencies

- Setup → Foundation → Outcomes (can parallel) → Polish
- Outcomes can proceed independently after Foundation
```
