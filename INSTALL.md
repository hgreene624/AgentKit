# AgentKit Installation Guide

## Quick Install

```bash
cd /Users/holden/Documents/AgentKit

# 1. Install dependencies
pip install rich requests

# 2. Install AgentKit
pip install -e .

# 3. Verify installation
agentkit --version
agentkit check
```

---

## Detailed Installation

### Step 1: Install Dependencies

AgentKit requires Python 3.11+ and two packages:

```bash
pip install rich requests
```

Or with uv (recommended):

```bash
uv pip install rich requests
```

### Step 2: Install AgentKit

From the AgentKit directory:

```bash
cd /Users/holden/Documents/AgentKit
pip install -e .
```

The `-e` flag installs in "editable" mode, meaning you can modify the code and changes take effect immediately.

### Step 3: Verify Installation

```bash
# Check version
agentkit --version

# Check environment
agentkit check
```

Expected output:
```
AgentKit v0.1.0
```

---

## Environment Check

Run `agentkit check` to see what's available:

```bash
agentkit check
```

This will show:
- Python version (3.11+ required)
- Available AI agents (Claude, Copilot, Cursor, Gemini)
- Project status (if in an AgentKit project)

---

## First Project

Create your first project:

```bash
# Option 1: Create new directory
agentkit init my-first-idea

# Option 2: Initialize in current directory
cd existing-folder
agentkit init . --ai claude

# Option 3: With specific agent and scripts
agentkit init pottery-project --ai claude --script bash
```

Follow the interactive prompts or use flags to specify options.

---

## Troubleshooting

### Command not found: agentkit

If you get `command not found`, try:

```bash
# Use python -m instead
python -m agentkit_cli check
python -m agentkit_cli init my-project

# Or check your PATH
which agentkit
echo $PATH

# Reinstall
cd /Users/holden/Documents/AgentKit
pip install -e . --force-reinstall
```

### ModuleNotFoundError: No module named 'rich'

Install dependencies:

```bash
pip install rich requests
```

### Permission denied (scripts)

If bash scripts aren't executable:

```bash
chmod +x .agentkit/scripts/bash/*.sh
```

---

## Usage

Once installed and initialized:

```bash
cd my-project

# 1. Edit constitution
nano .agentkit/memory/constitution.md

# 2. Start your AI agent
claude  # or code/cursor/gemini

# 3. Use workflow commands
/specify Build something amazing
/clarify
/plan
/task
/implement
```

---

## Updating

To update AgentKit after changes:

```bash
cd /Users/holden/Documents/AgentKit
git pull  # if using git
pip install -e . --upgrade
```

---

## Uninstalling

```bash
pip uninstall agentkit-cli
```

---

## Getting Help

- Check `README.md` for overview
- Run `agentkit --help` for commands
- Run `agentkit check` for environment status
- View command templates in `.agentkit/` after initialization

---

## Next Steps

1. ✅ Install AgentKit
2. ✅ Run `agentkit check`
3. Create your first project with `agentkit init`
4. Edit the constitution with your principles
5. Start creating with your AI agent!

Happy creating! 🎨✨
