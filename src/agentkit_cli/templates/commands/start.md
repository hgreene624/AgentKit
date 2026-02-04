# /start - Begin or Resume Workflow

Begin or continue the auto-orchestrated AgentKit workflow.

## Execution

1. **Read current state**
   - Load `.agentkit/workflow-state.yaml`
   - If missing, detect phase from existing documents
   - Sync state to documents if inconsistent (self-healing)

2. **Display progress** (if resuming)
   ```
   Welcome back! You're in the [PHASE] phase.
   Progress: [X/Y] phases complete
   [Current phase details if in_progress]
   ```

3. **Load phase instructions**
   - Read `.agentkit/phases/{current_phase}.md`
   - Follow the phase-specific guidance

4. **Begin/continue phase work**
   - If phase is pending: start with first questions
   - If phase is in_progress: continue from last_batch
   - If phase is completed: advance to next phase

5. **Update state after each interaction**
   - Save progress to workflow-state.yaml
   - Track questions answered, docs read

## Aliases
- `/continue` - Same as `/start`

## Notes
- This command orchestrates the full workflow automatically
- User just answers questions; agent handles phase transitions
- State is saved frequently to enable session resumption
