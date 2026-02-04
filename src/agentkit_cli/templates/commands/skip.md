# /skip - Skip Current Phase

Skip the current workflow phase and advance to the next one.

## Execution

1. **Confirm intent**
   ```
   ⚠️ You're about to skip the [CURRENT_PHASE] phase.

   This means:
   - [PHASE]-specific document won't be created
   - Later phases may have less context to work with
   - You can always come back with /[PHASE] command

   Are you sure? (yes/no)
   ```

2. **If confirmed**
   - Update workflow-state.yaml:
     - Mark current phase as "skipped" (or leave pending)
     - Advance current_phase to next phase
   - Announce: "Skipped [PHASE]. Now in [NEXT_PHASE] phase."
   - Begin next phase

3. **If declined**
   - Stay in current phase
   - Continue with `/start`

## Phase-Specific Warnings

### Skipping Constitution
"Without a constitution, the agent won't have guiding principles for recommendations."

### Skipping Specify
"Without a spec, planning will lack clear outcomes to work toward."

### Skipping Plan
"Without a plan, tasks will be generated without approach or timeline context."

### Skipping Task
"Without tasks, there's no structured work breakdown for implementation."

## Notes
- Cannot skip Implement (it's the final phase)
- Skipped phases can be revisited with manual commands (/constitution, /specify, etc.)
- Use sparingly - the workflow exists to ensure quality
