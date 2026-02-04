# Plan Phase

## Purpose
Define HOW the work will be done and WHEN. Determine approach, resources, timeline, and risks.

## Prerequisites
- spec.md must exist

## Adaptive Questioning

### Clarity Assessment
- **Low clarity**: No approach mentioned → ask 4-5 questions
- **Medium clarity**: General approach known, details needed → ask 2-3 questions
- **High clarity**: Method already decided → ask 1-2 confirming questions

### Question Bank (prioritized)
1. **Approach/Method** - How will you create the deliverables? What technique or process?
2. **Resources needed** - What tools, materials, skills, or help do you need?
3. **Dependencies** - What must happen first? What are you waiting on?
4. **Timeline/Milestones** - Key checkpoints? When should each outcome be ready?
5. **Risks & Contingencies** - What could go wrong? What's the backup plan?

### Presentation Rules
- Reference outcomes from spec.md when planning
- Suggest approaches based on project domain
- Consider constitution constraints when recommending
- Maximum 3 clarifications - infer reasonable defaults

## Completion Criteria
- Approach defined for achieving outcomes
- Resources and dependencies identified
- Timeline with milestones established
- Major risks acknowledged

## Output Document

Create `plan.md` in project root:

```yaml
---
project: "[PROJECT NAME]"
phase: plan
status: complete
date: [DATE]

approach:
  method: "[Primary approach/technique]"
  rationale: "[Why this approach]"

resources:
  tools: ["tool 1", "tool 2"]
  materials: ["material 1", "material 2"]
  skills: ["skill needed"]
  dependencies: ["what must happen first"]

timeline:
  start: "[start date or 'immediately']"
  milestones:
    - name: "[Milestone 1]"
      target: "[date or timeframe]"
      outcomes: [O1]
    - name: "[Milestone 2]"
      target: "[date or timeframe]"
      outcomes: [O1, O2]
  deadline: "[final deadline if any]"

risks:
  - risk: "[What could go wrong]"
    mitigation: "[How to prevent or handle]"
---

## Approach Details
[Prose explaining the method if YAML isn't sufficient]

## Dependencies
[Any blocking items or prerequisites]
```

## Transition
1. Save plan.md
2. Update workflow-state.yaml: plan=completed, current_phase=task
3. Summarize the approach
4. Announce: "✓ Plan complete! Moving to Task phase..."
5. Begin proposing task breakdown
