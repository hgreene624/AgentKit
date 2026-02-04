# Specify Phase

## Purpose
Capture WHAT will be created and WHY it matters. Define outcomes, requirements, and scope.

## Prerequisites
- constitution.md must exist

## Adaptive Questioning

### Clarity Assessment
- **Low clarity**: Vague idea, no details → ask 4-5 questions
- **Medium clarity**: Some definition, gaps to fill → ask 2-3 questions
- **High clarity**: Detailed description provided → ask 1-2 confirming questions

### Question Bank (prioritized)
1. **Problem/Opportunity** - What problem does this solve or opportunity does it address?
2. **Audience** - Who benefits from this? Who is it for?
3. **Deliverables** - What specific outputs will be created?
4. **Scope boundaries** - What's explicitly NOT included?
5. **Requirements** - What must be true for this to succeed?

### Presentation Rules
- Provide options with recommendations
- Reference constitution values when suggesting answers
- Group related questions (2-3 per batch based on clarity)
- Maximum 3 clarifications per phase

## Completion Criteria
- At least one Outcome defined with priority and validation criteria
- Key requirements documented
- Scope boundaries clear

## Output Document

Create `spec.md` in project root:

```yaml
---
project: "[PROJECT NAME]"
phase: specify
status: complete
date: [DATE]

outcomes:
  - id: O1
    title: "[Primary outcome]"
    priority: P1
    validation: "[How to verify independently]"
  - id: O2
    title: "[Secondary outcome]"
    priority: P2
    validation: "[How to verify]"

requirements:
  - id: R-001
    text: "[Thing] MUST [requirement]"
  - id: R-002
    text: "[Thing] MUST [requirement]"

scope:
  included: ["item 1", "item 2"]
  excluded: ["explicitly not included"]

constraints:
  budget: "[from constitution]"
  timeline: "[from constitution]"
---

## Context
[Brief prose on project vision - only what can't be captured in YAML]

## Success Scenarios
- When [situation], then [expected result]
- When [situation], then [expected result]
```

## Transition
1. Save spec.md
2. Update workflow-state.yaml: specify=completed, current_phase=plan
3. Summarize what was specified
4. Announce: "✓ Specification complete! Moving to Plan phase..."
5. Begin plan phase questions
