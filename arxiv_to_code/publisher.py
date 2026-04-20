"""Publish generated code to GitHub under a given org."""
from __future__ import annotations

import logging
import os
import subprocess
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def _sanitize_repo_name(title: str) -> str:
    """Convert a paper title to a valid GitHub repo name."""
    import re

    name = title.lower()
    name = re.sub(r"[^a-z0-9\s-]", "", name)
    name = re.sub(r"\s+", "-", name.strip())
    name = re.sub(r"-+", "-", name)
    return name[:50].rstrip("-") or "arxiv-paper"


def publish_to_github(
    paper: dict[str, Any],
    code_dir: Path,
    org: str = "AlexChen31337",
) -> str | None:
    """
    Create a GitHub repository and push the generated code.

    Args:
        paper: Paper dict with title and arxiv_id.
        code_dir: Directory containing generated code.
        org: GitHub org/user to create repo under.

    Returns:
        GitHub repo URL or None on failure.
    """
    repo_name = _sanitize_repo_name(paper["title"])
    full_repo = f"{org}/{repo_name}"
    description = f"Auto-generated scaffold from arxiv:{paper['arxiv_id']} — {paper['title'][:80]}"

    logger.info("Creating GitHub repo: %s", full_repo)

    # Init git in code_dir if needed
    git_dir = code_dir / ".git"
    if not git_dir.exists():
        subprocess.run(["git", "init"], cwd=code_dir, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "alex.chen31337@gmail.com"],
            cwd=code_dir,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Alex Chen"],
            cwd=code_dir,
            check=True,
            capture_output=True,
        )

    # Stage and commit
    subprocess.run(["git", "add", "."], cwd=code_dir, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", f"Initial scaffold for {paper['title'][:60]}"],
        cwd=code_dir,
        check=True,
        capture_output=True,
    )

    # Create repo via gh CLI
    result = subprocess.run(
        [
            "gh", "repo", "create", full_repo,
            "--public",
            "--description", description,
            "--source", str(code_dir),
            "--push",
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        logger.error("gh repo create failed: %s", result.stderr)
        return None

    repo_url = f"https://github.com/{full_repo}"
    logger.info("Published to %s", repo_url)
    return repo_url
