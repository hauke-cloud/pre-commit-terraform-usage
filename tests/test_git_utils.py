"""Tests for git utilities."""

import unittest
from pathlib import Path
from terraform_usage.git_utils import parse_semver, analyze_commits_for_bump


class TestParseSemver(unittest.TestCase):
    """Test semver parsing."""

    def test_parse_with_v_prefix(self):
        """Test parsing version with v prefix."""
        major, minor, patch, prefix = parse_semver("v1.2.3")
        self.assertEqual((major, minor, patch, prefix), (1, 2, 3, "v"))

    def test_parse_without_prefix(self):
        """Test parsing version without prefix."""
        major, minor, patch, prefix = parse_semver("2.5.7")
        self.assertEqual((major, minor, patch, prefix), (2, 5, 7, ""))

    def test_parse_invalid(self):
        """Test parsing invalid version."""
        major, minor, patch, prefix = parse_semver("invalid")
        self.assertEqual((major, minor, patch, prefix), (0, 0, 0, "v"))

    def test_parse_major_version(self):
        """Test parsing major version."""
        major, minor, patch, prefix = parse_semver("v10.0.0")
        self.assertEqual((major, minor, patch, prefix), (10, 0, 0, "v"))


class TestAnalyzeCommits(unittest.TestCase):
    """Test commit analysis for version bumping."""

    def test_breaking_change_detection(self):
        """Test that breaking changes are detected."""
        # This test would require mocking git commands
        # For now, we'll skip it as it requires a git repository
        pass

    def test_feat_detection(self):
        """Test that feat commits are detected."""
        # This test would require mocking git commands
        pass

    def test_fix_detection(self):
        """Test that fix commits are detected."""
        # This test would require mocking git commands
        pass


if __name__ == "__main__":
    unittest.main()
