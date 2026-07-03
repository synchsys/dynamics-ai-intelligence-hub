"""A small, versioned prompt library (#59, 8.2).

Parameterised system + user templates, rendered to the message list the
``AIClient`` expects. Required variables are derived from the template text
(via ``string.Formatter``) so metadata can't drift from the prompt, and a
missing variable is a clear :class:`PromptError` rather than a raw ``KeyError``
at call time. Reused by AI summaries (#62) and the CRM assistant (#63).
"""

import string
from collections.abc import Mapping
from dataclasses import dataclass


class PromptError(Exception):
    """A prompt template was missing required variables or does not exist."""


def _placeholders(*texts: str) -> tuple[str, ...]:
    names: list[str] = []
    for text in texts:
        for _literal, field, _spec, _conv in string.Formatter().parse(text):
            if field:
                names.append(field)
    return tuple(dict.fromkeys(names))  # de-duped, order-preserving


@dataclass(frozen=True)
class PromptTemplate:
    """A named system+user prompt pair with declared, auto-derived variables."""

    name: str
    system: str
    user: str

    @property
    def required_variables(self) -> tuple[str, ...]:
        return _placeholders(self.system, self.user)

    def render(self, **values: object) -> list[dict[str, str]]:
        """Render to a ``[{system}, {user}]`` message list, substituting ``values``."""
        missing = [v for v in self.required_variables if v not in values]
        if missing:
            raise PromptError(f"prompt '{self.name}' is missing variables: {', '.join(missing)}")
        return [
            {"role": "system", "content": self.system.format(**values)},
            {"role": "user", "content": self.user.format(**values)},
        ]


# --- templates --------------------------------------------------------------

CRM_QA = PromptTemplate(
    name="crm_qa",
    system=(
        "You are a helpful assistant for a CRM system. Answer the user's question "
        "using ONLY the CRM context provided below. If the context does not contain "
        "the answer, say you don't have that information — never invent records, "
        "names, or figures. Refer to records by their identifiers where relevant.\n\n"
        "CRM context:\n{context}"
    ),
    user="{question}",
)

SUMMARISE_ACTIVITY = PromptTemplate(
    name="summarise_activity",
    system=(
        "You summarise CRM activity records. Produce a concise, factual summary in "
        "at most {max_words} words. Do not add information beyond the record."
    ),
    user="Summarise this activity:\n{activity}",
)

ACCOUNT_BRIEFING = PromptTemplate(
    name="account_briefing",
    system=(
        "You brief a salesperson on an account before a call. Using only the data "
        "provided, give a short briefing covering who they are, recent interactions, "
        "and any open items. Be factual and concise."
    ),
    user="Account data:\n{account}\n\nRecent activities:\n{activities}",
)

LIBRARY: dict[str, PromptTemplate] = {
    template.name: template for template in (CRM_QA, SUMMARISE_ACTIVITY, ACCOUNT_BRIEFING)
}


def get(name: str) -> PromptTemplate:
    """Return the named template, or raise :class:`PromptError` if unknown."""
    try:
        return LIBRARY[name]
    except KeyError:
        raise PromptError(f"no prompt template named '{name}'") from None


def render(
    name: str, values: Mapping[str, object] | None = None, /, **kwargs: object
) -> list[dict[str, str]]:
    """Render a named template. Accepts a values mapping and/or keyword variables."""
    merged: dict[str, object] = {**(values or {}), **kwargs}
    return get(name).render(**merged)
