"""
Unit tests for AgentKit workflow state management (v0.3.0)
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from agentkit_cli.state import (
    WorkflowState,
    PhaseState,
    ProjectInfo,
    SessionState,
    read_state,
    write_state,
    get_or_create_state,
    detect_phase_from_documents,
    sync_state_to_documents,
    advance_phase,
    mark_phase_complete,
    PHASE_ORDER,
    PHASE_DOCUMENTS,
)


@pytest.fixture
def temp_project():
    """Create a temporary project directory for testing."""
    temp_dir = tempfile.mkdtemp()
    project_dir = Path(temp_dir)

    # Create minimal project structure
    agentkit_dir = project_dir / ".agentkit"
    agentkit_dir.mkdir(parents=True)

    yield project_dir

    # Cleanup
    shutil.rmtree(temp_dir)


class TestWorkflowState:
    """Tests for WorkflowState dataclass."""

    def test_default_state(self):
        """Test default state initialization."""
        state = WorkflowState()

        assert state.version == "0.3.0"
        assert state.current_phase == "constitution"
        assert len(state.phases) == 5
        assert all(phase in state.phases for phase in PHASE_ORDER)

    def test_phase_state_defaults(self):
        """Test PhaseState defaults."""
        phase = PhaseState()

        assert phase.status == "pending"
        assert phase.started_at is None
        assert phase.completed_at is None
        assert phase.questions_answered == 0
        assert phase.notes == []


class TestReadWriteState:
    """Tests for reading and writing state files."""

    def test_write_and_read_state(self, temp_project):
        """Test writing and reading state."""
        state = WorkflowState()
        state.project.name = "Test Project"
        state.current_phase = "specify"
        state.phases["constitution"].status = "completed"

        # Write state
        write_state(temp_project, state)

        # Verify file exists
        state_file = temp_project / ".agentkit" / "workflow-state.yaml"
        assert state_file.exists()

        # Read state back
        loaded_state = read_state(temp_project)

        assert loaded_state is not None
        assert loaded_state.project.name == "Test Project"
        assert loaded_state.current_phase == "specify"
        assert loaded_state.phases["constitution"].status == "completed"

    def test_read_nonexistent_state(self, temp_project):
        """Test reading state when file doesn't exist."""
        state = read_state(temp_project)
        assert state is None

    def test_get_or_create_state_new(self, temp_project):
        """Test get_or_create_state creates new state."""
        state = get_or_create_state(temp_project)

        assert state is not None
        assert state.version == "0.3.0"
        assert state.current_phase == "constitution"

    def test_get_or_create_state_existing(self, temp_project):
        """Test get_or_create_state loads existing state."""
        # Create initial state
        initial_state = WorkflowState()
        initial_state.project.name = "Existing Project"
        initial_state.current_phase = "plan"
        write_state(temp_project, initial_state)

        # Get state should load existing
        state = get_or_create_state(temp_project)

        assert state.project.name == "Existing Project"
        assert state.current_phase == "plan"


class TestDetectPhaseFromDocuments:
    """Tests for phase detection from documents."""

    def test_detect_no_documents(self, temp_project):
        """Test detection with no documents."""
        phase = detect_phase_from_documents(temp_project)
        assert phase == "constitution"

    def test_detect_with_constitution(self, temp_project):
        """Test detection with only constitution."""
        (temp_project / "constitution.md").write_text("# Constitution")

        phase = detect_phase_from_documents(temp_project)
        assert phase == "specify"

    def test_detect_with_spec(self, temp_project):
        """Test detection with constitution and spec."""
        (temp_project / "constitution.md").write_text("# Constitution")
        (temp_project / "spec.md").write_text("# Spec")

        phase = detect_phase_from_documents(temp_project)
        assert phase == "plan"

    def test_detect_with_plan(self, temp_project):
        """Test detection with constitution, spec, and plan."""
        (temp_project / "constitution.md").write_text("# Constitution")
        (temp_project / "spec.md").write_text("# Spec")
        (temp_project / "plan.md").write_text("# Plan")

        phase = detect_phase_from_documents(temp_project)
        assert phase == "task"

    def test_detect_with_tasks(self, temp_project):
        """Test detection with all planning documents."""
        (temp_project / "constitution.md").write_text("# Constitution")
        (temp_project / "spec.md").write_text("# Spec")
        (temp_project / "plan.md").write_text("# Plan")
        (temp_project / "tasks.md").write_text("# Tasks")

        phase = detect_phase_from_documents(temp_project)
        assert phase == "implement"


