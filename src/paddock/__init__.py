"""Paddock Club — the virtual-credit F1 predictions game (Epic 13).

Deterministic settlement over ingested OpenF1 data; the LLM proposes a
settlement spec at intake, code grades it (ADR-0008).
"""

from paddock.odds import FormTable, HeuristicPricer, Odds, OddsPricer, price_probability

# Note: the ML model pricer (paddock.odds_model.ModelPricer, #232) is not exported
# here because it requires the optional `analytics` extra (scikit-learn); import it
# directly with `from paddock.odds_model import ModelPricer`.

__all__ = ["Odds", "OddsPricer", "HeuristicPricer", "FormTable", "price_probability"]
