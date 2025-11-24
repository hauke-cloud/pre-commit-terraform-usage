"""Tests for usage block generator."""

import unittest
from terraform_usage.generator import generate_usage_block
from terraform_usage.parser import TerraformVariable


class TestGenerateUsageBlock(unittest.TestCase):
    """Test usage block generation."""

    def test_generate_empty_block(self):
        """Test generating usage block with no variables."""
        block = generate_usage_block([], module_name="test")
        self.assertIn("module", block)
        self.assertIn("test", block)

    def test_generate_with_required_only(self):
        """Test generating usage block with only required variables."""
        variables = [
            TerraformVariable("name", "string", "The name", None),
            TerraformVariable("count", "number", "The count", None),
        ]
        block = generate_usage_block(variables, module_name="test")
        self.assertIn("Required", block)
        self.assertNotIn("Optional", block)
        self.assertIn("name", block)
        self.assertIn("count", block)

    def test_generate_with_optional_only(self):
        """Test generating usage block with only optional variables."""
        variables = [
            TerraformVariable("name", "string", "The name", '"default"'),
            TerraformVariable("count", "number", "The count", "42"),
        ]
        block = generate_usage_block(variables, module_name="test")
        self.assertNotIn("Required", block)
        self.assertIn("Optional", block)
        self.assertIn("name", block)
        self.assertIn("count", block)

    def test_generate_with_mixed(self):
        """Test generating usage block with both required and optional variables."""
        variables = [
            TerraformVariable("required_name", "string", "Required", None),
            TerraformVariable("optional_name", "string", "Optional", '"default"'),
        ]
        block = generate_usage_block(variables, module_name="test")
        self.assertIn("Required", block)
        self.assertIn("Optional", block)
        self.assertIn("required_name", block)
        self.assertIn("optional_name", block)

    def test_generate_with_source_and_version(self):
        """Test generating usage block with source and version."""
        variables = []
        block = generate_usage_block(
            variables,
            module_name="test",
            source="github.com/user/repo",
            version="v1.0.0"
        )
        self.assertIn("source", block)
        self.assertIn("github.com/user/repo", block)
        self.assertIn("version", block)
        self.assertIn("v1.0.0", block)


if __name__ == "__main__":
    unittest.main()
