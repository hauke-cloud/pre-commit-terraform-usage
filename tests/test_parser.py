"""Tests for Terraform variable parser."""

import unittest
import tempfile
from pathlib import Path
from terraform_usage.parser import parse_terraform_variables, TerraformVariable


class TestTerraformVariable(unittest.TestCase):
    """Test TerraformVariable class."""

    def test_required_variable(self):
        """Test required variable (no default)."""
        var = TerraformVariable("test_var", "string", "Test variable", None)
        self.assertFalse(var.is_optional)
        self.assertEqual(var.name, "test_var")
        self.assertEqual(var.type, "string")
        self.assertEqual(var.description, "Test variable")

    def test_optional_variable(self):
        """Test optional variable (with default)."""
        var = TerraformVariable("test_var", "string", "Test variable", '"default"')
        self.assertTrue(var.is_optional)
        self.assertEqual(var.default, '"default"')

    def test_format_for_usage_required(self):
        """Test formatting required variable for usage."""
        var = TerraformVariable("name", "string", "The name", None)
        formatted = var.format_for_usage(10, 0)
        self.assertIn("name", formatted)
        self.assertIn("Required:", formatted)

    def test_format_for_usage_optional(self):
        """Test formatting optional variable for usage."""
        var = TerraformVariable("name", "string", "The name", '"default"')
        formatted = var.format_for_usage(10, 10)
        self.assertIn("name", formatted)
        self.assertIn("Optional:", formatted)


class TestParseVariables(unittest.TestCase):
    """Test parsing Terraform variable files."""

    def test_parse_simple_variable(self):
        """Test parsing a simple variable."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tf', delete=False) as f:
            f.write('''
variable "test_var" {
  description = "A test variable"
  type        = string
}
''')
            f.flush()
            
            variables = parse_terraform_variables(Path(f.name))
            
            Path(f.name).unlink()  # Clean up
            
            self.assertEqual(len(variables), 1)
            self.assertEqual(variables[0].name, "test_var")
            self.assertEqual(variables[0].description, "A test variable")
            self.assertEqual(variables[0].type, "string")
            self.assertIsNone(variables[0].default)

    def test_parse_variable_with_default(self):
        """Test parsing a variable with default value."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tf', delete=False) as f:
            f.write('''
variable "test_var" {
  description = "A test variable"
  type        = string
  default     = "default_value"
}
''')
            f.flush()
            
            variables = parse_terraform_variables(Path(f.name))
            
            Path(f.name).unlink()  # Clean up
            
            self.assertEqual(len(variables), 1)
            self.assertIsNotNone(variables[0].default)
            self.assertEqual(variables[0].default.strip('"'), "default_value")

    def test_parse_multiple_variables(self):
        """Test parsing multiple variables."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tf', delete=False) as f:
            f.write('''
variable "var1" {
  description = "First variable"
  type        = string
}

variable "var2" {
  description = "Second variable"
  type        = number
  default     = 42
}
''')
            f.flush()
            
            variables = parse_terraform_variables(Path(f.name))
            
            Path(f.name).unlink()  # Clean up
            
            self.assertEqual(len(variables), 2)
            self.assertEqual(variables[0].name, "var1")
            self.assertEqual(variables[1].name, "var2")
            self.assertIsNone(variables[0].default)
            self.assertIsNotNone(variables[1].default)


if __name__ == "__main__":
    unittest.main()
