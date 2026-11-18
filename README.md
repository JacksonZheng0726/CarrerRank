# CareerRank

CareerRank is an outcome-driven job-search intelligence platform. This repository currently implements **Phase 0 — Foundation** from the canonical [product specification](docs/PRODUCT_SPEC.md): a Next.js web application, FastAPI API, PostgreSQL with pgvector, Redis, authentication, health checks, migrations, automated tests, container builds, and CI.

Resume ingestion, jobs, matching, application tracking, analytics, workers, AI, and ML are intentionally outside Phase 0. There is no placeholder worker service; it will be introduced with the first real background workflow.

## Architecture

```text
careerrank/
|-- apps/
|   |-- api/                  FastAPI, SQLAlchemy, Alembic, pytest
|   `-- web/                  Next.js App Router, TypeScript, Vitest
|-- docs/
|   `-- PRODUCT_SPEC.md       Canonical product specification
|-- .github/workflows/ci.yml
|-- .env.example
|-- docker-compose.yml
|-- package.json
`-- pnpm-workspace.yaml
```

The browser calls the same-origin versioned path `/api/v1`; Next.js rewrites it to the FastAPI service using the server-only `API_URL`. This keeps browser authentication same-origin and does not expose the internal Compose hostname. PostgreSQL is the system of record. Redis is a required Phase 0 dependency and is reserved for later cache and queue work. Database schema changes are made only through Alembic.

## Prerequisites

- Node.js 22 or newer
- pnpm 10.15.0 (the repository and container build pin this release)
- Python 3.12 or newer
- Docker Desktop with the Linux container engine running
- Git

Install the pinned package manager once after installing Node.js:

```bash
npm install --global pnpm@10.15.0
pnpm --version
```

On Windows PowerShell, use `npm.cmd install --global pnpm@10.15.0` if the script execution policy blocks the `npm.ps1` shim.

## Configure the environment

Copy the template; `.env` is ignored by Git.

```bash
cp .env.example .env
```

PowerShell:

```powershell
Copy-Item .env.example .env
```

Generate two independent, URL-safe values—one for `POSTGRES_PASSWORD` and one for `JWT_SECRET`:

```bash
node -e "console.log(require('node:crypto').randomBytes(32).toString('hex'))"
```

Put the generated database password into both URLs in `.env`:

```dotenv
POSTGRES_PASSWORD=<generated-database-password>
DATABASE_URL=postgresql+psycopg://careerrank:<generated-database-password>@127.0.0.1:5432/careerrank
TEST_DATABASE_URL=postgresql+psycopg://careerrank:<generated-database-password>@127.0.0.1:5433/careerrank_test
JWT_SECRET=<independently-generated-jwt-secret>
```

The placeholders above must be replaced, including angle brackets. Hex output from the command is already URL-safe. Never reuse these development values in staging or production, and never commit `.env`.

Use `localhost` consistently for both the web and API URLs. Mixing `localhost` and `127.0.0.1` changes browser origin/site behavior and can prevent credentialed cookies from being sent.

## Run everything with Docker

The simplest setup builds the applications, starts PostgreSQL and Redis, runs the one-shot Alembic migration service, then starts the API and web containers:

```bash
docker compose up --build
```

Open:

- Web: <http://localhost:3000>
- API documentation: <http://localhost:8000/docs>
- Liveness: <http://localhost:8000/health/live>
- Readiness: <http://localhost:8000/health/ready>

Useful commands:

```bash
docker compose ps
docker compose logs api web
docker compose run --rm migrate
docker compose down
```

`docker compose down` retains the named PostgreSQL and Redis volumes. Adding `--volumes` permanently deletes local database and Redis data.

PostgreSQL and Redis are published only on the loopback interface for local tooling. Compose uses `postgres:5432` and `redis:6379` from inside containers; host processes use `127.0.0.1:5432` for PostgreSQL and `localhost:6379` for Redis. The explicit PostgreSQL address avoids a psycopg/Windows `localhost` resolution stall; database connections also have a five-second connect timeout.

## Run applications natively

Start only the infrastructure:

```bash
docker compose up -d postgres redis
```

Create and activate a Python environment, then install the API dependencies.

Linux/macOS:

```bash
python3.12 -m venv apps/api/.venv
source apps/api/.venv/bin/activate
python -m pip install --upgrade pip
python -m pip install --requirement apps/api/requirements-dev.txt
```

Windows PowerShell:

```powershell
py -3.12 -m venv apps/api/.venv
apps\api\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install --requirement apps/api/requirements-dev.txt
```

From the repository root, apply migrations and run FastAPI so it reads the root `.env`:

```bash
alembic -c apps/api/alembic.ini upgrade head
uvicorn --app-dir apps/api app.main:app --reload --host 0.0.0.0 --port 8000
```

In a second terminal, install and start the web application:

```bash
pnpm install
pnpm dev
```

## Authentication contract

Phase 0 exposes these endpoints:

```text
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
GET  /api/v1/auth/me
```

Passwords are validated and hashed with Argon2id. Email addresses are normalized before their database uniqueness constraint is applied. Access tokens are short-lived; refresh tokens rotate on every refresh and their server-side session records support revocation and reuse detection. Raw refresh tokens and raw CSRF tokens are not stored in PostgreSQL.

The browser cookie/header contract is exact:

| Name | Properties / use |
| --- | --- |
| `careerrank_access` | `HttpOnly`; `Path=/`; carries the short-lived access token |
| `careerrank_refresh` | `HttpOnly`; `Path=/api/v1/auth`; carries the rotating refresh token |
| `careerrank_csrf` | JavaScript-readable; `Path=/`; its value is sent in the CSRF header |
| `X-CSRF-Token` | Must match `careerrank_csrf` for authenticated state-changing requests, including refresh and logout |

Frontend requests that participate in authentication must use `credentials: "include"`. Registration and login do not require a pre-existing CSRF token. `GET /auth/me` is read-only. Refresh and logout require the double-submit CSRF value. A successful logout revokes the refresh-token family and clears all three cookies. Protected requests immediately reject the associated access token through the server-side family check; JWT expiration provides an additional upper bound.

Cookie-changing operations are serialized across tabs with the browser Web Locks API, and session changes reset active account queries in every tab through a storage event. Supported production browsers must provide Web Locks for the cross-tab serialization guarantee; a same-tab queue remains available in older test or embedded environments.

Local cookies use the names above with `SameSite=Lax` and `COOKIE_SECURE=false`. Staging and production require HTTPS, switch all three names to the browser-enforced `__Host-` prefix, widen the refresh cookie to `Path=/`, and keep cookies host-only. Credentialed CORS never uses a wildcard origin.

Authentication failures use a generic response and still perform password-hash verification to reduce account-enumeration timing signals.

## Health checks

`GET /health/live` answers whether the API process is running. It performs no network dependency checks and remains available when PostgreSQL or Redis is down.

`GET /health/ready` checks PostgreSQL and Redis with bounded timeouts. It returns HTTP 200 only when required Phase 0 dependencies are reachable and HTTP 503 otherwise. External AI providers are never part of readiness.

Use liveness for process restart decisions and readiness for load-balancer traffic admission. Do not use liveness to infer database availability.

## Migrations

Create a migration after changing SQLAlchemy metadata:

```bash
cd apps/api
alembic revision --autogenerate -m "describe the schema change"
alembic upgrade head
alembic check
```

The initial migration enables the `vector` extension and creates the Phase 0 tables. Application startup does not generate or mutate schema. Compose runs the explicit `migrate` service, and CI requires one Alembic head, applies it to real PostgreSQL, and checks for metadata drift.

## Tests and quality checks

Backend repository integration tests must use the disposable test database, never the development database. The test service uses pgvector PostgreSQL, host port `5433`, and a temporary filesystem that disappears with the container:

```bash
docker compose --profile test up -d postgres-test redis
```

Confirm the root `.env` has `TEST_DATABASE_URL` pointing to `127.0.0.1:5433/careerrank_test`, a test `REDIS_URL`, and `REQUIRE_INTEGRATION_TESTS=true`. The integration fixture reads those root values (explicit process environment variables take precedence) and fails instead of skipping when the required services are not configured. Then run from `apps/api`:

```bash
ruff check .
ruff format --check .
mypy app
pytest
```

Run the frontend checks from `apps/web`:

```bash
pnpm lint
pnpm typecheck
pnpm test
pnpm build
```

The backend suite uses real PostgreSQL for repository and API integration coverage and Redis where its behavior matters. SQLite is not a supported substitute because Phase 0 uses PostgreSQL UUID/JSONB behavior and the pgvector extension. Frontend tests use Vitest and React Testing Library.

## Continuous integration

[`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs on pull requests and pushes to `main` and blocks success on:

