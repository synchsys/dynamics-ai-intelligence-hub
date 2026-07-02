"""OpenF1 ingestion package.

A typed client over the OpenF1 public API, built on the ``api`` REST client and
``shared`` utilities. The settlement source of truth for the Paddock Club
predictions game (ADR-0008); feeds validation (4.3) and Dataverse persistence
(4.4).
"""

from openf1.client import DEFAULT_BASE_URL, OpenF1Client

__all__ = ["OpenF1Client", "DEFAULT_BASE_URL"]
