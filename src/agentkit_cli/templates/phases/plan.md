# Plan Phase

## Purpose
Define HOW the work will be done and WHEN. Determine approach, resources, timeline, and risks.

## Prerequisites
- spec.md must exist

## Conversation Flow

### Opening (REQUIRED)
After reading spec.md, start with an open-ended prompt:

> "How do you want to approach this? Do you have a method in mind, or would you like me to suggest an approach?"

**Wait for user response.** They may have a specific method or want guidance.

### Scoping Questions (OPEN-ENDED)
Ask these as open questions - user writes their own response, NO numbered options:
- "Walk me through how you'd approach this - what's the method?"
- "What tools, resources, or help do you need?"
- "What has to happen first? Any dependencies or blockers?"
- "What's your timeline - any deadlines or milestones?"

Let the user describe their approach. Propose alternatives if they're stuck.

### Clarifying Questions (NUMBERED OPTIONS)
After scoping, use numbered options to quickly fill gaps:

> "For the first milestone, which outcome should it cover?
> 1. O1 only
> 2. O1 and O2
> 3. All outcomes
> 4. Other"

Use numbered options for logistics decisions, not for approach discussions.

### Summary & Confirmation
Before creating the document, summarize the plan:

> "Here's the approach: [method, timeline, resources]. Does this work?"

Let them adjust before finalizing.

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