class TestSyncStateToDocuments:
    """Tests for state synchronization."""

    def test_sync_state_ahead_of_documents(self, temp_project):
        """Test syncing when state is ahead of documents."""
        # State says we're in plan phase
        state = WorkflowState()
        state.current_phase = "plan"
        state.phases["constitution"].status = "completed"
        state.phases["specify"].status = "completed"

        # But only constitution exists
        (temp_project / "constitution.md").write_text("# Constitution")

        # Sync should correct state
        synced = sync_state_to_documents(temp_project, state)

        assert synced.current_phase == "specify"
        assert synced.phases["specify"].status == "in_progress"

    def test_sync_documents_ahead_of_state(self, temp_project):
        """Test syncing when documents are ahead of state."""
        # State says we're still in constitution
        state = WorkflowState()
        state.current_phase = "constitution"

        # But spec and plan exist too
        (temp_project / "constitution.md").write_text("# Constitution")
        (temp_project / "spec.md").write_text("# Spec")
        (temp_project / "plan.md").write_text("# Plan")

        # Sync should advance state
        synced = sync_state_to_documents(temp_project, state)

        assert synced.current_phase == "task"
        assert synced.phases["constitution"].status == "completed"
        assert synced.phases["specify"].status == "completed"
        assert synced.phases["plan"].status == "completed"


class TestPhaseAdvancement:
    """Tests for phase advancement functions."""

    def test_advance_phase_basic(self, temp_project):
        """Test basic phase advancement."""
        state = WorkflowState()
        state.current_phase = "constitution"

        advanced = advance_phase(state)

        assert advanced.current_phase == "specify"
        assert advanced.phases["constitution"].status == "completed"
        assert advanced.phases["constitution"].completed_at is not None
        assert advanced.phases["specify"].status == "in_progress"
        assert advanced.phases["specify"].started_at is not None

    def test_advance_phase_at_end(self, temp_project):
        """Test advancing from last phase."""
        state = WorkflowState()
        state.current_phase = "implement"

        advanced = advance_phase(state)

        # Should stay at implement
        assert advanced.current_phase == "implement"

    def test_mark_phase_complete(self, temp_project):
        """Test marking specific phase complete."""
        state = WorkflowState()

        updated = mark_phase_complete(state, "constitution")

        assert updated.phases["constitution"].status == "completed"
        assert updated.phases["constitution"].completed_at is not None


class TestPhaseConstants:
    """Tests for phase order and document mappings."""

    def test_phase_order(self):
        """Test phase order is correct."""
        assert PHASE_ORDER == ["constitution", "specify", "plan", "task", "implement"]

    def test_phase_documents(self):
        """Test phase document mappings."""
        assert PHASE_DOCUMENTS["constitution"] == "constitution.md"
        assert PHASE_DOCUMENTS["specify"] == "spec.md"
        assert PHASE_DOCUMENTS["plan"] == "plan.md"
        assert PHASE_DOCUMENTS["task"] == "tasks.md"
        assert PHASE_DOCUMENTS["implement"] is None  # No document for implement


class TestSessionState:
    """Tests for session state tracking."""

    def test_session_state_persistence(self, temp_project):
        """Test that session state persists across reads/writes."""
        state = WorkflowState()
        state.session.docs_read = ["constitution", "spec"]
        state.session.last_question_batch = 3
        state.session.context_summary = "User wants a pottery studio"

        write_state(temp_project, state)
        loaded = read_state(temp_project)

        assert loaded.session.docs_read == ["constitution", "spec"]
        assert loaded.session.last_question_batch == 3
        assert loaded.session.context_summary == "User wants a pottery studio"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
