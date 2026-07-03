"""Tests for RAG ingestion — chunk boundaries, overlap, and metadata."""

import pytest

from rag import (
    Chunk,
    Document,
    chunk_text,
    ingest,
    ingest_markdown,
    load_markdown,
    retag,
    split_markdown_sections,
)

LOREM = " ".join(f"word{i}" for i in range(300))  # ~2000 chars


# --- chunk_text -------------------------------------------------------------


def test_short_text_is_one_chunk() -> None:
    assert chunk_text("just a short sentence", size=800) == ["just a short sentence"]


def test_empty_text_yields_no_chunks() -> None:
    assert chunk_text("   \n  ", size=800) == []


def test_long_text_splits_into_multiple_bounded_chunks() -> None:
    chunks = chunk_text(LOREM, size=200, overlap=40)
    assert len(chunks) > 1
    assert all(len(c) <= 200 for c in chunks)
    assert all(c == c.strip() and c for c in chunks)


def test_chunks_overlap() -> None:
    chunks = chunk_text(LOREM, size=200, overlap=60)
    # The end of one chunk reappears at the start of the next (shared words).
    first_tail = chunks[0].split()[-1]
    assert first_tail in chunks[1].split()


def test_no_word_is_split_across_a_chunk_boundary() -> None:
    chunks = chunk_text(LOREM, size=200, overlap=40)
    for c in chunks:
        assert not c.startswith("ord") and not c.endswith("wor")  # no mid-"word123" cuts


def test_whitespace_is_normalised() -> None:
    assert chunk_text("a\n\n  b\t c", size=800) == ["a b c"]


def test_word_longer_than_size_is_hard_split() -> None:
    # No whitespace to snap to — the chunker must still make progress.
    solid = "a" * 500
    chunks = chunk_text(solid, size=100, overlap=20)
    assert len(chunks) >= 5
    assert "".join(chunks).startswith("a" * 100)


@pytest.mark.parametrize("size,overlap", [(0, 0), (100, 100), (100, 150), (100, -1)])
def test_invalid_size_overlap_raise(size: int, overlap: int) -> None:
    with pytest.raises(ValueError):
        chunk_text("x", size=size, overlap=overlap)


# --- markdown sections ------------------------------------------------------


def test_split_markdown_sections_by_heading() -> None:
    md = "# Title\n\nintro\n\n## Rules\n\nno overtaking\n\n## Safety\n\nyellow flags"
    sections = split_markdown_sections(md)
    titles = [t for t, _ in sections]
    assert titles == ["Title", "Rules", "Safety"]
    assert sections[1] == ("Rules", "no overtaking")


def test_preamble_before_first_heading_kept_with_none_title() -> None:
    sections = split_markdown_sections("preamble text\n\n# Heading\n\nbody")
    assert sections[0] == (None, "preamble text")


def test_no_headings_returns_single_untitled_section() -> None:
    assert split_markdown_sections("just body") == [(None, "just body")]


def test_heading_with_empty_body_is_skipped() -> None:
    # Two consecutive headings: the first has no body and is dropped.
    sections = split_markdown_sections("# A\n\n# B\n\nbody")
    assert sections == [("B", "body")]


def test_blank_markdown_returns_nothing() -> None:
    assert split_markdown_sections("   ") == []


def test_load_markdown_makes_a_document_per_section() -> None:
    docs = load_markdown("regs.md", "# A\n\naaa\n\n# B\n\nbbb", access_tag="internal")
    assert [d.section for d in docs] == ["A", "B"]
    assert all(d.access_tag == "internal" and d.source == "regs.md" for d in docs)


# --- ingest -----------------------------------------------------------------


def test_ingest_carries_metadata_onto_chunks() -> None:
    doc = Document(source="regs.md", text=LOREM, access_tag="internal", section="Rules")
    result = ingest([doc], size=200, overlap=40)
    assert result.report.documents == 1
    assert result.report.chunks == len(result.chunks) > 1
    assert result.report.average_chunk_size > 0
    for i, chunk in enumerate(result.chunks):
        assert isinstance(chunk, Chunk)
        assert chunk.source == "regs.md"
        assert chunk.access_tag == "internal"
        assert chunk.section == "Rules"
        assert chunk.index == i
        assert chunk.id == f"regs.md#{i}"


def test_ingest_empty_documents_reports_zero() -> None:
    result = ingest([])
    assert result.chunks == []
    assert result.report.chunks == 0 and result.report.average_chunk_size == 0.0


def test_ingest_markdown_end_to_end() -> None:
    result = ingest_markdown(
        [
            ("regs.md", "# Sporting\n\n" + LOREM, "public"),
            ("crm.md", "# CRM\n\nhow to log a case", "internal"),
        ],
        size=200,
        overlap=40,
    )
    sources = {c.source for c in result.chunks}
    assert sources == {"regs.md", "crm.md"}
    tags = {c.source: c.access_tag for c in result.chunks}
    assert tags["crm.md"] == "internal"


def test_chunk_ids_are_unique_across_sections_of_one_source() -> None:
    # Two sections of the same file must not collide on id (search-doc key, #70).
    docs = load_markdown("regs.md", "# Overtaking\n\nDRS rules\n\n# Safety Car\n\nhold position")
    result = ingest(docs, size=200, overlap=40)
    ids = [c.id for c in result.chunks]
    assert len(ids) == len(set(ids)) == 2
    assert ids == ["regs.md#0", "regs.md#1"]


def test_retag_changes_access_tag() -> None:
    doc = Document(source="s", text="t")
    assert retag(doc, "confidential").access_tag == "confidential"
    assert doc.access_tag == "public"  # original unchanged
