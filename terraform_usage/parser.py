"""Terraform variable file parser."""

import re
from pathlib import Path
from typing import List, Optional


class TerraformVariable:
    """Represents a Terraform variable."""

    def __init__(self, name: str, var_type: str, description: str, default: Optional[str]):
        """Initialize a Terraform variable.

        Args:
            name: Variable name
            var_type: Variable type
            description: Variable description
            default: Default value (None if required)
        """
        self.name = name
        self.type = var_type
        self.description = description
        self.default = default
        self.is_optional = default is not None

    def format_for_usage(self, max_name_length: int = 0, max_value_length: int = 0) -> str:
        """Format variable for usage block with aligned equals signs and comments.

        Args:
            max_name_length: Maximum variable name length for alignment
            max_value_length: Maximum default value length for alignment

        Returns:
            Formatted variable line
        """
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
    """Parse Terraform variable definitions from a file.

    Args:
        file_path: Path to variables.tf file

    Returns:
        List of TerraformVariable objects
    """
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


def find_terraform_files(directory: Path) -> List[Path]:
    """Find all Terraform variable files in the directory.

    Args:
        directory: Directory to search

    Returns:
        List of variables.tf file paths
    """
    tf_files = []
    for pattern in ["variables.tf", "*.tfvars", "terraform.tfvars"]:
        tf_files.extend(directory.glob(pattern))

    # Filter to only variables.tf for now
    return [f for f in tf_files if f.name == "variables.tf"]
