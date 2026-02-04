"""
Integration tests for AgentKit v0.3.0 init and upgrade workflows.
"""

import pytest
import tempfile
import shutil
import os
from pathlib import Path
from argparse import Namespace

from agentkit_cli.init import (
    init_project,
    install_phase_instructions,
    create_workflow_state,
    install_minimal_agents_md,
)
from agentkit_cli.upgrade import (
    upgrade_project,
    check_version,
    infer_state_from_documents,
    backup_and_update_agents_md,
)
from agentkit_cli.state import read_state, PHASE_ORDER


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp = tempfile.mkdtemp()
    yield Path(temp)
    shutil.rmtree(temp)


@pytest.fixture
def temp_project_dir(temp_dir):
    """Create a temporary directory and change to it."""
    original_dir = os.getcwd()
    os.chdir(temp_dir)
    yield temp_dir
    os.chdir(original_dir)


class TestInitV030:
    """Tests for v0.3.0 project initialization."""

    def test_init_creates_phases_directory(self, temp_project_dir):
        """Test that init creates .agentkit/phases/ directory."""
        args = Namespace(
            project_name=".",
            ai="claude",
            script="bash",  # Provide script to avoid interactive prompt
            here=True,
            force=True,
        )

        result = init_project(args)

        phases_dir = temp_project_dir / ".agentkit" / "phases"
        assert phases_dir.exists()
        assert phases_dir.is_dir()

    def test_init_creates_phase_files(self, temp_project_dir):
        """Test that init creates all phase instruction files."""
        args = Namespace(
            project_name=".",
            ai="claude",
            script="bash",  # Provide script to avoid interactive prompt
            here=True,
            force=True,
        )

        init_project(args)

        phases_dir = temp_project_dir / ".agentkit" / "phases"
        expected_files = [
            "constitution.md",
            "specify.md",
            "plan.md",
            "task.md",
            "implement.md",
        ]

        for filename in expected_files:
            assert (phases_dir / filename).exists(), f"Missing {filename}"

    def test_init_creates_workflow_state(self, temp_project_dir):
        """Test that init creates workflow-state.yaml."""
        args = Namespace(
            project_name=".",
            ai="claude",
            script="bash",  # Provide script to avoid interactive prompt
            here=True,
            force=True,
        )

        init_project(args)

        state_file = temp_project_dir / ".agentkit" / "workflow-state.yaml"
        assert state_file.exists()

        state = read_state(temp_project_dir)
        assert state is not None
        assert state.version == "0.3.0"
        assert state.current_phase == "constitution"

    def test_init_creates_minimal_agents_md(self, temp_project_dir):
        """Test that init creates minimal AGENTS.md."""
        args = Namespace(
            project_name=".",
            ai="claude",
            script="bash",  # Provide script to avoid interactive prompt
            here=True,
            force=True,
        )

        init_project(args)

        agents_md = temp_project_dir / "AGENTS.md"
        assert agents_md.exists()

        content = agents_md.read_text()
        assert "auto-orchestrated workflow" in content
        assert ".agentkit/phases/" in content

    def test_init_creates_new_commands(self, temp_project_dir):
        """Test that init creates new v0.3.0 commands."""
        args = Namespace(
            project_name=".",
            ai="claude",
            script="bash",  # Provide script to avoid interactive prompt
            here=True,
            force=True,
        )

        init_project(args)

        commands_dir = temp_project_dir / ".claude" / "commands"
        expected_commands = ["start.md", "status.md", "skip.md"]

        for cmd in expected_commands:
            assert (commands_dir / cmd).exists(), f"Missing command {cmd}"


