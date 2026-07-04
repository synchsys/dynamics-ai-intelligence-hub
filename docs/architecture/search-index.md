# Azure AI Search index

The retrieval backbone of the RAG pipeline (#70): a vector + text + metadata
index populated from embedded chunks (#68) and queryable by both vector and
keyword search. This is what hybrid (#71), permission-aware (#72), and cited
(#73) retrieval build on.

## Resource

- **Service:** `racy-search-dev` (`rg-racy-ai-dev`, uksouth, **Free** tier).
  Free supports vector + keyword search; the semantic reranker (an option for
  #71) requires Basic or above.
- **Auth (dev):** the admin API key from `AZURE_SEARCH_KEY` (git-ignored `.env`).
  No secrets in source; Entra / Managed Identity is Epic 11.

## Index schema (`build_index`)

| Field | Type | Notes |
|-------|------|-------|
| `id` | `Edm.String` | key — the base64url-encoded chunk id (`source#index`) |
| `content` | `Edm.String` | searchable — the chunk text (keyword search) |
| `source` | `Edm.String` | filterable, facetable — provenance |
| `section` | `Edm.String` | filterable — the source heading |
| `access_tag` | `Edm.String` | filterable — **permission-aware retrieval (#72) filters on this** |
| `vector` | `Collection(Edm.Single)` | 1536-dim (text-embedding-3-small), HNSW profile |

Vector search uses an HNSW algorithm configuration bound to a vector-search
profile. Document keys must be restricted to letters/digits/`-`/`_`/`=`, so the
chunk id (which contains `.` and `#`) is **base64url-encoded** into the key via
`document_key()`.

## Components (`src/rag/index.py`)

- **`build_index(name, dimensions)`** — the `SearchIndex` definition (pure;
  unit-tested).
- **`to_document(embedded_chunk)`** — maps an embedded chunk to a search document
  (pure; unit-tested).
- **`KnowledgeIndex`** — wraps the SDK `SearchIndexClient` + `SearchClient`
  (injectable for tests): `create(recreate=)`, `upload(chunks)`, `delete()`,
  `keyword_search(query, access_filter=)`, `vector_search(vector, access_filter=)`.
  The `access_filter` parameter is where #72's permission trimming plugs in.

## Chunk id uniqueness

A source file splits into multiple section documents (#67); the chunk `index` is
a **per-source running counter**, so two sections of the same file get distinct
ids (`regs.md#0`, `regs.md#1`) and therefore distinct search-doc keys. (An
earlier per-section reset caused key collisions where the second section
overwrote the first — fixed in ingestion and covered by a regression test.)

## Testing

Schema and document mapping are pure and unit-tested; the client wrapper is
tested with injected fake clients (create/recreate/delete/upload/query wiring),
and the default-client construction via monkeypatched SDK constructors. A live
end-to-end smoke test (`scripts/rag/verify_index.py`) creates a temp index,
ingests + embeds a short source, uploads, and confirms a vector query and a
keyword query each return the relevant chunk — then deletes the temp index.
