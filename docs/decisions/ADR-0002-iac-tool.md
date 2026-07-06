# ADR-0002: Primary Infrastructure-as-Code tool

## Status

Accepted

## Context

The Azure resources (#89) need to be defined as code so they are reproducible,
reviewable, and destroyable — not click-ops. The dev environment was first stood
up interactively with `az` (App Insights, Key Vault, a user-assigned Managed
Identity, storage, and a Flex Consumption Function App, plus the role
assignments wiring the identity to Azure OpenAI / AI Search / Key Vault). That
imperative bootstrap now needs a declarative source of truth.

Both an `infrastructure/bicep/` and an `infrastructure/terraform/` tree exist as
placeholders; this ADR picks one as **primary**. Candidates:

- **Bicep** — Azure's first-party DSL. No state file to manage (ARM is the
  backing state), day-one support for new Azure resource types, native to the
  `az` tooling already in use, and the option Microsoft steers Azure-only teams
  to. Weaker for multi-cloud and has a smaller module ecosystem than Terraform.
- **Terraform** — cloud-agnostic, huge provider/module ecosystem, mature state
  and plan/apply workflow. But it adds state-backend management, the AzureRM
  provider often lags new Azure features, and multi-cloud is not a goal here.

## Decision

Use **Bicep** as the primary IaC tool. This is a single-cloud (Azure) portfolio
solution built end-to-end on Microsoft services (Dataverse, Azure OpenAI, AI
Search, Functions), so Bicep's first-party fidelity, zero state management, and
alignment with the `az` CLI already in the workflow outweigh Terraform's
multi-cloud strengths — which this project does not need. It also demonstrates
the Microsoft-aligned skillset the portfolio targets.

The `infrastructure/terraform/` tree is retired to a placeholder; if a future
requirement demands multi-cloud or a Terraform-shop context, it can be
reconsidered without disturbing the app code (IaC is deployment-time only).

## Consequences

- **Positive:** one declarative definition of every Azure resource; no state
  backend to secure/lock; new resource types available immediately; reviewable
  in PRs; `az deployment group create` / `what-if` for safe applies.
- **Negative / constraints:** Azure-only (acceptable — that is the platform);
  smaller module registry than Terraform (mitigated by first-party resource
  coverage and local modules).
- The hand-provisioned dev resources are now codified under
  `infrastructure/bicep/` (`main.bicep` + `modules/`, `environments/dev.bicepparam`)
  so the environment is reproducible; CI deployment is #88 / #180.

## Notes

Bicep is linted/compiled in review with `az bicep build`. Deployments are
scoped to a resource group: `az deployment group create -g rg-racy-ai-dev
-f infrastructure/bicep/main.bicep -p infrastructure/environments/dev.bicepparam`.
`what-if` is run before any apply against a live environment.
