# Development

## Prerequisites

- Python 3.9+
- [Poetry](https://python-poetry.org/)

## Install dependencies

```bash
git clone https://github.com/AlexIvanchyk/django-localekit
cd django-localekit
poetry install
poetry run pre-commit install
```

This installs all runtime and development dependencies (pytest, ruff, mkdocs-material, pre-commit, etc.) into an isolated virtual environment and registers the git hooks so they run automatically on every commit.

## Run the test suite

```bash
poetry run pytest
```

Run with verbose output:

```bash
poetry run pytest -v
```

Run a specific test file:

```bash
poetry run pytest tests/test_commands.py
```

Check test coverage:

```bash
poetry run coverage run -m pytest
poetry run coverage report
```

## Lint and format

Check for linting issues:

```bash
poetry run ruff check .
```

Auto-fix fixable issues:

```bash
poetry run ruff check --fix .
```

Check formatting:

```bash
poetry run ruff format --check .
```

Apply formatting:

```bash
poetry run ruff format .
```

## Preview documentation locally

```bash
poetry run mkdocs serve
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser. Changes to files in `docs/` are reflected live.

## Deploy documentation to GitHub Pages

```bash
poetry run mkdocs gh-deploy
```

This builds the site and pushes it to the `gh-pages` branch. The docs are then served at:

[https://alexivanchyk.github.io/django-localekit/](https://alexivanchyk.github.io/django-localekit/)

!!! note
    Make sure you have push access to the repository before running `gh-deploy`.
