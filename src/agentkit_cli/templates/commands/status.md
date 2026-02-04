# /status - Show Workflow Progress

Display current workflow state and progress.

## Execution

1. **Read state file**
   - Load `.agentkit/workflow-state.yaml`
   - If missing, detect from documents

2. **Display summary**
   ```
   ## Project: [NAME]

   **Current Phase**: [PHASE] ([STATUS])
   **Progress**: [X/5] phases complete

   ### Phase Status
   - [x] Constitution - completed
   - [>] Specify - in progress (3/8 questions)
   - [ ] Plan - pending
   - [ ] Task - pending
   - [ ] Implement - pending

   ### Current Phase Details
   [If in specify/plan: Questions answered: X/Y]
   [If in implement: Tasks completed: X/Y]

   ### Documents Created
   - constitution.md ✓
   - spec.md (in progress)
   ```

3. **Show next action**
   ```
   **Next**: Continue with `/start` or answer the pending questions.
   ```

## Output Format

Use clear visual indicators:
- `[x]` = completed
- `[>]` = in progress
- `[ ]` = pending
- `[!]` = blocked/error
