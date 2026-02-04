# Constitution Phase

## Purpose
Establish the project's guiding principles, constraints, and definition of done.

## Prerequisites
None - this is the first phase.

## Conversation Flow

### Opening (REQUIRED)
Start with an open-ended prompt - no suggested answers:

> "Tell me about your project. What are you trying to create?"

**Wait for user response.** Let them describe it in their own words.

### Scoping Questions (OPEN-ENDED)
Ask these as open questions - user writes their own response, NO numbered options:
- "What principles or values should guide this project?"
- "What constraints are you working with - budget, timeline, resources?"
- "How will you know when it's done? What does success look like?"

Let the user describe things in their own words. Have a back-and-forth conversation.

### Clarifying Questions (NUMBERED OPTIONS)
After scoping, use numbered options to quickly fill gaps:

> "For trade-offs, which takes priority?
> 1. Speed - get it done fast
> 2. Quality - get it done right
> 3. Cost - keep it cheap
> 4. Other"

Use numbered options when you need a quick decision on something specific.

### Summary & Confirmation
Before creating the document, summarize what you learned:

> "Here's what I'm hearing: [summary]. Does this capture it?"

Let them correct or add before finalizing.

## Completion Criteria
Core principles documented covering: values, constraints, and success definition.

## Output Document

Create `constitution.md` in project root:

```yaml
---
project: "[PROJECT NAME]"
created: [DATE]
values:
  primary: "[main guiding principle]"
  secondary: "[supporting principles]"
constraints:
  budget: "[if applicable]"
  timeline: "[deadline or duration]"
  resources: "[available resources/skills]"
success:
  definition: "[what done looks like]"
  criteria: ["measurable criterion 1", "criterion 2"]
---

## Guiding Principles
[Brief prose expanding on values if needed]

## Decision Framework
When trade-offs arise: [priority order or decision rules]
```

## Transition
1. Save constitution.md
2. Update workflow-state.yaml: constitution=completed, current_phase=specify
3. Announce: "✓ Constitution complete! Moving to Specify phase..."
4. Begin specify phase questions
