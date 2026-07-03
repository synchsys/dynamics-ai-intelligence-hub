"""Resolve a free-text driver reference to an OpenF1 ``driver_number``.

Used by intake (#230) before grading: an unresolved / ambiguous name yields
``None`` so the caller rejects-with-guidance or voids — never guesses.
"""

from openf1.models import Driver


def resolve_driver(reference: str | int, drivers: list[Driver]) -> int | None:
    """Return the ``driver_number`` for a name/acronym/number, or ``None`` if unresolved.

    A numeric reference is returned as-is. A string matches (case-insensitively)
    against full name, a surname within the full name, or acronym. Anything
    ambiguous (more than one match) or unmatched returns ``None``.
    """
    if isinstance(reference, int):
        return reference

    text = reference.strip().casefold()
    if not text:
        return None

    matches: set[int] = set()
    for driver in drivers:
        acronym = (driver.name_acronym or "").casefold()
        full = (driver.full_name or "").casefold()
        if text in (acronym, full) or (full and text in full.split()):
            matches.add(driver.driver_number)

    return matches.pop() if len(matches) == 1 else None
