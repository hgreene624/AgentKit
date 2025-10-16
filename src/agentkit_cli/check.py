"""
AgentKit check module - validates environment and installed tools
"""

import subprocess
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

# Tool checks configuration
TOOLS_TO_CHECK = {
    "python": {
        "command": ["python", "--version"],
        "min_version": "3.11",
        "required": True,
        "description": "Python interpreter"
    },
    "git": {
        "command": ["git", "--version"],
        "required": False,
        "description": "Version control (optional)"
    },
    "claude": {
        "command": ["claude", "--version"],
        "required": False,
        "description": "Claude Code CLI"
    },
    "code": {
        "command": ["code", "--version"],
        "required": False,
        "description": "VS Code (for Copilot)"
    },
    "cursor": {
        "command": ["cursor", "--version"],
        "required": False,
        "description": "Cursor editor"
    },
    "gemini": {
        "command": ["gemini", "--version"],
        "required": False,
        "description": "Gemini CLI"
    }
}


def check_environment(args) -> int:
    """
    Check environment and installed tools
    
    Args:
        args: Command line arguments from argparse
        
    Returns:
        Exit code (0 for success, 1 if required tools missing)
    """
    console.print("\n[bold cyan]AgentKit Environment Check[/bold cyan]\n")
    
    results = {}
    
    # Check each tool
    for tool_name, tool_config in TOOLS_TO_CHECK.items():
        status, version, message = check_tool(tool_name, tool_config)
        results[tool_name] = {
            "status": status,
            "version": version,
            "message": message,
            "required": tool_config["required"],
            "description": tool_config["description"]
        }
    
    # Display results in a table
    display_results(results)
    
    # Check if AgentKit is initialized in current directory
    check_agentkit_project()
    
    # Summary
    display_summary(results)
    
    # Return error if required tools are missing
    for tool_name, result in results.items():
        if result["required"] and result["status"] != "installed":
            return 1
            
    return 0


