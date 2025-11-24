"""Tests for README updater."""

import unittest
import tempfile
from pathlib import Path
from terraform_usage.readme_updater import update_readme, extract_metadata_from_readme


class TestReadmeUpdater(unittest.TestCase):
    """Test README.md update functionality."""

    def test_extract_metadata(self):
        """Test extracting metadata from README."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write('''# Test Module
<!-- BEGIN_AUTOMATED_TF_USAGE_BLOCK -->
<!-- MODULE: test-module -->
<!-- SOURCE: github.com/test/repo -->
<!-- VERSION: v1.0.0 -->
Some content
<!-- END_AUTOMATED_TF_USAGE_BLOCK -->
''')
            f.flush()
            
            module, source, version = extract_metadata_from_readme(Path(f.name))
            
            Path(f.name).unlink()  # Clean up
            
            self.assertEqual(module, "test-module")
            self.assertEqual(source, "github.com/test/repo")
            self.assertEqual(version, "v1.0.0")

    def test_update_readme_with_changes(self):
        """Test updating README when changes are needed."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write('''# Test Module
<!-- BEGIN_AUTOMATED_TF_USAGE_BLOCK -->
Old content
<!-- END_AUTOMATED_TF_USAGE_BLOCK -->
''')
            f.flush()
            
            result = update_readme(
                Path(f.name),
                "New content",
                module_name="test",
                source="github.com/test/repo",
                version="v1.0.0"
            )
            
            content = Path(f.name).read_text()
            Path(f.name).unlink()  # Clean up
            
            self.assertTrue(result)
            self.assertIn("New content", content)
            self.assertIn("MODULE: test", content)

    def test_update_readme_no_changes(self):
        """Test updating README when no changes are needed."""
        usage_content = "Test usage block"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(f'''# Test Module
<!-- BEGIN_AUTOMATED_TF_USAGE_BLOCK -->
{usage_content}
<!-- END_AUTOMATED_TF_USAGE_BLOCK -->
''')
            f.flush()
            
            result = update_readme(
                Path(f.name),
                usage_content,
                module_name="",
                source="",
                version=""
            )
            
            Path(f.name).unlink()  # Clean up
            
            self.assertFalse(result)

    def test_update_readme_missing_markers(self):
        """Test updating README without markers."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Test Module\nNo markers here")
            f.flush()
            
            result = update_readme(
                Path(f.name),
                "New content"
            )
            
            Path(f.name).unlink()  # Clean up
            
            self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
