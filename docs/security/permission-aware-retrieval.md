# Permission-aware retrieval

Retrieval trimmed to what the caller is authorised to see (#72) — the
differentiating enterprise capability that makes the RAG demo credible for
regulated contexts. Implemented in `src/rag/retrieval.py`; the *policy* is owned
by Epic 11 (11.B access boundaries).

## Model

1. **Access tags on data (from ingestion, #67).** Every chunk carries an
   `access_tag` (`public` → `internal` → `confidential`), a hierarchy where each
   level implicitly grants the ones before it.
2. **Role → allowed tags (`AccessPolicy`).** The caller's Dataverse security
   roles map to the highest access level they hold; `allowed_tags(roles)` returns
   that level and everything below it. Unknown/unprivileged roles resolve to the
   empty set.
3. **Allowed tags → search filter.** `filter_for(roles)` builds an OData
   `search.in(access_tag, '<tags>', ',')` filter. With no granted tags it returns
   a **deny-all** filter (`access_tag eq '__no_access__'`) that matches nothing.
4. **Filter applied at query time.** `Retriever.retrieve_for(query, roles)` passes
   the filter to the hybrid query, so Azure AI Search trims to permitted
   documents **before ranking** — a caller never receives, or even sees a snippet
   of, a document their role does not grant.

## Deny-by-default

The design fails closed: an unrecognised role, a typo, or an empty role list all
yield the deny-all filter and zero results. Access is only ever granted by an
explicit role→tag mapping — there is no "default allow" path.

## Default role mapping

| Role | Highest tag | Effective access |
|------|-------------|------------------|
| guest, reader | public | public |
| employee, salesperson | internal | public, internal |
| manager, administrator | confidential | public, internal, confidential |

The mapping is injectable (`AccessPolicy(role_access=...)`) so Epic 11 can govern
it centrally without changing retrieval code.

## Verification

Unit tests prove the role→tag resolution, filter construction, and — with a
filter-respecting fake index — that a **guest cannot retrieve a document a
manager can** (the core guarantee), plus deny-by-default for unknown roles. A
live check (`scripts/rag/verify_permission.py`) seeds public/internal/
confidential chunks in Azure AI Search and confirms: guest → `{public}`,
manager → all three, unknown role → nothing.
