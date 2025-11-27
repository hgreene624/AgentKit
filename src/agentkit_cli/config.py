"""
AgentKit configuration module - handles configuration and paths
"""

from pathlib import Path
from typing import Optional, Dict, Any
import json

# Package metadata
VERSION = "0.2.0"
PACKAGE_NAME = "agentkit-cli"

# Default paths
DEFAULT_AGENTKIT_DIR = ".agentkit"
DEFAULT_MEMORY_DIR = "memory"
DEFAULT_IDEAS_DIR = "ideas"
DEFAULT_TEMPLATES_DIR = "templates"
DEFAULT_SCRIPTS_DIR = "scripts"

# Agent configurations
AGENT_CONFIG = {
    "claude": {
        "name": "Claude Code",
        "command_dir": ".claude/commands",
        "file_extension": ".md",
        "check_command": "claude --version",
        "docs_url": "https://www.anthropic.com/claude-code"
    },
    "copilot": {
        "name": "GitHub Copilot",
        "command_dir": ".github/prompts",
        "file_extension": ".md",
        "check_command": "code --version",
        "docs_url": "https://github.com/features/copilot"
    },
    "cursor": {
        "name": "Cursor",
        "command_dir": ".cursor/commands",
        "file_extension": ".md",
        "check_command": "cursor --version",
        "docs_url": "https://cursor.sh"
    },
    "gemini": {
        "name": "Gemini CLI",
        "command_dir": ".gemini/commands",
        "file_extension": ".md",
        "check_command": "gemini --version",
        "docs_url": "https://github.com/google-gemini/gemini-cli"
    }
}

# Script configurations
SCRIPT_CONFIG = {
    "bash": {
        "name": "Bash (Linux/Mac)",
        "extension": ".sh",
        "shebang": "#!/usr/bin/env bash",
        "comment": "#"
    },
    "powershell": {
        "name": "PowerShell",
        "extension": ".ps1",
        "shebang": "# PowerShell script",
        "comment": "#"
    }
}


