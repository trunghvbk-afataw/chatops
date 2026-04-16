# Contributing to chatops-bridge

Thanks for your interest in contributing! This document explains how to develop, test, and release the package.

## Development Setup

### Clone and Install

```bash
git clone https://github.com/trunghvbk-afataw/chatops.git
cd chatops
pip install -e ".[discord-bot]"
```

### Run Tests

```bash
python -m pytest tests/
```

### Linting and Type Checking

```bash
python -m flake8 src/ examples/
python -m mypy src/
```

## Making Changes

1. Create a branch from `main`:
   ```bash
   git checkout -b feature/your-feature
   ```

2. Make your changes and commit:
   ```bash
   git add .
   git commit -m "Add your feature"
   ```

3. Push and open a pull request:
   ```bash
   git push origin feature/your-feature
   ```

## Code Style

- Follow PEP 8
- Use type hints for all functions
- Max line length: 120 characters
- Add docstrings to public functions

## Releasing a New Version

### Prerequisites

- Repository access with push rights
- GitHub environment configured for PyPI (see below)

### Steps

1. Update version in [pyproject.toml](pyproject.toml):
   ```toml
   version = "0.2.0"  # e.g., from 0.1.0
   ```

2. Update [CHANGELOG.md](CHANGELOG.md) with release notes:
   ```markdown
   ## [0.2.0] - YYYY-MM-DD
   
   ### Added
   - New feature description
   
   ### Fixed
   - Bug fix description
   ```

3. Commit changes:
   ```bash
   git add pyproject.toml CHANGELOG.md
   git commit -m "Release v0.2.0"
   ```

4. Create and push tag:
   ```bash
   git tag v0.2.0
   git commit --allow-empty -m "Release v0.2.0"
   git push origin v0.2.0
   ```

5. GitHub Actions will automatically:
   - Build the package
   - Validate metadata
   - Publish to PyPI
   - Create a GitHub release

Monitor the workflow in the [Actions tab](https://github.com/trunghvbk-afataw/chatops/actions).

### GitHub PyPI Setup (One-time)

Configure PyPI trusted publishing:

1. Go to **Settings** → **Environments**
2. Create environment named `pypi`
3. Set URL to `https://pypi.org/p/chatops-bridge`
4. No secrets needed - uses OIDC token from GitHub

See [PyPI trusted publishing docs](https://docs.pypi.org/trusted-publishers/).

### Manual Publishing (Fallback)

If automated publishing fails:

```bash
pip install build twine
python -m build
python -m twine check dist/*
python -m twine upload dist/*
```

Requires PyPI credentials in `~/.pypirc` or as environment variable.

## Verifying Release

After publishing:

1. Visit [https://pypi.org/project/chatops-bridge/](https://pypi.org/project/chatops-bridge/)
2. Verify version and release date
3. Test installation:
   ```bash
   pip install chatops-bridge==0.2.0
   ```

## Questions?

Open an issue or discussion on GitHub: [https://github.com/trunghvbk-afataw/chatops/issues](https://github.com/trunghvbk-afataw/chatops/issues)
