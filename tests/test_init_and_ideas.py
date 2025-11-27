from types import SimpleNamespace
from pathlib import Path

from agentkit_cli.init import init_project, create_idea_workspace
from agentkit_cli.config import AgentKitConfig
from agentkit_cli.check import check_version


def test_init_creates_structure_and_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    args = SimpleNamespace(
        ai="claude",
        script="bash",
        project_name=".",
        here=True,
        force=True,
    )

    result = init_project(args)
    assert result == 0

    agentkit_dir = tmp_path / ".agentkit"
    assert (agentkit_dir / "memory").is_dir()
    assert (agentkit_dir / "ideas").is_dir()
    assert (agentkit_dir / "templates" / "specification-template.md").is_file()
    assert (agentkit_dir / "templates" / "plan-template.md").is_file()
    assert (agentkit_dir / "templates" / "tasks-template.md").is_file()
    assert (agentkit_dir / "templates" / "research-template.md").is_file()
    assert (agentkit_dir / "templates" / "asset-map-template.md").is_file()
    assert (agentkit_dir / "templates" / "quickstart-template.md").is_file()
    assert (agentkit_dir / "templates" / "checklist-template.md").is_file()
    assert (agentkit_dir / "templates" / "constitution-template.md").is_file()

    config = AgentKitConfig(tmp_path)
    assert config.ai_agent == "claude"
    assert config.script_type == "bash"


def test_create_idea_workspace_numbers_and_slugs(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    init_args = SimpleNamespace(
        ai="claude",
        script="bash",
        project_name=".",
        here=True,
        force=True,
    )
    assert init_project(init_args) == 0

    create_args = SimpleNamespace(name="My First Idea", slug=None, force=False)
    assert create_idea_workspace(create_args) == 0

    first_dir = tmp_path / ".agentkit" / "ideas" / "001-my-first-idea"
    assert first_dir.is_dir()
    assert (first_dir / "spec.md").is_file()
    assert (first_dir / "plan.md").is_file()
    assert (first_dir / "tasks.md").is_file()
    assert (first_dir / "research.md").is_file()
    assert (first_dir / "asset-map.md").is_file()
    assert (first_dir / "quickstart.md").is_file()
    assert (first_dir / "checklists" / "requirements.md").is_file()
    assert (first_dir / "briefs").is_dir()

    second_args = SimpleNamespace(name="Second Idea", slug="custom", force=False)
    assert create_idea_workspace(second_args) == 0
    assert (tmp_path / ".agentkit" / "ideas" / "002-custom").is_dir()


def test_create_idea_workspace_fails_without_project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    create_args = SimpleNamespace(name="Orphan Idea", slug=None, force=False)
    result = create_idea_workspace(create_args)
    assert result == 1


def test_check_version_comparisons():
    assert check_version("Python 3.11.1", "3.11") is True
    assert check_version("Python 3.10.9", "3.11") is False


def test_spec_template_has_clear_boundary(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    args = SimpleNamespace(
        ai="claude",
        script="bash",
        project_name=".",
        here=True,
        force=True,
    )

    assert init_project(args) == 0

    template_path = tmp_path / ".agentkit" / "templates" / "specification-template.md"
    spec_text = template_path.read_text()

    assert "STOP: Do not add implementation details. Those belong in plan.md" in spec_text
    assert "## Related Documents" in spec_text
    assert "plan.md" in spec_text
    assert "## Implementation Phases" not in spec_text
