#!/bin/sh

# Fail the whole script if any single line fails
set -e

echo "***** Validate content of pyproject.toml and its consistency with poetry.lock *****"
poetry check --strict  # fail in case of warnings
echo "***** Check poetry dependencies *****"
poetry run deptry .
echo "***** Check formating with black *****"
poetry run black --diff --check .
echo "***** Sort module imports with isort *****"
poetry run isort --check .
echo "***** Check typing with mypy *****"
poetry run mypy --install-types --non-interactive .
echo "***** Lint the codebase *****"
poetry run pylint -E suncal tests
