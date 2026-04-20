"""Generate Python implementation scaffolds from arxiv papers using OpenAI."""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def build_scaffold(paper: dict[str, Any], output_dir: str | Path | None = None) -> Path | None:
    """
    Use OpenAI to generate a Python implementation scaffold for a paper.

    Args:
        paper: Paper dict with title, abstract, arxiv_id.
        output_dir: Base output directory. Defaults to /tmp/arxiv-to-code-build/output.

    Returns:
        Path to generated code directory, or None if generation failed.
    """
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        logger.warning("OPENAI_API_KEY not set — skipping code generation")
        return None

    try:
        from openai import OpenAI
    except ImportError:
        logger.error("openai package not installed")
        return None

    client = OpenAI(api_key=api_key)

    arxiv_id_safe = paper["arxiv_id"].replace("/", "_").replace(".", "_")
    if output_dir is None:
        output_dir = Path("/tmp/arxiv-to-code-build/output")
    out_path = Path(output_dir) / arxiv_id_safe
    out_path.mkdir(parents=True, exist_ok=True)

    prompt = f"""You are an expert ML engineer. Based on the following arxiv paper abstract, generate a clean, well-commented Python implementation scaffold.

Paper: {paper['title']}
Abstract: {paper['abstract'][:2000]}

Generate:
1. A main Python module implementing the core architecture/algorithm described
2. A README.md explaining what was implemented
3. A requirements.txt with necessary packages

Return your response as JSON with keys:
- "main_py": the main Python code (string)
- "readme_md": the README content (string)
- "requirements_txt": requirements (string)
- "filename": suggested filename for main_py (e.g. "model.py")

Be concrete and implement real classes/functions. Include docstrings. Use PyTorch if it's a neural network paper."""

    logger.info("Calling OpenAI API for paper: %s", paper["title"])
    try:
        response = client.chat.completions.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=4096,
        )
        content = response.choices[0].message.content
        data = json.loads(content)

        # Write files
        filename = data.get("filename", "model.py")
        (out_path / filename).write_text(data.get("main_py", ""), encoding="utf-8")
        (out_path / "README.md").write_text(data.get("readme_md", ""), encoding="utf-8")
        (out_path / "requirements.txt").write_text(
            data.get("requirements_txt", ""), encoding="utf-8"
        )

        logger.info("Generated scaffold at %s", out_path)
        return out_path

    except Exception as exc:
        logger.error("OpenAI API call failed: %s", exc)
        return None
