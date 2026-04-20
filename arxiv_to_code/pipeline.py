"""Main pipeline: fetch → score → build → publish."""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fetch recent arxiv papers, score them, and optionally generate code scaffolds."
    )
    parser.add_argument("--hours", type=int, default=48, help="Hours back to scan (default: 48)")
    parser.add_argument(
        "--max-results", type=int, default=100, help="Max papers to fetch (default: 100)"
    )
    parser.add_argument(
        "--org", type=str, default="AlexChen31337", help="GitHub org for publishing (default: AlexChen31337)"
    )
    parser.add_argument(
        "--top-n", type=int, default=5, help="Number of top papers to report (default: 5)"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="/tmp/arxiv-to-code-build/output",
        help="Output directory for generated code",
    )
    parser.add_argument(
        "--skip-build", action="store_true", help="Skip code generation even if API key is set"
    )
    parser.add_argument(
        "--skip-publish", action="store_true", help="Skip publishing to GitHub"
    )
    args = parser.parse_args()

    # --- Step 1: Fetch ---
    print(f"\n{'='*60}")
    print(f"Arxiv-to-Code Pipeline")
    print(f"{'='*60}")
    print(f"Scanning last {args.hours} hours, max {args.max_results} results...")

    from arxiv_to_code.fetcher import fetch_recent_papers
    papers = fetch_recent_papers(hours=args.hours, max_results=args.max_results)
    print(f"\n✓ Fetched {len(papers)} papers")

    if not papers:
        print("No papers found in the given time window. Exiting.")
        sys.exit(0)

    # --- Step 2: Score ---
    from arxiv_to_code.scorer import rank_papers
    ranked = rank_papers(papers)
    print(f"✓ Scored {len(ranked)} papers")

    # Report top N
    top_n = ranked[: args.top_n]
    print(f"\n{'='*60}")
    print(f"Top {args.top_n} Papers by Implementability Score")
    print(f"{'='*60}")
    for i, p in enumerate(top_n, 1):
        print(f"\n#{i} [{p['score']}/10] {p['title']}")
        print(f"   arxiv_id : {p['arxiv_id']}")
        print(f"   url      : {p['url']}")
        print(f"   published: {p.get('published', 'N/A')}")
        print(f"   authors  : {', '.join(p['authors'][:3])}{'...' if len(p['authors']) > 3 else ''}")
        abstract_preview = p["abstract"][:200].replace("\n", " ")
        print(f"   abstract : {abstract_preview}...")

    # --- Step 3: Build (optional) ---
    import os
    api_key = os.environ.get("OPENAI_API_KEY", "")
    code_dir = None
    built_paper = None

    if args.skip_build:
        print("\n[Build step skipped via --skip-build]")
    elif not api_key:
        print("\n[Build step skipped: OPENAI_API_KEY not set]")
    else:
        top_paper = ranked[0]
        print(f"\n{'='*60}")
        print(f"Generating code scaffold for top paper:")
        print(f"  {top_paper['title']}")
        print(f"{'='*60}")

        from arxiv_to_code.builder import build_scaffold
        code_dir = build_scaffold(top_paper, output_dir=args.output_dir)
        if code_dir:
            built_paper = top_paper
            print(f"✓ Code scaffold generated at: {code_dir}")
            for f in sorted(Path(code_dir).iterdir()):
                print(f"   - {f.name}")
        else:
            print("✗ Code generation failed (check logs)")

    # --- Step 4: Publish (optional) ---
    repo_url = None
    if code_dir and built_paper and not args.skip_publish:
        print(f"\n{'='*60}")
        print(f"Publishing to GitHub ({args.org})...")
        print(f"{'='*60}")
        from arxiv_to_code.publisher import publish_to_github
        repo_url = publish_to_github(built_paper, code_dir, org=args.org)
        if repo_url:
            print(f"✓ Published: {repo_url}")
        else:
            print("✗ Publishing failed (check logs)")
    elif code_dir and built_paper:
        print("\n[Publish step skipped via --skip-publish]")

    # --- Summary ---
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Papers scanned  : {len(papers)}")
    print(f"Top paper       : {ranked[0]['title'][:70]}")
    print(f"Top score       : {ranked[0]['score']}/10")
    print(f"Code generated  : {'Yes → ' + str(code_dir) if code_dir else 'No'}")
    print(f"GitHub repo     : {repo_url or 'Not published'}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
