"""Tests for the prompt library — deterministic rendering + variable checks."""

import pytest

from ai.prompts import LIBRARY, PromptError, PromptTemplate, get, render
from ai.prompts.library import _placeholders


def test_library_has_at_least_three_templates() -> None:
    assert len(LIBRARY) >= 3


def test_placeholders_are_derived_and_deduped() -> None:
    tmpl = PromptTemplate(name="t", system="{a} and {b}", user="{a} again")
    assert tmpl.required_variables == ("a", "b")


def test_render_produces_system_and_user_messages() -> None:
    messages = render("crm_qa", context="Account: Acme (id 1)", question="Who is Acme?")
    assert [m["role"] for m in messages] == ["system", "user"]
    assert "Acme (id 1)" in messages[0]["content"]
    assert messages[1]["content"] == "Who is Acme?"


def test_render_accepts_values_mapping() -> None:
    messages = render("crm_qa", {"context": "ctx", "question": "q?"})
    assert messages[0]["content"].endswith("ctx")
    assert messages[1]["content"] == "q?"


def test_summarise_template_renders_max_words() -> None:
    messages = render("summarise_activity", max_words=30, activity="Called customer.")
    assert "30 words" in messages[0]["content"]
    assert "Called customer." in messages[1]["content"]


def test_account_briefing_uses_both_fields() -> None:
    messages = render("account_briefing", account="Acme", activities="Call on Monday")
    assert "Acme" in messages[1]["content"]
    assert "Call on Monday" in messages[1]["content"]


def test_missing_variable_raises_prompt_error() -> None:
    with pytest.raises(PromptError, match="missing variables: question"):
        render("crm_qa", context="ctx")


def test_unknown_template_raises_prompt_error() -> None:
    with pytest.raises(PromptError, match="no prompt template named 'nope'"):
        get("nope")


def test_placeholders_helper_ignores_literals() -> None:
    assert _placeholders("no vars here", "just {x}") == ("x",)
