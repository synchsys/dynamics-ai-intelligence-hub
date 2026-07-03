# Prompt engineering patterns

Notes on the prompt-engineering patterns used in this repo, and how the prompt
library (`src/ai/prompts/`) codifies them. The goal is **versioned, reusable
prompts** shared across AI summaries (#62) and the CRM assistant (#63), rather
than ad-hoc strings scattered through feature code.

## The library

A `PromptTemplate` is a named **system + user** pair. Required variables are
derived from the template text with `string.Formatter`, so the declared
interface can't drift from the prompt, and a missing variable raises a clear
`PromptError` at render time instead of a raw `KeyError` mid-call. `render()`
returns the `[{system}, {user}]` message list the `AIClient` consumes.

Current templates: `crm_qa`, `summarise_activity`, `account_briefing`.

## Patterns

- **Ground, don't guess.** The `crm_qa` system prompt instructs the model to
  answer *only* from the supplied CRM context and to say when it doesn't know —
  never to invent records, names, or figures. This mirrors the
  reject-don't-guess rule enforced deterministically elsewhere (ADR-0008) and is
  the precursor to citation-backed RAG grounding (#65).
- **Separate instructions from data.** System prompts carry the role and rules;
  the data (CRM context, activity text, account record) is interpolated as a
  clearly delimited block. This keeps user/System boundaries clean and reduces
  prompt-injection surface (hardened further in #83).
- **Constrain the output.** Summary prompts bound length (`max_words`) and scope
  ("do not add information beyond the record"), so downstream code gets
  predictable text. For machine-consumed output we go further and use
  schema-constrained **structured outputs** (`ai.structured`) rather than prose.
- **Parameterise, don't concatenate.** Variables are named placeholders, so
  prompts are testable (they render deterministically) and reusable across
  features.

## Testing

Templates are pure and render deterministically, so they are unit-tested by
asserting the rendered messages contain the substituted variables and that a
missing variable raises `PromptError` — no model call required.
