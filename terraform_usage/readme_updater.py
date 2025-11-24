"""README.md update functionality."""

import re
import sys
from pathlib import Path
from typing import Optional, Tuple


def extract_metadata_from_readme(readme_path: Path) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Extract existing metadata from README.

    Args:
        readme_path: Path to README.md

    Returns:
        Tuple of (module_name, source, version) or (None, None, None)
    """
    if not readme_path.exists():
        return None, None, None

    content = readme_path.read_text()
    begin_marker = "<!-- BEGIN_AUTOMATED_TF_USAGE_BLOCK -->"

    if begin_marker not in content:
        return None, None, None

    metadata_pattern = re.compile(
        r'<!-- BEGIN_AUTOMATED_TF_USAGE_BLOCK -->\s*'
        r'(?:<!-- MODULE: (.*?) -->\s*)?'
        r'(?:<!-- SOURCE: (.*?) -->\s*)?'
        r'(?:<!-- VERSION: (.*?) -->\s*)?',
        re.DOTALL
    )

    match = metadata_pattern.search(content)
    if match:
        return match.group(1), match.group(2), match.group(3)

    return None, None, None


def update_readme(
    readme_path: Path,
    usage_block: str,
    module_name: str = "",
    source: str = "",
    version: str = ""
) -> bool:
    """Update README.md with the generated usage block.

    Args:
        readme_path: Path to README.md
        usage_block: Generated usage block content
        module_name: Module name for metadata
        source: Source URL for metadata
        version: Version for metadata

    Returns:
        True if changes were made, False otherwise
    """
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
