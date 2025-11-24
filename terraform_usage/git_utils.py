"""Git-related utilities for version and source detection."""

import re
import subprocess
from pathlib import Path
from typing import Optional, Tuple


def parse_semver(version: str) -> Tuple[int, int, int, str]:
    """Parse semantic version string into components.

    Args:
        version: Version string (e.g., 'v1.2.3' or '1.2.3')

    Returns:
        Tuple of (major, minor, patch, prefix)
    """
    match = re.match(r'^(v?)(\d+)\.(\d+)\.(\d+)', version)
    if match:
        prefix = match.group(1)
        major = int(match.group(2))
        minor = int(match.group(3))
        patch = int(match.group(4))
        return (major, minor, patch, prefix)
    return (0, 0, 0, 'v')


def analyze_commits_for_bump(directory: Path, since_tag: Optional[str] = None) -> str:
    """Analyze commits since last tag to determine version bump type.

    Returns 'major', 'minor', 'patch', or 'none' based on conventional commits.
    Logic based on svu (https://github.com/caarlos0/svu):
    - BREAKING CHANGE or ! suffix = major
    - feat: = minor
    - fix: = patch
    - chore: = none

    Args:
        directory: Path to git repository
        since_tag: Tag to analyze commits from (None = all commits)

    Returns:
        Bump type: 'major', 'minor', 'patch', or 'none'
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


def get_git_version(directory: Optional[Path] = None) -> Optional[str]:
    """Get the next git version based on svu logic.

    Analyzes conventional commits since the last tag to determine the next version.

    Args:
        directory: Path to git repository (None = current directory)

    Returns:
        Next version string or None if not in a git repository
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


def get_git_remote_url(directory: Optional[Path] = None) -> Optional[str]:
    """Get the git remote URL.

    Args:
        directory: Path to git repository (None = current directory)

    Returns:
        Cleaned remote URL or None if not available
    """
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


def get_module_name_from_path(directory: Optional[Path] = None) -> str:
    """Get module name from directory name or git repository name.

    Args:
        directory: Path to directory (None = current directory)

    Returns:
        Module name extracted from git remote or directory name
    """
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
