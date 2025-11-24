#!/usr/bin/env python3
"""
Terraform Usage Block Generator

This tool parses Terraform variable files and generates a usage block
with required and optional variables separated into sections.
Variables with default values are considered optional, others are required.
Supports custom templates for flexible output formatting.
"""

from terraform_usage.cli import main

if __name__ == "__main__":
    import sys
    sys.exit(main())
