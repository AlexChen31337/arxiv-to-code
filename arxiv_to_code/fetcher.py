"""Fetch recent papers from arxiv for CS/AI categories."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

import arxiv

logger = logging.getLogger(__name__)

CATEGORIES = ["cs.AI", "cs.LG", "cs.CL", "cs.CV", "stat.ML"]


def fetch_recent_papers(hours: int = 48, max_results: int = 100) -> list[dict[str, Any]]:
    """
    Fetch recent papers from arxiv filtered to CS/AI categories.

    Args:
        hours: How many hours back to look.
        max_results: Maximum number of papers to fetch.

    Returns:
        List of dicts with keys: arxiv_id, title, abstract, authors, url, published.
    """
    cutoff = datetime.now(tz=timezone.utc) - timedelta(hours=hours)
    logger.info("Fetching papers since %s (last %d hours)", cutoff.isoformat(), hours)

    # Build category query
    cat_query = " OR ".join(f"cat:{c}" for c in CATEGORIES)
    query = f"({cat_query})"

    client = arxiv.Client(page_size=100, delay_seconds=3, num_retries=3)
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
        sort_order=arxiv.SortOrder.Descending,
    )

    papers: list[dict[str, Any]] = []
    for result in client.results(search):
        # Only keep papers submitted within the time window
        if result.published and result.published < cutoff:
            break

        arxiv_id = result.entry_id.split("/abs/")[-1]
        papers.append(
            {
                "arxiv_id": arxiv_id,
                "title": result.title.strip(),
                "abstract": result.summary.strip(),
                "authors": [a.name for a in result.authors],
                "url": result.entry_id,
                "published": result.published.isoformat() if result.published else None,
                "categories": result.categories,
            }
        )

    logger.info("Fetched %d papers within the last %d hours", len(papers), hours)
    return papers
