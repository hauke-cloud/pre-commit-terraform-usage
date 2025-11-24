#!/usr/bin/env python3
"""Command-line interface for Terraform Usage Block Generator."""

import argparse
import re
import sys
from pathlib import Path
from typing import Set

from terraform_usage.git_utils import get_git_version, get_git_remote_url, get_module_name_from_path
from terraform_usage.parser import parse_terraform_variables, find_terraform_files
from terraform_usage.generator import generate_usage_block, load_template
from terraform_usage.readme_updater import update_readme, extract_metadata_from_readme


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments namespace
    """
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
        "--force-autodetect-source",
        action="store_true",
        help="Force auto-detection of source even when metadata exists in README",
    )
    parser.add_argument(
        "--force-autodetect-version",
        action="store_true",
        help="Force auto-detection of version even when metadata exists in README",
    )
    parser.add_argument(
        "--force-autodetect-module",
        action="store_true",
        help="Force auto-detection of module name even when metadata exists in README",
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

    return parser.parse_args()


def list_templates():
    """List available built-in templates."""
    print("Built-in templates:")
    print("  - default   : Standard format with code fences and sections")
    print("  - compact   : Compact format without extra spacing")
    print("  - minimal   : Just the module block, no code fences")
    print("  - detailed  : Extended format with usage instructions")
    print("\nTo use a built-in template, specify: --template templates/<name>.tpl")
    print("To create a custom template, see templates/ directory for examples")


def get_directories_from_args(args: argparse.Namespace) -> Set[Path]:
    """Get set of directories to process from arguments.

    Args:
        args: Parsed command-line arguments

    Returns:
        Set of directory paths to process
    """
    if args.files:
        # If files provided (pre-commit mode), process their directory
        directories = set(Path(f).parent for f in args.files if f.endswith('.tf'))
        if not directories:
            directories = {args.dir}
    else:
        directories = {args.dir}

    return directories


def resolve_metadata(
    args: argparse.Namespace,
    directory: Path,
    readme_path: Path
) -> tuple[str, str, str]:
    """Resolve module metadata from various sources.

    Priority order:
    1. Command-line arguments
    2. Auto-detection from git (if enabled)
    3. Existing README metadata (if not force-autodetecting)
    4. Fallback defaults

    Args:
        args: Parsed command-line arguments
        directory: Directory being processed
        readme_path: Path to README.md

    Returns:
        Tuple of (module_name, source, version)
    """
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
    # and force-autodetect is not enabled (check individually for each field)
    if readme_path.exists() and not (module_name and source and version):
        existing_module, existing_source, existing_version = extract_metadata_from_readme(readme_path)

        # Use existing metadata only if not force-autodetecting that specific field
        if not module_name and existing_module and not args.force_autodetect and not args.force_autodetect_module:
            module_name = existing_module
        if not source and existing_source and not args.force_autodetect and not args.force_autodetect_source:
            source = existing_source
        if not version and existing_version and not args.force_autodetect and not args.force_autodetect_version:
            version = existing_version

    # Use fallback defaults if still not set
    if not module_name:
        module_name = "example"

    return module_name, source, version


def check_mode(
    args: argparse.Namespace,
    readme_path: Path,
    usage_block: str,
    module_name: str,
    source: str,
    version: str
) -> int:
    """Run check mode to verify if README is up to date.

    Args:
        args: Parsed command-line arguments
        readme_path: Path to README.md
        usage_block: Generated usage block
        module_name: Module name
        source: Source URL
        version: Version string

    Returns:
        Exit code (0 = up to date, 1 = out of date)
    """
    if not readme_path.exists():
        print(f"README not found at {readme_path}", file=sys.stderr)
        return 1

    content = readme_path.read_text()
    begin_marker = "<!-- BEGIN_AUTOMATED_TF_USAGE_BLOCK -->"
    end_marker = "<!-- END_AUTOMATED_TF_USAGE_BLOCK -->"

    if begin_marker not in content or end_marker not in content:
        print(f"Markers not found in {readme_path}", file=sys.stderr)
        return 1

    # Extract current block including metadata
    pattern = re.compile(
        f"{re.escape(begin_marker)}(.*?){re.escape(end_marker)}",
        re.DOTALL
    )
    match = pattern.search(content)
    if not match:
        print(f"Could not extract usage block from {readme_path}", file=sys.stderr)
        return 1

    current_block = match.group(1).strip()

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
        return 1
    else:
        print(f"Usage block in {readme_path} is up to date")
        return 0


def process_directory(args: argparse.Namespace, directory: Path) -> int:
    """Process a single directory.

    Args:
        args: Parsed command-line arguments
        directory: Directory to process

    Returns:
        Exit code (0 = success/no changes, 1 = changes made or error)
    """
    # Find variables.tf
    tf_files = find_terraform_files(directory)

    if not tf_files:
        print(f"No variables.tf found in {directory}", file=sys.stderr)
        return 0

    # Parse all variables
    all_variables = []
    for tf_file in tf_files:
        variables = parse_terraform_variables(tf_file)
        all_variables.extend(variables)

    if not all_variables:
        print(f"No variables found in {directory}", file=sys.stderr)
        return 0

    # Determine README path
    readme_path = args.readme if args.readme else directory / "README.md"

    # Resolve metadata
    module_name, source, version = resolve_metadata(args, directory, readme_path)

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
        return check_mode(args, readme_path, usage_block, module_name, source, version)
    else:
        # Update mode
        if update_readme(readme_path, usage_block, module_name, source, version):
            print(f"Updated {readme_path}")
            return 1  # Signal to pre-commit that file was modified
        else:
            print(f"No changes needed for {readme_path}")
            return 0


def main() -> int:
    """Main entry point.

    Returns:
        Exit code
    """
    args = parse_arguments()

    # List templates if requested
    if args.list_templates:
        list_templates()
        return 0

    # Get directories to process
    directories = get_directories_from_args(args)

    exit_code = 0
    for directory in directories:
        result = process_directory(args, directory)
        if result != 0:
            exit_code = result

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
