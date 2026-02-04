"""
AgentKit upgrade module - migrates v0.2.0 projects to v0.3.0

Handles:
- Creating .agentkit/phases/ directory
- Installing phase instruction files
- Creating workflow-state.yaml from existing documents
- Updating AGENTS.md to minimal router
- Preserving existing work
"""

import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple

from rich.console import Console
from rich.prompt import Confirm
from rich.panel import Panel

from agentkit_cli.config import AgentKitConfig, is_agentkit_project
from agentkit_cli.state import (
    WorkflowState,
    PhaseState,
    ProjectInfo,
    SessionState,
    write_state,
    detect_phase_from_documents,
    PHASE_ORDER,
    PHASE_DOCUMENTS,
)
from agentkit_cli.init import (
    install_phase_instructions,
    install_minimal_agents_md,
    get_minimal_agents_md,
)

console = Console()


def upgrade_project(args) -> int:
    """
    Upgrade an existing AgentKit project to v0.3.0

    Args:
        args: Command line arguments from argparse

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        project_dir = Path.cwd()

        # Check if this is an AgentKit project
        if not is_agentkit_project(project_dir):
            console.print("[red]Error: Not inside an AgentKit project[/red]")
            console.print("Run 'agentkit init' to create a new project.")
            return 1

        # Check current version
        current_version, needs_upgrade = check_version(project_dir)

        if not needs_upgrade and not args.force:
            console.print(f"[green]Project is already at v0.3.0 or later[/green]")
            console.print("Use --force to re-run upgrade anyway.")
            return 0

        console.print(f"\n[bold cyan]AgentKit Upgrade[/bold cyan]")
        console.print(f"Project: [yellow]{project_dir.name}[/yellow]")
        console.print(f"Current version: [blue]{current_version}[/blue]")
        console.print(f"Target version: [green]0.3.0[/green]\n")

        # Show what will be done
        console.print("[bold]This upgrade will:[/bold]")
        console.print("  1. Create .agentkit/phases/ directory")
        console.print("  2. Install phase instruction files")
        console.print("  3. Create workflow-state.yaml from existing documents")
        console.print("  4. Backup and update AGENTS.md to minimal router")
        console.print("  5. Add new commands (/start, /status, /skip)")
        console.print()

        if not args.yes:
            if not Confirm.ask("Proceed with upgrade?", default=True):
                console.print("[yellow]Upgrade cancelled[/yellow]")
                return 0

        # Perform upgrade
        console.print("\n[bold]Upgrading...[/bold]")

        # Step 1: Create phases directory
        console.print("  Creating .agentkit/phases/...")
        phases_dir = project_dir / ".agentkit" / "phases"
        phases_dir.mkdir(parents=True, exist_ok=True)

        # Step 2: Install phase instruction files
        console.print("  Installing phase instruction files...")
        install_phase_instructions(project_dir)

        # Step 3: Create workflow state from existing documents
        console.print("  Creating workflow-state.yaml...")
        state = infer_state_from_documents(project_dir)
        write_state(project_dir, state)

        # Step 4: Backup and update AGENTS.md
        console.print("  Updating AGENTS.md...")
        backup_and_update_agents_md(project_dir)

        # Step 5: Add new commands
        console.print("  Adding new commands...")
        add_new_commands(project_dir)

        # Success message
        console.print()
        console.print(Panel.fit(
            f"[green]✓ Upgrade complete![/green]\n\n"
            f"Project upgraded to v0.3.0 (Auto-Orchestrated)\n\n"
            f"[bold]What's new:[/bold]\n"
            f"• Use /start to begin auto-orchestrated workflow\n"
            f"• Use /status to see progress\n"
            f"• Agent guides you through phases automatically\n"
            f"• Session state saved for resumability\n\n"
            f"[dim]Your existing files were preserved.[/dim]\n"
            f"[dim]AGENTS.md backup: AGENTS.md.backup[/dim]",
            title="🎉 Upgrade Complete",
            border_style="green"
        ))

        return 0

    except Exception as e:
        console.print(f"[red]Error during upgrade: {e}[/red]")
        import traceback
        traceback.print_exc()
        return 1


def check_version(project_dir: Path) -> Tuple[str, bool]:
    """
    Check the current project version and if upgrade is needed.

    Returns:
        Tuple of (current_version, needs_upgrade)
    """
    state_file = project_dir / ".agentkit" / "workflow-state.yaml"

    # If workflow-state.yaml exists with version 0.3.0, already upgraded
    if state_file.exists():
        try:
            content = state_file.read_text()
            if 'version: "0.3.0"' in content or "version: '0.3.0'" in content:
                return "0.3.0", False
        except Exception:
            pass

    # Check for phases directory
    phases_dir = project_dir / ".agentkit" / "phases"
    if phases_dir.exists() and any(phases_dir.iterdir()):
        return "0.3.0", False

    # Otherwise assume v0.2.0 or earlier
    return "0.2.0", True


def infer_state_from_documents(project_dir: Path) -> WorkflowState:
    """
    Infer workflow state from existing documents.

    Checks for constitution.md, spec.md, plan.md, tasks.md
    and sets phase statuses accordingly.
    """
    state = WorkflowState()
    state.project.name = project_dir.name
    state.project.created = datetime.now().isoformat()

    # Detect which documents exist
    docs_exist = {
        "constitution": (project_dir / "constitution.md").exists(),
        "specify": (project_dir / "spec.md").exists(),
        "plan": (project_dir / "plan.md").exists(),
        "task": (project_dir / "tasks.md").exists(),
    }

    # Determine current phase and mark completed phases
    current_phase = "constitution"

    for phase in PHASE_ORDER[:-1]:  # Exclude implement
        doc_name = PHASE_DOCUMENTS.get(phase)
        if doc_name and (project_dir / doc_name).exists():
            # This phase is complete
            state.phases[phase].status = "completed"
            state.phases[phase].completed_at = datetime.now().isoformat()

            # Move to next phase
            phase_idx = PHASE_ORDER.index(phase)
            if phase_idx + 1 < len(PHASE_ORDER):
                current_phase = PHASE_ORDER[phase_idx + 1]
        else:
            break

    state.current_phase = current_phase

    # Mark current phase as in_progress if not already complete
    if state.phases[current_phase].status != "completed":
        state.phases[current_phase].status = "in_progress"

    # Track which docs we found
    state.session.docs_read = [
        phase for phase, exists in docs_exist.items() if exists
    ]

    return state


def backup_and_update_agents_md(project_dir: Path):
    """
    Backup existing AGENTS.md and replace with minimal router.
    """
    agents_md = project_dir / "AGENTS.md"
    backup_path = project_dir / "AGENTS.md.backup"

    # Backup if exists
    if agents_md.exists():
        # Don't overwrite existing backup
        if not backup_path.exists():
            shutil.copy(agents_md, backup_path)

    # Write new minimal AGENTS.md
    install_minimal_agents_md(project_dir)


def add_new_commands(project_dir: Path):
    """
    Add new v0.3.0 commands to the agent's command directory.
    """
    config = AgentKitConfig(project_dir)

    # Determine command directory
    from agentkit_cli.init import AGENT_CONFIG

    ai_agent = config.ai_agent or "claude"
    agent_config = AGENT_CONFIG.get(ai_agent, AGENT_CONFIG["claude"])
    command_dir = project_dir / agent_config["command_dir"]
    ext = agent_config["file_extension"]

    # Import command getters
    from agentkit_cli.init import (
        get_start_command,
        get_continue_command,
        get_status_command,
        get_skip_command,
    )

    # New commands to add
    new_commands = {
        "start": get_start_command(),
        "continue": get_continue_command(),
        "status": get_status_command(),
        "skip": get_skip_command(),
    }

    # Write command files (don't overwrite if they exist)
    for name, content in new_commands.items():
        command_file = command_dir / f"{name}{ext}"
        if not command_file.exists():
            command_file.write_text(content)
