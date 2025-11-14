#!/bin/bash
# Setup script for terraform-usage-gen

set -e

echo "Setting up Terraform Usage Generator..."

# Make script executable
chmod +x terraform_usage_gen.py

echo "✓ Script is now executable"

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Check if pre-commit is installed
if command -v pre-commit &> /dev/null; then
    echo "✓ pre-commit is installed"
    
    # Install pre-commit hooks if .pre-commit-config.yaml exists and in a git repo
    if [ -f .pre-commit-config.yaml ] && [ -d .git ]; then
        echo "Installing pre-commit hooks..."
        pre-commit install
        echo "✓ Pre-commit hooks installed"
    elif [ -f .pre-commit-config.yaml ]; then
        echo "⚠ Not in a git repository - skipping pre-commit hook installation"
    fi
else
    echo "⚠ pre-commit is not installed"
    echo "  Install it with: pip install pre-commit"
fi

# Test the tool
echo ""
echo "Testing the tool..."
python3 terraform_usage_gen.py --dir . --check

if [ $? -eq 0 ]; then
    echo "✓ Tool is working correctly"
else
    echo "⚠ Tool check failed - updating documentation..."
    python3 terraform_usage_gen.py --dir .
fi

echo ""
echo "Setup complete! 🎉"
echo ""
echo "Usage:"
echo "  Generate docs: python3 terraform_usage_gen.py --dir ."
echo "  Check docs:    python3 terraform_usage_gen.py --dir . --check"
