<!-- Copilot / AI agent instructions for contributors and automated agents -->
# Copilot instructions — Imtiaz Marketplace (concise)

These notes give immediate, repository-specific context for AI coding agents and for contributors using Copilot-style workflows.

- Project type: Python FastAPI microservices (multiple services under `services/`) using Postgres, Kafka, and Dapr. Protobuf messages live under `shared/proto` and generated pb2 modules under `shared/events`.

## Big picture (quick)
- Event-driven microservices: services publish/subscribe domain events (Kafka + Dapr pubsub). Key services: `user-service`, `product-service` (others exist under `services/`).
- Data stores: each service uses PostgreSQL (see `infrastructure/postgres/*`). DB init scripts: `infrastructure/postgres/init-multiple-databases.sh`.
- Proto & messages: source .proto files live in `shared/proto/*.proto`; generated Python files appear under `shared/events/*.py` (e.g. `product_created_pb2.py`). Use `scripts/generate-proto.sh` to regenerate bindings.

## Key files and conventions (use these as authoritative examples)
- Service structure (consistent pattern): `services/<name>/app/` with subpackages:
  - `api` (FastAPI routers) — example: `services/product-service/app/api/product.py`
  - `domain` (domain models and logic)
  - `models` (DB models) — example: `services/product-service/app/models/product.py`
  - `repositories` (DB access) — example: `services/product-service/app/repositories/product_repo.py`
  - `services` (application services) — example: `services/product-service/app/services/product_service.py`
  - `events` or `publishers` (Dapr publishing) — example: `services/user-service/app/events/publisher.py`

## Event wiring & integration points
- Dapr components are in `infrastructure/dapr/components/` (e.g. `pubsub-kafka.yaml`). Changes to event naming or topics must be mirrored here and in code that publishes/subscribes.
- Generated pb2 modules in `shared/events/` are imported directly by services to serialize/deserialize events (do not hand-edit generated files).

## Concrete commands (copyable)
- Start infra (Docker Compose): `cd infrastructure && docker-compose up -d`
- Start a single service locally (example):
  - In `services/user-service`: `uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` (the repo uses `uv` helper in READMEs)
- Regenerate protobufs: `./scripts/generate-proto.sh` (run from repo root). After regenerating, check-in only the intended generated files per team policy.
- Run tests (service-local): `cd services/<service-name> && uv run pytest` or `pytest -q` — many service README files use `uv run pytest`.
- Run alembic migrations: `cd services/<service-name> && alembic upgrade head` (services that include `alembic/` follow this pattern).

## Project-specific patterns agents should follow
- Prefer existing service layering: controllers/api -> services -> repositories -> models/domain. When adding logic, place code in the smallest appropriate layer (e.g., business rules go in `services/` or `domain/`, data access in `repositories/`).
- Event messages: publish protobuf-typed payloads using Dapr's pubsub. Use `shared/events/<name>_pb2.py` for message classes rather than ad-hoc dicts.
- Naming: topics and event names are kebab or dot-style in YAMLs and code (follow existing examples: `user.registered`, `product.created`). Mirror exactly between code and `infrastructure/dapr/components/*.yaml`.

## Examples to reference when generating or modifying code
- Publishing an event: check `services/user-service/app/events/publisher.py` for Dapr + pb2 usage.
- Product domain flow: `services/product-service/app/api/product.py` -> `services/product-service/app/services/product_service.py` -> `services/product-service/app/repositories/product_repo.py`.

## Tests and CI hints
- Unit and integration tests live in each service under `services/<service>/tests/` — follow pytest conventions.
- Use `uv run pytest` in services that provide `uv` helper in `pyproject.toml`/`uv.lock`.

## What not to change without review
- Do not change generated files in `shared/events/` unless regenerating from `.proto` and documenting the change.
- Avoid silent changes to `infrastructure/dapr/components/*.yaml` or `docker-compose*.yml` that rename topics or pubsub names — those require coordinated updates across services.

## When you need more context (suggested places to read)
- `README.md` (repo root) — contains architecture summary and quick-start
- `infrastructure/docker-compose.yml` and `infrastructure/dapr/components/pubsub-kafka.yaml` — infra wiring
- `shared/proto/*` and `shared/events/*` — message contracts
- Service-level READMEs: `services/*/README.md` for service-specific commands and env var lists

If any part of this file is unclear or you want me to expand examples (e.g., a concrete code snippet showing pb2 event publishing pattern), tell me which service and I will add a short, copy-pasteable example.
