# Constitution Phase

## Purpose
Establish the project's guiding principles, constraints, and definition of done.

## Prerequisites
None - this is the first phase.

## Prior Work Detection (FIRST)

Before starting the conversation, scan the project folder for existing files:
- Data files: `*.json`, `*.csv`, `*.xlsx`, `*.parquet`
- Analysis: `*.ipynb`, `*.py`, reports/, outputs/, results/
- Documentation: `*.md` files (not constitution.md, spec.md, plan.md, tasks.md)
- Other: any files that suggest prior work

If found, mention them:
> "I noticed this project folder contains existing files: [list key files]
> Should I incorporate these into our planning, or are we starting fresh?"

Record the decision. If incorporating, reference these files in later phases.

## Conversation Flow

### Opening (REQUIRED)
Start with an open-ended prompt - no suggested answers:

> "Tell me about your project. What are you trying to create?"

**Wait for user response.** Let them describe it in their own words.

### Technical Scoping (OPEN-ENDED)
Focus on understanding the concrete scope first. Ask open questions:
- "What are the main inputs? (data sources, APIs, files, user input)"
- "Who will use this? What's their technical level?"
- "What constraints are you working with - timeline, budget, technology stack?"
- "How will you know it's done? What's the minimum for a working version?"

**Priority**: Clarify the technical reality before discussing abstract values.
Have a back-and-forth conversation. Ask follow-ups to understand the scope deeply.

### Guiding Principles (NUMBERED OPTIONS)
After the scope is clear, **propose** guiding principles based on what you learned:

> "Based on what you've described, which principle should guide decisions?
> 1. Reliability - data accuracy and uptime matter most
> 2. Speed to market - get something working fast, iterate later
> 3. Flexibility - easy to adapt as requirements change
> 4. Simplicity - minimal complexity, easy to maintain
> 5. Other"

Propose options that fit the project context. Don't ask users to define values from scratch.

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
