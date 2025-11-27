"""
AgentKit initialization module - handles project setup
"""

import os
import sys
import shutil
from pathlib import Path
from typing import Optional

from agentkit_cli.config import AgentKitConfig, ProjectPaths, ensure_directory
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

# Agent configurations
AGENT_CONFIG = {
    "claude": {
        "name": "Claude Code",
        "command_dir": ".claude/commands",
        "file_extension": ".md",
        "check_command": "claude --version"
    },
    "copilot": {
        "name": "GitHub Copilot",
        "command_dir": ".github/prompts",
        "file_extension": ".md",
        "check_command": "code --version"
    },
    "cursor": {
        "name": "Cursor",
        "command_dir": ".cursor/commands",
        "file_extension": ".md",
        "check_command": "cursor --version"
    },
    "gemini": {
        "name": "Gemini CLI",
        "command_dir": ".gemini/commands",
        "file_extension": ".md",
        "check_command": "gemini --version"
    }
}

# Script configurations
SCRIPT_CONFIG = {
    "bash": {
        "name": "Bash (Linux/Mac)",
        "extension": ".sh",
        "shebang": "#!/usr/bin/env bash"
    },
    "powershell": {
        "name": "PowerShell",
        "extension": ".ps1",
        "shebang": "# PowerShell script"
    },
    "ps": {
        "name": "PowerShell",
        "extension": ".ps1",
        "shebang": "# PowerShell script"
    }
}


