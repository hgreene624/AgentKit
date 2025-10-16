# Installing AgentKit with UV

AgentKit uses `uv` for fast, reliable Python package management (like SpeckKit).

## Prerequisites

Install `uv` if you haven't already:

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv
```

## Installation

### Install Latest Version from GitHub

```bash
uv tool install git+https://github.com/hgreene624/agentkit.git
```

### Install Specific Version

```bash
uv tool install git+https://github.com/hgreene624/agentkit.git@v0.2.0
```

### Upgrade Existing Installation

```bash
uv tool upgrade agentkit-cli
```

### Uninstall

```bash
uv tool uninstall agentkit-cli
```

## Usage

After installation with `uv tool install`, the `agentkit` command will be available globally:

```bash
# Initialize a new project
agentkit init my-project

# Or initialize in current directory
agentkit init . --here

# Check installation
agentkit --version
```

## Development Installation

For development, use editable install:

```bash
# Clone the repository
git clone https://github.com/hgreene624/agentkit.git
cd agentkit

# Install in editable mode
uv pip install -e .
```

## Why UV?

- **Fast**: 10-100x faster than pip
- **Reliable**: Deterministic resolution
- **Modern**: Built in Rust, like SpeckKit uses
- **Compatible**: Works with existing Python tooling

## Comparison with pip

| Task | pip | uv |
|------|-----|-----|
| Install from GitHub | `pip install git+https://...` | `uv tool install git+https://...` |
| Upgrade | `pip install --upgrade` | `uv tool upgrade` |
| Uninstall | `pip uninstall` | `uv tool uninstall` |
| Speed | Standard | 10-100x faster |

## Troubleshooting

### Command not found after installation

Make sure `uv`'s tool bin directory is in your PATH:

```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="$HOME/.local/bin:$PATH"
```

### Permission errors

UV tools are installed per-user by default, no sudo needed.

### Reinstall from scratch

```bash
uv tool uninstall agentkit-cli
uv cache clean
uv tool install git+https://github.com/hgreene624/agentkit.git
```
