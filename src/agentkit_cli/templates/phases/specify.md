# Specify Phase

## Purpose
Capture WHAT will be created and WHY it matters. Define outcomes, requirements, and scope.

## Prerequisites
- constitution.md must exist

## Conversation Flow

### Opening (REQUIRED)
Start with an open-ended prompt - no suggested answers:

> "What specifically do you want to create? Describe the deliverables and outcomes you're aiming for."

**Wait for user response.** Let them describe the scope in their own words.

### Scoping Questions (OPEN-ENDED)
Ask these as open questions - user writes their own response, NO numbered options:
- "What problem does this solve or opportunity does it create?"
- "Who is this for? Who benefits?"
- "What are the specific deliverables - what will exist when you're done?"
- "What's explicitly NOT included in this project?"

Let the user describe the scope in their own words. Dig deeper with follow-ups.

### Clarifying Questions (NUMBERED OPTIONS)
After scoping, use numbered options to quickly fill gaps:

> "What's the priority for these outcomes?
> 1. O1 is must-have, O2 is nice-to-have
> 2. Both are equally important
> 3. Other"

Use numbered options for specific decisions, not for scoping.

### Summary & Confirmation
Before creating the document, summarize the spec:

> "Let me summarize what we're building: [outcomes, requirements, scope]. Anything to add or change?"

Let them refine before finalizing.

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
