# Development Environment Setup Guide

## Option 1: Using Poetry (Recommended)

### Install Poetry
```bash
# Install Poetry (official installer)
curl -sSL https://install.python-poetry.org | python3 -

# Or via pip (alternative)
pip install poetry
```

### Setup Project with Poetry
```bash
# Navigate to project directory
cd ai_finance_assistant

# Install all dependencies (creates virtual env automatically)
poetry install

# Activate the Poetry shell
poetry shell

# Run the application
poetry run streamlit run src/web_app/main.py

# Run tests
poetry run pytest

# Add new dependencies
poetry add new-package
poetry add --group dev new-dev-package
```

### Poetry Benefits
- ✅ Automatic virtual environment management
- ✅ Dependency resolution and lock files
- ✅ Clean separation of dev/prod dependencies
- ✅ Easy package publishing
- ✅ Better dependency conflict resolution

---

## Option 2: Traditional pip + venv (Current Setup)

### Setup Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies (optional)
pip install -r requirements-dev.txt
```

### Managing Dependencies
```bash
# Add new package
pip install new-package
pip freeze > requirements.txt

# Remove package
pip uninstall package-name
pip freeze > requirements.txt
```

---

## Option 3: pip-tools (Advanced pip)

### Install pip-tools
```bash
pip install pip-tools
```

### Create requirements.in files
```bash
# requirements.in (main dependencies)
langchain>=0.1.0
openai>=1.12.0
streamlit>=1.31.0

# requirements-dev.in (dev dependencies)
-r requirements.in
pytest>=7.4.3
black>=23.12.1
```

### Compile and install
```bash
# Compile to requirements.txt
pip-compile requirements.in
pip-compile requirements-dev.in

# Install
pip-sync requirements.txt requirements-dev.txt
```

---

## Recommendation: Use Poetry

Poetry is the modern standard for Python dependency management because:

1. **Automatic virtual environment management**
2. **Dependency resolution** (prevents conflicts)
3. **Lock files** for reproducible builds
4. **Clean project structure**
5. **Easy publishing** if you want to share your package

### Quick Start with Poetry:
```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Setup project
cd ai_finance_assistant
poetry install

# Start developing
poetry shell
poetry run python src/web_app/main.py
```

Your current `requirements.txt` files will still work, but Poetry provides a much better development experience!
