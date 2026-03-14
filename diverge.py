#!/usr/bin/env python3
"""Diverge — Multi-Agent Creativity Engine.

Forces multiple AI agents into deliberately opposing thinking directions,
then synthesizes the divergent outputs to produce genuinely creative ideas.

Usage:
    python3 diverge.py --problem "your problem here"
    python3 diverge.py --problem "mean reversion crypto" --domain trading
    python3 diverge.py --problem "AI triage for ED" --domain clinical --rounds 2
"""

import argparse
import asyncio
import json
import os
import sys
from dataclasses import asdict, dataclass, field

import anthropic

from lenses import Lens, available_domains, get_lenses

MODEL = "claude-sonnet-4-20250514"


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

@dataclass
class AgentOutput:
    lens_name: str
    lens_color: str
    ideas: str  # Raw text from the agent


@dataclass
class Synthesis:
    round_num: int
    problem: str
    agent_outputs: list[AgentOutput]
    overlaps: str
    hybrid_ideas: str
    most_counterintuitive: str
    novel_framing: str
    top_ideas: str
    raw_synthesis: str


@dataclass
class DivergenceResult:
    problem: str
    domain: str
    rounds: list[Synthesis] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class DivergenceEngine:
    def __init__(self, model: str = MODEL):
        self.client = anthropic.AsyncAnthropic()
        self.model = model

    async def _run_agent(self, problem: str, lens: Lens) -> AgentOutput:
        """Run a single divergent agent."""
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=1500,
            messages=[
                {
                    "role": "user",
                    "content": f"Problem: {problem}\n\n{lens.system_prompt}",
                }
            ],
        )
        text = response.content[0].text
        return AgentOutput(
            lens_name=lens.name,
            lens_color=lens.color,
            ideas=text,
        )

    async def _synthesize_call(
        self, problem: str, agent_outputs: list[AgentOutput]
    ) -> str:
        """Call Claude to synthesize divergent outputs."""
        outputs_text = "\n\n---\n\n".join(
            f"## {o.lens_name} ({o.lens_color})\n{o.ideas}" for o in agent_outputs
        )
        prompt = f"""You are synthesizing outputs from multiple divergent-thinking agents who each approached the same problem from radically different angles.

Problem: {problem}

Agent outputs:
{outputs_text}

Analyze these outputs and produce a synthesis with the following sections:

### Surprising Overlaps
Did 2+ agents independently converge on a similar insight? This is a strong signal.

### Hybrid Ideas
Combine elements from different agents into ideas none individually produced.

### Most Counterintuitive Viable Idea
The single idea that sounds most wrong but has the strongest logical grounding.

### Novel Framing
Reframe the original problem based on what the divergent exploration revealed.

### Top 3 Ideas (Ranked)
For each:
- **Idea**: One-line summary
- **Origin**: Which agent(s) produced it
- **Why it's interesting**: What makes this non-obvious
- **First step**: One concrete action to test it

Be genuinely creative, not encyclopedic. The whole point is to escape median AI answers."""

        response = await self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    async def diverge(
        self,
        problem: str,
        domain: str = "general",
        num_agents: int = 3,
    ) -> DivergenceResult:
        """Run a single round of divergent thinking."""
        lenses = get_lenses(domain, num_agents)
        result = DivergenceResult(problem=problem, domain=domain)

        synthesis = await self._run_round(problem, lenses, round_num=1)
        result.rounds.append(synthesis)
        return result

    async def _run_round(
        self, problem: str, lenses: list[Lens], round_num: int
    ) -> Synthesis:
        """Execute one diverge-then-synthesize round."""
        # Phase 1: Run agents in parallel
        agent_outputs = await asyncio.gather(
            *[self._run_agent(problem, lens) for lens in lenses]
        )

        # Phase 2: Synthesize
        raw_synthesis = await self._synthesize_call(problem, list(agent_outputs))

        return Synthesis(
            round_num=round_num,
            problem=problem,
            agent_outputs=list(agent_outputs),
            overlaps="",  # Extracted from raw_synthesis for structured access
            hybrid_ideas="",
            most_counterintuitive="",
            novel_framing="",
            top_ideas="",
            raw_synthesis=raw_synthesis,
        )

    async def chain(
        self,
        problem: str,
        domain: str = "general",
        rounds: int = 2,
        num_agents: int = 3,
    ) -> DivergenceResult:
        """Chain multiple diverge rounds — each round's synthesis feeds the next."""
        lenses = get_lenses(domain, num_agents)
        result = DivergenceResult(problem=problem, domain=domain)

        current_problem = problem
        for r in range(1, rounds + 1):
            synthesis = await self._run_round(current_problem, lenses, round_num=r)
            result.rounds.append(synthesis)

            if r < rounds:
                # Feed synthesis into next round as a refined problem
                current_problem = (
                    f"Original problem: {problem}\n\n"
                    f"Previous round's synthesis (build on this, go deeper):\n"
                    f"{synthesis.raw_synthesis}"
                )

        return result

    def synthesize(self, agent_outputs: list[AgentOutput]) -> str:
        """Synchronous synthesis for external callers."""
        return asyncio.run(
            self._synthesize_call("(see agent outputs)", agent_outputs)
        )


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

COLOR_MAP = {
    "red": "\033[91m",
    "magenta": "\033[95m",
    "yellow": "\033[93m",
    "green": "\033[92m",
    "blue": "\033[94m",
}
RESET = "\033[0m"
BOLD = "\033[1m"


def print_result(result: DivergenceResult, use_json: bool = False):
    if use_json:
        # Serialize to JSON
        data = {
            "problem": result.problem,
            "domain": result.domain,
            "rounds": [
                {
                    "round": s.round_num,
                    "agents": [
                        {"lens": o.lens_name, "ideas": o.ideas}
                        for o in s.agent_outputs
                    ],
                    "synthesis": s.raw_synthesis,
                }
                for s in result.rounds
            ],
        }
        print(json.dumps(data, indent=2))
        return

    print(f"\n{BOLD}{'=' * 60}")
    print(f"DIVERGE — {result.problem}")
    print(f"Domain: {result.domain}")
    print(f"{'=' * 60}{RESET}\n")

    for synthesis in result.rounds:
        print(f"{BOLD}--- Round {synthesis.round_num} ---{RESET}\n")

        for output in synthesis.agent_outputs:
            color = COLOR_MAP.get(output.lens_color, "")
            print(f"{color}{BOLD}[{output.lens_name}]{RESET}")
            print(f"{output.ideas}\n")

        print(f"{BOLD}--- Synthesis ---{RESET}\n")
        print(synthesis.raw_synthesis)
        print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Diverge — Multi-Agent Creativity Engine"
    )
    parser.add_argument(
        "--problem", "-p", required=True, help="The problem or idea to explore"
    )
    parser.add_argument(
        "--domain",
        "-d",
        default="general",
        choices=available_domains(),
        help="Domain preset for lens selection (default: general)",
    )
    parser.add_argument(
        "--rounds",
        "-r",
        type=int,
        default=1,
        help="Number of chained diverge rounds (default: 1)",
    )
    parser.add_argument(
        "--agents",
        "-n",
        type=int,
        default=3,
        help="Number of agents per round (default: 3)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON instead of formatted text",
    )

    args = parser.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    engine = DivergenceEngine()

    if args.rounds > 1:
        result = asyncio.run(
            engine.chain(args.problem, args.domain, args.rounds, args.agents)
        )
    else:
        result = asyncio.run(
            engine.diverge(args.problem, args.domain, args.agents)
        )

    print_result(result, use_json=args.json)


if __name__ == "__main__":
    main()
