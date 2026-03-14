# Diverge — Multi-Agent Creativity Engine

## What This Is
Forces multiple AI agents into deliberately opposing thinking directions, then synthesizes the divergent outputs to produce genuinely creative ideas. Based on divergent/convergent thinking research applied to LLM multi-agent orchestration.

## Key Files
- `diverge.py` — Main engine, CLI entry point
- `lenses.py` — Lens definitions (thinking constraints) organized by domain
- `~/.claude/commands/diverge.md` — Claude Code slash command version

## Domains
- **general** — Inverter / Analogist / Constraint Breaker
- **trading** — Bull Thesis / Bear Thesis / Regime Change
- **clinical** — Patient-First / Provider-First / System-First

## Usage
```bash
# CLI
python3 diverge.py --problem "your problem" --domain general --rounds 1

# Claude Code slash command
/diverge "your problem"
```

## Development Notes
- Uses `anthropic` Python SDK with direct API calls
- Agents run concurrently via `asyncio.gather`
- Open Brain integration is optional — works without it
- Adding a new domain: define lenses in `lenses.py`, add to `DOMAIN_PRESETS`
