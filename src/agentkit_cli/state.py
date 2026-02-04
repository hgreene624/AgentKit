"""
AgentKit workflow state management module.

Handles reading, writing, and detecting workflow state for auto-orchestrated projects.
"""

import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field, asdict

try:
    import yaml
except ImportError:
    # Fallback for environments without PyYAML
    yaml = None


# Phase order for workflow progression
PHASE_ORDER = ["constitution", "specify", "plan", "task", "implement"]

# Document files that indicate phase completion
PHASE_DOCUMENTS = {
    "constitution": "constitution.md",
    "specify": "spec.md",
    "plan": "plan.md",
    "task": "tasks.md",
    "implement": None,  # Implement phase has no single document
}


@dataclass
class PhaseState:
    """State of a single workflow phase."""
    status: str = "pending"  # pending | in_progress | completed
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    questions_total: int = 0
    questions_answered: int = 0
    last_batch: int = 0
    tasks_total: int = 0
    tasks_completed: int = 0
    notes: List[str] = field(default_factory=list)


@dataclass
class SessionState:
    """Current session tracking."""
    last_active: Optional[str] = None
    docs_read: List[str] = field(default_factory=list)
    last_question_batch: int = 0
    context_summary: Optional[str] = None


@dataclass
class ProjectInfo:
    """Project metadata."""
    name: str = ""
    created: Optional[str] = None
    domain: Optional[str] = None


