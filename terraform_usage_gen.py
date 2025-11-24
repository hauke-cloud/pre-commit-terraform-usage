#!/usr/bin/env python3
"""
Terraform Usage Block Generator

This tool parses Terraform variable files and generates a usage block
with required and optional variables separated into sections.
Variables with default values are considered optional, others are required.
Supports custom templates for flexible output formatting.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional


# Built-in default template
DEFAULT_TEMPLATE = """```hcl
module "{module_name}" {{
{source_line}{version_line}
{required_variables}
{optional_variables}}}
```"""


def parse_semver(version: str) -> Tuple[int, int, int, str]:
    """Parse semantic version string into components.

    Returns (major, minor, patch, prefix) tuple.
    """
    # Match version with optional 'v' prefix
    match = re.match(r'^(v?)(\d+)\.(\d+)\.(\d+)', version)
    if match:
        prefix = match.group(1)
        major = int(match.group(2))
        minor = int(match.group(3))
        patch = int(match.group(4))
        return (major, minor, patch, prefix)
    return (0, 0, 0, 'v')


def analyze_commits_for_bump(directory: Path, since_tag: str = None) -> str:
    """Analyze commits since last tag to determine version bump type.

    Returns 'major', 'minor', 'patch', or 'none' based on conventional commits.
    Logic based on svu (https://github.com/caarlos0/svu):
    - BREAKING CHANGE or ! suffix = major
    - feat: = minor
    - fix: = patch
    - chore: = none
    """
    try:
        # Get commits since the tag
        if since_tag:
            cmd = ["git", "log", f"{since_tag}..HEAD", "--pretty=%s"]
        else:
            cmd = ["git", "log", "--pretty=%s"]

        result = subprocess.run(
            cmd,
            cwd=directory,
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode != 0:
            return 'none'

        commits = result.stdout.strip().split('\n')
        if not commits or commits == ['']:
            return 'none'

        # Analyze commits for the highest priority bump
        has_breaking = False
        has_feat = False
        has_fix = False

        for commit in commits:
            commit_lower = commit.lower()

            # Check for breaking changes
            if 'breaking change:' in commit_lower or re.search(r'^[a-z]+!:', commit_lower):
                has_breaking = True
                break  # Major is highest priority

            # Check for features
            if commit_lower.startswith('feat:') or commit_lower.startswith('feat('):
                has_feat = True

            # Check for fixes
            if commit_lower.startswith('fix:') or commit_lower.startswith('fix('):
                has_fix = True

        if has_breaking:
            return 'major'
        elif has_feat:
            return 'minor'
        elif has_fix:
            return 'patch'
        else:
            return 'none'

    except (subprocess.TimeoutExpired, FileNotFoundError):
        return 'none'


def get_git_version(directory: Path = None) -> Optional[str]:
    """Get the next git version based on svu logic.

    Analyzes conventional commits since the last tag to determine the next version.
    """
    if directory is None:
        directory = Path.cwd()

    try:
        # Check if we're in a git repository
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=directory,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            return None

        # Get the latest tag
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            cwd=directory,
            capture_output=True,
            text=True,
            timeout=5
        )

        current_tag = None
        if result.returncode == 0 and result.stdout.strip():
            current_tag = result.stdout.strip()

        # If we have a tag, analyze commits since then to determine next version
        if current_tag:
            bump_type = analyze_commits_for_bump(directory, current_tag)

            if bump_type == 'none':
                # No commits warrant a version bump, return current tag
                return current_tag

            # Parse current version
            major, minor, patch, prefix = parse_semver(current_tag)

            # Apply bump
            if bump_type == 'major':
                major += 1
                minor = 0
                patch = 0
            elif bump_type == 'minor':
                minor += 1
                patch = 0
            elif bump_type == 'patch':
                patch += 1

            return f"{prefix}{major}.{minor}.{patch}"

        # No tags exist - check if there are any commits
        result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=directory,
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0 and result.stdout.strip() != '0':
            # We have commits but no tags - analyze all commits
            bump_type = analyze_commits_for_bump(directory, None)

            if bump_type == 'major':
                return "v1.0.0"
            elif bump_type == 'minor':
                return "v0.1.0"
            elif bump_type == 'patch':
                return "v0.0.1"
            else:
                # Default to v0.1.0 if no conventional commits
                return "v0.1.0"

        # No commits at all
        return None

    except (subprocess.TimeoutExpired, FileNotFoundError):
        # Git not available or timeout
        pass

    return None


def get_git_remote_url(directory: Path = None) -> Optional[str]:
    """Get the git remote URL."""
    if directory is None:
        directory = Path.cwd()

    try:
        result = subprocess.run(
            ["git", "config", "--get", "remote.origin.url"],
            cwd=directory,
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0 and result.stdout.strip():
            url = result.stdout.strip()

            # Clean up the URL
            # Remove .git suffix
            url = re.sub(r'\.git$', '', url)

            # Convert SSH to HTTPS format for display
            # git@github.com:user/repo -> github.com/user/repo
            url = re.sub(r'^git@([^:]+):', r'\1/', url)

            # Remove https:// or http:// prefix for cleaner display
            url = re.sub(r'^https?://', '', url)

            return url

    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return None


def get_module_name_from_path(directory: Path = None) -> str:
    """Get module name from directory name or git repository name."""
    if directory is None:
        directory = Path.cwd()

    # Try to get from git remote URL first
    remote_url = get_git_remote_url(directory)
    if remote_url:
        # Extract last part of the path
        parts = remote_url.rstrip('/').split('/')
        if parts:
            return parts[-1]

    # Fall back to directory name
    return directory.name


class TerraformVariable:
    """Represents a Terraform variable."""

    def __init__(self, name: str, var_type: str, description: str, default: Optional[str]):
        self.name = name
        self.type = var_type
        self.description = description
        self.default = default
        self.is_optional = default is not None

    def format_for_usage(self, max_name_length: int = 0, max_value_length: int = 0) -> str:
        """Format variable for usage block with aligned equals signs and comments."""
        name_padding = " " * (max_name_length - len(self.name))

        if self.default is not None:
            # Format the default value for display
            default_str = self.default.strip()
            # For multi-line defaults, just show first line or summarize
            if '\n' in default_str:
                value_str = "..."
            else:
                value_str = default_str

            value_padding = " " * (max_value_length - len(value_str))
            return f"  # {self.name}{name_padding} = {value_str}{value_padding} # Optional: {self.description}"
        else:
            # For required variables, no default value
            value_padding = " " * max_value_length
            return f"  {self.name}{name_padding} = {value_padding} # Required: {self.description}"


def parse_terraform_variables(file_path: Path) -> List[TerraformVariable]:
    """Parse Terraform variable definitions from a file."""
    variables = []
    content = file_path.read_text()

    # Find variable blocks using a more robust approach
    # Split by 'variable' keyword but keep track of braces
    lines = content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check if line starts a variable definition
        var_match = re.match(r'\s*variable\s+"([^"]+)"\s*\{', line)
        if var_match:
            var_name = var_match.group(1)

            # Find the matching closing brace
            brace_count = 1
            var_block_lines = []
            i += 1

            while i < len(lines) and brace_count > 0:
                current_line = lines[i]
                var_block_lines.append(current_line)

                # Count braces (simple approach, might need refinement for strings)
                brace_count += current_line.count('{') - current_line.count('}')
                i += 1

            var_block = '\n'.join(var_block_lines)

            # Extract type
            type_match = re.search(r'type\s*=\s*(.+?)(?=\n|$)', var_block, re.MULTILINE)
            var_type = type_match.group(1).strip() if type_match else "any"

            # Extract description
            desc_match = re.search(r'description\s*=\s*"([^"]*)"', var_block)
            description = desc_match.group(1) if desc_match else ""

            # Check for default value - look for "default" keyword
            has_default = re.search(r'\bdefault\s*=', var_block) is not None

            # Extract default value if it exists
            default_value = None
            if has_default:
                default_match = re.search(r'default\s*=\s*(.+?)(?=\n\s*\}|\n\s*[a-z_]+\s*=)', var_block, re.DOTALL)
                if default_match:
                    default_value = default_match.group(1).strip()

            variables.append(TerraformVariable(var_name, var_type, description, default_value))
        else:
            i += 1

    return variables


def generate_usage_block(variables: List[TerraformVariable], module_name: str = "example",
                        source: str = "", version: str = "", template: str = None) -> str:
    """Generate the complete usage block from parsed variables using a template."""
    required_vars = [v for v in variables if not v.is_optional]
    optional_vars = [v for v in variables if v.is_optional]

    # Calculate max variable name length for alignment
    all_vars = required_vars + optional_vars
    max_name_length = max(len(v.name) for v in all_vars) if all_vars else 0

    # Calculate max default value length for alignment
    max_value_length = 0
    for var in optional_vars:
        if var.default:
            default_str = var.default.strip()
            if '\n' not in default_str:
                max_value_length = max(max_value_length, len(default_str))
            else:
                max_value_length = max(max_value_length, 3)  # "..."

    # Build required variables section
    required_lines = []
    if required_vars:
        required_lines.append("  ############")
        required_lines.append("  # Required #")
        required_lines.append("  ############")
        for var in required_vars:
            required_lines.append(var.format_for_usage(max_name_length, max_value_length))

    # Build optional variables section
    optional_lines = []
    if optional_vars:
        if required_vars:
            optional_lines.append("")
        optional_lines.append("  ############")
        optional_lines.append("  # Optional #")
        optional_lines.append("  ############")
        for var in optional_vars:
            optional_lines.append(var.format_for_usage(max_name_length, max_value_length))

    # Prepare template variables
    source_line = f'  source  = "{source}"\n' if source else ""
    version_line = f'  version = "{version}"\n' if version else ""

    # Add spacing after source/version if there are variables
    if (source_line or version_line) and (required_vars or optional_vars):
        if version_line:
            version_line += "\n"
        elif source_line:
            source_line += "\n"

    required_variables = "\n".join(required_lines) if required_lines else ""
    optional_variables = "\n".join(optional_lines) if optional_lines else ""

    # Use provided template or default
    if template is None:
        template = DEFAULT_TEMPLATE

    # Replace template variables
    output = template.format(
        module_name=module_name,
        source=source,
        version=version,
        source_line=source_line,
        version_line=version_line,
        required_variables=required_variables,
        optional_variables=optional_variables
    )

    return output


def load_template(template_path: Path) -> str:
    """Load a template from a file."""
    if not template_path.exists():
        print(f"Warning: Template file {template_path} not found", file=sys.stderr)
        return DEFAULT_TEMPLATE

    template_content = template_path.read_text()

    # Remove comment lines (lines starting with #)
    lines = []
    for line in template_content.split('\n'):
        if not line.strip().startswith('#'):
            lines.append(line)

    return '\n'.join(lines)


def update_readme(readme_path: Path, usage_block: str, module_name: str = "",
                 source: str = "", version: str = "") -> bool:
    """Update README.md with the generated usage block."""
    if not readme_path.exists():
        print(f"Warning: {readme_path} not found", file=sys.stderr)
        return False

    content = readme_path.read_text()

    # Define markers
    begin_marker = "<!-- BEGIN_AUTOMATED_TF_USAGE_BLOCK -->"
    end_marker = "<!-- END_AUTOMATED_TF_USAGE_BLOCK -->"

    # Check if markers exist
    if begin_marker not in content or end_marker not in content:
        print(f"Warning: Markers not found in {readme_path}", file=sys.stderr)
        print(f"Please add the following markers to your README.md:", file=sys.stderr)
        print(f"{begin_marker}", file=sys.stderr)
        print(f"{end_marker}", file=sys.stderr)
        return False

    # Extract existing metadata if present
    metadata_pattern = re.compile(
        r'<!-- BEGIN_AUTOMATED_TF_USAGE_BLOCK -->\s*'
        r'(?:<!-- MODULE: (.*?) -->\s*)?'
        r'(?:<!-- SOURCE: (.*?) -->\s*)?'
        r'(?:<!-- VERSION: (.*?) -->\s*)?',
        re.DOTALL
    )

    match = metadata_pattern.search(content)
    if match and not module_name:
        # Use existing metadata if not provided via command line
        existing_module = match.group(1) or "example"
        existing_source = match.group(2) or ""
        existing_version = match.group(3) or ""

        if not module_name:
            module_name = existing_module
        if not source:
            source = existing_source
        if not version:
            version = existing_version

    # Prepare metadata comments
    metadata_lines = []
    if module_name:
        metadata_lines.append(f"<!-- MODULE: {module_name} -->")
    if source:
        metadata_lines.append(f"<!-- SOURCE: {source} -->")
    if version:
        metadata_lines.append(f"<!-- VERSION: {version} -->")

    metadata_str = "\n".join(metadata_lines)
    if metadata_str:
        metadata_str += "\n"

    # Replace content between markers
    pattern = re.compile(
        f"{re.escape(begin_marker)}.*?{re.escape(end_marker)}",
        re.DOTALL
    )

    new_content = pattern.sub(
        f"{begin_marker}\n{metadata_str}{usage_block}\n{end_marker}",
        content
    )

    # Check if content changed
    if content == new_content:
        return False  # No changes needed

    readme_path.write_text(new_content)
    return True  # Changes made


def find_terraform_files(directory: Path) -> List[Path]:
    """Find all Terraform variable files in the directory."""
    tf_files = []
    for pattern in ["variables.tf", "*.tfvars", "terraform.tfvars"]:
        tf_files.extend(directory.glob(pattern))

    # Filter to only variables.tf for now
    return [f for f in tf_files if f.name == "variables.tf"]


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate Terraform usage blocks for README.md"
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Files to check (used by pre-commit)",
    )
    parser.add_argument(
        "--dir",
        type=Path,
        default=Path.cwd(),
        help="Directory to process (default: current directory)",
    )
    parser.add_argument(
        "--readme",
        type=Path,
        help="Path to README.md (default: <dir>/README.md)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check if documentation is up to date (exit 1 if not)",
    )
    parser.add_argument(
        "--module-name",
        type=str,
        help="Module name for the usage block (default: auto-detected from git or directory name)",
    )
    parser.add_argument(
        "--source",
        type=str,
        help="Module source URL (default: auto-detected from git remote URL)",
    )
    parser.add_argument(
        "--version",
        type=str,
        help="Module version (default: auto-detected from latest git tag)",
    )
    parser.add_argument(
        "--no-auto-detect",
        action="store_true",
        help="Disable automatic detection of module name, source, and version from git",
    )
    parser.add_argument(
        "--force-autodetect",
        action="store_true",
        help="Force auto-detection even when version/source/module metadata exists in README",
    )
    parser.add_argument(
        "--template",
        type=Path,
        help="Path to custom template file (default: built-in template)",
    )
    parser.add_argument(
        "--list-templates",
        action="store_true",
        help="List available built-in templates",
    )

    args = parser.parse_args()

    # List templates if requested
    if args.list_templates:
        print("Built-in templates:")
        print("  - default   : Standard format with code fences and sections")
        print("  - compact   : Compact format without extra spacing")
        print("  - minimal   : Just the module block, no code fences")
        print("  - detailed  : Extended format with usage instructions")
        print("\nTo use a built-in template, specify: --template templates/<name>.tpl")
        print("To create a custom template, see templates/ directory for examples")
        return 0

    # Determine directory to process
    if args.files:
        # If files provided (pre-commit mode), process their directory
        directories = set(Path(f).parent for f in args.files if f.endswith('.tf'))
        if not directories:
            directories = {args.dir}
    else:
        directories = {args.dir}

    exit_code = 0

    for directory in directories:
        # Find variables.tf
        tf_files = find_terraform_files(directory)

        if not tf_files:
            print(f"No variables.tf found in {directory}", file=sys.stderr)
            continue

        # Parse all variables
        all_variables = []
        for tf_file in tf_files:
            variables = parse_terraform_variables(tf_file)
            all_variables.extend(variables)

        if not all_variables:
            print(f"No variables found in {directory}", file=sys.stderr)
            continue

        # Determine README path
        readme_path = args.readme if args.readme else directory / "README.md"

        # Extract metadata from command line arguments
        module_name = args.module_name or ""
        source = args.source or ""
        version = args.version or ""

        # Auto-detect from git if not explicitly provided via command line and auto-detect is enabled
        if not args.no_auto_detect:
            if not args.module_name:
                detected_module = get_module_name_from_path(directory)
                if detected_module:
                    module_name = detected_module

            if not args.source:
                git_url = get_git_remote_url(directory)
                if git_url:
                    source = git_url

            if not args.version:
                git_version = get_git_version(directory)
                if git_version:
                    version = git_version

        # Fall back to existing README metadata only if auto-detection didn't provide values
        # and force-autodetect is not enabled
        if not args.force_autodetect and readme_path.exists() and not (module_name and source and version):
            content = readme_path.read_text()
            begin_marker = "<!-- BEGIN_AUTOMATED_TF_USAGE_BLOCK -->"

            if begin_marker in content:
                metadata_pattern = re.compile(
                    r'<!-- BEGIN_AUTOMATED_TF_USAGE_BLOCK -->\s*'
                    r'(?:<!-- MODULE: (.*?) -->\s*)?'
                    r'(?:<!-- SOURCE: (.*?) -->\s*)?'
                    r'(?:<!-- VERSION: (.*?) -->\s*)?',
                    re.DOTALL
                )
                match = metadata_pattern.search(content)
                if match:
                    if not module_name and match.group(1):
                        module_name = match.group(1)
                    if not source and match.group(2):
                        source = match.group(2)
                    if not version and match.group(3):
                        version = match.group(3)

        # Use fallback defaults if still not set
        if not module_name:
            module_name = "example"

        # Load template if specified
        template = None
        if args.template:
            template = load_template(args.template)

        # Generate usage block with metadata
        usage_block = generate_usage_block(
            all_variables,
            module_name=module_name,
            source=source,
            version=version,
            template=template
        )

        if args.check:
            # Check mode: verify if update is needed
            if readme_path.exists():
                content = readme_path.read_text()
                begin_marker = "<!-- BEGIN_AUTOMATED_TF_USAGE_BLOCK -->"
                end_marker = "<!-- END_AUTOMATED_TF_USAGE_BLOCK -->"

                if begin_marker in content and end_marker in content:
                    # Extract current block including metadata
                    pattern = re.compile(
                        f"{re.escape(begin_marker)}(.*?){re.escape(end_marker)}",
                        re.DOTALL
                    )
                    match = pattern.search(content)
                    if match:
                        current_block = match.group(1).strip()

                        # Extract metadata from current block to use in comparison
                        metadata_pattern = re.compile(
                            r'(?:<!-- MODULE: (.*?) -->\s*)?'
                            r'(?:<!-- SOURCE: (.*?) -->\s*)?'
                            r'(?:<!-- VERSION: (.*?) -->\s*)?',
                            re.DOTALL
                        )
                        meta_match = metadata_pattern.match(current_block)
                        if meta_match and not module_name:
                            module_name = meta_match.group(1) or "example"
                            source = meta_match.group(2) or ""
                            version = meta_match.group(3) or ""

                            # Regenerate with extracted metadata
                            usage_block = generate_usage_block(
                                all_variables,
                                module_name=module_name,
                                source=source,
                                version=version,
                                template=template
                            )

                        # Prepare expected block with metadata
                        metadata_lines = []
                        if module_name:
                            metadata_lines.append(f"<!-- MODULE: {module_name} -->")
                        if source:
                            metadata_lines.append(f"<!-- SOURCE: {source} -->")
                        if version:
                            metadata_lines.append(f"<!-- VERSION: {version} -->")

                        metadata_str = "\n".join(metadata_lines)
                        if metadata_str:
                            expected_block = f"{metadata_str}\n{usage_block}"
                        else:
                            expected_block = usage_block

                        if current_block != expected_block.strip():
                            print(f"Usage block in {readme_path} is out of date", file=sys.stderr)
                            exit_code = 1
                        else:
                            print(f"Usage block in {readme_path} is up to date")
        else:
            # Update mode
            if update_readme(readme_path, usage_block, module_name, source, version):
                print(f"Updated {readme_path}")
                exit_code = 1  # Signal to pre-commit that file was modified
            else:
                print(f"No changes needed for {readme_path}")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
