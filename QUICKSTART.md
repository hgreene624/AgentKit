# AgentKit Quick Start

## 3-Minute Setup

```bash
# 1. Navigate to AgentKit
cd /Users/holden/Documents/AgentKit

# 2. Install
pip install rich requests
pip install -e .

# 3. Test it
agentkit check

# 4. Create project
agentkit init test-project --ai claude

# 5. Start working
cd test-project
nano .agentkit/memory/constitution.md
claude
```

## Workflow

Once your AI agent is running:

```
/specify [describe your idea]
/clarify [answer questions to sharpen it]
/plan [define the approach]
/task [break it down]
/implement [make it real]
```

## Example

```
/specify
Build an n8n workflow to automate text message responses
for business hours and location questions. Should feel
personal, not robotic.

/clarify
[Agent asks questions about triggers, tone, edge cases]

/plan
Use n8n + Twilio. Keyword detection. Template responses
with variables. Test mode before live.

/task
[Agent breaks into A/U/M/H tasks]

/implement
[Agent executes, asks for input when needed]
```

## File Structure

```
Your Project/
└── .agentkit/
    ├── memory/
    │   └── constitution.md    ← Edit this first!
    ├── ideas/
    │   └── 001-your-idea/
    │       ├── specification.md
    │       ├── plan.md
    │       ├── tasks.md
    │       └── outputs/
    └── templates/
```

## Need Help?

- `agentkit --help` - Show commands
- `agentkit check` - Verify environment
- See `README.md` for full docs
- See `INSTALL.md` for troubleshooting

---

**That's it! You're ready to create.** 🚀