class AgentKitConfig:
    """Configuration manager for AgentKit projects"""
    
    def __init__(self, project_dir: Optional[Path] = None):
        """
        Initialize configuration
        
        Args:
            project_dir: Project directory (defaults to current directory)
        """
        self.project_dir = project_dir or Path.cwd()
        self.agentkit_dir = self.project_dir / DEFAULT_AGENTKIT_DIR
        self.config_file = self.agentkit_dir / "config.json"
        self._config: Dict[str, Any] = {}
        
        if self.config_file.exists():
            self.load()
    
    def load(self):
        """Load configuration from file"""
        try:
            with open(self.config_file, 'r') as f:
                self._config = json.load(f)
        except Exception as e:
            # If config doesn't exist or is invalid, start fresh
            self._config = {}
    
    def save(self):
        """Save configuration to file"""
        self.agentkit_dir.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, 'w') as f:
            json.dump(self._config, f, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        self._config[key] = value
    
    @property
    def ai_agent(self) -> Optional[str]:
        """Get configured AI agent"""
        return self.get("ai_agent")
    
    @ai_agent.setter
    def ai_agent(self, value: str):
        """Set AI agent"""
        if value not in AGENT_CONFIG:
            raise ValueError(f"Unknown AI agent: {value}")
        self.set("ai_agent", value)
    
    @property
    def script_type(self) -> Optional[str]:
        """Get configured script type"""
        return self.get("script_type")
    
    @script_type.setter
    def script_type(self, value: str):
        """Set script type"""
        if value not in SCRIPT_CONFIG:
            raise ValueError(f"Unknown script type: {value}")
        self.set("script_type", value)
    
    def is_initialized(self) -> bool:
        """Check if project is initialized"""
        return self.agentkit_dir.exists() and \
               (self.agentkit_dir / DEFAULT_MEMORY_DIR).exists()
    
    def get_ideas_dir(self) -> Path:
        """Get ideas directory path"""
        return self.agentkit_dir / DEFAULT_IDEAS_DIR
    
    def get_templates_dir(self) -> Path:
        """Get templates directory path"""
        return self.agentkit_dir / DEFAULT_TEMPLATES_DIR
    
    def get_scripts_dir(self) -> Path:
        """Get scripts directory path"""
        script_type = self.script_type or "bash"
        return self.agentkit_dir / DEFAULT_SCRIPTS_DIR / script_type
    
    def get_command_dir(self) -> Path:
        """Get command directory path for configured AI agent"""
        agent = self.ai_agent
        if not agent or agent not in AGENT_CONFIG:
            raise ValueError("AI agent not configured")
        return self.project_dir / AGENT_CONFIG[agent]["command_dir"]
    
    def list_ideas(self) -> list[Path]:
        """List all idea directories"""
        ideas_dir = self.get_ideas_dir()
        if not ideas_dir.exists():
            return []
        return sorted([d for d in ideas_dir.iterdir() if d.is_dir()])
    
    def get_next_idea_number(self) -> str:
        """Get the next idea number"""
        ideas = self.list_ideas()
        if not ideas:
            return "001"
        
        # Extract numbers from existing ideas
        max_num = 0
        for idea_dir in ideas:
            name = idea_dir.name
            if name[:3].isdigit():
                num = int(name[:3])
                if num > max_num:
                    max_num = num
        
        return f"{max_num + 1:03d}"
    
    def create_idea_slug(self, name: str) -> str:
        """
        Create a URL-friendly slug from idea name
        
        Args:
            name: Idea name
            
        Returns:
            Slug string (e.g., "n8n-text-automation")
        """
        import re
        
        # Convert to lowercase
        slug = name.lower()
        
        # Replace spaces and special chars with hyphens
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        
        # Remove leading/trailing hyphens
        slug = slug.strip('-')
        
        # Limit length and word count
        words = slug.split('-')[:4]  # Max 4 words
        slug = '-'.join(words)[:50]  # Max 50 chars
        
        return slug
    
    def get_agent_config(self, agent: Optional[str] = None) -> Dict[str, Any]:
        """
        Get configuration for an AI agent
        
        Args:
            agent: Agent name (uses configured agent if None)
            
        Returns:
            Agent configuration dict
        """
        agent = agent or self.ai_agent
        if not agent or agent not in AGENT_CONFIG:
            raise ValueError(f"Unknown AI agent: {agent}")
        return AGENT_CONFIG[agent]
    
    def get_script_config(self, script_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get configuration for a script type
        
        Args:
            script_type: Script type (uses configured type if None)
            
        Returns:
            Script configuration dict
        """
        script_type = script_type or self.script_type
        if not script_type or script_type not in SCRIPT_CONFIG:
            raise ValueError(f"Unknown script type: {script_type}")
        return SCRIPT_CONFIG[script_type]


class ProjectPaths:
    """Helper class for managing project paths"""
    
    def __init__(self, project_dir: Path):
        self.project = project_dir
        self.agentkit = project_dir / DEFAULT_AGENTKIT_DIR
        self.memory = self.agentkit / DEFAULT_MEMORY_DIR
        self.ideas = self.agentkit / DEFAULT_IDEAS_DIR
        self.templates = self.agentkit / DEFAULT_TEMPLATES_DIR
        self.scripts = self.agentkit / DEFAULT_SCRIPTS_DIR
        
    def idea_dir(self, idea_name: str) -> Path:
        """Get path to specific idea directory"""
        return self.ideas / idea_name
    
    def idea_spec(self, idea_name: str) -> Path:
        """Get path to idea specification"""
        return self.idea_dir(idea_name) / "spec.md"
    
    def idea_plan(self, idea_name: str) -> Path:
        """Get path to idea plan"""
        return self.idea_dir(idea_name) / "plan.md"
    
    def idea_tasks(self, idea_name: str) -> Path:
        """Get path to idea tasks"""
        return self.idea_dir(idea_name) / "tasks.md"
    
    def idea_outputs(self, idea_name: str) -> Path:
        """Get path to idea outputs directory"""
        return self.idea_dir(idea_name) / "outputs"
    
    def constitution(self) -> Path:
        """Get path to constitution file"""
        return self.memory / "constitution.md"


def get_package_data_dir() -> Path:
    """
    Get the package data directory containing templates
    
    Returns:
        Path to package data directory
    """
    # This would point to the installed package data
    # For development, might point to source tree
    import agentkit_cli
    package_dir = Path(agentkit_cli.__file__).parent
    return package_dir / "data"


def ensure_directory(path: Path) -> Path:
    """
    Ensure directory exists, create if necessary
    
    Args:
        path: Directory path
        
    Returns:
        The path (for chaining)
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def is_agentkit_project(directory: Optional[Path] = None) -> bool:
    """
    Check if directory is an AgentKit project
    
    Args:
        directory: Directory to check (defaults to current)
        
    Returns:
        True if directory contains .agentkit structure
    """
    directory = directory or Path.cwd()
    agentkit_dir = directory / DEFAULT_AGENTKIT_DIR
    return agentkit_dir.exists() and \
           (agentkit_dir / DEFAULT_MEMORY_DIR).exists()


def find_agentkit_root(start_dir: Optional[Path] = None) -> Optional[Path]:
    """
    Find AgentKit project root by walking up directory tree
    
    Args:
        start_dir: Starting directory (defaults to current)
        
    Returns:
        Path to project root or None if not found
    """
    current = start_dir or Path.cwd()
    
    # Walk up to root
    for parent in [current] + list(current.parents):
        if is_agentkit_project(parent):
            return parent
    
    return None
