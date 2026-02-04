# /start - Begin or Resume Workflow

Begin or continue the auto-orchestrated AgentKit workflow.

## Execution

1. **Read current state**
   - Load `.agentkit/workflow-state.yaml`
   - If missing, detect phase from existing documents
   - Sync state to documents if inconsistent (self-healing)

2. **Context discovery** (first run only)
   - Scan project folder for existing files:
     - Data files: `*.json`, `*.csv`, `*.xlsx`
     - Prior analysis: `*.ipynb`, reports/, outputs/
     - Documentation: `*.md` files not part of AgentKit
   - If found, ask user:
     > "I found existing files in this project: [list files]
     > Should I incorporate them into our planning, or start fresh?"
   - Record decision in workflow-state.yaml

3. **Display progress** (if resuming)
   ```
   Welcome back! You're in the [PHASE] phase.
   Progress: [X/Y] phases complete
   [Current phase details if in_progress]
   ```

4. **Load phase instructions**
   - Read `.agentkit/phases/{current_phase}.md`
   - Follow the phase-specific guidance

5. **Begin/continue phase work**
   - If phase is pending: start with opening prompt (open-ended)
   - If phase is in_progress: continue conversation
   - If phase is completed: advance to next phase

6. **Update state after each interaction**
   - Save progress to workflow-state.yaml
   - Track questions answered, docs read

## Aliases
- `/continue` - Same as `/start`

## Notes
- This command orchestrates the full workflow automatically
- User describes things in their own words; agent asks follow-up questions
- State is saved frequently to enable session resumption
