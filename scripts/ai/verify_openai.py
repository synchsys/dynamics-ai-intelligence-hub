"""Live smoke test for the Azure OpenAI client (#58).

Reads .env, builds the real AIClient (Entra auth via the Dataverse service
principal), and makes one chat + one embedding call against racy-openai-dev.
Run: python scripts/ai/verify_openai.py
"""

import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))


def _load_env() -> None:
    env = pathlib.Path(__file__).resolve().parents[2] / ".env"
    for line in env.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


def main() -> int:
    _load_env()
    from ai import AIClient, AzureOpenAIConfig

    config = AzureOpenAIConfig.from_env()
    client = AIClient(config)
    print(f"endpoint={config.endpoint}  chat={config.chat_deployment}  "
          f"embed={config.embedding_deployment}  auth={'key' if config.uses_key else 'entra'}")

    reply = client.chat([{"role": "user", "content": "Reply with exactly: pong"}])
    print(f"chat -> {reply!r}")

    vectors = client.embed(["hello from the Dynamics AI Intelligence Hub"])
    print(f"embed -> {len(vectors)} vector(s), dim={len(vectors[0])}")

    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
