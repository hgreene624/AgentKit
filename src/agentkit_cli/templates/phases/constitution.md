# Constitution Phase

## Purpose
Establish the project's guiding principles, constraints, and definition of done.

## Prerequisites
None - this is the first phase.

## Adaptive Questioning

### Clarity Assessment
- **Low clarity**: User gave brief/vague project description → ask 4-5 questions
- **Medium clarity**: User provided some context → ask 2-3 questions
- **High clarity**: User gave detailed brief → ask 1-2 confirming questions

### Question Bank (prioritized)
1. **Core values** - What principles guide this project? (quality vs speed, innovation vs proven, budget-conscious vs premium)
2. **Aesthetic/style** - Any style preferences or standards to maintain?
3. **Constraints** - Budget, timeline, resources, or skills limitations?
4. **Decision framework** - When trade-offs arise, what takes priority?
5. **Definition of done** - What does success look like? How will you know it's complete?

### Presentation Rules
- Provide multiple choice options (a, b, c, d, Other)
- Recommend an answer with 1-sentence reasoning
- Accept user's choice or custom input
- Maximum 3 clarifications - make informed guesses for rest

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
