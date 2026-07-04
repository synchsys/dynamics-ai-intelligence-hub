"""Live end-to-end verification of the Azure AI Search index (#70).

Against the real racy-search-dev service: create a temporary index, ingest +
embed a short knowledge source, upload the chunks, then confirm a vector query
and a keyword query each return the relevant chunk. The temp index is deleted
afterwards, so the run is repeatable and leaves nothing behind.

Run: python scripts/rag/verify_index.py
"""

import dataclasses
import os
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))


def _load_env() -> None:
    for line in (pathlib.Path(__file__).resolve().parents[2] / ".env").read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


SOURCE = (
    "# Overtaking and DRS\n\n"
    "Drivers must not leave the track and gain a lasting advantage. The drag "
    "reduction system (DRS) may be used only within designated activation zones.\n\n"
    "# Safety Car\n\n"
    "When the safety car is deployed, overtaking is forbidden and all drivers must "
    "reduce speed and hold position until racing resumes."
)


def main() -> int:
    _load_env()
    from ai import AIClient, AzureOpenAIConfig
    from rag import KnowledgeIndex, SearchConfig, embed_chunks, ingest_markdown

    client = AIClient(AzureOpenAIConfig.from_env())
    base = SearchConfig.from_env()
    config = dataclasses.replace(base, index="racy-knowledge-verify")
    ki = KnowledgeIndex(config)

    result = ingest_markdown([("regs.md", SOURCE, "public")], size=200, overlap=40)
    run = embed_chunks(client, result.chunks)
    print(f"chunks={run.embedded} dims={run.dimensions}")

    ok = False
    try:
        ki.create(recreate=True)
        ki.upload(run.chunks)

        # Uploaded documents take a moment to become queryable.
        query_vector = client.embed(["when are drivers allowed to use DRS?"])[0]
        vhits: list = []
        for _ in range(15):  # wait until all uploaded chunks are queryable
            time.sleep(2)
            vhits = ki.vector_search(query_vector, top=len(run.chunks))
            if len(vhits) >= len(run.chunks):
                break
        khits = ki.keyword_search("safety car", top=2)

        print(f"vector hits:  {[(h['section'], round(h['score'], 3)) for h in vhits]}")
        print(f"keyword hits: {[(h['section'], round(h['score'], 3)) for h in khits]}")
        # AC: each query returns the relevant chunk (present in top-k).
        vector_ok = any("DRS" in (h["section"] or "") for h in vhits)
        keyword_ok = bool(khits) and "Safety" in (khits[0]["section"] or "")
        ok = vector_ok and keyword_ok
        print(f"vector_ok={vector_ok} keyword_ok={keyword_ok}")
    finally:
        ki.delete()
        print("deleted temp index")

    print("OK" if ok else "FAILURES PRESENT")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
