"""The RAG evaluation set — questions with expected sources (#74).

Each case pairs a question with the section it should be answered from and a few
keywords a relevant answer should contain. Kept as data so the eval is
reproducible and can grow. The default set targets a small F1 sporting-regulations
corpus (one section per topic).
"""

from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class EvalCase:
    """One evaluation question with its expected source section and answer cues."""

    question: str
    expected_section: str
    keywords: tuple[str, ...] = ()
    roles: Sequence[str] = ("employee",)


# The knowledge corpus the default set expects (source, markdown). One H1 section
# per topic; section titles are the expected retrieval targets.
DEFAULT_CORPUS: tuple[tuple[str, str], ...] = (
    (
        "regs.md",
        "# DRS\n\nThe drag reduction system may be used only within designated activation "
        "zones, and only when a driver is within one second of the car ahead.\n\n"
        "# Safety Car\n\nWhen the safety car is deployed, overtaking is forbidden and drivers "
        "must reduce speed and hold position until the track is clear.\n\n"
        "# Pit Stops\n\nThe pit lane has a strictly enforced speed limit; an unsafe release "
        "from a pit stop is penalised by the stewards.\n\n"
        "# Track Limits\n\nA driver who leaves the track and gains a lasting advantage must "
        "give the position back or face a penalty.\n\n"
        "# Points\n\nChampionship points are awarded to the top ten finishers, with an extra "
        "point for the fastest lap if the driver finishes in the points.\n\n"
        "# Flags\n\nA blue flag warns a driver that a faster car is about to lap them and they "
        "must let it pass.\n\n"
        "# Tyres\n\nEach driver must use at least two different dry tyre compounds during a "
        "dry race.\n\n"
        "# Formation Lap\n\nDrivers complete a formation lap before the start; overtaking is "
        "not permitted unless a car is delayed.\n\n"
        "# Parc Ferme\n\nUnder parc fermé conditions teams may not change the car setup "
        "without incurring a penalty.\n\n"
        "# Penalties\n\nStewards may impose time penalties, grid drops, or drive-through "
        "penalties for breaches of the sporting regulations.",
    ),
)


DEFAULT_EVAL_SET: tuple[EvalCase, ...] = (
    EvalCase("When can a driver use DRS?", "DRS", ("zone", "one second")),
    EvalCase(
        "Is overtaking allowed under the safety car?", "Safety Car", ("overtaking", "forbidden")
    ),
    EvalCase("What happens on an unsafe pit release?", "Pit Stops", ("penalised", "pit")),
    EvalCase(
        "What if a driver gains an advantage off track?", "Track Limits", ("advantage", "penalty")
    ),
    EvalCase("How are championship points awarded?", "Points", ("ten", "point")),
    EvalCase("What does a blue flag mean?", "Flags", ("blue", "pass")),
    EvalCase("How many tyre compounds must be used in a dry race?", "Tyres", ("two", "compound")),
    EvalCase(
        "Is overtaking allowed on the formation lap?", "Formation Lap", ("formation", "overtaking")
    ),
    EvalCase("Can teams change setup under parc fermé?", "Parc Ferme", ("setup", "penalty")),
    EvalCase("What penalties can stewards impose?", "Penalties", ("penalty", "stewards")),
    EvalCase("When is the fastest-lap point awarded?", "Points", ("fastest lap", "point")),
    EvalCase("What must a driver do when shown a blue flag?", "Flags", ("let", "pass")),
)


def default_cases() -> tuple[EvalCase, ...]:
    return DEFAULT_EVAL_SET


def merged_corpus(access_tag: str = "public") -> list[tuple[str, str, str]]:
    """The default corpus as ``(source, text, access_tag)`` for ``ingest_markdown``."""
    return [(source, text, access_tag) for source, text in DEFAULT_CORPUS]