@dataclass
class WorkflowState:
    """Complete workflow state for an AgentKit project."""
    version: str = "0.3.0"
    project: ProjectInfo = field(default_factory=ProjectInfo)
    current_phase: str = "constitution"
    session: SessionState = field(default_factory=SessionState)
    phases: Dict[str, PhaseState] = field(default_factory=lambda: {
        phase: PhaseState() for phase in PHASE_ORDER
    })

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary for YAML serialization."""
        return {
            "version": self.version,
            "project": {
                "name": self.project.name,
                "created": self.project.created,
                "domain": self.project.domain,
            },
            "current_phase": self.current_phase,
            "session": {
                "last_active": self.session.last_active,
                "docs_read": self.session.docs_read,
                "last_question_batch": self.session.last_question_batch,
                "context_summary": self.session.context_summary,
            },
            "phases": {
                name: {
                    "status": phase.status,
                    "started_at": phase.started_at,
                    "completed_at": phase.completed_at,
                    "questions_total": phase.questions_total,
                    "questions_answered": phase.questions_answered,
                    "last_batch": phase.last_batch,
                    "tasks_total": phase.tasks_total,
                    "tasks_completed": phase.tasks_completed,
                    "notes": phase.notes,
                }
                for name, phase in self.phases.items()
            },
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowState":
        """Create WorkflowState from dictionary."""
        state = cls()

        if "version" in data:
            state.version = data["version"]

        if "project" in data:
            proj = data["project"]
            state.project = ProjectInfo(
                name=proj.get("name", ""),
                created=proj.get("created"),
                domain=proj.get("domain"),
            )

        if "current_phase" in data:
            state.current_phase = data["current_phase"]

        if "session" in data:
            sess = data["session"]
            state.session = SessionState(
                last_active=sess.get("last_active"),
                docs_read=sess.get("docs_read", []),
                last_question_batch=sess.get("last_question_batch", 0),
                context_summary=sess.get("context_summary"),
            )

        if "phases" in data:
            for name, phase_data in data["phases"].items():
                if name in state.phases:
                    state.phases[name] = PhaseState(
                        status=phase_data.get("status", "pending"),
                        started_at=phase_data.get("started_at"),
                        completed_at=phase_data.get("completed_at"),
                        questions_total=phase_data.get("questions_total", 0),
                        questions_answered=phase_data.get("questions_answered", 0),
                        last_batch=phase_data.get("last_batch", 0),
                        tasks_total=phase_data.get("tasks_total", 0),
                        tasks_completed=phase_data.get("tasks_completed", 0),
                        notes=phase_data.get("notes", []),
                    )

        return state


def get_state_file_path(project_path: Path) -> Path:
    """Get the path to the workflow state file."""
    return project_path / ".agentkit" / "workflow-state.yaml"


def read_state(project_path: Path) -> Optional[WorkflowState]:
    """
    Read workflow state from file.

    Returns None if file doesn't exist, WorkflowState otherwise.
    Returns default WorkflowState on parse errors.
    """
    state_file = get_state_file_path(project_path)

    if not state_file.exists():
        return None

    try:
        if yaml is None:
            # Fallback: simple YAML parsing for basic structure
            return _read_state_fallback(state_file)

        with open(state_file, "r") as f:
            data = yaml.safe_load(f)

        if data is None:
            return WorkflowState()

        return WorkflowState.from_dict(data)

    except Exception:
        # Return default state on any error
        return WorkflowState()


def _read_state_fallback(state_file: Path) -> WorkflowState:
    """Fallback state reading without PyYAML."""
    # Simple parsing for basic fields
    state = WorkflowState()
    try:
        content = state_file.read_text()
        for line in content.split("\n"):
            if "current_phase:" in line:
                phase = line.split(":", 1)[1].strip()
                if phase in PHASE_ORDER:
                    state.current_phase = phase
            elif "name:" in line and "project" in content[:content.index(line)]:
                state.project.name = line.split(":", 1)[1].strip().strip('"')
    except Exception:
        pass
    return state


def write_state(project_path: Path, state: WorkflowState) -> bool:
    """
    Write workflow state to file.

    Returns True on success, False on failure.
    """
    state_file = get_state_file_path(project_path)

    # Ensure .agentkit directory exists
    state_file.parent.mkdir(parents=True, exist_ok=True)

    # Update last_active timestamp
    state.session.last_active = datetime.now().isoformat()

    try:
        if yaml is None:
            return _write_state_fallback(state_file, state)

        with open(state_file, "w") as f:
            yaml.dump(state.to_dict(), f, default_flow_style=False, sort_keys=False)

        return True

    except Exception:
        return False


def _write_state_fallback(state_file: Path, state: WorkflowState) -> bool:
    """Fallback state writing without PyYAML."""
    try:
        lines = [
            f'version: "{state.version}"',
            "project:",
            f'  name: "{state.project.name}"',
            f"  created: {state.project.created or 'null'}",
            f"  domain: {state.project.domain or 'null'}",
            f"current_phase: {state.current_phase}",
            "session:",
            f"  last_active: {state.session.last_active or 'null'}",
            f"  docs_read: {state.session.docs_read}",
            "phases:",
        ]

        for name in PHASE_ORDER:
            phase = state.phases[name]
            lines.append(f"  {name}:")
            lines.append(f"    status: {phase.status}")
            if phase.completed_at:
                lines.append(f"    completed_at: {phase.completed_at}")

        state_file.write_text("\n".join(lines) + "\n")
        return True

    except Exception:
        return False


def detect_phase_from_documents(project_path: Path) -> str:
    """
    Detect current workflow phase based on which documents exist.

    This is the fallback/self-healing mechanism when state file
    is missing or inconsistent.
    """
    # Check documents in reverse order (most advanced first)
    for phase in reversed(PHASE_ORDER[:-1]):  # Exclude implement
        doc_name = PHASE_DOCUMENTS.get(phase)
        if doc_name and (project_path / doc_name).exists():
            # This phase is complete, so we're on the next one
            phase_idx = PHASE_ORDER.index(phase)
            if phase_idx + 1 < len(PHASE_ORDER):
                return PHASE_ORDER[phase_idx + 1]
            return "implement"

    # No documents found, start from beginning
    return "constitution"


def sync_state_to_documents(project_path: Path, state: WorkflowState) -> WorkflowState:
    """
    Self-healing: sync workflow state to match actual documents.

    Trust documents over state file:
    - If documents exist that the state doesn't reflect, advance state
    - If state claims to be ahead but documents don't exist, roll back state
    """
    detected_phase = detect_phase_from_documents(project_path)
    detected_idx = PHASE_ORDER.index(detected_phase)
    current_idx = PHASE_ORDER.index(state.current_phase)

    # Always sync state to match detected phase from documents
    if detected_idx != current_idx:
        state.current_phase = detected_phase

        # Mark phases before detected as completed
        for i in range(detected_idx):
            phase_name = PHASE_ORDER[i]
            if state.phases[phase_name].status != "completed":
                state.phases[phase_name].status = "completed"
                if not state.phases[phase_name].completed_at:
                    state.phases[phase_name].completed_at = datetime.now().isoformat()

        # Mark current phase as in_progress
        state.phases[detected_phase].status = "in_progress"

        # If rolling back, reset phases that are no longer complete
        if detected_idx < current_idx:
            for i in range(detected_idx, len(PHASE_ORDER)):
                phase_name = PHASE_ORDER[i]
                if i > detected_idx:
                    state.phases[phase_name].status = "pending"
                    state.phases[phase_name].completed_at = None

    return state


def update_phase_status(
    project_path: Path,
    phase: str,
    status: str,
    **kwargs
) -> bool:
    """
    Update the status of a specific phase.

    Additional kwargs can include:
    - questions_total, questions_answered, last_batch (for specify/plan)
    - tasks_total, tasks_completed (for implement)
    """
    state = read_state(project_path)

    if phase not in state.phases:
        return False

    state.phases[phase].status = status

    # Update additional fields
    for key, value in kwargs.items():
        if hasattr(state.phases[phase], key):
            setattr(state.phases[phase], key, value)

    # If completing a phase, record timestamp and advance
    if status == "completed":
        state.phases[phase].completed_at = datetime.now().isoformat()

        # Advance to next phase
        phase_idx = PHASE_ORDER.index(phase)
        if phase_idx + 1 < len(PHASE_ORDER):
            state.current_phase = PHASE_ORDER[phase_idx + 1]
            state.phases[state.current_phase].status = "in_progress"

    return write_state(project_path, state)


def mark_doc_read(project_path: Path, doc_name: str) -> bool:
    """Mark a document as read in the current session."""
    state = read_state(project_path)

    if doc_name not in state.session.docs_read:
        state.session.docs_read.append(doc_name)

    return write_state(project_path, state)


def get_phase_progress(state: WorkflowState) -> Dict[str, Any]:
    """Get a summary of workflow progress."""
    completed = sum(1 for p in state.phases.values() if p.status == "completed")
    total = len(PHASE_ORDER)

    current = state.phases.get(state.current_phase, PhaseState())

    return {
        "current_phase": state.current_phase,
        "phases_completed": completed,
        "phases_total": total,
        "current_status": current.status,
        "questions_progress": f"{current.questions_answered}/{current.questions_total}"
            if current.questions_total > 0 else None,
        "tasks_progress": f"{current.tasks_completed}/{current.tasks_total}"
            if current.tasks_total > 0 else None,
    }


def create_initial_state(project_path: Path, project_name: str, domain: Optional[str] = None) -> WorkflowState:
    """Create and save initial workflow state for a new project."""
    state = WorkflowState()
    state.project.name = project_name
    state.project.created = datetime.now().isoformat()
    state.project.domain = domain
    state.current_phase = "constitution"
    state.phases["constitution"].status = "in_progress"

    write_state(project_path, state)
    return state


def get_or_create_state(project_path: Path) -> WorkflowState:
    """
    Get existing state or create a new one.

    Returns existing state if workflow-state.yaml exists,
    otherwise creates and returns a new default state.
    """
    state_file = get_state_file_path(project_path)

    if state_file.exists():
        return read_state(project_path)

    # Create new default state
    state = WorkflowState()
    state.project.name = project_path.name
    state.project.created = datetime.now().isoformat()
    return state


def advance_phase(state: WorkflowState) -> WorkflowState:
    """
    Advance to the next phase in the workflow.

    Marks current phase as completed and moves to the next one.
    Returns the updated state (does not write to disk).
    """
    current_idx = PHASE_ORDER.index(state.current_phase)

    # Mark current phase as completed
    state.phases[state.current_phase].status = "completed"
    state.phases[state.current_phase].completed_at = datetime.now().isoformat()

    # Advance to next phase if not at end
    if current_idx + 1 < len(PHASE_ORDER):
        next_phase = PHASE_ORDER[current_idx + 1]
        state.current_phase = next_phase
        state.phases[next_phase].status = "in_progress"
        state.phases[next_phase].started_at = datetime.now().isoformat()

    return state


def mark_phase_complete(state: WorkflowState, phase: str) -> WorkflowState:
    """
    Mark a specific phase as complete.

    Returns the updated state (does not write to disk).
    """
    if phase in state.phases:
        state.phases[phase].status = "completed"
        state.phases[phase].completed_at = datetime.now().isoformat()

    return state
