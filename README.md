# arxiv-to-code

Auto-implements arxiv papers as Python code scaffolds.

## Features

- Fetches recent CS/AI papers from arxiv (cs.AI, cs.LG, cs.CL, cs.CV, stat.ML)
- Scores papers by implementation-ability using keyword heuristics
- Generates Python code scaffolds via OpenAI API (optional)
- Publishes generated code to GitHub (optional)

## Usage

```bash
# Fetch and score papers from the last 48 hours
uv run python -m arxiv_to_code.pipeline --hours 48 --max-results 100

# With code generation and publishing
OPENAI_API_KEY=sk-... uv run python -m arxiv_to_code.pipeline \
    --hours 48 --max-results 100 --org AlexChen31337
```

## Arguments

| Flag | Default | Description |
|------|---------|-------------|
| `--hours` | 48 | Hours back to scan |
| `--max-results` | 100 | Max papers to fetch |
| `--org` | AlexChen31337 | GitHub org for publishing |
| `--top-n` | 5 | Number of top papers to report |
| `--skip-build` | false | Skip code generation |
| `--skip-publish` | false | Skip GitHub publishing |

## Environment Variables

- `OPENAI_API_KEY` — Required for code generation step
- `OPENAI_MODEL` — Override model (default: `gpt-4o-mini`)

## License

MIT
