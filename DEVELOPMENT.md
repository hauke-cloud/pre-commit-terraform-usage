# Development

This document provides information for developers working on the Terraform Usage Block Validator.

## Project Structure

```
.
├── terraform_usage/          # Main package
│   ├── __init__.py           # Package initialization
│   ├── cli.py                # Command-line interface
│   ├── git_utils.py          # Git version/source detection
│   ├── parser.py             # Terraform variable parser
│   ├── generator.py          # Usage block generator
│   └── readme_updater.py     # README.md updater
├── tests/                    # Test suite
│   ├── test_git_utils.py     # Git utilities tests
│   ├── test_parser.py        # Parser tests
│   ├── test_generator.py     # Generator tests
│   └── test_readme_updater.py # README updater tests
├── .github/workflows/        # CI/CD workflows
│   ├── python-tests.yml      # Python code testing (runs on code changes)
│   ├── test-action.yml       # GitHub Action testing (runs on action.yml changes)
│   ├── check-terraform-usage.yml  # Example: Check workflow
│   └── update-terraform-usage.yml # Example: Update workflow
├── terraform_usage_gen.py    # Main entry point script
├── action.yml                # GitHub Action definition
├── pyproject.toml            # Python project configuration
└── README.md                 # User documentation
```

## Setting Up Development Environment

1. **Clone the repository:**
   ```bash
   git clone https://github.com/hauke-cloud/pre-commit-terraform-usage.git
   cd pre-commit-terraform-usage
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install development dependencies:**
   ```bash
   pip install pytest pytest-cov black flake8 isort mypy
   ```

## Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=terraform_usage --cov-report=term-missing

# Run specific test file
python -m pytest tests/test_parser.py -v

# Run specific test
python -m pytest tests/test_parser.py::TestTerraformVariable::test_required_variable -v
```

## Code Quality

```bash
# Format code with black
black terraform_usage tests

# Check code style with flake8
flake8 terraform_usage tests --max-line-length=120

# Sort imports with isort
isort terraform_usage tests

# Type checking with mypy
mypy terraform_usage --ignore-missing-imports
```

## Workflow Separation

The project uses separate GitHub Actions workflows:

### Python Code Testing (`python-tests.yml`)
- **Triggers:** Changes to Python code, tests, or project configuration
- **Purpose:** Test the Python package itself
- **Matrix:** Tests across multiple Python versions (3.8-3.12) and OS (Linux, macOS, Windows)
- **Jobs:**
  - Unit tests with pytest
  - Code coverage reporting
  - Linting with flake8, black, isort

### GitHub Action Testing (`test-action.yml`)
- **Triggers:** Changes to `action.yml` or the test workflow itself
- **Purpose:** Test the GitHub Action functionality
- **Jobs:**
  - Test check mode
  - Test update mode
  - Test with custom directories
  - Test with multiple modules

### Example Workflows
- `check-terraform-usage.yml`: Example of using the action to check usage blocks
- `update-terraform-usage.yml`: Example of using the action to auto-update usage blocks

This separation ensures:
1. Python code changes don't trigger unnecessary action tests
2. Action configuration changes don't run full Python test matrix
3. Faster CI/CD feedback loops
4. Clearer test failure attribution

## Making Changes

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the modular structure:
   - Add new features to appropriate modules in `terraform_usage/`
   - Add tests for new functionality in `tests/`
   - Update documentation in `README.md` or `DEVELOPMENT.md`

3. **Run tests locally:**
   ```bash
   python -m pytest tests/ -v
   black terraform_usage tests
   flake8 terraform_usage tests --max-line-length=120
   ```

4. **Commit using conventional commits:**
   ```bash
   git commit -m "feat: add new feature"
   git commit -m "fix: fix bug"
   git commit -m "docs: update documentation"
   ```

5. **Push and create a pull request:**
   ```bash
   git push origin feature/your-feature-name
   ```

## Adding New Tests

When adding new functionality:

1. **Add unit tests** to the appropriate test file in `tests/`
2. **Test edge cases** including error conditions
3. **Aim for high coverage** (target: >80%)
4. **Use descriptive test names** that explain what is being tested

Example test structure:
```python
def test_feature_name_with_specific_scenario(self):
    """Test that feature works correctly with specific input."""
    # Arrange
    input_data = create_test_input()
    
    # Act
    result = function_under_test(input_data)
    
    # Assert
    self.assertEqual(result, expected_output)
```

## Module Responsibilities

- **`cli.py`**: Argument parsing, workflow orchestration, user interaction
- **`git_utils.py`**: Git operations (version detection, remote URLs, commits analysis)
- **`parser.py`**: Terraform file parsing, variable extraction
- **`generator.py`**: Usage block generation, template handling
- **`readme_updater.py`**: README.md manipulation, metadata extraction

## Release Process

1. Ensure all tests pass
2. Update version in `pyproject.toml` and `terraform_usage/__init__.py`
3. Update `CHANGELOG.md` (if exists)
4. Create a git tag following semantic versioning:
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   git push origin v1.0.0
   ```

## Troubleshooting

### Tests fail with import errors
Ensure you're in the virtual environment and the package is importable:
```bash
source .venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Workflows fail on push
Check which workflow failed:
- If `python-tests.yml` failed: Python code issue
- If `test-action.yml` failed: GitHub Action configuration issue
- If example workflows failed: Variables or README out of sync

## Contributing

See the main `README.md` for contribution guidelines including:
- Code style requirements
- Commit message conventions (conventional commits)
- Pull request process