def init_project(args) -> int:
    """
    Initialize a new AgentKit project
    
    Args:
        args: Command line arguments from argparse
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        # Determine project directory
        if args.here or args.project_name == ".":
            project_dir = Path.cwd()
            project_name = project_dir.name
        else:
            project_name = args.project_name
            project_dir = Path.cwd() / project_name
            
        console.print(f"\n[bold cyan]AgentKit Initialization[/bold cyan]")
        console.print(f"Project: [yellow]{project_name}[/yellow]")
        console.print(f"Location: [blue]{project_dir}[/blue]\n")
        
        # Check if directory exists and is not empty
        if project_dir.exists() and any(project_dir.iterdir()):
            if not args.force:
                console.print("[yellow]⚠️  Directory is not empty[/yellow]")
                if not Confirm.ask("Continue anyway?", default=False):
                    console.print("[red]Initialization cancelled[/red]")
                    return 1
                    
        # Create project directory if it doesn't exist
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Select AI agent
        ai_agent = args.ai
        if not ai_agent:
            ai_agent = select_ai_agent()
            
        if ai_agent not in AGENT_CONFIG:
            console.print(f"[red]Error: Unknown AI agent '{ai_agent}'[/red]")
            return 1
            
        # Select script type
        script_type = args.script
        if script_type == "ps":
            script_type = "powershell"
            
        if not script_type:
            script_type = select_script_type()
            
        if script_type not in SCRIPT_CONFIG:
            console.print(f"[red]Error: Unknown script type '{script_type}'[/red]")
            return 1
        
        # Persist selected agent and script type for later commands
        config = AgentKitConfig(project_dir)
        config.ai_agent = ai_agent
        config.script_type = script_type
        config.save()
            
        # Create project structure
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            
            task = progress.add_task("Creating project structure...", total=None)
            create_project_structure(project_dir, ai_agent, script_type)
            progress.update(task, completed=True)
            
            task = progress.add_task("Installing templates...", total=None)
            install_templates(project_dir, ai_agent)
            progress.update(task, completed=True)
            
            task = progress.add_task("Creating helper scripts...", total=None)
            create_scripts(project_dir, script_type)
            progress.update(task, completed=True)
            
            task = progress.add_task("Setting up command files...", total=None)
            setup_commands(project_dir, ai_agent)
            progress.update(task, completed=True)
            
        # Success message
        console.print()
        console.print(Panel.fit(
            f"[green]✓ Project initialized successfully![/green]\n\n"
            f"AI Agent: [cyan]{AGENT_CONFIG[ai_agent]['name']}[/cyan]\n"
            f"Script Type: [cyan]{SCRIPT_CONFIG[script_type]['name']}[/cyan]\n\n"
            f"[bold]Next Steps:[/bold]\n"
            f"1. cd {project_name if not args.here else '.'}\n"
            f"2. Run your AI agent (e.g., 'claude')\n"
            f"3. Use /constitution to set up your principles\n"
            f"4. Use /specify to start your first project\n"
            f"5. Follow workflow: /plan → /task → /implement",
            title="🎉 AgentKit Ready",
            border_style="green"
        ))
        
        return 0
        
    except Exception as e:
        console.print(f"[red]Error during initialization: {e}[/red]")
        import traceback
        traceback.print_exc()
        return 1


def select_ai_agent() -> str:
    """Prompt user to select an AI agent"""
    console.print("[bold]Select your AI agent:[/bold]")
    
    choices = []
    for key, config in AGENT_CONFIG.items():
        choices.append(f"{key} - {config['name']}")
        
    for i, choice in enumerate(choices, 1):
        console.print(f"  {i}. {choice}")
        
    while True:
        selection = Prompt.ask(
            "Enter number or name",
            choices=[str(i) for i in range(1, len(choices) + 1)] + list(AGENT_CONFIG.keys()),
            default="1"
        )
        
        # Handle number selection
        if selection.isdigit():
            idx = int(selection) - 1
            if 0 <= idx < len(AGENT_CONFIG):
                return list(AGENT_CONFIG.keys())[idx]
        
        # Handle name selection
        if selection in AGENT_CONFIG:
            return selection
            

def select_script_type() -> str:
    """Prompt user to select script type"""
    console.print("\n[bold]Select script type:[/bold]")
    
    # Detect platform and suggest default
    default_script = "bash" if os.name != "nt" else "powershell"
    
    console.print(f"  1. bash - Bash (Linux/Mac)")
    console.print(f"  2. powershell - PowerShell (Windows/Cross-platform)")
    
    selection = Prompt.ask(
        "Enter number or name",
        choices=["1", "2", "bash", "powershell", "ps"],
        default="1" if default_script == "bash" else "2"
    )
    
    if selection == "1" or selection == "bash":
        return "bash"
    elif selection == "2" or selection in ["powershell", "ps"]:
        return "powershell"
        
    return default_script


def create_project_structure(project_dir: Path, ai_agent: str, script_type: str):
    """Create the base directory structure"""

    # Create .agentkit structure (hidden, for internal use)
    agentkit_dir = project_dir / ".agentkit"

    # Memory directory
    (agentkit_dir / "memory").mkdir(parents=True, exist_ok=True)
    (agentkit_dir / "ideas").mkdir(parents=True, exist_ok=True)

    # Scripts directory
    script_dir = agentkit_dir / "scripts" / script_type
    script_dir.mkdir(parents=True, exist_ok=True)

    # Templates directory
    (agentkit_dir / "templates").mkdir(parents=True, exist_ok=True)

    # Agent-specific command directory
    agent_config = AGENT_CONFIG[ai_agent]
    command_dir = project_dir / agent_config["command_dir"]
    command_dir.mkdir(parents=True, exist_ok=True)

    # Create visible project directories
    (project_dir / "deliverables").mkdir(parents=True, exist_ok=True)
    (project_dir / "notes").mkdir(parents=True, exist_ok=True)


def install_templates(project_dir: Path, ai_agent: str):
    """Install template files from package"""

    templates_dir = project_dir / ".agentkit" / "templates"

    # Constitution template - create blank in visible directory
    constitution_template = get_constitution_template()
    constitution_file = project_dir / "constitution.md"
    constitution_file.write_text(constitution_template)

    # Also keep copy in memory for reference
    memory_constitution = project_dir / ".agentkit" / "memory" / "constitution.md"
    memory_constitution.write_text(constitution_template)

    # Specification template (keep in templates)
    spec_template = get_specification_template()
    (templates_dir / "specification-template.md").write_text(spec_template)

    # Plan template (keep in templates)
    plan_template = get_plan_template()
    (templates_dir / "plan-template.md").write_text(plan_template)

    # Tasks template (keep in templates)
    tasks_template = get_tasks_template()
    (templates_dir / "tasks-template.md").write_text(tasks_template)


def _read_template(path: Path, fallback) -> str:
    """Load a template file with a callable fallback"""
    try:
        return path.read_text()
    except FileNotFoundError:
        return fallback()


def create_scripts(project_dir: Path, script_type: str):
    """Create helper scripts"""
    
    script_dir = project_dir / ".agentkit" / "scripts" / script_type
    script_config = SCRIPT_CONFIG[script_type]
    ext = script_config["extension"]
    
    # Common utilities script
    common_script = get_common_script(script_type)
    common_file = script_dir / f"common{ext}"
    common_file.write_text(common_script)
    if script_type == "bash":
        common_file.chmod(0o755)
        
    # Create new idea script
    create_idea_script = get_create_idea_script(script_type)
    create_file = script_dir / f"create-new-idea{ext}"
    create_file.write_text(create_idea_script)
    if script_type == "bash":
        create_file.chmod(0o755)
        
    # Setup plan script
    setup_plan_script = get_setup_plan_script(script_type)
    setup_file = script_dir / f"setup-plan{ext}"
    setup_file.write_text(setup_plan_script)
    if script_type == "bash":
        setup_file.chmod(0o755)


def create_idea_workspace(args) -> int:
    """
    Create a new idea directory with numbered slug and starter templates
    """
    project_dir = Path.cwd()
    config = AgentKitConfig(project_dir)

    if not config.is_initialized():
        console.print("[red]Error: Not inside an AgentKit project[/red]")
        return 1

    try:
        idea_number = config.get_next_idea_number()
        slug_base = args.slug or args.name
        slug = config.create_idea_slug(slug_base) if slug_base else ""
        idea_name = f"{idea_number}-{slug}" if slug else idea_number

        paths = ProjectPaths(project_dir)
        idea_dir = paths.idea_dir(idea_name)

        if idea_dir.exists() and not args.force:
            console.print(f"[red]Idea directory already exists: {idea_dir}[/red]")
            console.print("Use --force to overwrite existing files.")
            return 1

        ensure_directory(idea_dir)
        ensure_directory(paths.idea_outputs(idea_name))

        templates_dir = project_dir / ".agentkit" / "templates"
        spec_template = _read_template(
            templates_dir / "specification-template.md",
            get_specification_template,
        )
        plan_template = _read_template(
            templates_dir / "plan-template.md",
            get_plan_template,
        )
        tasks_template = _read_template(
            templates_dir / "tasks-template.md",
            get_tasks_template,
        )

        paths.idea_spec(idea_name).write_text(spec_template)
        paths.idea_plan(idea_name).write_text(plan_template)
        paths.idea_tasks(idea_name).write_text(tasks_template)

        console.print(Panel.fit(
            f"[green]✓ Idea created[/green]\n\n"
            f"Name: [cyan]{args.name}[/cyan]\n"
            f"Directory: [blue]{idea_dir}[/blue]\n"
            f"Files: spec.md, plan.md, tasks.md, outputs/",
            title="New Idea",
            border_style="green"
        ))

        return 0
    except Exception as e:
        console.print(f"[red]Error creating idea: {e}[/red]")
        import traceback
        traceback.print_exc()
        return 1


def setup_commands(project_dir: Path, ai_agent: str):
    """Setup command files for the selected AI agent"""
    
    agent_config = AGENT_CONFIG[ai_agent]
    command_dir = project_dir / agent_config["command_dir"]
    ext = agent_config["file_extension"]
    
    # Get command templates
    commands = {
        "constitution": get_constitution_command(),
        "specify": get_specify_command(),
        "clarify": get_clarify_command(),
        "plan": get_plan_command(),
        "task": get_task_command(),
        "implement": get_implement_command()
    }
    
    # Write command files
    for name, content in commands.items():
        command_file = command_dir / f"{name}{ext}"
        command_file.write_text(content)


# Template getters

def get_constitution_template() -> str:
    """Return the constitution template content"""
    return """---
