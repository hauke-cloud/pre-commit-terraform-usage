"""Usage block generation."""

from pathlib import Path
from typing import List, Optional

from .parser import TerraformVariable


# Built-in default template
DEFAULT_TEMPLATE = """```hcl
module "{module_name}" {{
{source_line}{version_line}
{required_variables}
{optional_variables}}}
```"""


def load_template(template_path: Path) -> str:
    """Load a template from a file.

    Args:
        template_path: Path to template file

    Returns:
        Template content with comments removed
    """
    if not template_path.exists():
        return DEFAULT_TEMPLATE

    template_content = template_path.read_text()

    # Remove comment lines (lines starting with #)
    lines = []
    for line in template_content.split('\n'):
        if not line.strip().startswith('#'):
            lines.append(line)

    return '\n'.join(lines)


def generate_usage_block(
    variables: List[TerraformVariable],
    module_name: str = "example",
    source: str = "",
    version: str = "",
    template: Optional[str] = None
) -> str:
    """Generate the complete usage block from parsed variables using a template.

    Args:
        variables: List of parsed Terraform variables
        module_name: Name of the module
        source: Module source URL
        version: Module version
        template: Custom template string (None = use default)

    Returns:
        Formatted usage block
    """
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