- backend Ruff formatting/linting and mypy checks;
- Alembic upgrade, single-head validation, metadata drift validation, and pytest against pgvector PostgreSQL plus Redis;
- frontend ESLint, strict TypeScript, Vitest, and production build;
- Python and JavaScript dependency audits; and
- API and web container builds, runtime startup smoke checks, and Compose configuration validation.

CI credentials are ephemeral test-only values. The workflow does not publish images or deploy; deployment belongs to a later phase.

## Troubleshooting

- **Docker cannot connect to the Linux engine:** start Docker Desktop and wait until `docker info` succeeds.
- **`pnpm` is not found:** run `npm install --global pnpm@10.15.0`; on Windows use the `npm.cmd` variant above.
- **Readiness returns 503:** inspect `docker compose ps` and `docker compose logs postgres redis api`; liveness can still return 200 by design.
- **Cookies are absent:** verify the browser request uses `credentials: "include"`, the frontend origin exactly matches `CORS_ORIGINS`, and local `COOKIE_SECURE` is `false`.
- **A migration cannot create `vector`:** use the specified `pgvector/pgvector` image rather than a plain PostgreSQL image.
- **Tests appear to target port 5432:** stop and correct `TEST_DATABASE_URL`; integration tests must target the isolated port 5433 database.

## Specification and scope

[`docs/PRODUCT_SPEC.md`](docs/PRODUCT_SPEC.md) is the source of truth. If this README and the specification conflict, follow the specification and update the implementation and documentation together. Phase 0 deliberately does not ship resume, job, matching, worker, application, analytics, AI, or ML functionality.