project: [Project Name]
status: template
last_updated: [DATE]
---

# Project Constitution

**Purpose**: This document captures your creative principles, constraints, and decision-making framework.

---

## Article I: Creative Principles

### Your Principles:

- [Add your creative principles here]
- Example: Simple and clear over clever and complex
- Example: Authenticity over perfection

## Article II: Aesthetic & Style

### Your Aesthetic:

- [Add your aesthetic preferences here]
- Example: Warm and personal communication style
- Example: Minimal and clean design aesthetic

## Article III: Constraints & Boundaries

### Your Constraints:

- [Add your constraints here]
- Example: Budget: Maximum $X per project
- Example: Time: Available Y hours per week

## Article IV: Decision-Making Framework

### Your Framework:

- [Add your decision framework here]
- Example: When speed conflicts with quality → quality wins
- Example: When uncertain → ask, don't assume

## Article V: Success Criteria

### Your Success Criteria:

- [Add your success definition here]
- Example: Ships and gets used > perfect but unreleased
- Example: Solves the core problem well > feature-rich
"""


def get_specification_template() -> str:
    """Return the specification template content"""
    return """# Specification: [IDEA NAME]

**Idea Number**: [###]
**Status**: Draft
**Created**: [DATE]
**Last Updated**: [DATE]

## Initial Vision

**The Spark**: [What you want to exist]

**The Why**: [Your motivation]

**The Change**: [What will be different]

## Context

**Background**: [What led to this idea]

**Current State**: [What exists now]

**Desired State**: [What should exist]

## Clarifications

### Round 1: Vision Clarity [PENDING]

**Q1: What problem does this solve, really?**
A: [NEEDS CLARIFICATION]

**Q2: What does success feel like?**
A: [NEEDS CLARIFICATION]

**Q3: What would make you abandon this?**
A: [NEEDS CLARIFICATION]

**Q4: Who is this for (including yourself)?**
A: [NEEDS CLARIFICATION]

### Round 2: Scope Definition [PENDING]

**Q5: What's explicitly IN scope?**
A: [NEEDS CLARIFICATION]

**Q6: What's explicitly OUT of scope?**
A: [NEEDS CLARIFICATION]

**Q7: What are the must-haves vs. nice-to-haves?**
A: [NEEDS CLARIFICATION]

**Q8: What are your constraints?**
A: [NEEDS CLARIFICATION]

### Round 3: Aesthetic & Approach [PENDING]

**Q9: What's the tone/style/vibe?**
A: [NEEDS CLARIFICATION]

**Q10: What are examples of things you love?**
A: [NEEDS CLARIFICATION]

**Q11: What are examples of what you DON'T want?**
A: [NEEDS CLARIFICATION]

**Q12: How does this fit with your broader goals?**
A: [NEEDS CLARIFICATION]

## Requirements

### Functional Requirements

**FR-001**: [Specific requirement]

### Experience Requirements

**XR-001**: [Experience requirement]

### Constraint Requirements

**CR-001**: [Constraint requirement]

## Success Criteria

**You'll know this is working when...**

1. [Measurable or observable outcome]

## Review Checklist

**Before proceeding to /plan, verify:**

- [ ] Vision is clear and compelling
- [ ] All mandatory clarification rounds completed
- [ ] No [NEEDS CLARIFICATION] markers in critical sections
- [ ] Requirements are specific and testable
- [ ] Success criteria are defined
- [ ] Constitutional alignment confirmed
"""


def get_plan_template() -> str:
    """Return the plan template content"""
    return """# Implementation Plan: [IDEA NAME]

**Idea Number**: [###]
**Status**: Draft
**Created**: [DATE]

## Plan Overview

**Approach Summary**: [One paragraph describing the approach]

**Key Decisions**: [Major choices made]

**Timeline Estimate**: [Realistic timeframe]

## Constitutional Alignment

**This plan honors the following constitutional principles**:

- ✅ [Principle and how plan aligns]

## Approach & Methodology

### Overall Strategy

**What We're Building**: [Clear description]

**Why This Approach**: [Rationale]

**How It Works**: [High-level flow]

### Key Components

**Component 1: [Name]**
- Purpose: [What it does]
- Approach: [How it will be created]
- Tools: [What tools/methods]
- Owner: [Agent | User | Collaborative]

## Implementation Phases

### Phase 1: Foundation & Research
**Goal**: [What phase accomplishes]
**Duration**: [Estimate]

### Phase 2: Core Development
**Goal**: [What phase accomplishes]
**Duration**: [Estimate]

### Phase 3: Refinement & Polish
**Goal**: [What phase accomplishes]
**Duration**: [Estimate]

### Phase 4: Finalization
**Goal**: [What phase accomplishes]
**Duration**: [Estimate]

## Output Specifications

### Primary Deliverables

**Deliverable 1: [Name]**
- Format: [File type/medium]
- Location: `outputs/[filename]`

## Next Steps

**Ready for `/task`**:
- [ ] Plan reviewed and approved
- [ ] Tool setup complete
- [ ] Resources available
"""


def get_tasks_template() -> str:
    """Return the tasks template content"""
    return """---
project: [Project Name]
date: [DATE]
status: draft
---

# Project Tasks: [Project Name]

## Tasks

[ ] T001: [Task description]

[ ] T002: [Task description]

[ ] T003: [Task description]

---

## Notes

Task ID Format:
- Single phase: T001, T002, T003...
- Multiple phases: T001 (Phase 1), T101 (Phase 2), T201 (Phase 3)...

Mark tasks complete by changing [ ] to [x]
"""


def get_common_script(script_type: str) -> str:
    """Return common utilities script"""
    if script_type == "bash":
        return """#!/usr/bin/env bash
# Common utilities for AgentKit

# Get the next idea number
get_next_idea_number() {
    local ideas_dir=".agentkit/ideas"
    if [ ! -d "$ideas_dir" ] || [ -z "$(ls -A $ideas_dir 2>/dev/null)" ]; then
        echo "001"
        return
    fi
    
    local max_num=0
    for dir in "$ideas_dir"/*; do
        if [ -d "$dir" ]; then
            local num=$(basename "$dir" | grep -oE '^[0-9]+')
            if [ -n "$num" ] && [ "$num" -gt "$max_num" ]; then
                max_num=$num
            fi
        fi
    done
    
    printf "%03d" $((max_num + 1))
}

# Create idea directory
create_idea_dir() {
    local idea_name=$1
    local idea_dir=".agentkit/ideas/$idea_name"
    
    mkdir -p "$idea_dir/outputs"
    echo "$idea_dir"
}
"""
    else:  # powershell
        return """# PowerShell script
# Common utilities for AgentKit

function Get-NextIdeaNumber {
    $ideasDir = ".agentkit/ideas"
    if (!(Test-Path $ideasDir) -or !(Get-ChildItem $ideasDir)) {
        return "001"
    }
    
    $maxNum = 0
    Get-ChildItem $ideasDir -Directory | ForEach-Object {
        if ($_.Name -match '^(\\d+)') {
            $num = [int]$matches[1]
            if ($num -gt $maxNum) {
                $maxNum = $num
            }
        }
    }
    
    return "{0:D3}" -f ($maxNum + 1)
}

function New-IdeaDirectory {
    param([string]$IdeaName)
    
    $ideaDir = ".agentkit/ideas/$IdeaName"
    New-Item -ItemType Directory -Force -Path "$ideaDir/outputs" | Out-Null
    return $ideaDir
}
"""


def get_create_idea_script(script_type: str) -> str:
    """Return create new idea script"""
    if script_type == "bash":
        return """#!/usr/bin/env bash
# Create a new idea from template

source "$(dirname "$0")/common.sh"

# Get next number and create directory
IDEA_NUM=$(get_next_idea_number)
IDEA_SLUG="$1"
IDEA_NAME="${IDEA_NUM}-${IDEA_SLUG}"

echo "Creating idea: $IDEA_NAME"
IDEA_DIR=$(create_idea_dir "$IDEA_NAME")

# Copy templates
cp .agentkit/templates/specification-template.md "$IDEA_DIR/spec.md"
cp .agentkit/templates/plan-template.md "$IDEA_DIR/plan.md"
cp .agentkit/templates/tasks-template.md "$IDEA_DIR/tasks.md"

echo "Idea created at: $IDEA_DIR"
"""
    else:
        return """# PowerShell script
# Create a new idea from template

. "$PSScriptRoot\\common.ps1"

$ideaNum = Get-NextIdeaNumber
$ideaSlug = $args[0]
$ideaName = "$ideaNum-$ideaSlug"

Write-Host "Creating idea: $ideaName"
$ideaDir = New-IdeaDirectory $ideaName

# Copy templates
Copy-Item .agentkit/templates/specification-template.md "$ideaDir/spec.md"
Copy-Item .agentkit/templates/plan-template.md "$ideaDir/plan.md"
Copy-Item .agentkit/templates/tasks-template.md "$ideaDir/tasks.md"

Write-Host "Idea created at: $ideaDir"
"""


def get_setup_plan_script(script_type: str) -> str:
    """Return setup plan script"""
    if script_type == "bash":
        return """#!/usr/bin/env bash
# Setup plan for current idea

IDEA_DIR=$1

if [ -z "$IDEA_DIR" ]; then
    echo "Usage: setup-plan.sh <idea-directory>"
    exit 1
fi

# Copy plan template
cp .agentkit/templates/plan-template.md "$IDEA_DIR/plan.md"
cp .agentkit/templates/tasks-template.md "$IDEA_DIR/tasks.md"

echo "Plan templates created in $IDEA_DIR"
"""
    else:
        return """# PowerShell script
# Setup plan for current idea

param([string]$IdeaDir)

if (!$IdeaDir) {
    Write-Host "Usage: setup-plan.ps1 <idea-directory>"
    exit 1
}

# Copy plan template
Copy-Item .agentkit/templates/plan-template.md "$IdeaDir/plan.md"
Copy-Item .agentkit/templates/tasks-template.md "$IdeaDir/tasks.md"

Write-Host "Plan templates created in $IdeaDir"
"""


def get_constitution_command() -> str:
    """Return /constitution command content"""
    return """# /constitution - Create Your Creative Principles

Create or update your project constitution with governing principles.

[Command implementation to be completed]
"""


def get_specify_command() -> str:
    """Return /specify command content"""
    return """# /specify - Capture Your Idea

Transform an initial idea into a structured specification.

[Command implementation from templates - to be completed]
"""


def get_clarify_command() -> str:
    """Return /clarify command content"""
    return """# /clarify - Sharpen Your Idea

Structured inquiry to transform fuzzy vision into clear specification.

[Command implementation from templates - to be completed]
"""


def get_plan_command() -> str:
    """Return /plan command content"""
    return """# /plan - Define Your Approach

Create implementation plan based on clarified specification.

[Command implementation to be completed]
"""


def get_task_command() -> str:
    """Return /task command content"""
    return """# /task - Break Down Into Actions

Generate categorized, actionable task list.

[Command implementation to be completed]
"""


def get_implement_command() -> str:
    """Return /implement command content"""
    return """# /implement - Execute and Create

Execute tasks and generate outputs.

[Command implementation to be completed]
"""
