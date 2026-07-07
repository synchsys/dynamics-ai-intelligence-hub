"""The GenAI evaluation set (#66) — labelled summary/answer cases.

Each case pairs a **source** (the grounding context) and a **prompt** with the
**output** under evaluation, plus the relevance **keywords** a good output should
contain. Kept as data so the eval is reproducible and can grow. The set mixes
faithful outputs with a few deliberately flawed ones (``should_pass=False``) —
ungrounded (facts not in the source) or off-topic — so the harness demonstrably
*catches* weaknesses rather than only rubber-stamping good output.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class GenAICase:
    """One GenAI output to evaluate against its source and expected cues."""

    id: str
    task: str  # "summary" | "answer"
    source: str  # grounding context the output must stay faithful to
    prompt: str  # the question / instruction that produced the output
    output: str  # the generated text under evaluation
    keywords: tuple[str, ...]  # relevance cues a good output contains
    should_pass: bool = True  # False for intentionally-flawed cases


_MONZA = (
    "The Italian Grand Prix was held at Monza. Verstappen started on pole and led "
    "every lap to win ahead of Norris and Leclerc. Hamilton retired with an engine "
    "failure on lap 40. It was a dry race run on the medium and hard tyre compounds."
)
_SUPPORT = (
    "Case CASE-0007 was raised by Acme Systems reporting an outage of the billing "
    "portal. Priority is High. The support agent restored service by restarting the "
    "gateway and the case was resolved the same day."
)
_ACCOUNT = (
    "Account Apex Dynamics is based in Cork. It has three open opportunities worth a "
    "combined 180,000 and one active support case about integration errors."
)


DEFAULT_EVAL_SET: tuple[GenAICase, ...] = (
    # --- faithful summaries ---
    GenAICase(
        "sum-monza-1",
        "summary",
        _MONZA,
        "Summarise the race.",
        "Verstappen won the Italian Grand Prix at Monza from pole ahead of Norris and "
        "Leclerc; Hamilton retired with engine failure.",
        ("verstappen", "monza", "norris"),
    ),
    GenAICase(
        "sum-monza-2",
        "summary",
        _MONZA,
        "Summarise the race.",
        "It was a dry race at Monza on medium and hard compounds; Verstappen led every lap.",
        ("dry", "monza", "compounds"),
    ),
    GenAICase(
        "sum-support-1",
        "summary",
        _SUPPORT,
        "Summarise the case.",
        "Case CASE-0007 from Acme Systems reported a billing portal outage; the agent "
        "restarted the gateway and resolved it the same day.",
        ("acme", "outage", "resolved"),
    ),
    GenAICase(
        "sum-account-1",
        "summary",
        _ACCOUNT,
        "Summarise the account.",
        "Apex Dynamics, based in Cork, has three open opportunities and one active "
        "support case about integration errors.",
        ("apex", "cork", "opportunities"),
    ),
    # --- faithful answers ---
    GenAICase(
        "ans-winner",
        "answer",
        _MONZA,
        "Who won and where?",
        "Verstappen won the Italian Grand Prix at Monza.",
        ("verstappen", "monza"),
    ),
    GenAICase(
        "ans-retire",
        "answer",
        _MONZA,
        "Why did Hamilton retire?",
        "Hamilton retired with an engine failure on lap 40.",
        ("hamilton", "engine"),
    ),
    GenAICase(
        "ans-tyres",
        "answer",
        _MONZA,
        "Which tyre compounds were used?",
        "The race used the medium and hard tyre compounds.",
        ("medium", "hard"),
    ),
    GenAICase(
        "ans-case-priority",
        "answer",
        _SUPPORT,
        "What priority is the case?",
        "Case CASE-0007 is High priority.",
        ("high", "priority"),
    ),
    GenAICase(
        "ans-case-fix",
        "answer",
        _SUPPORT,
        "How was the case resolved?",
        "The agent restarted the gateway, restoring the billing portal.",
        ("gateway", "restart"),
    ),
    GenAICase(
        "ans-account-city",
        "answer",
        _ACCOUNT,
        "Where is the account based?",
        "Apex Dynamics is based in Cork.",
        ("cork",),
    ),
    # --- deliberately flawed (harness should flag these) ---
    GenAICase(
        "flaw-ungrounded",
        "summary",
        _MONZA,
        "Summarise the race.",
        "The quarterly earnings call reported strong shareholder dividends and a new "
        "product launch in the enterprise cloud division.",
        ("verstappen", "monza"),
        should_pass=False,
    ),  # hallucinated: nothing from source
    GenAICase(
        "flaw-offtopic",
        "answer",
        _SUPPORT,
        "How was the case resolved?",
        "Acme Systems is a company that uses a billing portal.",
        ("gateway", "restart"),
        should_pass=False,
    ),  # grounded but misses the ask
    GenAICase(
        "flaw-both",
        "answer",
        _ACCOUNT,
        "Where is the account based?",
        "The weather forecast predicts rain across the northern counties tomorrow.",
        ("cork",),
        should_pass=False,
    ),  # ungrounded AND irrelevant
)
