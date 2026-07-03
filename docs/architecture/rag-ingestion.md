# RAG ingestion and chunking

The entry point to the RAG pipeline (#67): load knowledge sources, split them
into overlapping chunks, and attach the metadata retrieval depends on. Chunks
are the units later embedded (#68) and indexed in Azure AI Search (#70).

## Pipeline

```
markdown/text source ─► load_markdown()         # one Document per heading section
                     ─► chunk_text()             # overlapping, word-snapped chunks
                     ─► Chunk(source, text, index, access_tag, section)
```

`ingest(documents)` / `ingest_markdown(sources)` run this end to end and return
an `IngestionResult` with the chunks and an `IngestionReport` (document count,
chunk count, average chunk size).

## Chunking choice

- **Unit:** characters (simple, dependency-free, deterministic — no tokenizer
  needed for a portfolio pipeline).
- **Size:** `DEFAULT_CHUNK_SIZE = 800` chars (≈150–200 tokens) — large enough to
  hold a coherent passage, small enough to keep retrieval precise and stay well
  under embedding limits.
- **Overlap:** `DEFAULT_CHUNK_OVERLAP = 150` chars (≈19%) — carries context
  across boundaries so an answer spanning a cut is still retrievable.
- **Word snapping:** cuts snap back to the nearest whitespace so chunks don't
  split words mid-token; a single token longer than `size` is hard-split so the
  loop always makes progress.

Size/overlap are parameters on every entry point, so the choice can be tuned per
source without code changes; the defaults above are the recorded starting point.

## Metadata

Each `Chunk` carries:

- **`source`** + **`index`** (and a derived `id` of `source#index`) — provenance
  for citations (#73).
- **`section`** — the markdown heading the chunk came from, for finer citation
  and filtering.
- **`access_tag`** — the permission label (`public`, `internal`, …) that
  **permission-aware retrieval (#72)** filters on. Set per source at load time;
  `retag()` produces a re-tagged copy. Carrying the tag from ingestion means
  access control is a property of the data, not bolted on at query time.

## Testing

Pure functions, unit-tested on chunk boundaries (size cap, overlap present, no
mid-word cuts, whitespace normalisation, over-long tokens), markdown section
splitting (headings, preamble, empty sections), and metadata propagation onto
every chunk.
