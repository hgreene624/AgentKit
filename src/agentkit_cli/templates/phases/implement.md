# Implement Phase

## Purpose
Execute tasks and create deliverables. Track progress through completion.

## Prerequisites
- tasks.md must exist

## Process

Work through tasks systematically:
1. Start with Setup phase tasks
2. Complete Foundation phase (blocks all outcomes)
3. Work through Outcome phases (can be parallel if resources allow)
4. Finish with Polish phase

### For Each Task
1. Announce which task you're starting
2. Execute the work or guide user through it
3. Mark task complete: `- [x] T001 ...`
4. Update workflow-state.yaml with tasks_completed count
5. At checkpoints, pause for validation

### Parallel Tasks
Tasks marked [P] can be worked simultaneously if:
- Different resources/outputs (no conflicts)
- User has capacity for parallel work
- Not blocked by incomplete dependencies

### Checkpoints
After each outcome phase:
- Pause and summarize what was completed
- Ask user to validate the outcome
- Confirm ready to proceed to next phase

### Handling Blockers
If a task is blocked:
1. Note the blocker
2. Skip to next unblocked task
3. Return to blocked task when resolved
4. Update tasks.md with notes if needed

## Completion Criteria
- All tasks marked complete: `- [x]`
- All outcomes validated
- Deliverables created in `deliverables/` folder (if applicable)

## Progress Tracking

Update workflow-state.yaml after each task:
```yaml
phases:
  implement:
    status: in_progress
    tasks_total: 15
    tasks_completed: 7
```

## Output

Deliverables go in `deliverables/` folder:
```
deliverables/
├── [outcome-1-outputs]/
├── [outcome-2-outputs]/
└── [final-deliverables]/
```

## Completion

When all tasks are done:
1. Update all tasks to `[x]` in tasks.md
2. Update workflow-state.yaml: implement=completed
3. Summarize what was created
4. Announce: "✓ Project complete! All outcomes delivered."
5. List deliverables and their locations
