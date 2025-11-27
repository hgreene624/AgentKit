# AgentKit Quick Start

## Zero-to-Project from GitHub (3–5 minutes)

```bash
# 1) Install AgentKit from GitHub (pick one)
# Recommended: UV (fast)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv tool install git+https://github.com/hgreene624/agentkit.git

# Or: pip
pip install git+https://github.com/hgreene624/agentkit.git

# 2) Verify the CLI
agentkit --version
agentkit check

# 3) Create a new project (in your current directory)
agentkit init my-idea --ai claude  # supports claude/copilot/cursor/gemini
cd my-idea

# 4) Create your first idea workspace
agentkit idea "My first idea"
ls .agentkit/ideas

# 5) Open constitution or start your agent
nano constitution.md   # or use your editor
claude                 # then run workflow commands below
```

## Workflow Commands (inside your AI agent)

```
/constitution   Set/adjust principles
/specify        Capture the idea
/clarify        Answer prompts to sharpen it
/plan           Turn the spec into a plan
/task           Break plan into tasks
/implement      Execute and create
```

## Example Flow

```
/specify Build an n8n workflow to automate SMS replies for hours/location.
/clarify [Agent asks about tone, triggers, edge cases...]
/plan Use n8n + Twilio; keyword routing; test mode first.
/task [Agent outputs categorized tasks]
/implement [Agent executes tasks and requests inputs]
```

## Project Layout

```
my-idea/
└── .agentkit/
    ├── memory/
    │   └── constitution.md
    ├── ideas/
    │   └── 001-my-first-idea/
    │       ├── spec.md
    │       ├── plan.md
    │       ├── tasks.md
    │       └── outputs/
    └── templates/
```

## Need Help?

- `agentkit --help` — show commands
- `agentkit check` — verify environment
- `README.md` — concepts and workflow
- `INSTALL.md` — troubleshooting and install options

**You're ready to create.** 🚀
