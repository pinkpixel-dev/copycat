#!/bin/bash

# Format Python code with ruff
ruff format .

# Fix linting issues with ruff
ruff check --fix .

echo "✅ Code formatting and linting complete!"