class TestUpgradeV030:
    """Tests for upgrading v0.2.0 projects to v0.3.0."""

    def create_v020_project(self, project_dir):
        """Create a minimal v0.2.0 project structure."""
        # Create .agentkit directory (v0.2.0 style)
        agentkit_dir = project_dir / ".agentkit"
        agentkit_dir.mkdir(parents=True)

        # Create memory directory (required for is_agentkit_project)
        memory_dir = agentkit_dir / "memory"
        memory_dir.mkdir()

        # Create config file
        config_file = agentkit_dir / "config.yaml"
        config_file.write_text("ai_agent: claude\nproject_version: 0.2.0\n")

        # Create old-style AGENTS.md
        agents_md = project_dir / "AGENTS.md"
        agents_md.write_text("""# AgentKit Agent Instructions

This is the v0.2.0 AGENTS.md with lots of content...

## /constitution
...detailed instructions...

## /specify
...detailed instructions...
""")

        # Create commands directory
        commands_dir = project_dir / ".claude" / "commands"
        commands_dir.mkdir(parents=True)

        return project_dir

    def test_check_version_v020(self, temp_dir):
        """Test version detection for v0.2.0 project."""
        self.create_v020_project(temp_dir)

        version, needs_upgrade = check_version(temp_dir)

        assert version == "0.2.0"
        assert needs_upgrade is True

    def test_check_version_v030(self, temp_dir):
        """Test version detection for already upgraded project."""
        self.create_v020_project(temp_dir)

        # Add v0.3.0 markers
        phases_dir = temp_dir / ".agentkit" / "phases"
        phases_dir.mkdir()
        (phases_dir / "constitution.md").write_text("# Phase")

        version, needs_upgrade = check_version(temp_dir)

        assert version == "0.3.0"
        assert needs_upgrade is False

    def test_infer_state_from_no_documents(self, temp_dir):
        """Test state inference with no documents."""
        self.create_v020_project(temp_dir)

        state = infer_state_from_documents(temp_dir)

        assert state.current_phase == "constitution"
        assert state.phases["constitution"].status == "in_progress"

    def test_infer_state_from_existing_documents(self, temp_dir):
        """Test state inference with existing documents."""
        self.create_v020_project(temp_dir)

        # Create some workflow documents
        (temp_dir / "constitution.md").write_text("# Constitution")
        (temp_dir / "spec.md").write_text("# Spec")

        state = infer_state_from_documents(temp_dir)

        assert state.current_phase == "plan"
        assert state.phases["constitution"].status == "completed"
        assert state.phases["specify"].status == "completed"
        assert state.phases["plan"].status == "in_progress"

    def test_backup_agents_md(self, temp_dir):
        """Test that upgrade backs up AGENTS.md."""
        self.create_v020_project(temp_dir)
        original_content = (temp_dir / "AGENTS.md").read_text()

        backup_and_update_agents_md(temp_dir)

        # Check backup exists
        backup = temp_dir / "AGENTS.md.backup"
        assert backup.exists()
        assert backup.read_text() == original_content

        # Check new AGENTS.md is minimal
        new_content = (temp_dir / "AGENTS.md").read_text()
        assert "auto-orchestrated workflow" in new_content

    def test_full_upgrade(self, temp_project_dir):
        """Test full upgrade from v0.2.0 to v0.3.0."""
        self.create_v020_project(temp_project_dir)

        # Create some existing documents
        (temp_project_dir / "constitution.md").write_text("# My Constitution")

        args = Namespace(force=False, yes=True)
        result = upgrade_project(args)

        assert result == 0

        # Check phases directory created
        phases_dir = temp_project_dir / ".agentkit" / "phases"
        assert phases_dir.exists()
        assert (phases_dir / "constitution.md").exists()

        # Check state file created
        state = read_state(temp_project_dir)
        assert state is not None
        assert state.version == "0.3.0"
        assert state.current_phase == "specify"  # After constitution

        # Check AGENTS.md updated
        agents_md = temp_project_dir / "AGENTS.md"
        assert "auto-orchestrated workflow" in agents_md.read_text()

        # Check backup created
        assert (temp_project_dir / "AGENTS.md.backup").exists()


class TestPhaseInstructions:
    """Tests for phase instruction file installation."""

    def test_install_phase_instructions(self, temp_dir):
        """Test installing phase instruction files."""
        agentkit_dir = temp_dir / ".agentkit"
        agentkit_dir.mkdir()

        install_phase_instructions(temp_dir)

        phases_dir = agentkit_dir / "phases"
        assert phases_dir.exists()

        for phase in PHASE_ORDER:
            phase_file = phases_dir / f"{phase}.md"
            assert phase_file.exists(), f"Missing {phase}.md"

            content = phase_file.read_text()
            assert len(content) > 100  # Should have substantial content

    def test_phase_files_not_overwritten(self, temp_dir):
        """Test that existing phase files are not overwritten."""
        agentkit_dir = temp_dir / ".agentkit"
        phases_dir = agentkit_dir / "phases"
        phases_dir.mkdir(parents=True)

        # Create custom phase file
        custom_content = "# My Custom Phase Instructions"
        (phases_dir / "constitution.md").write_text(custom_content)

        install_phase_instructions(temp_dir)

        # Custom file should be preserved
        assert (phases_dir / "constitution.md").read_text() == custom_content


class TestWorkflowStateCreation:
    """Tests for workflow state file creation."""

    def test_create_workflow_state(self, temp_dir):
        """Test creating initial workflow state."""
        agentkit_dir = temp_dir / ".agentkit"
        agentkit_dir.mkdir()

        create_workflow_state(temp_dir, "My Project")

        state = read_state(temp_dir)
        assert state is not None
        assert state.project.name == "My Project"
        assert state.current_phase == "constitution"
        # Constitution starts as in_progress since it's the active phase
        assert state.phases["constitution"].status == "in_progress"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
