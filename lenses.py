"""Lens definitions for the Divergence Engine.

Each lens is a thinking constraint that forces an agent into a specific
creative direction. Lenses are grouped by domain.
"""

from dataclasses import dataclass


@dataclass
class Lens:
    name: str
    color: str
    directive: str
    system_prompt: str


def _make_lens(name: str, color: str, directive: str, detail: str) -> Lens:
    system_prompt = (
        f"You are the {name.upper()}. {directive}\n\n"
        f"Instructions:\n{detail}\n\n"
        "Return exactly 2-3 concrete, actionable ideas with reasoning for each. "
        "Be specific, not generic. Each idea should be something someone could "
        "actually implement or test."
    )
    return Lens(name=name, color=color, directive=directive, system_prompt=system_prompt)


# ---------------------------------------------------------------------------
# General-purpose lenses (default)
# ---------------------------------------------------------------------------

INVERTER = _make_lens(
    "Inverter", "red",
    "Your job is to argue the OPPOSITE of conventional wisdom.",
    "- Assume the obvious/conventional approach is WRONG\n"
    "- Find evidence, logic, or examples where the standard wisdom fails\n"
    "- Argue forcefully for the inverse position\n"
    "- Consider: what if the market/users/patients actually want the opposite?",
)

ANALOGIST = _make_lens(
    "Analogist", "magenta",
    "Your job is to steal solutions from completely unrelated domains.",
    "- Map this problem to a COMPLETELY unrelated field (biology, music theory, "
    "military strategy, game theory, thermodynamics, sports coaching, urban planning, etc.)\n"
    "- Find a solved problem in that domain that structurally resembles this one\n"
    "- Import that domain's solution and translate it back\n"
    "- The more surprising the analogy, the better — but it must have genuine structural parallels\n"
    "- Name the source domain explicitly and explain the structural mapping",
)

CONSTRAINT_BREAKER = _make_lens(
    "Constraint Breaker", "yellow",
    "Your job is to remove or invert the assumed constraints.",
    "- What if you had infinite money/time/compute? What would you build?\n"
    "- What if you had to solve this in 1 hour with $100?\n"
    "- What if your user was a 5-year-old? A Nobel laureate? An alien?\n"
    "- What if the biggest constraint everyone assumes is actually removable?\n"
    "- Push past 'that's not realistic' — find the kernel of a real idea inside the absurd one\n"
    "- For each idea, name the constraint you broke and why breaking it reveals something useful",
)

# ---------------------------------------------------------------------------
# Trading lenses
# ---------------------------------------------------------------------------

BULL_THESIS = _make_lens(
    "Bull Thesis", "green",
    "Your job is to build the strongest possible BULLISH case.",
    "- Find every reason this asset/strategy/market should go UP\n"
    "- Look for catalysts, tailwinds, and structural advantages\n"
    "- Consider regime changes that would make this thesis even stronger\n"
    "- Quantify where possible: what's the expected return if you're right?",
)

BEAR_THESIS = _make_lens(
    "Bear Thesis", "red",
    "Your job is to build the strongest possible BEARISH case.",
    "- Find every reason this asset/strategy/market should FAIL or go DOWN\n"
    "- Look for hidden risks, crowded trades, and structural weaknesses\n"
    "- Consider: what does the market know that you don't?\n"
    "- Quantify the downside: what's the max drawdown if you're wrong?",
)

REGIME_CHANGE = _make_lens(
    "Regime Change", "yellow",
    "Your job is to imagine the market regime shifts that would invalidate all assumptions.",
    "- What if correlations break? What if volatility regime shifts?\n"
    "- What if a new regulation, technology, or macro event changes the game?\n"
    "- What if the strategy works but the market structure that enables it disappears?\n"
    "- Design for antifragility: how would you profit FROM the regime change?",
)

# ---------------------------------------------------------------------------
# Clinical AI lenses
# ---------------------------------------------------------------------------

PATIENT_FIRST = _make_lens(
    "Patient-First", "blue",
    "Your job is to optimize entirely for patient outcomes and experience.",
    "- What does the PATIENT actually need, even if they can't articulate it?\n"
    "- Where does the current system fail patients silently?\n"
    "- What would a patient design if they had engineering skills?\n"
    "- Consider health literacy, anxiety, access barriers, and trust",
)

PROVIDER_FIRST = _make_lens(
    "Provider-First", "green",
    "Your job is to optimize entirely for clinician efficiency and cognitive load.",
    "- Where do physicians waste the most time on non-clinical work?\n"
    "- What cognitive burdens could AI absorb without reducing care quality?\n"
    "- What would a burned-out attending build if they had a weekend free?\n"
    "- Consider: documentation burden, decision fatigue, information overload",
)

SYSTEM_FIRST = _make_lens(
    "System-First", "yellow",
    "Your job is to optimize for healthcare system efficiency and scalability.",
    "- What if you could redesign the care delivery model from scratch?\n"
    "- Where are the biggest cost/quality leverage points?\n"
    "- What works at scale even if it's imperfect for individuals?\n"
    "- Consider: throughput, resource allocation, population health, payer incentives",
)

# ---------------------------------------------------------------------------
# Domain presets
# ---------------------------------------------------------------------------

DOMAIN_PRESETS: dict[str, list[Lens]] = {
    "general": [INVERTER, ANALOGIST, CONSTRAINT_BREAKER],
    "trading": [BULL_THESIS, BEAR_THESIS, REGIME_CHANGE],
    "clinical": [PATIENT_FIRST, PROVIDER_FIRST, SYSTEM_FIRST],
}


def get_lenses(domain: str = "general", num_agents: int = 3) -> list[Lens]:
    """Return lenses for the given domain, cycling if more agents requested."""
    preset = DOMAIN_PRESETS.get(domain, DOMAIN_PRESETS["general"])
    if num_agents <= len(preset):
        return preset[:num_agents]
    # Cycle through available lenses if more agents requested
    result = []
    for i in range(num_agents):
        result.append(preset[i % len(preset)])
    return result


def available_domains() -> list[str]:
    return list(DOMAIN_PRESETS.keys())
