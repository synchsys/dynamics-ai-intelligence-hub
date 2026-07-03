"""Live smoke test for RAG embeddings (#68).

Ingests a short knowledge source, embeds the chunks via the real Azure OpenAI
embeddings deployment, checks the vector dimensions, and confirms a re-run
reuses cached vectors (idempotent). No Dataverse writes.

Run: python scripts/rag/verify_embeddings.py
"""

import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))


def _load_env() -> None:
    for line in (pathlib.Path(__file__).resolve().parents[2] / ".env").read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


def main() -> int:
    _load_env()
    from ai import AIClient, AzureOpenAIConfig
    from rag import InMemoryEmbeddingCache, embed_chunks, ingest_markdown

    client = AIClient(AzureOpenAIConfig.from_env())
    source = (
        "# Overtaking\n\nDrivers must not leave the track and gain a lasting advantage. "
        "DRS may be used only in designated zones.\n\n# Safety Car\n\n"
        "When the safety car is deployed, overtaking is forbidden and drivers must reduce speed."
    )
    result = ingest_markdown([("regs.md", source, "public")], size=120, overlap=30)
    run = embed_chunks(client, result.chunks, batch_size=8)
    print(f"chunks={result.report.chunks} embedded={run.embedded} dims={run.dimensions}")

    rerun = embed_chunks(client, result.chunks, cache=InMemoryEmbeddingCache(run.chunks))
    print(f"re-run embedded={rerun.embedded} reused={rerun.reused}")

    ok = run.dimensions == 1536 and rerun.embedded == 0 and rerun.reused == len(run.chunks)
    print("OK" if ok else "FAILURES PRESENT")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
