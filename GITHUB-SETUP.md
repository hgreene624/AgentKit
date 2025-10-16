# GitHub Setup Guide for AgentKit

## Prerequisites

- GitHub account
- Git installed locally
- AgentKit v0.2.0 ready to upload

## Step 1: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `agentkit` (or `AgentKit`)
3. Description: "Creative idea development toolkit for AI agents"
4. Choose: Public
5. **DO NOT** initialize with README (we already have one)
6. Click "Create repository"

## Step 2: Initialize Git Repository Locally

```bash
cd /Users/holdengreene/Documents/AgentKit

# Initialize git (if not already done)
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit - AgentKit v0.2.0"
```

## Step 3: Connect to GitHub and Push

Replace `hgreene624` with your GitHub username:

```bash
# Add remote
git remote add origin https://github.com/hgreene624/agentkit.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 4: Create First Release (Optional but Recommended)

1. Go to your GitHub repository
2. Click "Releases" → "Create a new release"
3. Tag: `v0.2.0`
4. Title: `AgentKit v0.2.0 - Major Workflow Improvements`
5. Description: Copy from CHANGELOG.md
6. Click "Publish release"

## Step 5: Installing from GitHub

Once uploaded, anyone can install AgentKit directly from GitHub.

### Recommended: UV Installation

```bash
# Install latest version
uv tool install git+https://github.com/hgreene624/agentkit.git

# Install specific version (tag)
uv tool install git+https://github.com/hgreene624/agentkit.git@v0.2.0

# Upgrade existing installation
uv tool upgrade agentkit-cli

# Uninstall
uv tool uninstall agentkit-cli
```

### Alternative: Pip Installation

```bash
# Install latest version
pip install git+https://github.com/hgreene624/agentkit.git

# Install specific version (tag)
pip install git+https://github.com/hgreene624/agentkit.git@v0.2.0

# Upgrade existing installation
pip install --upgrade git+https://github.com/hgreene624/agentkit.git
```

### Development Installation

```bash
git clone https://github.com/hgreene624/agentkit.git
cd agentkit
uv pip install -e .
```

## Step 6: Update README with Installation Instructions

Update README.md to include:

```markdown
## Installation

Install directly from GitHub:

\`\`\`bash
pip install git+https://github.com/hgreene624/agentkit.git
\`\`\`

Or install a specific version:

\`\`\`bash
pip install git+https://github.com/hgreene624/agentkit.git@v0.2.0
\`\`\`
```

## Step 7: Future Updates

When you make changes:

```bash
# Make your changes

# Stage changes
git add .

# Commit
git commit -m "Description of changes"

# Push to GitHub
git push origin main

# For new versions, create a new release/tag
git tag v0.3.0
git push origin v0.3.0
```

## Troubleshooting

### Authentication Issues

If you get authentication errors, you may need to:

1. Use SSH instead of HTTPS:
   ```bash
   git remote set-url origin git@github.com:hgreene624/agentkit.git
   ```

2. Or use a Personal Access Token (PAT):
   - Go to GitHub → Settings → Developer settings → Personal access tokens
   - Generate new token with `repo` permissions
   - Use token as password when prompted

### Installation Issues

If users encounter installation issues:

```bash
# Uninstall old version first
pip uninstall agentkit-cli

# Clear pip cache
pip cache purge

# Reinstall
pip install git+https://github.com/hgreene624/agentkit.git
```

## Notes

- The package name in `pyproject.toml` is `agentkit-cli`
- The command is `agentkit`
- Users install with: `pip install git+https://github.com/hgreene624/agentkit.git`
- The actual package installed will be `agentkit-cli` but command is `agentkit`