def check_tool(tool_name: str, tool_config: dict) -> tuple[str, str, str]:
    """
    Check if a tool is installed
    
    Args:
        tool_name: Name of the tool
        tool_config: Configuration dict for the tool
        
    Returns:
        Tuple of (status, version, message)
        status: "installed", "not_found", "error"
        version: Version string or empty
        message: Additional information
    """
    try:
        result = subprocess.run(
            tool_config["command"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            version = result.stdout.strip().split('\n')[0]
            
            # Check version requirement if specified
            if "min_version" in tool_config:
                if not check_version(version, tool_config["min_version"]):
                    return (
                        "installed",
                        version,
                        f"⚠️  Version {tool_config['min_version']}+ required"
                    )
            
            return ("installed", version, "")
        else:
            return ("error", "", "Command failed")
            
    except FileNotFoundError:
        return ("not_found", "", "")
    except subprocess.TimeoutExpired:
        return ("error", "", "Command timed out")
    except Exception as e:
        return ("error", "", str(e))


def check_version(version_string: str, min_version: str) -> bool:
    """
    Check if version meets minimum requirement
    
    Args:
        version_string: Actual version (e.g., "Python 3.11.5")
        min_version: Minimum required version (e.g., "3.11")
        
    Returns:
        True if version is sufficient
    """
    try:
        # Extract version numbers
        import re
        actual = re.search(r'(\d+\.?\d*\.?\d*)', version_string)
        if not actual:
            return False
            
        actual_parts = [int(x) for x in actual.group(1).split('.') if x]
        required_parts = [int(x) for x in min_version.split('.') if x]
        
        # Pad to same length
        while len(actual_parts) < len(required_parts):
            actual_parts.append(0)
            
        # Compare
        for a, r in zip(actual_parts, required_parts):
            if a > r:
                return True
            elif a < r:
                return False
                
        return True  # Equal
        
    except Exception:
        return False


def display_results(results: dict):
    """Display check results in a formatted table"""
    
    table = Table(title="Tool Status", show_header=True, header_style="bold cyan")
    table.add_column("Tool", style="cyan", width=15)
    table.add_column("Status", width=12)
    table.add_column("Version", style="dim", width=30)
    table.add_column("Description", style="dim")
    
    for tool_name, result in results.items():
        # Format status with color and icon
        if result["status"] == "installed":
            status_str = "[green]✓ Installed[/green]"
        elif result["status"] == "not_found":
            if result["required"]:
                status_str = "[red]✗ Missing[/red]"
            else:
                status_str = "[yellow]○ Not Found[/yellow]"
        else:  # error
            status_str = "[red]✗ Error[/red]"
            
        # Add required indicator
        tool_display = tool_name
        if result["required"]:
            tool_display += " *"
            
        table.add_row(
            tool_display,
            status_str,
            result["version"] + (" " + result["message"] if result["message"] else ""),
            result["description"]
        )
    
    console.print(table)
    console.print("\n[dim]* Required tool[/dim]\n")


def check_agentkit_project():
    """Check if current directory is an AgentKit project"""
    
    agentkit_dir = Path(".agentkit")
    
    if not agentkit_dir.exists():
        console.print("[yellow]ℹ  Current directory is not an AgentKit project[/yellow]")
        console.print("[dim]Run 'agentkit init' to initialize[/dim]\n")
        return
        
    # Check structure
    checks = {
        "Constitution": agentkit_dir / "memory" / "constitution.md",
        "Templates": agentkit_dir / "templates",
        "Scripts": agentkit_dir / "scripts",
        "Ideas": agentkit_dir / "ideas"
    }
    
    console.print("[bold]AgentKit Project Status:[/bold]")
    
    all_good = True
    for name, path in checks.items():
        if path.exists():
            console.print(f"  [green]✓[/green] {name}")
        else:
            console.print(f"  [red]✗[/red] {name} missing")
            all_good = False
            
    if all_good:
        console.print("[green]✓ Project structure is complete[/green]\n")
        
        # Count ideas
        ideas_dir = agentkit_dir / "ideas"
        idea_count = len(list(ideas_dir.iterdir())) if ideas_dir.exists() else 0
        if idea_count > 0:
            console.print(f"[cyan]📁 {idea_count} idea(s) in progress[/cyan]\n")
        else:
            console.print("[dim]No ideas yet. Use /specify to create one![/dim]\n")
    else:
        console.print("[yellow]⚠️  Project structure incomplete[/yellow]")
        console.print("[dim]Run 'agentkit init --here --force' to repair[/dim]\n")


def display_summary(results: dict):
    """Display summary and recommendations"""
    
    # Count AI agents found
    ai_agents = ["claude", "code", "cursor", "gemini"]
    agents_found = [name for name in ai_agents if results.get(name, {}).get("status") == "installed"]
    
    if not agents_found:
        console.print(Panel.fit(
            "[yellow]⚠️  No AI agents detected[/yellow]\n\n"
            "AgentKit works with:\n"
            "  • Claude Code - https://www.anthropic.com/claude-code\n"
            "  • GitHub Copilot - https://github.com/features/copilot\n"
            "  • Cursor - https://cursor.sh\n"
            "  • Gemini CLI - https://github.com/google-gemini/gemini-cli\n\n"
            "Install at least one AI agent to use AgentKit.",
            title="🤖 AI Agent Required",
            border_style="yellow"
        ))
    else:
        agents_list = ", ".join([a.title() for a in agents_found])
        console.print(Panel.fit(
            f"[green]✓ AI agent(s) detected: {agents_list}[/green]\n\n"
            "You're ready to use AgentKit!\n\n"
            "[bold]Quick Start:[/bold]\n"
            "1. agentkit init my-project\n"
            "2. cd my-project\n"
            "3. Edit .agentkit/memory/constitution.md\n"
            "4. Run your AI agent\n"
            "5. Use /specify to start your first idea",
            title="✨ Ready to Go",
            border_style="green"
        ))
    
    # Check Python version
    python_result = results.get("python", {})
    if python_result.get("status") == "installed":
        if python_result.get("message"):
            console.print(f"\n[yellow]{python_result['message']}[/yellow]")
    elif python_result.get("required"):
        console.print("\n[red]✗ Python 3.11+ is required to run AgentKit[/red]")
        
    console.print()


def get_system_info():
    """Get basic system information"""
    import platform
    
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "python_version": platform.python_version(),
        "architecture": platform.machine()
    }
