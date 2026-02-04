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
    "codex": {
        "name": "Codex",
        "command_dir": ".codex/commands",
        "file_extension": ".md",
        "check_command": "codex --version"
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

            # v0.3.0: Auto-orchestration setup
            task = progress.add_task("Setting up auto-orchestration (v0.3.0)...", total=None)
            install_phase_instructions(project_dir)
            create_workflow_state(project_dir, project_name)
            install_minimal_agents_md(project_dir)
            progress.update(task, completed=True)

        # Success message
        console.print()
        console.print(Panel.fit(
            f"[green]✓ Project initialized successfully![/green]\n\n"
            f"AI Agent: [cyan]{AGENT_CONFIG[ai_agent]['name']}[/cyan]\n"
            f"Script Type: [cyan]{SCRIPT_CONFIG[script_type]['name']}[/cyan]\n"
            f"Version: [cyan]0.3.0 (Auto-Orchestrated)[/cyan]\n\n"
            f"[bold]Next Steps:[/bold]\n"
            f"1. cd {project_name if not args.here else '.'}\n"
            f"2. Run your AI agent (e.g., 'claude')\n"
            f"3. Say 'start a project about...' or use /start\n"
            f"4. Agent will guide you: constitution → specify → plan → task → implement\n\n"
            f"[dim]Manual commands still work: /specify, /plan, /task, /implement[/dim]",
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

    # v0.3.0: Phases directory for modular phase instructions
    (agentkit_dir / "phases").mkdir(parents=True, exist_ok=True)

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

    # Save a reusable template copy
    (templates_dir / "constitution-template.md").write_text(constitution_template)

    # Specification template (keep in templates)
    spec_template = get_specification_template()
    (templates_dir / "specification-template.md").write_text(spec_template)

    # Plan template (keep in templates)
    plan_template = get_plan_template()
    (templates_dir / "plan-template.md").write_text(plan_template)

    # Tasks template (keep in templates)
    tasks_template = get_tasks_template()
    (templates_dir / "tasks-template.md").write_text(tasks_template)

    # Research template
    research_template = get_research_template()
    (templates_dir / "research-template.md").write_text(research_template)

    # Asset map template
    asset_map_template = get_asset_map_template()
    (templates_dir / "asset-map-template.md").write_text(asset_map_template)

    # Quickstart template
    quickstart_template = get_quickstart_template()
    (templates_dir / "quickstart-template.md").write_text(quickstart_template)

    # Checklist template
    checklist_template = get_checklist_template()
    (templates_dir / "checklist-template.md").write_text(checklist_template)


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

    # Prerequisite check script
    prereq_script = get_prerequisites_script(script_type)
    prereq_file = script_dir / f"check-prerequisites{ext}"
    prereq_file.write_text(prereq_script)
    if script_type == "bash":
        prereq_file.chmod(0o755)

    # Agent context updater
    update_context_script = get_update_agent_context_script(script_type)
    update_context_file = script_dir / f"update-agent-context{ext}"
    update_context_file.write_text(update_context_script)
    if script_type == "bash":
        update_context_file.chmod(0o755)

    # Suggest next idea/feature name
    suggest_script = get_suggest_name_script(script_type)
    suggest_file = script_dir / f"suggest-name{ext}"
    suggest_file.write_text(suggest_script)
    if script_type == "bash":
        suggest_file.chmod(0o755)

    # Tasks export helper
    tasks_export_script = get_tasks_export_script(script_type)
    tasks_export_file = script_dir / f"tasks-export{ext}"
    tasks_export_file.write_text(tasks_export_script)
    if script_type == "bash":
        tasks_export_file.chmod(0o755)

    # Constitution sync helper
    constitution_sync_script = get_constitution_sync_script(script_type)
    constitution_sync_file = script_dir / f"constitution-sync{ext}"
    constitution_sync_file.write_text(constitution_sync_script)
    if script_type == "bash":
        constitution_sync_file.chmod(0o755)

    # Tasks to issues helper
    tasks_issues_script = get_tasks_to_issues_script(script_type)
    tasks_issues_file = script_dir / f"tasks-to-issues{ext}"
    tasks_issues_file.write_text(tasks_issues_script)
    if script_type == "bash":
        tasks_issues_file.chmod(0o755)

    # Issues JSON export helper
    tasks_issues_json_script = get_tasks_to_issues_json_script(script_type)
    tasks_issues_json_file = script_dir / f"tasks-to-issues-json{ext}"
    tasks_issues_json_file.write_text(tasks_issues_json_script)
    if script_type == "bash":
        tasks_issues_json_file.chmod(0o755)

    # Tasks to GitHub push helper
    tasks_issues_push_script = get_tasks_to_github_push_script(script_type)
    tasks_issues_push_file = script_dir / f"tasks-to-github-push{ext}"
    tasks_issues_push_file.write_text(tasks_issues_push_script)
    if script_type == "bash":
        tasks_issues_push_file.chmod(0o755)

    # Template propagation helper (flag/copy)
    template_sync_script = get_template_sync_script(script_type)
    template_sync_file = script_dir / f"template-sync{ext}"
    template_sync_file.write_text(template_sync_script)
    if script_type == "bash":
        template_sync_file.chmod(0o755)

    # GitHub issues helper (command list)
    gh_issues_script = get_tasks_to_github_script(script_type)
    gh_issues_file = script_dir / f"tasks-to-github{ext}"
    gh_issues_file.write_text(gh_issues_script)
    if script_type == "bash":
        gh_issues_file.chmod(0o755)


# ============================================================================
# v0.3.0: Auto-Orchestration Support
# ============================================================================

def install_phase_instructions(project_dir: Path):
    """Install phase instruction files for auto-orchestrated workflow (v0.3.0)"""

    phases_dir = project_dir / ".agentkit" / "phases"
    phases_dir.mkdir(parents=True, exist_ok=True)

    # Phase instruction content
    phase_files = {
        "constitution.md": get_phase_constitution(),
        "specify.md": get_phase_specify(),
        "plan.md": get_phase_plan(),
        "task.md": get_phase_task(),
        "implement.md": get_phase_implement(),
    }

    for filename, content in phase_files.items():
        phase_file = phases_dir / filename
        # Don't overwrite existing phase files (user may have customized)
        if not phase_file.exists():
            phase_file.write_text(content)


def create_workflow_state(project_dir: Path, project_name: str):
    """Create initial workflow-state.yaml for auto-orchestrated workflow (v0.3.0)"""
    from datetime import datetime

    state_file = project_dir / ".agentkit" / "workflow-state.yaml"

    content = f'''version: "0.3.0"
project:
  name: "{project_name}"
  created: "{datetime.now().isoformat()}"
  domain: null
current_phase: constitution
session:
  last_active: null
  docs_read: []
phases:
  constitution:
    status: in_progress
  specify:
    status: pending
  plan:
    status: pending
  task:
    status: pending
  implement:
    status: pending
'''
    state_file.write_text(content)


def install_minimal_agents_md(project_dir: Path):
    """Install minimal AGENTS.md router for auto-orchestrated workflow (v0.3.0)"""

    agents_md = project_dir / "AGENTS.md"
    content = get_minimal_agents_md()
    agents_md.write_text(content)


def get_minimal_agents_md() -> str:
    """Return minimal AGENTS.md router content"""
    return '''# AgentKit Auto-Orchestrated Project

This project uses AgentKit's auto-orchestrated workflow. The agent guides you through each phase automatically.

## Workflow Instructions

1. **Sync state with documents** - Always verify state matches actual documents before proceeding
2. Read `.agentkit/workflow-state.yaml` to determine current phase
3. Load phase instructions from `.agentkit/phases/{current_phase}.md`
4. Follow phase instructions to guide user through conversation
5. When phase completes (document exists with content), update state and transition

## State Detection & Self-Healing

If state file is missing, corrupted, or inconsistent with documents:
- No constitution.md → constitution phase
- No spec.md → specify phase
- No plan.md → plan phase
- No tasks.md → task phase
- All exist → implement phase

**Trust documents over state file.** If state claims to be ahead of documents, roll back.

## Available Commands

- `/start` or `/continue` - Resume auto-orchestrated workflow
- `/status` - Show current phase and progress
- `/skip` - Skip current phase (requires confirmation)
- `/specify`, `/plan`, `/task`, `/implement` - Manual phase jump

## Conversation Style

- **Technical scoping first**: Understand concrete details (inputs, users, constraints) before abstract values
- **Open-ended for scope**: Let user describe technical reality in their own words
- **Numbered options for values/decisions**: Propose guiding principles based on what you learned
- Have a back-and-forth dialogue, not an interrogation
- Summarize and confirm before creating documents
- Update workflow state after each phase completes
'''


def get_phase_constitution() -> str:
    """Return constitution phase instruction content"""
    return '''# Constitution Phase

## Purpose
Establish the project's guiding principles, constraints, and definition of done.

## Prerequisites
None - this is the first phase.

## Prior Work Detection (FIRST)

Scan the project folder for existing files:
- Data files: `*.json`, `*.csv`, `*.xlsx`
- Analysis: `*.ipynb`, reports/, outputs/
- Documentation: `*.md` files (not AgentKit docs)

If found, mention them:
> "I noticed existing files in this project: [list key files]
> Should I incorporate these into our planning, or are we starting fresh?"

## Conversation Flow

### Opening (REQUIRED)
Start with an open-ended prompt - no suggested answers:

> "Tell me about your project. What are you trying to create?"

**Wait for user response.** Let them describe it in their own words.

### Technical Scoping (OPEN-ENDED)
Focus on understanding concrete scope first. Ask open questions:
- "What are the main inputs? (data sources, APIs, files, user input)"
- "Who will use this? What's their technical level?"
- "What constraints are you working with - timeline, budget, tech stack?"
- "How will you know it's done? What's the minimum for a working version?"

**Priority**: Clarify technical reality before discussing abstract values.

### Guiding Principles (NUMBERED OPTIONS)
After scope is clear, **propose** principles based on what you learned:

> "Based on what you've described, which principle should guide decisions?
> 1. Reliability - accuracy and uptime matter most
> 2. Speed to market - get something working fast
> 3. Flexibility - easy to adapt as requirements change
> 4. Simplicity - minimal complexity, easy to maintain
> 5. Other"

Propose options that fit the project context.

### Summary & Confirmation
Before creating the document, summarize:
> "Here's what I'm hearing: [summary]. Does this capture it?"

## Completion Criteria
Core principles documented covering: values, constraints, and success definition.

## Transition
1. Save constitution.md
2. Update workflow-state.yaml: constitution=completed, current_phase=specify
3. Announce: "✓ Constitution complete! Moving to Specify phase..."
'''


def get_phase_specify() -> str:
    """Return specify phase instruction content"""
    return '''# Specify Phase

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
Ask as open questions - user writes their own response, NO numbered options:
- "What problem does this solve or opportunity does it create?"
- "Who is this for? Who benefits?"
- "What are the specific deliverables - what will exist when you're done?"
- "What's explicitly NOT included in this project?"

### Clarifying Questions (NUMBERED OPTIONS)
After scoping, use numbered options for quick decisions:

> "What's the priority for these outcomes?
> 1. O1 is must-have, O2 is nice-to-have
> 2. Both are equally important
> 3. Other"

### Summary & Confirmation
Before creating the document, summarize:
> "Let me summarize what we're building: [outcomes, requirements, scope]. Anything to add?"

## Completion Criteria
- At least one Outcome defined with priority and validation criteria
- Key requirements documented
- Scope boundaries clear

## Transition
1. Save spec.md
2. Update workflow-state.yaml: specify=completed, current_phase=plan
3. Announce: "✓ Specification complete! Moving to Plan phase..."
'''


def get_phase_plan() -> str:
    """Return plan phase instruction content"""
    return '''# Plan Phase

## Purpose
Define HOW the work will be done and WHEN. Determine approach, resources, timeline, and risks.

## Prerequisites
- spec.md must exist

## Conversation Flow

### Opening (REQUIRED)
Start with an open-ended prompt referencing the spec:

> "Looking at your outcomes in spec.md, how are you thinking about approaching this? What's your general plan?"

**Wait for user response.** Let them describe their approach in their own words.

### Scoping Questions (OPEN-ENDED)
Ask these as open questions - user writes their own response, NO numbered options:
- "What resources, tools, or skills will you need to complete this?"
- "Are there any dependencies or things that need to happen first?"
- "What milestones or checkpoints would help you track progress?"
- "What could go wrong, and how would you handle it?"

Let the user describe things in their own words. Have a back-and-forth conversation.

### Clarifying Questions (NUMBERED OPTIONS)
After scoping, use numbered options to quickly fill gaps:

> "For timeline, what pace works best?
> 1. Sprint - intensive work over days
> 2. Steady - regular progress over weeks
> 3. Flexible - no fixed timeline
> 4. Other"

Use numbered options when you need a quick decision on something specific.

### Summary & Confirmation
Before creating the document, summarize what you learned:

> "Here's the plan I'm capturing: [summary]. Does this look right?"

Let them correct or add before finalizing.

## Completion Criteria
- Approach defined for achieving outcomes
- Resources and dependencies identified
- Timeline with milestones established

## Output Document
Create `plan.md` in project root with YAML frontmatter containing approach, resources, timeline, and risks.

## Transition
1. Save plan.md
2. Update workflow-state.yaml: plan=completed, current_phase=task
3. Announce: "✓ Plan complete! Moving to Task phase..."
'''


def get_phase_task() -> str:
    """Return task phase instruction content"""
    return '''# Task Phase

## Purpose
Break the plan into actionable, trackable tasks organized by outcome.

## Prerequisites
- plan.md must exist

## Setup (BEFORE task breakdown)

### Create Project Structure
If plan.md defines a project structure (directories, folders), offer to create them:

> "The plan defines this structure: [list directories from plan]
> Should I create these directories now?"

If yes, create the directories. This ensures the project is ready for implementation.

## Process
1. Agent proposes task breakdown based on plan and outcomes
2. User reviews and adjusts
3. Agent finalizes tasks.md

### Task Format
`- [ ] T001 [P?] [O1?] Description → artifact`
- T001: Sequential task ID
- [P]: Parallelizable (optional)
- [O1]: Belongs to Outcome 1 (optional)
- → artifact: What this task produces

### Organization
1. **Setup** - Gather resources, prepare workspace
2. **Foundation** - Blocking work (must complete first)
3. **Outcome phases** - One section per outcome (P1, P2, P3...)
4. **Polish** - Final quality checks

## Completion Criteria
- Every outcome has associated tasks
- Tasks have clear artifacts/outputs
- User has confirmed the breakdown

## Output Document
Create `tasks.md` in project root with checkbox format organized by phase.

## Transition
1. Save tasks.md
2. Update workflow-state.yaml: task=completed, current_phase=implement
3. Announce: "✓ Tasks defined! Ready to implement..."
'''


def get_phase_implement() -> str:
    """Return implement phase instruction content"""
    return '''# Implement Phase

## Purpose
Execute tasks and create deliverables. Track progress through completion.

## Prerequisites
- tasks.md must exist

## Process
1. Start with Setup phase tasks
2. Complete Foundation phase (blocks all outcomes)
3. Work through Outcome phases
4. Finish with Polish phase

### For Each Task
1. Announce which task you're starting
2. Execute the work or guide user through it
3. Mark task complete: `- [x] T001 ...`
4. Update workflow-state.yaml with tasks_completed count

### Checkpoints
After each outcome phase, pause for validation.

## Completion Criteria
- All tasks marked complete: `- [x]`
- All outcomes validated
- Deliverables created in `deliverables/` folder

## Completion
When all tasks are done:
1. Update all tasks to `[x]` in tasks.md
2. Update workflow-state.yaml: implement=completed
3. Announce: "✓ Project complete! All outcomes delivered."
'''


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
        research_template = _read_template(
            templates_dir / "research-template.md",
            get_research_template,
        )
        asset_map_template = _read_template(
            templates_dir / "asset-map-template.md",
            get_asset_map_template,
        )
        quickstart_template = _read_template(
            templates_dir / "quickstart-template.md",
            get_quickstart_template,
        )
        checklist_template = _read_template(
            templates_dir / "checklist-template.md",
            get_checklist_template,
        )

        paths.idea_spec(idea_name).write_text(spec_template)
        paths.idea_plan(idea_name).write_text(plan_template)
        paths.idea_tasks(idea_name).write_text(tasks_template)
        paths.idea_dir(idea_name).joinpath("research.md").write_text(
            research_template
        )
        paths.idea_dir(idea_name).joinpath("asset-map.md").write_text(
            asset_map_template
        )
        paths.idea_dir(idea_name).joinpath("quickstart.md").write_text(
            quickstart_template
        )

        checklists_dir = ensure_directory(paths.idea_dir(idea_name) / "checklists")
        checklists_dir.joinpath("requirements.md").write_text(checklist_template)

        ensure_directory(paths.idea_dir(idea_name) / "briefs")

        console.print(Panel.fit(
            f"[green]✓ Idea created[/green]\n\n"
            f"Name: [cyan]{args.name}[/cyan]\n"
            f"Directory: [blue]{idea_dir}[/blue]\n"
            "Files: spec.md, plan.md, tasks.md, research.md, "
            "asset-map.md, quickstart.md, checklists/, briefs/, outputs/",
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
        "implement": get_implement_command(),
        "checklist": get_checklist_command(),
        "tasks-to-issues": get_tasks_to_issues_command(),
        # v0.3.0: Auto-orchestration commands
        "start": get_start_command(),
        "continue": get_continue_command(),
        "status": get_status_command(),
        "skip": get_skip_command(),
    }

    # Write command files
    for name, content in commands.items():
        command_file = command_dir / f"{name}{ext}"
        command_file.write_text(content)


# Template getters

def get_constitution_template() -> str:
    """Return the constitution template content"""
    return """<!--
Sync Impact Report:
- Version: [OLD] -> [NEW]
- Ratified: [DATE] | Last Amended: [DATE]
- Sections: Added [..], Removed [..], Renamed [..]
- Templates/Commands: spec [ ], plan [ ], tasks [ ], checklist [ ], clarify [ ]
- TODOs: [list deferred placeholders]
-->
---
project: [Project Name]
status: active
version: [VERSION]
ratified: [DATE]
last_amended: [DATE]
---

# Project Constitution

**Purpose**: This document captures your creative principles, constraints, and decision-making framework.

---

## Article I: Creative Principles

### Your Principles:

- [Principle 1]
- [Principle 2]
- [Principle 3]

## Article II: Aesthetic & Style

### Your Aesthetic:

- [Voice, tone, and style rules]
- [Visual preferences if relevant]

## Article III: Constraints & Boundaries

### Your Constraints:

- Budget: [limit or TBD]
- Time: [availability]
- Context: [domain, industry, audience]

## Article IV: Decision-Making Framework

### Your Framework:

- When speed conflicts with quality → [rule]
- When innovation conflicts with stability → [rule]
- When uncertain → [rule]

## Article V: Success Criteria

### Your Success Criteria:

- [Outcome 1]
- [Outcome 2]
- [Outcome 3]

## Governance

- How to amend: [procedure]
- Who approves: [roles]
- Versioning policy: [rules for bumping version]
"""


def get_specification_template() -> str:
    """Return the specification template content"""
    return """# Specification: [IDEA NAME]

**Idea Number**: [###]
**Status**: Draft
**Created**: [DATE]
**Last Updated**: [DATE]

> STOP: Do not add implementation details. Those belong in plan.md (how/when).

This specification answers: What are we building and why? Keep it free of implementation phases, task lists, timelines, roles, or risk mitigations.

## Problem

**Core Problem**: [Concise statement of the need]

## Desired Outcome

**Outcome**: [What will exist / change]
**Who Benefits**: [Who is affected]
**Why Now**: [Urgency or trigger]

## Context

**Background**: [What led to this idea]

**Current State**: [What exists now]

**Desired State**: [What should exist]

## Scope

**In Scope**:
- [What is explicitly included]

**Out of Scope**:
- [What is explicitly excluded]

**Assumptions & Constraints**:
- [Known constraints or dependencies]
  - Budget/Time: [if applicable]
  - Safety/Compliance: [if applicable]
  - Tone/Style: [if applicable]
  - Operational limits: [hours, seasonality, capacity]

## Outcomes & Validation (mandatory)

### Outcome 1 - [Brief Title] (Priority: P1)

[Describe what will be achieved and who benefits]

**Why this priority**: [Value/impact]

**How to validate**: [How to verify this outcome independently]

**Success Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected result]
2. **Given** [initial state], **When** [action], **Then** [expected result]

---

### Outcome 2 - [Brief Title] (Priority: P2)

[Describe what will be achieved and who benefits]

**Why this priority**: [Value/impact]

**How to validate**: [How to verify this outcome independently]

**Success Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected result]

---

### Outcome 3 - [Brief Title] (Priority: P3)

[Describe what will be achieved and who benefits]

**Why this priority**: [Value/impact]

**How to validate**: [How to verify this outcome independently]

**Success Scenarios**:

1. **Given** [initial state], **When** [action], **Then** [expected result]

### Edge Cases

- What happens when [boundary condition]?
- How does the system handle [error scenario]?

## Requirements (mandatory)

### Functional Requirements

- **FR-001**: [Specific requirement]
- **FR-002**: [Specific requirement]
- **FR-003**: [Specific requirement]
- **FR-004**: [Specific requirement]
- **FR-005**: [Specific requirement]

### Experience Requirements

- **XR-001**: [Experience requirement]

### Constraint Requirements

- **CR-001**: [Constraint requirement]

## Key Assets / Elements (if relevant)

- **[Asset/Element 1]**: [Purpose, audience, dependencies]
- **[Asset/Element 2]**: [Purpose, audience, dependencies]

## Success Criteria (mandatory)

**You'll know this is working when...**

1. [Measurable or observable outcome]
2. [Additional outcomes]

## Key Decisions

- [Decision 1 and rationale]
- [Decision 2 and rationale]

## Related Documents

- `plan.md` — implementation approach, phases, tasks, timelines, roles, risks.
- `research.md` — clarifications resolved before planning.

## Clarifications

Use `[NEEDS CLARIFICATION: question]` sparingly (max 3) and resolve before planning.

## Domain Examples (optional — replace or delete if not relevant)

- **Menu/food popup**: in scope = seasonal menu, sourcing; out of scope = permanent kitchen build; constraints = dietary safety, sourcing radius, budget per plate.
- **Business ops/SOP**: in scope = expense approvals, roles; out of scope = payroll provider swap; constraints = compliance, auditability, thresholds.
- **Creative doc (D&D/game)**: in scope = factions/quests/mechanics; out of scope = final art assets; constraints = tone, lore consistency, playtime target.
- **Service launch (climbing)**: in scope = indoor offering; out of scope = outdoor guiding until permits; constraints = safety, insurance, staffing, capacity.
"""


def get_plan_template() -> str:
    """Return the plan template content"""
    return """# Implementation Plan: [IDEA NAME]

**Idea Number**: [###]
**Status**: Draft
**Created**: [DATE]

> Input: spec.md defines WHAT and WHY. This plan covers HOW and WHEN.

## Summary

**Approach Summary**: [One paragraph describing the approach]

**Key Decisions**: [Major choices made]

**Timeline Estimate**: [Realistic timeframe]

## Spec Reference

- Problem/Outcome summary: [Link back to spec.md]
- Scope guardrails (in/out): [Key boundaries to honor]
- Success criteria: [What this plan must satisfy]
- Decisions to honor: [From spec.md]

## Technical Context

**Language/Version**: [e.g., Python 3.11 or NEEDS CLARIFICATION]  
**Primary Dependencies**: [e.g., FastAPI, React]  
**Storage**: [DB/files/none]  
**Testing**: [pytest, playwright, etc.]  
**Target Platform**: [e.g., Linux server, iOS, web]  
**Performance Goals**: [domain-specific metric]  
**Constraints**: [latency, accessibility, compliance]  
**Scale/Scope**: [users/volume/surfaces]

## Research Plan

- Top questions to resolve (RQ-01...): [list]
- Expected outputs: findings + proposed decisions in research.md
- Timeboxes/owners: [who/how long]

## Constitution Check

- Principle: [How the plan aligns or justification if violated]
- Principle: [...]

## Project Structure

**Docs**: spec.md, plan.md, research.md, asset-map.md, quickstart.md, briefs/, tasks.md  
**Source layout**:

```text
src/
├── models/
├── services/
└── cli/

tests/
├── contract/
├── integration/
└── unit/
```

**Structure Decision**: [Document chosen structure and why]

## Phases & Sequencing

### Phase 0: Research & Clarification
- Goal: Resolve open questions and document in `research.md`.
- Outputs: research.md updated, clarifications answered, proposals drafted.

### Phase 1: Design
- Goal: Produce `asset-map.md`, `briefs/`, and `quickstart.md`.
- Outputs: assets/elements mapped, briefs/standards, quickstart steps.

### Phase 2: Implementation Planning
- Goal: Break down stories/tasks and dependencies; schedule remaining research tasks.
- Outputs: tasks.md updated per story with parallelism markers and [R] tasks.

### Phase 3: Delivery & Validation
- Goal: Execute tasks, validate against success criteria, update quickstart/checklists.

## Risks and Dependencies

- Risk: [Description] — Mitigation: [Plan]
- Dependency: [System/owner] — Status: [Open/Ready]

## Outputs & Handoffs

- plan.md (this file) ready for `/task`.
- Supporting docs refreshed: research.md, asset-map.md, quickstart.md, briefs/.
- Open questions to resolve: [list or NONE]
"""


def get_tasks_template() -> str:
    """Return the tasks template content"""
    return """---
project: [Project Name]
date: [DATE]
status: draft
---

# Project Tasks: [Project Name]

## Legend
- **[A]** = Agent can execute autonomously
- **[U]** = Agent needs user guidance/approval
- **[M]** = Manual task for user only
- **[H]** = Hybrid collaborative task
- **[P]** = Can be done in parallel

## Phase 1: Foundation & Research

- [ ] T001 [R][A] Research: [question] (output: findings + proposal in research.md)
- [ ] T002 [A] Capture remaining clarifications in research.md
- [ ] T003 [A] Validate constitution alignment

## Phase 2: Core Development

- [ ] T101 [P][A] [Surface/Story] Create draft of [asset/doc] in [path]
- [ ] T102 [A] [Surface/Story] Add constraints/acceptance notes
- [ ] T103 [U] [Surface/Story] Confirm acceptance scenarios with stakeholder

## Phase 3: Tests (if requested)

- [ ] T201 [P][A] [Surface/Story] Validation/checklist update for [asset/doc]
- [ ] T202 [A] [Surface/Story] Pilot/feedback session and notes

## Phase 4: Polish & Docs

- [ ] T301 [A] Update quickstart.md with latest steps/findings
- [ ] T302 [A] Update checklists/requirements.md with new scope
- [ ] T303 [A] Finalize briefs and decisions in research.md

## Dependencies & Sequencing

- Foundation must precede Core Development.
- User stories proceed in priority order unless marked [P].
- Research tasks [R] unblock later phases; close or timebox before execution.

Mark tasks complete by changing [ ] to [x].
"""


def get_research_template() -> str:
    """Return the research template content"""
    return """# Research Notes: [IDEA NAME]

**Idea Number**: [###]  
**Created**: [DATE]  
**Status**: Draft

## Open Questions (ranked)

| ID | Question | Owner (A/U/H) | Priority | Status |
| --- | --- | --- | --- | --- |
| RQ-01 | [What do we need to learn?] | [A/U/H] | High | Open |

## Findings

- **RQ-01**: [Finding summary] (Source: [link], Confidence: [Low/Med/High])
- **RQ-02**: ...

## Proposed Decisions

| ID | Proposal | Rationale | Options Considered | Confidence |
| --- | --- | --- | --- | --- |
| RD-01 | [Proposed choice] | [Why this is best] | [Alternatives] | [L/M/H] |

## Decisions (locked)

| ID | Decision | Date | Who | Notes |
| --- | --- | --- | --- | --- |
| RD-01 | [Decision text] | [DATE] | [Name/Role] | [Notes] |

## Sources (audit)

- [Title](link) — [1–2 line relevance], [Date]
- [Title](link) — ...
"""


def get_asset_map_template() -> str:
    """Return the asset map template content"""
    return """# Asset Map: [IDEA NAME]

**Idea Number**: [###]  
**Created**: [DATE]  
**Status**: Draft

## Key Assets / Elements

- **[Asset/Element]**: [Purpose, audience, format, owner]
- **[Asset/Element]**: [...]

## Relationships & Dependencies

- [Asset] depends on [Asset] because [reason]
- [Asset] feeds [Asset] (handoff/reuse)

## Constraints & Standards

- [Style/tone/brand rules, compliance, safety, sourcing limits]

## Status

- [Asset] — Not started / Draft / In review / Final

## Domain Examples (optional — replace or delete if not relevant)

- **Menu**: sections (appetizers, mains, desserts), signature dishes, sourcing notes, allergens, equipment needs, plating standards.
- **Accounting SOP**: policies, approval thresholds, forms/templates, system touchpoints, audit trails.
- **Creative/GDD/D&D**: regions, factions, NPCs, quests, mechanics, items, scenes; relationships between factions/quests; tone/style rules.
- **Climbing business**: services (indoor classes, memberships), safety protocols, gear inventory, staff roles, waiver flow.
- **Pool cleanup**: contaminants list, treatments, equipment, maintenance SOPs, safety notes.
"""


def get_quickstart_template() -> str:
    """Return the quickstart template content"""
    return """# Quickstart: [IDEA NAME]

**Idea Number**: [###]  
**Created**: [DATE]

## Prerequisites

- [Tools/resources]
- [People/approvals required]
- [Safety/compliance prerequisites]

## Setup

```bash
[commands]
```

## How to Run

```bash
[run command]
```

## Smoke Checks

- [ ] Core path works end-to-end (or pilot/feedback run)
- [ ] Key safety/compliance/quality checks satisfied
- [ ] Acceptance criteria validated against spec/briefs
"""


def get_checklist_template() -> str:
    """Return the checklist template content"""
    return """# Specification Quality Checklist: [IDEA NAME]

**Created**: [DATE]
**Reference**: spec.md

## Content Quality

- [ ] No implementation details (languages, frameworks, APIs)
- [ ] Written for stakeholders (clear, concise)
- [ ] All mandatory sections completed

## Requirement Completeness

- [ ] No [NEEDS CLARIFICATION] markers in critical sections
- [ ] Edge cases captured
- [ ] Success criteria measurable

## Traceability & Consistency

- [ ] Requirements align with constitution
- [ ] User stories have priorities and acceptance scenarios
- [ ] Scope in/out is explicit
- [ ] Research decisions are cited (research.md) and reflected in briefs/plan
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
cp .agentkit/templates/research-template.md "$IDEA_DIR/research.md"
cp .agentkit/templates/asset-map-template.md "$IDEA_DIR/asset-map.md"
cp .agentkit/templates/quickstart-template.md "$IDEA_DIR/quickstart.md"

mkdir -p "$IDEA_DIR/checklists"
cp .agentkit/templates/checklist-template.md "$IDEA_DIR/checklists/requirements.md"
mkdir -p "$IDEA_DIR/briefs"

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
Copy-Item .agentkit/templates/research-template.md "$ideaDir/research.md"
Copy-Item .agentkit/templates/asset-map-template.md "$ideaDir/asset-map.md"
Copy-Item .agentkit/templates/quickstart-template.md "$ideaDir/quickstart.md"

New-Item -ItemType Directory -Force -Path "$ideaDir/checklists" | Out-Null
Copy-Item .agentkit/templates/checklist-template.md "$ideaDir/checklists/requirements.md"
New-Item -ItemType Directory -Force -Path "$ideaDir/briefs" | Out-Null

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
cp .agentkit/templates/research-template.md "$IDEA_DIR/research.md"
cp .agentkit/templates/asset-map-template.md "$IDEA_DIR/asset-map.md"
cp .agentkit/templates/quickstart-template.md "$IDEA_DIR/quickstart.md"

mkdir -p "$IDEA_DIR/checklists"
cp .agentkit/templates/checklist-template.md "$IDEA_DIR/checklists/requirements.md"
mkdir -p "$IDEA_DIR/briefs"

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
Copy-Item .agentkit/templates/research-template.md "$IdeaDir/research.md"
Copy-Item .agentkit/templates/asset-map-template.md "$IdeaDir/asset-map.md"
Copy-Item .agentkit/templates/quickstart-template.md "$IdeaDir/quickstart.md"

New-Item -ItemType Directory -Force -Path "$IdeaDir/checklists" | Out-Null
Copy-Item .agentkit/templates/checklist-template.md "$IdeaDir/checklists/requirements.md"
New-Item -ItemType Directory -Force -Path "$IdeaDir/briefs" | Out-Null

Write-Host "Plan templates created in $IdeaDir"
"""


def get_prerequisites_script(script_type: str) -> str:
    """Return prerequisite checker script"""
    if script_type == "bash":
        return """#!/usr/bin/env bash
# Check presence of project/idea documents and emit JSON or text.

set -e

JSON=false
REQUIRE_PLAN=false
REQUIRE_TASKS=false
INCLUDE_BRIEFS=false
PATHS_ONLY=false
FEATURE_DIR=\".\"

while [[ $# -gt 0 ]]; do
    case \"$1\" in
        --json) JSON=true ;;
        --require-plan) REQUIRE_PLAN=true ;;
        --require-tasks) REQUIRE_TASKS=true ;;
        --include-briefs) INCLUDE_BRIEFS=true ;;
        --paths-only) PATHS_ONLY=true ;;
        *) FEATURE_DIR=\"$1\" ;;
    esac
    shift
done

# Detect git branch if available
BRANCH=\"no-git\"
if command -v git >/dev/null 2>&1 && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo \"detached\")
fi

ROOT=$(pwd)

SPEC=\"$FEATURE_DIR/spec.md\"
PLAN=\"$FEATURE_DIR/plan.md\"
TASKS=\"$FEATURE_DIR/tasks.md\"
RESEARCH=\"$FEATURE_DIR/research.md\"
ASSET_MAP=\"$FEATURE_DIR/asset-map.md\"
QUICKSTART=\"$FEATURE_DIR/quickstart.md\"
BRIEFS=\"$FEATURE_DIR/briefs\"
CHECKLISTS=\"$FEATURE_DIR/checklists\"

missing=()
[ -f \"$SPEC\" ] || missing+=(\"spec.md\")
if $REQUIRE_PLAN && [ ! -f \"$PLAN\" ]; then missing+=(\"plan.md\"); fi
if $REQUIRE_TASKS && [ ! -f \"$TASKS\" ]; then missing+=(\"tasks.md\"); fi

available=()
[ -f \"$PLAN\" ] && available+=(\"plan.md\")
[ -f \"$TASKS\" ] && available+=(\"tasks.md\")
[ -f \"$RESEARCH\" ] && available+=(\"research.md\")
[ -f \"$ASSET_MAP\" ] && available+=(\"asset-map.md\")
[ -f \"$QUICKSTART\" ] && available+=(\"quickstart.md\")
[ -d \"$BRIEFS\" ] && available+=(\"briefs/\")
[ -d \"$CHECKLISTS\" ] && available+=(\"checklists/\")

if $PATHS_ONLY; then
    if $JSON; then
        printf '{\"root\":\"%s\",\"branch\":\"%s\",\"feature_dir\":\"%s\",\"spec\":\"%s\",\"plan\":\"%s\",\"tasks\":\"%s\",\"research\":\"%s\",\"asset_map\":\"%s\",\"quickstart\":\"%s\",\"briefs\":\"%s\",\"checklists\":\"%s\"}\\n' \
            \"$ROOT\" \"$BRANCH\" \"$FEATURE_DIR\" \"$SPEC\" \"$PLAN\" \"$TASKS\" \"$RESEARCH\" \"$ASSET_MAP\" \"$QUICKSTART\" \"$BRIEFS\" \"$CHECKLISTS\"
    else
        echo \"ROOT: $ROOT\"
        echo \"BRANCH: $BRANCH\"
        echo \"FEATURE_DIR: $FEATURE_DIR\"
        echo \"SPEC: $SPEC\"
        echo \"PLAN: $PLAN\"
        echo \"TASKS: $TASKS\"
        echo \"RESEARCH: $RESEARCH\"
        echo \"ASSET_MAP: $ASSET_MAP\"
        echo \"QUICKSTART: $QUICKSTART\"
        echo \"BRIEFS: $BRIEFS\"
        echo \"CHECKLISTS: $CHECKLISTS\"
    fi
    exit 0
fi

if $JSON; then
    printf '{\"root\":\"%s\",\"branch\":\"%s\",\"feature_dir\":\"%s\",\"missing\":[' \"$ROOT\" \"$BRANCH\" \"$FEATURE_DIR\"
    if [ ${#missing[@]} -gt 0 ]; then
        printf '\"%s\"' \"${missing[0]}\"
        for item in \"${missing[@]:1}\"; do printf ',\"%s\"' \"$item\"; done
    fi
    printf '],\"available\":['
    if [ ${#available[@]} -gt 0 ]; then
        printf '\"%s\"' \"${available[0]}\"
        for item in \"${available[@]:1}\"; do printf ',\"%s\"' \"$item\"; done
    fi
    printf ']}\n'
else
    echo \"ROOT: $ROOT\"
    echo \"BRANCH: $BRANCH\"
    echo \"FEATURE_DIR: $FEATURE_DIR\"
    echo \"Missing: ${missing[*]:-(none)}\"
    echo \"Available: ${available[*]:-(none)}\"
fi

if [ ${#missing[@]} -gt 0 ]; then
    exit 1
fi
"""
    else:
        return """# PowerShell script
# Check presence of project/idea documents and emit JSON or text.

param(
    [switch]$Json,
    [switch]$RequirePlan,
    [switch]$RequireTasks,
    [switch]$IncludeBriefs,
    [switch]$PathsOnly,
    [string]$FeatureDir = "."
)

function Get-Branch {
    if (Get-Command git -ErrorAction SilentlyContinue) {
        $inside = git rev-parse --is-inside-work-tree 2>$null
        if ($LASTEXITCODE -eq 0) {
            $b = git rev-parse --abbrev-ref HEAD 2>$null
            if ($LASTEXITCODE -eq 0) { return $b }
        }
    }
    return "no-git"
}

$root = (Get-Location).Path
$branch = Get-Branch

$spec = Join-Path $FeatureDir "spec.md"
$plan = Join-Path $FeatureDir "plan.md"
$tasks = Join-Path $FeatureDir "tasks.md"
$research = Join-Path $FeatureDir "research.md"
$assetMap = Join-Path $FeatureDir "asset-map.md"
$quickstart = Join-Path $FeatureDir "quickstart.md"
$briefs = Join-Path $FeatureDir "briefs"
$checklists = Join-Path $FeatureDir "checklists"

$missing = @()
if (-not (Test-Path $spec)) { $missing += "spec.md" }
if ($RequirePlan -and -not (Test-Path $plan)) { $missing += "plan.md" }
if ($RequireTasks -and -not (Test-Path $tasks)) { $missing += "tasks.md" }

$available = @()
if (Test-Path $plan) { $available += "plan.md" }
if (Test-Path $tasks) { $available += "tasks.md" }
if (Test-Path $research) { $available += "research.md" }
if (Test-Path $assetMap) { $available += "asset-map.md" }
if (Test-Path $quickstart) { $available += "quickstart.md" }
if (Test-Path $briefs) { $available += "briefs/" }
if (Test-Path $checklists) { $available += "checklists/" }

if ($PathsOnly) {
    if ($Json) {
        $payload = [pscustomobject]@{
            root = $root
            branch = $branch
            feature_dir = $FeatureDir
            spec = $spec
            plan = $plan
            tasks = $tasks
            research = $research
            asset_map = $assetMap
            quickstart = $quickstart
            briefs = $briefs
            checklists = $checklists
        }
        $payload | ConvertTo-Json -Depth 3
    } else {
        Write-Host "ROOT: $root"
        Write-Host "BRANCH: $branch"
        Write-Host "FEATURE_DIR: $FeatureDir"
        Write-Host "SPEC: $spec"
        Write-Host "PLAN: $plan"
        Write-Host "TASKS: $tasks"
        Write-Host "RESEARCH: $research"
        Write-Host "ASSET_MAP: $assetMap"
        Write-Host "QUICKSTART: $quickstart"
        Write-Host "BRIEFS: $briefs"
        Write-Host "CHECKLISTS: $checklists"
    }
    exit 0
}

if ($Json) {
    $payload = [pscustomobject]@{
        root = $root
        branch = $branch
        feature_dir = $FeatureDir
        missing = $missing
        available = $available
    }
    $payload | ConvertTo-Json -Depth 3
} else {
    Write-Host "ROOT: $root"
    Write-Host "BRANCH: $branch"
    Write-Host "FEATURE_DIR: $FeatureDir"
    Write-Host "Missing: " ($missing -join ', ')
    Write-Host "Available: " ($available -join ', ')
}

if ($missing.Count -gt 0) { exit 1 }
"""


def get_update_agent_context_script(script_type: str) -> str:
    """Return agent context updater script"""
    if script_type == "bash":
        return """#!/usr/bin/env bash
# Append structured notes to agent context, avoiding duplicates.

CONTEXT_FILE=\".claude/agent-context.md\"
ENTRY=\"$*\"

if [ -z \"$ENTRY\" ]; then
    echo \"Usage: update-agent-context.sh <note>\" >&2
    exit 1
fi

mkdir -p \"$(dirname \"$CONTEXT_FILE\")\"
touch \"$CONTEXT_FILE\"

# Skip if already recorded
if grep -Fq \"$ENTRY\" \"$CONTEXT_FILE\"; then
    echo \"Note already recorded: $CONTEXT_FILE\"
    exit 0
fi

{
    echo \"- $(date -Iseconds): $ENTRY\"
} >> \"$CONTEXT_FILE\"

echo \"Context updated: $CONTEXT_FILE\"
"""
    else:
        return """# PowerShell script
# Append structured notes to agent context, avoiding duplicates.

param([Parameter(Mandatory=$true, ValueFromRemainingArguments=$true)][string[]]$Note)

$contextFile = ".claude/agent-context.md"
$entry = $Note -join " "

New-Item -ItemType Directory -Force -Path (Split-Path $contextFile) | Out-Null
if (!(Test-Path $contextFile)) { New-Item -ItemType File -Path $contextFile | Out-Null }

$existing = Get-Content $contextFile
if ($existing -match [regex]::Escape($entry)) {
    Write-Host "Note already recorded: $contextFile"
    exit 0
}

"- $(Get-Date -Format o): $entry" | Out-File -FilePath $contextFile -Append -Encoding utf8

Write-Host "Context updated: $contextFile"
"""


def get_suggest_name_script(script_type: str) -> str:
    """Return suggest-name helper script"""
    if script_type == "bash":
        return """#!/usr/bin/env bash
# Suggest next idea/feature name by scanning .agentkit/ideas and git branches (if available).

SLUG=\"$1\"
ROOT=$(pwd)

max_num=0

# From ideas directories
if [ -d .agentkit/ideas ]; then
  for dir in .agentkit/ideas/*; do
    [ -d \"$dir\" ] || continue
    base=$(basename \"$dir\")
    num=${base%%-*}
    if [[ \"$num\" =~ ^[0-9]+$ ]] && [ \"$num\" -gt \"$max_num\" ]; then
      max_num=$num
    fi
  done
fi

# From git branches
if command -v git >/dev/null 2>&1 && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  while IFS= read -r b; do
    num=${b%%-*}
    if [[ \"$num\" =~ ^[0-9]+$ ]] && [ \"$num\" -gt \"$max_num\" ]; then
      max_num=$num
    fi
  done < <(git for-each-ref --format='%(refname:short)' refs/heads/)
fi

next_num=$(printf \"%03d\" $((max_num + 1)))

if [ -n \"$SLUG\" ]; then
  echo \"${next_num}-${SLUG}\"
else
  echo \"$next_num\"
fi
"""
    else:
        return """# PowerShell script
# Suggest next idea/feature name by scanning .agentkit/ideas and git branches (if available).

param([string]$Slug)

$max = 0

if (Test-Path ".agentkit/ideas") {
    Get-ChildItem ".agentkit/ideas" -Directory | ForEach-Object {
        if ($_.Name -match '^([0-9]+)') {
            $n = [int]$matches[1]
            if ($n -gt $max) { $max = $n }
        }
    }
}

if (Get-Command git -ErrorAction SilentlyContinue) {
    $branches = git for-each-ref --format='%(refname:short)' refs/heads/ 2>$null
    foreach ($b in $branches) {
        if ($b -match '^([0-9]+)') {
            $n = [int]$matches[1]
            if ($n -gt $max) { $max = $n }
        }
    }
}

$next = "{0:D3}" -f ($max + 1)
if ($Slug) {
    Write-Host \"$next-$Slug\"
} else {
    Write-Host $next
}
"""


def get_tasks_export_script(script_type: str) -> str:
    """Return tasks export helper script"""
    if script_type == "bash":
        return """#!/usr/bin/env bash
# Export tasks.md to CSV (id,status,description).

INPUT=${1:-tasks.md}
OUTPUT=${2:-tasks.csv}

if [ ! -f "$INPUT" ]; then
    echo "Input tasks file not found: $INPUT" >&2
    exit 1
fi

echo "id,status,description" > "$OUTPUT"
awk '/^- \\[[ x]\\]/ {
    status = ($2=="[x]") ? "done" : "open";
    line = $0;
    sub(/^- \\[[ x]\\] */, "", line);
    id="";
    if (match(line, /T[0-9]+/)) {id=substr(line, RSTART, RLENGTH);}
    gsub(/,/, " ", line);
    printf "%s,%s,%s\\n", id, status, line;
}' "$INPUT" >> "$OUTPUT"
echo "Exported to $OUTPUT"
"""
    else:
        return """# PowerShell script
# Export tasks.md to CSV (id,status,description).

param(
    [string]$Input = "tasks.md",
    [string]$Output = "tasks.csv"
)

if (!(Test-Path $Input)) {
    Write-Error "Input tasks file not found: $Input"
    exit 1
}

$rows = @("id,status,description")

Get-Content $Input | ForEach-Object {
    if ($_ -match '^- \\[[ x]\\]') {
        $status = ($_ -match '^- \\[x\\]') ? "done" : "open"
        $line = $_ -replace '^- \\[[ x]\\] *', ''
        $id = ""
        if ($line -match '(T[0-9]+)') { $id = $matches[1] }
        $line = $line -replace ',', ' '
        $rows += "$id,$status,$line"
    }
}

$rows | Out-File -FilePath $Output -Encoding utf8
Write-Host "Exported to $Output"
"""


def get_constitution_sync_script(script_type: str) -> str:
    """Return constitution sync helper script"""
    if script_type == "bash":
        return """#!/usr/bin/env bash
# Sync constitution.md to .agentkit/memory and ensure a Sync Impact Report header exists.

SRC="constitution.md"
DEST=".agentkit/memory/constitution.md"
APPLY_TEMPLATES=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply-templates) APPLY_TEMPLATES=true ;;
  esac
  shift
done

if [ ! -f "$SRC" ]; then
    echo "constitution.md not found" >&2
    exit 1
fi

mkdir -p "$(dirname "$DEST")"

# Ensure Sync Impact Report header exists
if ! grep -q "Sync Impact Report" "$SRC"; then
    tmp=$(mktemp)
    cat <<'HDR' > "$tmp"
<!--
Sync Impact Report:
- Version: [OLD] -> [NEW]
- Ratified: [DATE] | Last Amended: [DATE]
- Sections: Added [..], Removed [..], Renamed [..]
- Templates/Commands: spec [ ], plan [ ], tasks [ ], checklist [ ], clarify [ ]
- TODOs: [list deferred placeholders]
-->
HDR
    cat "$SRC" >> "$tmp"
    mv "$tmp" "$SRC"
fi

cp "$SRC" "$DEST"
echo "Synced constitution to $DEST"

if $APPLY_TEMPLATES; then
    if [ -x ".agentkit/scripts/bash/template-sync.sh" ]; then
        .agentkit/scripts/bash/template-sync.sh --apply
    else
        echo "template-sync.sh not found or not executable; skipping template sync"
    fi
fi
"""
    else:
        return """# PowerShell script
# Sync constitution.md to .agentkit/memory and ensure a Sync Impact Report header exists.

$src = "constitution.md"
$dest = ".agentkit/memory/constitution.md"
$ApplyTemplates = $false

param(
    [switch]$ApplyTemplates
)

if (!(Test-Path $src)) {
    Write-Error "constitution.md not found"
    exit 1
}

New-Item -ItemType Directory -Force -Path (Split-Path $dest) | Out-Null

$content = Get-Content $src
if (-not ($content -match "Sync Impact Report")) {
    $header = @(
        "<!--"
        "Sync Impact Report:"
        "- Version: [OLD] -> [NEW]"
        "- Ratified: [DATE] | Last Amended: [DATE]"
        "- Sections: Added [..], Removed [..], Renamed [..]"
        "- Templates/Commands: spec [ ], plan [ ], tasks [ ], checklist [ ], clarify [ ]"
        "- TODOs: [list deferred placeholders]"
        "-->"
    )
    $content = $header + $content
    $content | Out-File -FilePath $src -Encoding utf8
}

Copy-Item $src $dest -Force
Write-Host "Synced constitution to $dest"

if ($ApplyTemplates) {
    $templateSync = ".agentkit/scripts/powershell/template-sync.ps1"
    if (Test-Path $templateSync) {
        & $templateSync --Apply
    } else {
        Write-Host "template-sync.ps1 not found; skipping template sync"
    }
}
"""


def get_tasks_to_issues_script(script_type: str) -> str:
    """Return tasks to issues export helper script"""
    if script_type == "bash":
        return """#!/usr/bin/env bash
# Convert tasks.md to a simple issues.csv (title,body,labels).

INPUT=${1:-tasks.md}
OUTPUT=${2:-issues.csv}
LABELS=${3:-task}

if [ ! -f "$INPUT" ]; then
    echo "Input tasks file not found: $INPUT" >&2
    exit 1
fi

echo "title,body,labels" > "$OUTPUT"
awk '/^- \\[[ x]\\]/ {
    line=$0
    status = ($2=="[x]") ? "done" : "open"
    sub(/^- \\[[ x]\\] */, "", line)
    id=""
    if (match(line, /T[0-9]+/)) {id=substr(line, RSTART, RLENGTH)}
    gsub(/\"/, \"\"\"\") line
    printf "\"%s\",\"%s\",\"%s\"\n", (id ? id \" \" line : line), "Status: " status, LABELS
}' "$INPUT" >> "$OUTPUT"
echo "Exported issues to $OUTPUT"
"""
    else:
        return """# PowerShell script
# Convert tasks.md to a simple issues.csv (title,body,labels).

param(
    [string]$Input = "tasks.md",
    [string]$Output = "issues.csv",
    [string]$Labels = "task"
)

if (!(Test-Path $Input)) {
    Write-Error "Input tasks file not found: $Input"
    exit 1
}

$rows = @("title,body,labels")

Get-Content $Input | ForEach-Object {
    if ($_ -match '^- \\[[ x]\\]') {
        $status = ($_ -match '^- \\[x\\]') ? "done" : "open"
        $line = $_ -replace '^- \\[[ x]\\] *', ''
        $id = ""
        if ($line -match '(T[0-9]+)') { $id = $matches[1] }
        $title = if ($id) { "$id $line" } else { $line }
        $body = "Status: $status"
        $title = $title -replace '\"','\"\"'
        $body = $body -replace '\"','\"\"'
        $rows += "\"$title\",\"$body\",\"$Labels\""
    }
}

$rows | Out-File -FilePath $Output -Encoding utf8
Write-Host "Exported issues to $Output"
"""


def get_tasks_to_issues_json_script(script_type: str) -> str:
    """Return tasks to issues JSON export helper script"""
    if script_type == "bash":
        return """#!/usr/bin/env bash
# Convert tasks.md to issues.json (array of {title,body,labels}) for API use.

INPUT=${1:-tasks.md}
OUTPUT=${2:-issues.json}
LABELS=${3:-task}

if [ ! -f "$INPUT" ]; then
    echo "Input tasks file not found: $INPUT" >&2
    exit 1
fi

echo "[" > "$OUTPUT"
first=true
while IFS= read -r line; do
    if [[ "$line" =~ ^-\\ \\[[\\ x]\\] ]]; then
        status=$(echo "$line" | grep -q "\\[x\\]" && echo "done" || echo "open")
        body="Status: $status"
        clean=${line#*- [x] }
        clean=${clean#*- [ ] }
        id=""
        if [[ "$clean" =~ (T[0-9]+) ]]; then id=${BASH_REMATCH[1]}; fi
        title=$clean
        title=${title//\"/\\\"}
        body=${body//\"/\\\"}
        labels=$LABELS
        if ! $first; then echo "," >> "$OUTPUT"; fi
        first=false
        printf '  {"title":"%s","body":"%s","labels":["%s"]}' "$title" "$body" "$labels" >> "$OUTPUT"
    fi
done < "$INPUT"
echo "" >> "$OUTPUT"
echo "]" >> "$OUTPUT"
echo "Exported issues to $OUTPUT"
"""
    else:
        return """# PowerShell script
# Convert tasks.md to issues.json (array of {title,body,labels}) for API use.

param(
    [string]$Input = "tasks.md",
    [string]$Output = "issues.json",
    [string]$Labels = "task"
)

if (!(Test-Path $Input)) {
    Write-Error "Input tasks file not found: $Input"
    exit 1
}

$items = @()

Get-Content $Input | ForEach-Object {
    if ($_ -match '^- \\[[ x]\\]') {
        $status = ($_ -match '^- \\[x\\]') ? "done" : "open"
        $body = "Status: $status"
        $line = $_ -replace '^- \\[[ x]\\] *', ''
        $id = ""
        if ($line -match '(T[0-9]+)') { $id = $matches[1] }
        $title = $line
        $labels = @($Labels)
        $items += [pscustomobject]@{ title = $title; body = $body; labels = $labels }
    }
}

$items | ConvertTo-Json -Depth 3 | Out-File -FilePath $Output -Encoding utf8
Write-Host "Exported issues to $Output"
"""


def get_template_sync_script(script_type: str) -> str:
    """Return template/command propagation helper script"""
    if script_type == "bash":
        return """#!/usr/bin/env bash
# Copy updated templates/commands into project if they differ. Dry-run by default.

SRC_TEMPLATES=".agentkit/templates"
DEST_TEMPLATES=".agentkit/templates"
DRY_RUN=true

while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply) DRY_RUN=false ;;
  esac
  shift
done

copy_if_changed() {
  src=$1; dest=$2
  if ! cmp -s "$src" "$dest"; then
    if $DRY_RUN; then
      echo "DIFF: $dest (would update from $src)"
    else
      cp "$src" "$dest"
      echo "UPDATED: $dest"
    fi
  fi
}

# Templates
for f in specification-template.md plan-template.md tasks-template.md checklist-template.md asset-map-template.md research-template.md quickstart-template.md constitution-template.md; do
  if [ -f "$SRC_TEMPLATES/$f" ] && [ -f "$DEST_TEMPLATES/$f" ]; then
    copy_if_changed "$SRC_TEMPLATES/$f" "$DEST_TEMPLATES/$f"
  fi
done

# Commands
for f in constitution clarify specify plan task implement checklist; do
  src=".claude/commands/$f.md"
  dest=".claude/commands/$f.md"
  if [ -f "$src" ] && [ -f "$dest" ]; then
    copy_if_changed "$src" "$dest"
  fi
done

if $DRY_RUN; then
  echo "Dry run complete. Re-run with --apply to copy."
fi
"""
    else:
        return """# PowerShell script
# Copy updated templates/commands into project if they differ. Dry-run by default.

param([switch]$Apply)

$dryRun = -not $Apply

function Copy-IfChanged {
    param([string]$Src, [string]$Dest)
    if (Test-Path $Src -and Test-Path $Dest) {
        $same = Compare-Object (Get-Content $Src) (Get-Content $Dest)
        if ($same) {
            if ($dryRun) { Write-Host "DIFF: $Dest (would update from $Src)" }
            else {
                Copy-Item $Src $Dest -Force
                Write-Host "UPDATED: $Dest"
            }
        }
    }
}

# Templates
$templates = @("specification-template.md","plan-template.md","tasks-template.md","checklist-template.md","asset-map-template.md","research-template.md","quickstart-template.md","constitution-template.md")
foreach ($f in $templates) {
    Copy-IfChanged ".agentkit/templates/$f" ".agentkit/templates/$f"
}

# Commands
$commands = @("constitution.md","clarify.md","specify.md","plan.md","task.md","implement.md","checklist.md")
foreach ($f in $commands) {
    Copy-IfChanged ".claude/commands/$f" ".claude/commands/$f"
}

if ($dryRun) { Write-Host "Dry run complete. Re-run with --apply to copy." }
"""


def get_tasks_to_github_script(script_type: str) -> str:
    """Return helper to generate GitHub issue commands"""
    if script_type == "bash":
        return """#!/usr/bin/env bash
# Generate GitHub issue create commands from tasks.md (requires gh CLI if executed).

INPUT=${1:-tasks.md}
OUTPUT=${2:-gh-issues.sh}
LABELS=${3:-task}

if [ ! -f "$INPUT" ]; then
    echo "Input tasks file not found: $INPUT" >&2
    exit 1
fi

echo "#!/usr/bin/env bash" > "$OUTPUT"
echo "# Generated commands to create issues from $INPUT" >> "$OUTPUT"

while IFS= read -r line; do
    if [[ "$line" =~ ^-\\ \\[[\\ x]\\] ]]; then
        status=$(echo "$line" | grep -q "\\[x\\]" && echo "done" || echo "open")
        clean=${line#*- [x] }
        clean=${clean#*- [ ] }
        title=${clean//\"/\\\"}
        body="Status: $status"
        echo "gh issue create --title \"$title\" --body \"$body\" --label \"$LABELS\"" >> "$OUTPUT"
    fi
done < "$INPUT"

chmod +x "$OUTPUT"
echo "Generated GitHub issue commands in $OUTPUT (review before running)"
"""
    else:
        return """# PowerShell script
# Generate GitHub issue create commands from tasks.md (requires gh CLI if executed).

param(
    [string]$Input = "tasks.md",
    [string]$Output = "gh-issues.ps1",
    [string]$Labels = "task"
)

if (!(Test-Path $Input)) {
    Write-Error "Input tasks file not found: $Input"
    exit 1
}

$lines = @("# Generated commands to create issues from $Input")

Get-Content $Input | ForEach-Object {
    if ($_ -match '^- \\[[ x]\\]') {
        $status = ($_ -match '^- \\[x\\]') ? "done" : "open"
        $clean = $_ -replace '^- \\[[ x]\\] *', ''
        $title = $clean -replace '\"','\"\"'
        $body = "Status: $status"
        $lines += "gh issue create --title \"$title\" --body \"$body\" --label \"$Labels\""
    }
}

$lines | Out-File -FilePath $Output -Encoding utf8
Write-Host "Generated GitHub issue commands in $Output (review before running)"
"""


def get_tasks_to_github_push_script(script_type: str) -> str:
    """Return helper to create GitHub issues directly via gh CLI"""
    if script_type == "bash":
        return """#!/usr/bin/env bash
# Create GitHub issues from tasks.md using gh CLI.

INPUT=${1:-tasks.md}
LABELS=${2:-task}

if [ ! -f "$INPUT" ]; then
    echo "Input tasks file not found: $INPUT" >&2
    exit 1
fi

if ! command -v gh >/dev/null 2>&1; then
    echo "gh CLI not found; install GitHub CLI first." >&2
    exit 1
fi

while IFS= read -r line; do
    if [[ "$line" =~ ^-\\ \\[[\\ x]\\] ]]; then
        status=$(echo "$line" | grep -q "\\[x\\]" && echo "done" || echo "open")
        clean=${line#*- [x] }
        clean=${clean#*- [ ] }
        title=${clean//\"/\\\"}
        body="Status: $status"
        gh issue create --title "$title" --body "$body" --label "$LABELS"
    fi
done < "$INPUT"
"""
    else:
        return """# PowerShell script
# Create GitHub issues from tasks.md using gh CLI.

param(
    [string]$Input = "tasks.md",
    [string]$Labels = "task"
)

if (!(Test-Path $Input)) {
    Write-Error "Input tasks file not found: $Input"
    exit 1
}

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Error "gh CLI not found; install GitHub CLI first."
    exit 1
}

Get-Content $Input | ForEach-Object {
    if ($_ -match '^- \\[[ x]\\]') {
        $status = ($_ -match '^- \\[x\\]') ? "done" : "open"
        $clean = $_ -replace '^- \\[[ x]\\] *', ''
        $title = $clean -replace '\"','\"\"'
        $body = "Status: $status"
        gh issue create --title "$title" --body "$body" --label "$Labels"
    }
}
"""

def get_constitution_command() -> str:
    """Return /constitution command content"""
    return """# /constitution - Set Principles & Governance

Purpose: capture non-negotiable principles, style, constraints, and decision rules in `constitution.md` and mirror them into `.agentkit/memory/constitution.md`.

Handoff: `/specify` next. Gate: constitution ready (no critical TODOs) before moving on.

Workflow:
1) Load the template from `.agentkit/templates/constitution-template.md`.
2) Collect or infer values for all placeholders (version, dates, principles, governance). If something is unknown, mark `TODO(<field>)` and note it.
3) Update semantic version:
   - MAJOR: breaking changes to principles/governance
   - MINOR: new sections or meaningful additions
   - PATCH: clarifications/typos
4) Write the completed constitution to both `constitution.md` (user-facing) and `.agentkit/memory/constitution.md` (agent reference).
5) Add a Sync Impact Report at the top of `constitution.md`:
   - Version old -> new; Ratified, Last Amended dates
   - Added/Removed/Renamed sections
   - Templates/commands affected (spec/plan/tasks/checklist/clarify/checklist) with ✅ updated or ⚠️ TODO
   - TODO placeholders deferred
6) Propagation checklist (apply where relevant):
   - Update spec/plan/tasks/checklist templates to reflect new principles/gates.
   - Update command prompts (constitution checks, gates).
   - Copy the updated constitution into `.agentkit/memory/constitution.md`.
   - Run `.agentkit/scripts/bash/template-sync.sh --apply` (or PowerShell equivalent) to copy updated templates/commands.
   - Align `spec.md` scope/constraints/tone/acceptance with constitution changes (add TODOs if unresolved).
   - Record any manual follow-ups in the report as ⚠️ TODO.

Quality gates:
- No leftover bracketed placeholders unless intentionally TODO'd.
- ISO dates (YYYY-MM-DD).
- Principles are testable (avoid vague \"should\").
"""


def get_specify_command() -> str:
    """Return /specify command content"""
    return """# /specify - Capture the What and Why

Create a crisp specification in `spec.md` that answers WHAT and WHY only (no implementation).

Handoff: `/clarify` (if needed), then `/checklist`, then `/plan`. Gate: spec complete with ≤3 NEEDS CLARIFICATION markers, top unknowns logged to research.

Steps:
1) Parse the user description and extract actors, actions, constraints, and success signals.
2) Ask up to three clarifying questions only if they change scope/requirements materially.
3) Fill `spec.md` from `.agentkit/templates/specification-template.md`:
   - Problem, Desired Outcome, Scope (in/out/assumptions), Success Criteria, Key Decisions, Related Docs.
   - User stories with priorities and acceptance scenarios.
   - Mark unclear items with `[NEEDS CLARIFICATION: question]` (max 3).
4) Identify the top 2–3 unknowns; log them in `research.md` (Open Questions) and propose [R] tasks for `/task`.
5) Draft preliminary constitution signals (principles/constraints/tone/safety) into `constitution.md` as TODO-marked entries if the template is still placeholder-only.
6) Keep implementation out: if HOW/WHEN appears, park it as a note for `/plan`.
7) Update `checklists/requirements.md` from the checklist template to validate spec quality.

Quality gates:
- At least one P1 user story with acceptance scenarios.
- Success criteria are measurable and tech-agnostic.
- No implementation phases, timelines, or roles.
"""


def get_clarify_command() -> str:
    """Return /clarify command content"""
    return """# /clarify - Resolve Critical Unknowns

Goal: ask and resolve up to 5 high-impact questions before planning.

Handoff: `/plan` (run after clarifications are recorded). Gate: stop at 5 questions; only proceed to `/plan` if no high-impact ambiguities remain.

Process:
1) Load `spec.md` and `research.md` (Open Questions). Extract domain, audience, scope, constraints, and risks from the user message.
2) Build a short list of candidate questions; keep only those that materially change scope, acceptance, safety/compliance, or feasibility.
3) Ask questions one at a time (max 5). For each:
   - Offer a recommended answer (best practice + brief rationale) and, if helpful, a 2–5 option table.
   - Allow a short free-form answer (<=5 words) as an alternative.
4) When an answer is accepted:
   - Record it in `research.md` (Findings/Proposed Decisions or Decisions if final).
   - Apply it to the right section of `spec.md` (user stories, scope in/out, success criteria, constraints, edge cases).
   - Remove or resolve any `[NEEDS CLARIFICATION]` it covers.
5) Stop early if no critical ambiguities remain; otherwise, surface any Deferred/Open items for `/task` as `[R]` research tasks.

6) End with a coverage summary (Clear / Resolved / Deferred / Outstanding) so the next command knows the risk.

Rules:
- Prioritize by impact × uncertainty; skip low-impact style preferences.
- Keep questions concise; avoid duplicates of already-answered content.
- If user declines more questions, summarize outstanding items and proceed.
"""


def get_plan_command() -> str:
    """Return /plan command content"""
    return """# /plan - Define How and When

Use `spec.md` (WHAT/WHY) as input and produce `plan.md` that covers HOW/WHEN.

Gates: run `/clarify` first; proceed only if no critical ambiguities are open or they are tracked as `[R]` tasks with owners/timeboxes.
Handoff: `/task` next. Also update `checklists/requirements.md` if scope/constraints change.

Steps:
1) Run `.agentkit/scripts/bash/check-prerequisites.sh --json --require-plan` to verify files and gather available docs (use PowerShell variant on Windows).
2) Load: `spec.md`, `research.md` (if present), `constitution.md` for alignment.
3) Fill `plan.md` from the template:
   - Summary + key decisions tied to spec.
   - Creative/operational context (audience, tone, channels, constraints, resources).
   - Constitution check (note any violations and justifications).
   - Project structure decision.
   - Research plan: top questions, outputs, owners, timeboxes.
   - Phases with goals/durations and handoff to `/task`.
4) Generate/update supporting docs: ensure `research.md`, `asset-map.md`, `quickstart.md`, and `briefs/` placeholders exist (do not over-write user edits).
5) Record any open clarifications for `/clarify` or `/specify` follow-up and create [R] tasks for remaining research.

Quality gates:
- No implementation code; plan remains high-level but actionable.
- Explicit dependencies, risks, and sequencing.
- Outputs are path-specific (no \"TBD\" unless captured as TODO).
"""


def get_task_command() -> str:
    """Return /task command content"""
    return """# /task - Break Down Into Actions

Generate categorized, actionable task list organized by user story and phase.

Handoff: `/implement` next. Gate: prerequisites satisfied via `check-prerequisites` (spec/plan/tasks), [R] tasks captured for open questions.

Inputs: `plan.md`, `spec.md`, `asset-map.md`, `briefs/`, `quickstart.md`.

Steps:
1) Confirm prerequisites with `.agentkit/scripts/bash/check-prerequisites.sh --json --include-tasks`.
2) For each user story or output surface, list tasks using `[ID] [P?] [Story/Surface] Description`.
3) Add research tasks with `[R]` tag for open questions; include expected output in `research.md` and a timebox.
4) Include dependencies and suggested parallelism markers `[P]`.
5) Only include validation/pilot tasks if requested; otherwise mark as optional.
6) Keep tasks specific with locations or artifacts (e.g., `briefs/menu.md`, `assets/maps/region.md`).
7) Append to `tasks.md` instead of overwriting user edits where possible.
"""


def get_implement_command() -> str:
    """Return /implement command content"""
    return """# /implement - Execute and Create

Purpose: execute tasks, keep outputs organized, and update context.

Handoff: when tasks and acceptance criteria are satisfied, update quickstart/checklists and report back. Gate: prerequisites satisfied via `check-prerequisites --require-plan --require-tasks`.

Steps:
1) Read `tasks.md` and pick the next task; restate the goal and acceptance criteria.
2) For `[R]` research tasks: restate the question, gather sources with citations, propose a decision with options and confidence, and update `research.md` (Findings/Proposed Decisions/Decisions).
3) For other tasks: work in small commits/chunks; validate against constitution and spec requirements.
4) Update `quickstart.md` with any new setup/run steps and `checklists/requirements.md` if scope changes.
5) Capture learnings/decisions with `.agentkit/scripts/bash/update-agent-context.sh "<note>"`.
6) When a task is done, mark it in `tasks.md` and summarize what changed.
"""


def get_checklist_command() -> str:
    """Return /checklist command content"""
    return """# /checklist - Validate Specification Quality

Purpose: create a requirements-quality checklist in `checklists/requirements.md`.

Gate: run after `/specify` (and `/clarify` if used) to ensure requirements are testable before `/plan`.
Handoff: `/plan` and `/task` use this checklist as acceptance gates.

Steps:
1) Load `spec.md` (and `plan.md` if available) to capture scope, user stories, and risks.
2) Draft checklist items as questions about requirement quality (completeness, clarity, consistency, coverage, measurability). Avoid implementation testing.
3) Reference spec sections or mark `[Gap]` where content is missing.
4) Ensure ≥80% of items include a traceability marker (Spec reference or Gap/Ambiguity); cite research/briefs when decisions depend on them.
5) Include items for research quality: sources cited, decisions justified, confidence stated.
6) Append new checklist items instead of overwriting user edits.
"""


def get_tasks_to_issues_command() -> str:
    """Return /tasks-to-issues command content"""
    return """# /tasks-to-issues - Turn Tasks into GitHub Issues

Purpose: convert `tasks.md` into GitHub issues using MCP (or halt if not a GitHub remote).

Outline:
1) Run `.agentkit/scripts/bash/check-prerequisites.sh --json --require-tasks --include-tasks` (or PowerShell equivalent) to get FEATURE_DIR and TASKS path.
2) Ensure git remote is GitHub:
   - `git config --get remote.origin.url`
   - If not a GitHub URL, STOP (do not create issues).
3) For each task in tasks.md:
   - Use GitHub MCP server `github/github-mcp-server/issue_write` to create an issue.
   - Title = task line (include task ID if present), Body = status + any dependencies, Labels = `task`.
4) Do not create issues in any repo other than the detected remote.

If MCP not available, STOP and report that issues were not created.
"""


# ============================================================================
# v0.3.0: Auto-Orchestration Commands
# ============================================================================

def get_start_command() -> str:
    """Return /start command content for auto-orchestrated workflow"""
    return """# /start - Begin or Resume Workflow

Begin or continue the auto-orchestrated AgentKit workflow.

## Execution

1. **Read current state**
   - Load `.agentkit/workflow-state.yaml`
   - If missing, detect phase from existing documents
   - Sync state to documents if inconsistent (self-healing)

2. **Context discovery** (first run only)
   - Scan project folder for existing files:
     - Data files: `*.json`, `*.csv`, `*.xlsx`
     - Prior analysis: `*.ipynb`, reports/, outputs/
     - Documentation: `*.md` files not part of AgentKit
   - If found, ask user:
     > "I found existing files in this project: [list files]
     > Should I incorporate them into our planning, or start fresh?"
   - Record decision in workflow-state.yaml

3. **Display progress** (if resuming)
   ```
   Welcome back! You're in the [PHASE] phase.
   Progress: [X/Y] phases complete
   ```

4. **Load phase instructions**
   - Read `.agentkit/phases/{current_phase}.md`
   - Follow the phase-specific guidance

5. **Begin/continue phase work**
   - If phase is pending: start with opening prompt (open-ended)
   - If phase is in_progress: continue conversation
   - If phase is completed: advance to next phase

6. **Update state after each interaction**
   - Save progress to workflow-state.yaml
   - Track questions answered, docs read

## Notes
- This command orchestrates the full workflow automatically
- User describes things in their own words; agent asks follow-up questions
- State is saved frequently to enable session resumption
"""


def get_continue_command() -> str:
    """Return /continue command content (alias for /start)"""
    return """# /continue - Resume Workflow

Alias for `/start`. Continues the auto-orchestrated workflow from where you left off.

See `/start` for full documentation.
"""


def get_status_command() -> str:
    """Return /status command content"""
    return """# /status - Show Workflow Progress

Display current workflow state and progress.

## Execution

1. **Read state file**
   - Load `.agentkit/workflow-state.yaml`
   - If missing, detect from documents

2. **Display summary**
   ```
   ## Project: [NAME]

   **Current Phase**: [PHASE] ([STATUS])
   **Progress**: [X/5] phases complete

   ### Phase Status
   - [x] Constitution - completed
   - [>] Specify - in progress (3/8 questions)
   - [ ] Plan - pending
   - [ ] Task - pending
   - [ ] Implement - pending

   ### Documents Created
   - constitution.md ✓
   - spec.md (in progress)
   ```

3. **Show next action**
   ```
   **Next**: Continue with `/start` or answer the pending questions.
   ```

## Output Format
- `[x]` = completed
- `[>]` = in progress
- `[ ]` = pending
"""


def get_skip_command() -> str:
    """Return /skip command content"""
    return """# /skip - Skip Current Phase

Skip the current workflow phase and advance to the next one.

## Execution

1. **Confirm intent**
   ```
   ⚠️ You're about to skip the [CURRENT_PHASE] phase.

   This means:
   - [PHASE]-specific document won't be created
   - Later phases may have less context to work with
   - You can always come back with /[PHASE] command

   Are you sure? (yes/no)
   ```

2. **If confirmed**
   - Update workflow-state.yaml: advance current_phase to next
   - Announce: "Skipped [PHASE]. Now in [NEXT_PHASE] phase."
   - Begin next phase

3. **If declined**
   - Stay in current phase
   - Continue with `/start`

## Phase-Specific Warnings
- Skipping Constitution: "No guiding principles for recommendations"
- Skipping Specify: "Planning will lack clear outcomes"
- Skipping Plan: "Tasks generated without approach context"
- Skipping Task: "No structured work breakdown"
- Cannot skip Implement (final phase)
"""
