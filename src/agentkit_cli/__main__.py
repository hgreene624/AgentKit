#!/usr/bin/env python3
"""
AgentKit CLI - Creative Idea Development with AI Agents

A toolkit for transforming fuzzy ideas into concrete realities through
structured workflows with AI agents.
"""

import sys
import argparse
from pathlib import Path

# Import version from package
try:
    from agentkit_cli import __version__
    VERSION = __version__
except ImportError:
    VERSION = "0.1.0"

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
        choices=["claude", "copilot", "cursor", "gemini"],
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
    
    # agentkit check command
    check_parser = subparsers.add_parser(
        "check",
        help="Check for installed AI agents and prerequisites"
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
    elif args.command == "check":
        from agentkit_cli.check import check_environment
        return check_environment(args)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
