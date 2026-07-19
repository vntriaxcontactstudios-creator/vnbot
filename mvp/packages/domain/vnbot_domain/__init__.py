"""VNBOT Domain — Shared Python package (pure, no framework imports).

This package contains the domain layer of VNBOT: entities, value objects,
rules, and ports. It must NEVER import FastAPI, SQLAlchemy, Redis, LLM SDKs,
or any external SDK. Those belong in the infrastructure layer.

See: docs/03-ESQUEMA-BACKEND-VNBOT.md §4.1 (dependency rule)
"""

__version__ = "0.1.0"
