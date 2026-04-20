"""Score arxiv papers for implementation-ability."""
from __future__ import annotations

import re
from typing import Any

# Keywords that strongly suggest a novel implementable contribution
HIGH_VALUE_KEYWORDS = [
    r"\bwe propose\b",
    r"\bwe present\b",
    r"\bwe introduce\b",
    r"\bour method\b",
    r"\bour model\b",
    r"\bour approach\b",
    r"\bour framework\b",
    r"\bour architecture\b",
    r"\bnew architecture\b",
    r"\bnovel architecture\b",
    r"\bnovel algorithm\b",
    r"\bnew algorithm\b",
    r"\balgorithm\b",
    r"\barchitecture\b",
    r"\bimplementation\b",
    r"\bcode is available\b",
    r"\bcode available\b",
    r"\bopen.?source\b",
    r"\bgithub\.com\b",
    r"\btraining procedure\b",
    r"\btraining pipeline\b",
]

# Keywords that reduce score (survey/theoretical/analysis-only papers)
PENALTY_KEYWORDS = [
    r"\bsurvey\b",
    r"\bliterature review\b",
    r"\bsystematic review\b",
    r"\bmeta.?analysis\b",
    r"\bwe analyze\b",
    r"\banalysis of\b",
    r"\btheoretical analysis\b",
    r"\bwe study\b",
    r"\bposition paper\b",
]

# Bonus keywords for clear technical implementations
BONUS_KEYWORDS = [
    r"\btransformer\b",
    r"\bneural network\b",
    r"\btraining\b",
    r"\bfine.?tun\b",
    r"\bbenchmark\b",
    r"\bstate.of.the.art\b",
    r"\bSOTA\b",
    r"\bexperiments show\b",
    r"\bwe evaluate\b",
    r"\bbaseline\b",
    r"\bmodule\b",
    r"\blayer\b",
    r"\bencoder\b",
    r"\bdecoder\b",
    r"\battention\b",
]


def score_paper(paper: dict[str, Any]) -> float:
    """
    Score a paper for implementation-ability on a 0-10 scale.

    Uses heuristics based on:
    - Presence of high-value keywords in title + abstract
    - Absence of penalty keywords
    - Bonus for technical implementation details
    """
    text = (paper.get("title", "") + " " + paper.get("abstract", "")).lower()

    score = 0.0

    # High-value keywords (each worth 1.0, max 5.0)
    hv_hits = sum(1 for pat in HIGH_VALUE_KEYWORDS if re.search(pat, text, re.IGNORECASE))
    score += min(hv_hits * 1.0, 5.0)

    # Bonus keywords (each worth 0.4, max 3.0)
    bonus_hits = sum(1 for pat in BONUS_KEYWORDS if re.search(pat, text, re.IGNORECASE))
    score += min(bonus_hits * 0.4, 3.0)

    # Penalties (each worth -1.5, min penalty -3.0)
    penalty_hits = sum(1 for pat in PENALTY_KEYWORDS if re.search(pat, text, re.IGNORECASE))
    score -= min(penalty_hits * 1.5, 3.0)

    # Title bonus: if title looks like a named method/model (+1.0)
    title = paper.get("title", "")
    if re.search(r"^[A-Z][A-Za-z0-9]+([-:]\s|\s[A-Z])", title):
        score += 0.5  # Looks like a named system (e.g. "GPT-4: ..." or "FlashAttn ...")

    # Clamp to [0, 10]
    score = max(0.0, min(10.0, score))
    return round(score, 2)


def rank_papers(papers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return papers sorted by score descending, with score added."""
    scored = []
    for p in papers:
        p_copy = dict(p)
        p_copy["score"] = score_paper(p)
        scored.append(p_copy)
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored
