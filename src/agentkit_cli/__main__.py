#!/usr/bin/env python3
"""
AgentKit CLI - Creative Idea Development with AI Agents

A toolkit for transforming fuzzy ideas into concrete realities through
structured workflows with AI agents.
"""

import sys
import argparse
import subprocess
from pathlib import Path

# Import version from package
try:
    from agentkit_cli import __version__
    VERSION = __version__
except ImportError:
    VERSION = "0.2.0"

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog="agentkit",
        description="Creative idea development toolkit for AI agents",
        epilog="Learn more at: https://github.com/yourusername/agentkit"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"AgentKit v{VERSION}"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # agentkit init command
    init_parser = subparsers.add_parser(
        "init",
        help="Initialize a new AgentKit project"
    )
    init_parser.add_argument(
        "project_name",
        nargs="?",
        default=".",
        help="Name for your project directory (or . for current directory)"
    )
    init_parser.add_argument(
        "--ai",
        choices=["claude", "copilot", "codex", "cursor", "gemini"],
        help="AI agent to configure for"
    )
    init_parser.add_argument(
        "--script",
        choices=["bash", "powershell", "ps"],
        help="Script type: bash (Linux/Mac) or powershell/ps (Windows)"
    )
    init_parser.add_argument(
        "--here",
        action="store_true",
        help="Initialize in current directory instead of creating new one"
    )
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="Force initialization even if directory is not empty"
    )

    # agentkit idea command
    idea_parser = subparsers.add_parser(
        "idea",
        help="Create a new idea workspace inside an AgentKit project"
    )
    idea_parser.add_argument(
        "name",
        help="Idea name or title"
    )
    idea_parser.add_argument(
        "--slug",
        help="Optional slug override for the idea directory name"
    )
    idea_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing idea directory if it exists"
    )
    
    # agentkit check command
    check_parser = subparsers.add_parser(
        "check",
        help="Check for installed AI agents and prerequisites"
    )

    # agentkit upgrade command (project upgrade to v0.3.0)
    upgrade_parser = subparsers.add_parser(
        "upgrade",
        help="Upgrade existing project to v0.3.0 (auto-orchestrated workflow)"
    )
    upgrade_parser.add_argument(
        "--force",
        action="store_true",
        help="Force upgrade even if already at v0.3.0"
    )
    upgrade_parser.add_argument(
        "-y", "--yes",
        action="store_true",
        help="Skip confirmation prompt"
    )

    # agentkit update command (update CLI via pip)
    update_parser = subparsers.add_parser(
        "update",
        help="Update AgentKit CLI to latest version (pip-based)"
    )
    update_parser.add_argument(
        "--source",
        default="agentkit-cli",
        help="Package or URL to install (default: agentkit-cli)"
    )
    update_parser.add_argument(
        "--use-git",
        action="store_true",
        help="Use git source https://github.com/hgreene624/AgentKit.git"
    )

    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    # Route to appropriate handler
    if args.command == "init":
        from agentkit_cli.init import init_project
        return init_project(args)
    elif args.command == "idea":
        from agentkit_cli.init import create_idea_workspace
        return create_idea_workspace(args)
    elif args.command == "check":
        from agentkit_cli.check import check_environment
        return check_environment(args)
    elif args.command == "upgrade":
        from agentkit_cli.upgrade import upgrade_project
        return upgrade_project(args)
    elif args.command == "update":
        target = args.source
        if args.use_git:
            target = "git+https://github.com/hgreene624/AgentKit.git"
        cmd = [sys.executable, "-m", "pip", "install", "--upgrade", target]
        try:
            print(f"Updating AgentKit via: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
            print("Update completed.")
            return 0
        except subprocess.CalledProcessError as exc:
            print(f"Update failed: {exc}")
            return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
