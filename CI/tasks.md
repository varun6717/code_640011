# tasks.md — ci_ui Phase 5 implementation task list

**Project:** `ci_ui` — Custom Interchange UI for the Mastercard agreement-change orchestration pipeline
**Phase:** 5 — Implementation task list for VDI Copilot execution
**Status:** generated per the Phase 5 Tasks.md Generation Task Chat
**Companion documents** (consulted during authorship; **not** transferred across the air gap with this file):

- `01_PROJECT_RULEBOOK.md` — 8 operating rules
- `02_HANDOFF_DOCUMENT_v2.md` — project plan and §10 tasks.md structure spec
- `backend-spec.md` — Phase 1 backend snapshot
- `functional-integration-spec.md` — Phase 2 screens and flows
- `tech-spec.md` — Phase 3 architecture
- `visual-mockup.jsx` — Phase 4 React reference
- `03_DECISIONS_LOG.md` — D-001 through D-073 active stack

Per the air-gap operating model (D-016 + D-022): this `tasks.md` is the only artifact that crosses to VDI. Every file path, code snippet, API signature, embedded JSX, contract excerpt, and acceptance criterion is reproduced inline. Tasks do **not** reference external files that won't exist on VDI.

---

## How VDI Copilot uses this document

Each task is self-contained. Read the task in question, gather the inline embedded context, and execute. Copilot context is fresh per task — cross-task dependencies are declared explicitly via `**Depends on:** TN, TN+1` at the task header, with the prerequisite's relevant outputs (file paths, function signatures, schemas) **already embedded inline** in the dependent task. Never assume Copilot has read a prior task's content; everything needed is in the current task body.

When V (the developer) reviews a Copilot-completed task:

1. Check the acceptance criteria checklist — every item must be testable, not aspirational.
2. Verify the task did NOT modify files outside its declared "touches files" list.
3. If a task surfaces a question Copilot can't resolve, V escalates to the Coordinator chat for a Decisions Log entry rather than letting Copilot guess.

---

## Per-task structure (mandatory)

Every task follows this exact format:

```
## TN — <short descriptive name>

**Depends on:** [list of prior task numbers, or "none"]
**Touches files:** [list of files this task creates or modifies — Copilot must not touch others]
**Estimated effort:** [small / medium / large]

### Goal
[2-3 sentences: what this task accomplishes]

### Context
[Quoted relevant sections from backend-spec, tech-spec, functional-spec, or
Decisions Log. Embedded inline; never referenced.]

### Implementation
[Specific instructions. File paths absolute under repo root, code or pseudocode
for what to build, embedded HTML/JSX from visual-mockup.jsx for screens,
specific patterns to follow.]

### Acceptance criteria
- [ ] [Specific testable condition 1]
- [ ] [Specific testable condition 2]
- [ ] [etc]

### Notes
[Anything Copilot needs to know that doesn't fit elsewhere — calibration notes,
known-open questions, gotchas observed during spec authorship.]
```

The section header itself uses a checkbox at the top so V can mark progress:

```
- [ ] T42 — POST /api/runs/{id}/approve endpoint
```

---

## Section index

The 11 sections below organize the ≈93 tasks by domain. Within a section, tasks are flat-numbered. Section letters are organizational; task numbers (T0, T1, T-B1, etc.) are the canonical references. Sections later in the list build on outputs from earlier sections.

| Section | Domain | Task range | Approx tasks |
|---|---|---|---|
| **A** | Setup & foundation (monorepo, scaffolds, config, fonts, aesthetic tokens) | T0..T7 | 8 |
| **B** | Database & migrations (SQLite tables, runner, helpers, MAID index) | T-B1..T-B4 | 4 |
| **C** | State derivation & lifecycle plumbing (infer_state, locks, failure detection, event ingestion) | T-C1..T-C6 | 6 |
| **D** | Adapter layer (StorageClient, PipelineRunner — real + mock per Rule 7) | T-D1..T-D6 | 6 |
| **E** | FastAPI endpoints (16 endpoints + middleware + dependencies) | T-E1..T-E18 | 18 |
| **F** | Frontend infrastructure & shared components (React Query, SSE, Error Boundaries, BaseTableWithDrawer, AppShell, primitives) | T-F1..T-F10 | 10 |
| **G** | Runs List screen (rows, filters, search, pagination, live updates) | T-G1..T-G8 | 8 |
| **H** | Run Detail screen (Activity / Results / Issues tabs, drawer, Approve / Retry / Re-run) | T-H1..T-H18 | 18 |
| **I** | Artifact Preview screen (split-pane, PDF viewer, navigation) | T-I1..T-I6 | 6 |
| **J** | Production deployment shape (single-uvicorn, static mount, dev proxy, runbook) | T-J1..T-J4 | 4 |
| **K** | End-to-end verification (happy path, failure paths, concurrency UX) | T-K1..T-K5 | 5 |

---

## Global conventions

These conventions apply across every task; they are stated here once rather than repeated per task.

**Paths.** Forward slashes throughout (Windows VDI accepts them in Python and Node). Paths beginning `/api/`, `/web/`, or `/` are relative to the `ci_ui/` repo root. Paths beginning with an absolute drive letter or `/home/` are absolute filesystem paths.

**Imports in TypeScript files.** Use the `@/` alias for `web/src/...` paths (configured in T2's `vite.config.ts` and `tsconfig.json`). Example: `import { foo } from '@/features/shared/api/client'`.

**Imports in Python files.** Use the `api.` package prefix (e.g., `from api.config import settings`). The FastAPI app is invoked from the `ci_ui/` repo root so `api/` resolves cleanly as a package.

**Decisions Log references.** When a task quotes a D-NNN decision, the quote is the substance; the citation `(D-NNN)` is for traceability. Copilot does not need to read the Decisions Log itself — the relevant content is embedded.

**Single-lock model.** Per V's Phase 5 directive resolving D-057's §11.6 known-open: the lock model is single-instance-of-any-phase (one lock total), NOT D-050's per-phase model. UI tooltip strings reflect this with "An active operation is in progress" rather than separate staged/approval messaging. The schema preserves a nullable `phase` column for future migration to a two-lock model if the partner later confirms safe concurrency.

**Adapter profile default.** Per D-066: `ADAPTER_PROFILE=mock` is the default. Sections A-K develop entirely against mock fixtures preserved per D-026; flipping to `ADAPTER_PROFILE=real` requires only `.env` edits, no code change.

**Error envelope.** All API endpoints return errors in the single envelope shape from D-061 §7.4 (see T-E2). Frontend renders backend errors via the envelope; frontend-originating errors use the catalog at `web/src/features/shared/errors/messages.ts` (T-F5 + D-064).

**Component reuse.** `BaseTableWithDrawer` (T-F8) is the dumb prop-driven component used by both the Run Detail Results tab (T-HX) and Artifact Preview's artifact pane (T-IX) per D-062. Component contains no data-fetching or global-store access; parents own React Query hooks and pass data down.
# Section A — Setup & foundation

This section establishes the monorepo, both package skeletons, configuration loading, font vendoring, and the aesthetic token layer. Every subsequent section depends on the scaffold landing first.

Section index:

- [ ] T0 — Monorepo scaffold
- [ ] T1 — FastAPI backend scaffold
- [ ] T2 — React + Vite + TypeScript scaffold
- [ ] T3 — Feature-based directory layout + ESLint boundaries
- [ ] T4 — pydantic-settings Settings class + 13-variable env schema
- [ ] T5 — `.env.example` files for both packages
- [ ] T6 — Font vendoring (General Sans + JetBrains Mono)
- [ ] T7 — Aesthetic CSS variable tokens (deep oceanic palette)

---

## T0 — Monorepo scaffold

**Depends on:** none
**Touches files:** `/.gitignore`, `/README.md`, `/package.json` (root), `/api/` (empty directory), `/web/` (empty directory)
**Estimated effort:** small

### Goal

Create the top-level monorepo structure with two empty package directories (`/api/` for FastAPI, `/web/` for React), a unified `.gitignore` covering both Python and Node, and an optional root-level `package.json` for the `concurrently` dev-orchestration script. This is the foundation every other task depends on.

### Context

From D-066 (Configuration management, Phase 3):

> **Monorepo with `/api/` and `/web/` subdirectories.** Single git repo (single Bitbucket clone on VDI per D-022); FastAPI backend at `/api/`, React frontend at `/web/`. Phase 5 tasks.md transfers cleanly as a single artifact; task numbering stays linear without disambiguating between repos. Cross-cutting Phase 7 verification operates against one tree.

From D-067 (Deployment shape):

> **Dev workflow: dual-terminal.** Backend: `cd api && uvicorn main:app --reload` (FastAPI with hot reload). Frontend: `cd web && npm run dev` (Vite dev server on 5173 with HMR; Vite's `server.proxy` config routes `/api/*` to `localhost:8000`). Browser visits `http://localhost:5173` for active development. A root-level convenience script (`npm run dev:all` via `concurrently`) is optional and documented as a quality-of-life addition.

### Implementation

Create the following directory structure at the `ci_ui/` repo root (which itself lives as a sibling directory to `CI_Vision/` per the agreed workspace layout — `CI_Main/CI_Vision/` and `CI_Main/ci_ui/`):

```
ci_ui/
├── .gitignore
├── README.md
├── package.json      (optional, for `concurrently` dev orchestration)
├── api/              (empty for now; populated by T1)
└── web/              (empty for now; populated by T2)
```

**File: `/.gitignore`** — covers Python, Node, IDE artifacts, and both packages' env files:

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
.pytest_cache/
.venv/
venv/
env/

# Node
node_modules/
dist/
.vite/
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Env files (per D-066 secrets handling)
.env
.env.local
.env.*.local
api/.env
web/.env

# OS / IDE
.DS_Store
Thumbs.db
.vscode/
.idea/
*.swp
*.swo

# App-state (SQLite database lives at api/data/ per D-066 SQLITE_DB_PATH default)
api/data/

# Operational outputs (created per-run; per D-066 OUTPUT_BASE_FOLDER default).
# Note: in production V's OUTPUT_BASE_FOLDER points at CI_Vision/output/ which
# is OUTSIDE this repo, so this gitignore entry only protects accidental dev
# runs that use the in-repo default.
api/output/

# Build artifacts
web/dist/
```

**File: `/README.md`** — top-level orientation only; per-package READMEs live in `/api/README.md` and `/web/README.md` (created in T1 and T2):

````markdown
# ci_ui — Custom Interchange UI

Web UI for the Mastercard Custom Interchange agreement-change orchestration pipeline. Wraps the existing pipeline at `../CI_Vision/` (sibling repo, never modified by this codebase).

## Repository layout

- `/api/` — FastAPI backend (Python 3.11+)
- `/web/` — React frontend (Node 20+, TypeScript, Vite)

## Quick start (development)

Open two terminals.

Terminal 1 — backend:
```
cd api
python -m venv .venv && .venv\Scripts\activate    # Windows VDI
# or: source .venv/bin/activate                   # Linux/macOS
pip install -r requirements.txt
copy .env.example .env                            # then edit ALLOWED_INPUT_ROOTS
uvicorn main:app --reload
```

Terminal 2 — frontend:
```
cd web
npm install
copy .env.example .env
npm run dev
```

Visit http://localhost:5173 (Vite dev server proxies `/api/*` to the backend).

## Production (single uvicorn serves both)

```
cd web && npm run build       # produces web/dist/
cd ..\api && uvicorn main:app --host 0.0.0.0 --port 8000
```

Visit http://vdi-host:8000.

## Configuration

See `api/.env.example` and `web/.env.example` for the full 13-variable env schema.
````

**File: `/package.json`** — optional root file for the `concurrently` orchestration. Do NOT install root-level deps the children should own; this exists only for the `dev:all` convenience script:

```json
{
  "name": "ci_ui",
  "private": true,
  "version": "0.0.0",
  "description": "Monorepo root — see api/ and web/ for the actual packages.",
  "scripts": {
    "dev:all": "concurrently -n api,web -c blue,green \"cd api && uvicorn main:app --reload\" \"cd web && npm run dev\""
  },
  "devDependencies": {
    "concurrently": "^9.0.0"
  }
}
```

### Acceptance criteria

- [ ] Repository root contains exactly four entries plus `.gitignore` and `README.md`: `api/`, `web/`, `package.json`, plus the two dotfiles
- [ ] `/api/` and `/web/` directories exist but are otherwise empty (populated by T1 and T2)
- [ ] `git status` after fresh clone shows only the four checked-in files plus this commit message; no env or `node_modules` directories tracked
- [ ] `git check-ignore api/.env web/.env api/data/ web/dist/ web/node_modules/` returns clean (all five ignored)
- [ ] `npm install` from root succeeds (only installs `concurrently`) and `npm run dev:all` is at least syntactically valid (will fail at runtime until T1 and T2 land their packages)

### Notes

The root `package.json` is genuinely optional — V can skip it and use two terminals manually if `concurrently` is unwanted. Mark this task complete either way; do not block on the script working since `cd api && uvicorn ...` requires T1 to land first.

Filesystem path style in this tasks.md uses forward slashes throughout for consistency, including on Windows VDI. Python and Node both accept forward slashes on Windows; the runbook entries above also work cross-platform.

---

## T1 — FastAPI backend scaffold

**Depends on:** T0
**Touches files:** `/api/main.py`, `/api/requirements.txt`, `/api/README.md`, `/api/__init__.py`, `/api/routers/__init__.py`, `/api/routers/runs.py`, `/api/routers/system.py`, `/api/adapters/__init__.py`, `/api/db/__init__.py`, `/api/dependencies.py`
**Estimated effort:** small

### Goal

Create the FastAPI application skeleton under `/api/`. Wire CORS, mount a placeholder `/api/health` endpoint, register empty router modules that downstream tasks fill in, and pin Python dependencies. No business logic in this task — pure scaffold so Sections B through E have a working surface to attach to.

### Context

From D-067 (Deployment shape, Phase 3):

> **Production serving on VDI: single uvicorn process serves both.** FastAPI mounts the built `/web/dist/` directory as static files at `/`; all API routes live under `/api/*`. One process, one port (`API_PORT` per D-066), one deployable unit.

From D-065 calibration note:

> **CSRF / CORS posture.** `X-Operator-ID` is identity, not auth — anyone can put any value in the header. CSRF protection rests on CORS being locked down to same-origin and the API not accepting cross-origin POSTs from untrusted contexts. Phase 5 should set FastAPI CORS middleware to same-origin explicitly rather than relying on header values for auth-like decisions.

From D-061 (API contract):

> URL convention: `/api/...` namespace; run-scoped resources nested under `/api/runs/{run_id}/...`; cross-run queries on `/api/runs?...`. A health-check endpoint (`GET /api/health`) is implicit ops hygiene; recommended but not in the operator-facing inventory.

### Implementation

**File: `/api/requirements.txt`** — pinned versions (use these exactly to avoid VDI-side resolution surprises):

```
fastapi==0.115.0
uvicorn[standard]==0.32.0
pydantic==2.9.2
pydantic-settings==2.6.0
python-multipart==0.0.12
sse-starlette==2.1.3
```

`sse-starlette` is included now because Section C will use `EventSourceResponse`. No SQLite driver pin needed — `sqlite3` is in the Python stdlib.

**File: `/api/__init__.py`** — empty file marking `api/` as a package.

**File: `/api/main.py`** — the FastAPI app factory plus placeholders for routers populated in Section E:

```python
"""
ci_ui FastAPI application.

Routers attached in Section E (Endpoints). Adapters wired in Section D.
Lifecycle and state inference plumbing land in Section C.
This file is the composition root; downstream tasks add to it incrementally.
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Settings is created in T4; import will fail until then. That is expected.
from api.config import settings

# Routers are created in Section E; for now they are empty modules.
from api.routers import runs as runs_router
from api.routers import system as system_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown hooks. Populated by Section C (state plumbing)
    and Section B (DB migrations + maid_index backfill)."""
    # Startup work goes here (DB migrations, backfill jobs, etc.)
    yield
    # Shutdown work goes here


app = FastAPI(
    title="ci_ui",
    description="Custom Interchange UI — backend",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS: same-origin only in production (uvicorn serves both api and web).
# In dev the Vite proxy handles same-origin appearance to the browser.
# Per D-065 calibration: do NOT allow arbitrary origins; X-Operator-ID is
# identity, not auth, so cross-origin POSTs must be blocked at the CORS layer.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        f"http://{settings.api_host}:{settings.api_port}",
        f"http://localhost:{settings.api_port}",
        # Dev-only Vite origins; trim in production deployment per the runbook
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-Operator-ID"],
)


@app.get("/api/health")
def health():
    """Implicit ops-hygiene endpoint per D-061; not in operator-facing inventory."""
    return {"status": "ok"}


# Routers — each module exports a FastAPI APIRouter named `router`.
app.include_router(runs_router.router, prefix="/api")
app.include_router(system_router.router, prefix="/api")


# Static frontend serving (production only).
# In dev the Vite dev server hosts /web/dist/ contents itself.
# The mount is conditional on the build directory existing so dev startup
# does not fail when web/dist/ has not been built yet.
WEB_DIST = Path(__file__).parent.parent / "web" / "dist"
if WEB_DIST.exists():
    app.mount("/", StaticFiles(directory=str(WEB_DIST), html=True), name="web")
```

**File: `/api/dependencies.py`** — stub for the authz seam per D-065; real dependencies land in Section E:

```python
"""
FastAPI dependency stubs per D-065.

`require_operator` always passes in MVP; it attaches the X-Operator-ID header
value to the request context for audit-log writing and toast attribution.
`require_admin` is a no-op in MVP; production swaps in real role-based check.

When production lands real auth, both functions are search-and-replace
targets — the dependency-injection sites in the routers do not change.
"""

import uuid
from fastapi import Header


def require_operator(x_operator_id: str | None = Header(default=None)) -> str:
    """Extract operator identity from the X-Operator-ID header.

    MVP behavior: if the header is missing (browser localStorage cleared,
    private mode, request originating outside the SPA), generate a
    server-side UUID and continue. Per D-065 calibration: blocking would
    break the operator's first visit before localStorage is populated.
    """
    if not x_operator_id:
        return f"server-{uuid.uuid4()}"
    return x_operator_id


def require_admin(x_operator_id: str | None = Header(default=None)) -> str:
    """No-op in MVP per D-030. Production swaps in real role check.

    When production lands RBAC: look up the operator's role and raise 403
    if not admin. Until then, accept the same identity as require_operator.
    """
    return require_operator(x_operator_id)
```

**File: `/api/routers/__init__.py`** — empty marker.

**File: `/api/routers/runs.py`** — empty router stub (populated in Section E):

```python
"""Run lifecycle and run data endpoints. Populated in Section E."""

from fastapi import APIRouter

router = APIRouter(tags=["runs"])

# Endpoints land here in Section E:
# - POST /runs/start, /runs/{run_id}/approve, /runs/{run_id}/retry-approve, /runs/{run_id}/rerun
# - GET /runs, /runs/{run_id}, /runs/{run_id}/base-table, /runs/{run_id}/drawer/{match_tag},
#   /runs/{run_id}/raw-extract/{match_tag}, /runs/{run_id}/issues, /runs/{run_id}/events,
#   /runs/{run_id}/pdf, /runs/{run_id}/jira-info
```

**File: `/api/routers/system.py`** — empty router stub:

```python
"""System endpoints: input-folders, locks, events (SSE). Populated in Section E."""

from fastapi import APIRouter

router = APIRouter(tags=["system"])

# Endpoints land here in Section E:
# - GET /input-folders, /locks, /events
```

**File: `/api/adapters/__init__.py`** and **`/api/db/__init__.py`** — empty markers for the adapter and DB packages populated in Sections D, B, C.

**File: `/api/README.md`**:

````markdown
# ci_ui — backend

FastAPI app. Python 3.11+.

## Setup

```
python -m venv .venv
.venv\Scripts\activate          # Windows VDI
# or: source .venv/bin/activate # Linux/macOS
pip install -r requirements.txt
copy .env.example .env          # then edit ALLOWED_INPUT_ROOTS
```

## Run (dev)

```
uvicorn main:app --reload
```

App listens on http://127.0.0.1:8000 by default.

## Run (production)

```
uvicorn main:app --host 0.0.0.0 --port 8000
```

See `.env.example` for the full configuration surface.
````

### Acceptance criteria

- [ ] `cd api && pip install -r requirements.txt` succeeds in a fresh venv with Python 3.11+
- [ ] `cd api && uvicorn main:app --reload` starts the server **after T4 lands** (T1 alone will fail at `from api.config import settings` — this is expected and unblocks T4)
- [ ] After T4 lands: `curl http://127.0.0.1:8000/api/health` returns `{"status":"ok"}`
- [ ] CORS middleware rejects requests from origins not in the allowlist (verify by hitting from `http://example.com:5173` if reachable; expect 403 / blocked)
- [ ] `api/routers/runs.py` and `api/routers/system.py` exist, import successfully, and contribute zero endpoints — they are placeholders for Section E
- [ ] `api/dependencies.py` exports `require_operator` and `require_admin`; `require_operator` returns the header value or a generated `server-...` UUID

### Notes

The `from api.config import settings` import in `main.py` will fail until T4 lands. This is intentional — T1 produces the skeleton, T4 produces `config.py`, and the cycle resolves when both are in place. Acceptance criterion 2 explicitly acknowledges this.

CORS allowlist includes `http://localhost:5173` and `http://127.0.0.1:5173` for the Vite dev server. These can be removed by the production team during the AWS ECS swap per D-067 — the production env will run the built bundle behind a reverse proxy, not the Vite dev server.

`allow_methods` is restricted to `["GET", "POST"]` — no `PUT`/`PATCH`/`DELETE` endpoints exist in D-061's 16-endpoint inventory. If a future endpoint needs another verb, extend this list explicitly rather than using `["*"]`.

---

## T2 — React + Vite + TypeScript scaffold

**Depends on:** T0
**Touches files:** `/web/package.json`, `/web/vite.config.ts`, `/web/tsconfig.json`, `/web/tsconfig.node.json`, `/web/index.html`, `/web/src/main.tsx`, `/web/src/App.tsx`, `/web/src/vite-env.d.ts`, `/web/README.md`
**Estimated effort:** medium

### Goal

Stand up the Vite + React + TypeScript app shell with React Router, React Query, and Zustand providers wired. Configure Vite's `server.proxy` to route `/api/*` to the FastAPI backend in dev. No screens or real routes in this task — `App.tsx` renders a placeholder until Section F lands the AppShell, SmartFallback resolver, and route table.

### Context

From D-062 (Frontend component architecture):

> **React Query (server state) + Zustand (UI state).** React Query owns API-response caching, refetching, and SSE-driven invalidation; cache keys map to the D-061 endpoint URLs. Zustand owns the small UI-state surface: current filter chip selection, drawer open/closed, search input value, Artifact Preview divider position, current Run Detail tab.
>
> **React Router for SPA routing.** Routes: `/` → smart-fallback resolver per D-038; `/runs` → Runs List; `/runs/new` → Run Detail in pre-run state; `/runs/:id` → Run Detail (tab state in-session, not in URL per `functional-integration-spec.md` §9.5); `/runs/:id/artifact` → Artifact Preview.
>
> **Vite as build tooling.** Fast HMR, small bundles, native TypeScript, modern default for new React apps. Standard `npm run dev` / `npm run build` workflow.

From D-067 (Deployment):

> Frontend: `cd web && npm run dev` (Vite dev server on 5173 with HMR; Vite's `server.proxy` config routes `/api/*` to `localhost:8000`).

From D-064 (Error handling):

> **No automatic retry.** ... React Query's automatic-refetch-on-mount and refetch-on-window-focus are also disabled for the operator-action mutations.

### Implementation

**File: `/web/package.json`** — pin versions to avoid resolution surprises on VDI:

```json
{
  "name": "ci_ui-web",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0"
  },
  "dependencies": {
    "@tanstack/react-query": "^5.59.0",
    "lucide-react": "^0.453.0",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-pdf": "^9.1.0",
    "react-router-dom": "^6.27.0",
    "zustand": "^5.0.0"
  },
  "devDependencies": {
    "@types/react": "^18.3.11",
    "@types/react-dom": "^18.3.0",
    "@typescript-eslint/eslint-plugin": "^8.8.0",
    "@typescript-eslint/parser": "^8.8.0",
    "@vitejs/plugin-react": "^4.3.2",
    "eslint": "^8.57.1",
    "eslint-plugin-boundaries": "^4.2.2",
    "eslint-plugin-react-hooks": "^4.6.2",
    "eslint-plugin-react-refresh": "^0.4.12",
    "typescript": "^5.6.2",
    "vite": "^5.4.8"
  }
}
```

`react-pdf` is listed here because Section I depends on it; it has a moderate install footprint and we want it resolved at T2 install time so VDI install cycles don't repeat. `lucide-react` is used throughout the mockup for icons (Activity, Play, CheckCircle, etc.) and is the canonical icon library for this project.

**File: `/web/vite.config.ts`** — server proxy, alias for `@/`, build output to `dist/`:

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'node:path'

// Per D-067: dev uses Vite's server.proxy to route /api/* to the FastAPI
// backend; production uses single-uvicorn static-file serving.
//
// Per D-066 calibration: API_PORT (backend) and VITE_API_BASE_URL (frontend)
// must stay coordinated. Default port here is 8000 to match D-066's
// API_PORT default. If you change one, change both.

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: false,
        secure: false,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        // Route-based code splitting per D-063 calibration: react-pdf only
        // loads when /runs/:id/artifact is navigated to. The actual lazy()
        // wrapping happens in Section I; this configuration enables it.
        manualChunks: {
          'react-pdf': ['react-pdf'],
        },
      },
    },
  },
})
```

**File: `/web/tsconfig.json`** — strict mode on:

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

**File: `/web/tsconfig.node.json`**:

```json
{
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true,
    "strict": true
  },
  "include": ["vite.config.ts"]
}
```

**File: `/web/index.html`**:

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Custom Interchange UI</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

**File: `/web/src/vite-env.d.ts`** — Vite's env-var type declarations including the project's `VITE_*` vars:

```typescript
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
```

**File: `/web/src/main.tsx`** — providers wired; placeholder `<App />` rendering until Section F:

```typescript
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'

import App from './App'

// React Query defaults per D-064:
// - Mutations get retry: false explicitly (set per-hook, not globally)
// - Queries: short staleTime; rely on SSE-driven invalidation per D-062
// - No refetchOnWindowFocus for mutations (queries can refetch automatically)
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5_000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
    mutations: {
      // Explicit retry: false per D-064 calibration. Individual mutation
      // hooks must NOT override this without considering duplicate-side-effect
      // risk (e.g., submit_to_jira retry would risk duplicate Jira tickets).
      retry: false,
    },
  },
})

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </QueryClientProvider>
  </StrictMode>,
)
```

**File: `/web/src/App.tsx`** — placeholder; replaced in Section F when the AppShell, SmartFallback, and route table land:

```typescript
/**
 * App composition root. Populated by Section F (frontend infrastructure):
 * - AppShell with segmented toggle
 * - SmartFallback resolver against GET /api/locks
 * - Route table for /runs, /runs/new, /runs/:id, /runs/:id/artifact
 * - Error Boundaries at app root + per-screen
 *
 * Until Section F lands, this renders a placeholder so the scaffold boots.
 */
export default function App() {
  return (
    <div style={{ padding: 24, fontFamily: 'system-ui' }}>
      <h1>ci_ui scaffold</h1>
      <p>App shell lands in Section F.</p>
    </div>
  )
}
```

**File: `/web/README.md`**:

````markdown
# ci_ui — frontend

React + TypeScript + Vite SPA.

## Setup

```
npm install
copy .env.example .env
```

## Run (dev)

```
npm run dev
```

Vite dev server runs at http://localhost:5173. Requests to `/api/*` are proxied to http://localhost:8000 (the FastAPI backend; see `../api/README.md`).

## Build (production)

```
npm run build
```

Output goes to `dist/`. The FastAPI backend serves these files at `/` in production via `StaticFiles` mount (see `../api/main.py`).

## Lint

```
npm run lint
```

ESLint enforces feature-boundary rules per D-062 (cross-feature imports must flow through `src/features/shared/`). See `.eslintrc.cjs` in T3.
````

### Acceptance criteria

- [ ] `cd web && npm install` succeeds on Node 20+
- [ ] `cd web && npm run dev` starts the Vite dev server on port 5173
- [ ] Browser visits to `http://localhost:5173` render the "ci_ui scaffold" placeholder
- [ ] With the FastAPI backend running on port 8000, `fetch('/api/health')` from the dev-server origin returns `{"status":"ok"}` (verifies `server.proxy` is wired)
- [ ] `cd web && npm run build` produces `web/dist/` with `index.html` and chunked assets
- [ ] `web/dist/` contains a separate chunk for `react-pdf` (verify with `ls web/dist/assets/` showing a `react-pdf-*.js` chunk)
- [ ] The browser console shows no React Strict Mode double-render warnings or React Query provider errors on dev-server load

### Notes

`@vitejs/plugin-react` enables React Fast Refresh in dev. Strict Mode is on; expect dev-only double-effect-firing if any hook misbehaves under `<StrictMode>`.

`manualChunks` for `react-pdf` is configured here in the Vite build config but the actual `React.lazy()` wrapping of the Artifact Preview route is in Section I. Without the lazy wrapper, the chunk is still split but loaded on initial app load — the lazy() in Section I is what makes the chunk load on-demand.

React Query's default `retry: false` for mutations is set globally here. Individual mutation hooks in Sections G/H/I should NOT override this without explicit reasoning. The risk is duplicate side effects (especially `submit_to_jira` per D-064 calibration).

---

## T3 — Feature-based directory layout + ESLint boundaries

**Depends on:** T2
**Touches files:** `/web/.eslintrc.cjs`, `/web/.eslintignore`, `/web/src/features/runs/` (full tree), `/web/src/features/artifact-preview/` (full tree), `/web/src/features/shared/` (full tree)
**Estimated effort:** small

### Goal

Create the empty feature-based directory tree under `/web/src/features/` per D-062, with placeholder `index.ts` files in each sub-directory so the imports resolve cleanly. Configure ESLint to enforce the cross-feature import rule mechanically — D-062 explicitly calls out that "Declaring it isn't enough."

### Context

From D-062 (Frontend component architecture, Phase 3):

> **Feature-based directory structure.** Top-level layout: `src/features/runs/`, `src/features/artifact-preview/`, `src/features/shared/`. Each feature contains its own `screens/`, `components/`, `hooks/`, `stores/`, `api/`, `sse/`. Shared primitives (button, modal, table primitives) live in `features/shared/`. Cross-feature imports flow through `shared/` only — features don't import each other directly.

From D-062 calibration note:

> *Cross-feature import discipline needs enforcement.* The "features import only from `shared/`" rule needs an arch-test or lint rule (e.g., `eslint-plugin-boundaries`) to stop drift. Declaring it isn't enough.

### Implementation

**Directory tree to create under `/web/src/features/`:**

```
src/features/
├── runs/
│   ├── screens/
│   │   └── .gitkeep
│   ├── components/
│   │   └── .gitkeep
│   ├── hooks/
│   │   └── .gitkeep
│   ├── stores/
│   │   └── .gitkeep
│   ├── api/
│   │   └── .gitkeep
│   ├── sse/
│   │   └── .gitkeep
│   └── index.ts             (re-exports the public API of the feature)
├── artifact-preview/
│   ├── screens/
│   │   └── .gitkeep
│   ├── components/
│   │   └── .gitkeep
│   ├── hooks/
│   │   └── .gitkeep
│   ├── stores/
│   │   └── .gitkeep
│   ├── api/
│   │   └── .gitkeep
│   └── index.ts
└── shared/
    ├── components/
    │   └── .gitkeep
    ├── hooks/
    │   └── .gitkeep
    ├── stores/
    │   └── .gitkeep
    ├── api/
    │   └── .gitkeep
    ├── sse/
    │   └── .gitkeep
    ├── errors/
    │   └── messages.ts      (catalog scaffold per D-064; populated in Section F)
    ├── styles/
    │   └── .gitkeep
    └── index.ts
```

**File: `/web/src/features/runs/index.ts`**:

```typescript
/**
 * Public API of the `runs` feature.
 *
 * Other features may import from this index only — never from internal
 * subdirectories. Enforced by ESLint boundaries rule per D-062.
 *
 * Currently empty; populated by Sections G (Runs List) and H (Run Detail).
 */
export {}
```

**File: `/web/src/features/artifact-preview/index.ts`**:

```typescript
/**
 * Public API of the `artifact-preview` feature.
 *
 * Currently empty; populated by Section I.
 */
export {}
```

**File: `/web/src/features/shared/index.ts`**:

```typescript
/**
 * Public API of the `shared` feature.
 *
 * Cross-feature imports must flow through this index per D-062.
 *
 * Currently empty; populated by Section F (AppShell, BaseTableWithDrawer,
 * StateBadge, ActionPill, EntryPill, TabBar, Toast, Error Boundaries,
 * error catalog, SSE client manager, API client).
 */
export {}
```

**File: `/web/src/features/shared/errors/messages.ts`** — catalog scaffold per D-064; populated in Section F:

```typescript
/**
 * Frontend error message catalog per D-064.
 *
 * Backend-originating errors (per D-061 envelope) render the server-supplied
 * `message` + `remediation_hint` directly; no entry in this catalog needed.
 *
 * This catalog holds messages for frontend-originating errors only:
 * Error Boundary catches, network drops detected by React Query before a
 * response arrives, PDF render failures, SSE disconnects, etc.
 *
 * Populated in Section F.
 */

export const FRONTEND_ERROR_MESSAGES: Record<string, { message: string; hint?: string }> = {
  // Section F populates these. Example shape:
  // NETWORK_UNREACHABLE: {
  //   message: "Could not reach the server.",
  //   hint: "Check that the backend is running and try again.",
  // },
}
```

**File: `/web/.eslintrc.cjs`** — feature-boundary rules per D-062 calibration:

```javascript
/* eslint-env node */
module.exports = {
  root: true,
  env: { browser: true, es2020: true },
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react-hooks/recommended',
  ],
  ignorePatterns: ['dist', '.eslintrc.cjs', 'public/fonts'],
  parser: '@typescript-eslint/parser',
  plugins: [
    'react-refresh',
    'boundaries',
  ],
  settings: {
    'boundaries/elements': [
      { type: 'feature-runs',             pattern: 'src/features/runs/**' },
      { type: 'feature-artifact-preview', pattern: 'src/features/artifact-preview/**' },
      { type: 'feature-shared',           pattern: 'src/features/shared/**' },
    ],
    'boundaries/include': ['src/**/*'],
  },
  rules: {
    // Per D-062: features import only from shared; shared imports from nothing.
    'boundaries/element-types': ['error', {
      default: 'disallow',
      rules: [
        // Feature `runs` may import from itself and from `shared` only.
        { from: 'feature-runs', allow: ['feature-runs', 'feature-shared'] },
        // Feature `artifact-preview` same shape.
        { from: 'feature-artifact-preview', allow: ['feature-artifact-preview', 'feature-shared'] },
        // `shared` may import from nothing else inside `features/`.
        { from: 'feature-shared', allow: ['feature-shared'] },
      ],
    }],
    'react-refresh/only-export-components': [
      'warn',
      { allowConstantExport: true },
    ],
    // Allow `_` prefix on unused params (matches the React idiom for event handlers).
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
  },
}
```

**File: `/web/.eslintignore`**:

```
dist
node_modules
public/fonts
*.config.ts
*.config.js
```

### Acceptance criteria

- [ ] Directory tree under `/web/src/features/` matches the layout above exactly (three feature directories, each with sub-directories per D-062)
- [ ] `cd web && npm run lint` passes with zero errors on the scaffold
- [ ] **Boundary test (deliberate violation):** create a temporary file `web/src/features/runs/screens/TestImportViolation.tsx` that does `import x from '../../artifact-preview'`; running `npm run lint` reports a `boundaries/element-types` error pointing at that line. Delete the test file after verifying.
- [ ] **Allowed import test:** the same file doing `import x from '../../shared'` passes lint
- [ ] `web/src/features/shared/errors/messages.ts` exports `FRONTEND_ERROR_MESSAGES` as a typed Record (empty for now)

### Notes

The `.gitkeep` files exist only to make the empty directories committable. They can be deleted as soon as a real file lands in each sub-directory.

D-062's "features don't import each other directly" rule is bidirectional — `artifact-preview` can't import from `runs` either, even though Artifact Preview is accessed from Run Detail's Results tab. The cross-feature contract is: shared `<BaseTableWithDrawer>` (in `shared/`) is consumed by both `runs` (Results tab) and `artifact-preview` (artifact pane). Neither feature reaches into the other.

If a future Phase 5 task surfaces a genuine cross-feature dependency the lint rule blocks, the answer is to move the shared piece into `shared/`, not to relax the rule. Document any such promotion in a follow-up Decisions Log proposal back to V.

---

## T4 — pydantic-settings Settings class + 13-variable env schema

**Depends on:** T1
**Touches files:** `/api/config.py`
**Estimated effort:** medium

### Goal

Create the typed `Settings` class that loads all 13 environment variables (12 backend per D-066 + 1 added in Phase 5 for `JPMC_JIRA_BASE_URL` per D-073 resolution). Wire fail-fast validation with helpful error messages, including the conditional-required check on `PIPELINE_MODULE_PATH`. The frontend `VITE_API_BASE_URL` is loaded by Vite separately (T5 covers the `.env.example` files for both packages).

### Context

From D-066 (Configuration management):

> **Env schema — 12 variables across both packages.**
> *Backend `/api/.env`:* `ADAPTER_PROFILE` (default `mock`), `MOCK_LATENCY` (default `realistic`), `MOCK_FAILURE` (default `none`), `PIPELINE_MODULE_PATH` (required when ADAPTER_PROFILE=real), `PYTHON_INTERPRETER` (default `python3`), `OUTPUT_BASE_FOLDER` (default `./output`), `ALLOWED_INPUT_ROOTS` (required, comma-separated), `SQLITE_DB_PATH` (default `./data/ci_pipeline.db`), `LOG_LEVEL` (default `INFO`), `API_HOST` (default `127.0.0.1`), `API_PORT` (default `8000`).
> *Frontend `/web/.env`:* `VITE_API_BASE_URL` (default `http://localhost:8000`).

From D-066 calibration:

> *`PIPELINE_MODULE_PATH` is conditionally required (when `ADAPTER_PROFILE=real`).* Pydantic-settings handles this cleanly via `@model_validator`. The validation error message should also be conditional — *"`PIPELINE_MODULE_PATH` is required when `ADAPTER_PROFILE=real`; not needed for `mock`"* rather than a generic "required field missing." Saves an investigation cycle for someone running mock mode.

From D-073 calibration (Phase 5 resolution):

> Recommended resolution path for the open questions: backend constructs full URLs server-side in `GET /api/runs/{run_id}/jira-info` (per D-061), returning `{epic_key, epic_url, story_key, story_url, sharepoint_path}` rather than just keys. This consolidates URL-pattern knowledge in one place (backend), avoids extending D-066's env schema with a 13th variable on the frontend side (where `VITE_*` vars are baked at build time per D-066's calibration note), and lets the production team change the Jira host or pattern without a frontend rebuild.

The 13th variable is `JPMC_JIRA_BASE_URL` on the **backend** side; the frontend remains at 1 variable (`VITE_API_BASE_URL`). Total backend variables now 12.

### Implementation

**File: `/api/config.py`**:

```python
"""
Application configuration.

Loaded once at startup via pydantic-settings; consumed by FastAPI
dependency injection elsewhere. Fail-fast validation per D-066: the
backend refuses to boot if any required variable is missing or malformed.

Schema:
    ADAPTER_PROFILE       — "mock" | "real" (default: "mock")
    MOCK_LATENCY          — "realistic" | "instant" (default: "realistic")
    MOCK_FAILURE          — "none" | "staged" | "approval" (default: "none")
    PIPELINE_MODULE_PATH  — required when ADAPTER_PROFILE=real; absolute path
                            to the pipeline package on VDI (typically
                            ...\\CI_Main\\CI_Vision)
    PYTHON_INTERPRETER    — interpreter used for subprocess pipeline calls
                            (default: "python3")
    OUTPUT_BASE_FOLDER    — root directory for run output folders
                            (default: "./output"; production sets to
                            ...\\CI_Main\\CI_Vision\\output)
    ALLOWED_INPUT_ROOTS   — required; comma-separated list of allowed input
                            root directories (per D-013 allowlist)
    SQLITE_DB_PATH        — app-state SQLite DB path
                            (default: "./data/ci_pipeline.db")
    JPMC_JIRA_BASE_URL    — base URL for JPMC Jira (per D-073 Phase 5
                            resolution); used by /api/runs/{id}/jira-info
                            to construct Epic/Story URLs server-side.
                            Default: "https://jira.jpmchase.net"
    LOG_LEVEL             — Python logging level (default: "INFO")
    API_HOST              — uvicorn bind host (default: "127.0.0.1";
                            override to "0.0.0.0" for production via CLI
                            per D-067 calibration)
    API_PORT              — uvicorn bind port (default: 8000)

Frontend's VITE_API_BASE_URL is loaded by Vite separately; see
/web/.env.example.
"""

from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Adapter selection ---
    adapter_profile: Literal["mock", "real"] = Field(
        default="mock",
        description="Which adapter implementations to use globally.",
    )
    mock_latency: Literal["realistic", "instant"] = Field(
        default="realistic",
        description="MockPipelineRunner event-cadence mode.",
    )
    mock_failure: Literal["none", "staged", "approval"] = Field(
        default="none",
        description="MockPipelineRunner failure injection mode.",
    )

    # --- Real-adapter requirements ---
    pipeline_module_path: str | None = Field(
        default=None,
        description=(
            "Absolute path to the pipeline package on VDI. "
            "Required when adapter_profile='real'."
        ),
    )
    python_interpreter: str = Field(
        default="python3",
        description="Python interpreter for subprocess pipeline calls.",
    )

    # --- Filesystem layout ---
    output_base_folder: str = Field(
        default="./output",
        description="Root directory under which run folders are created.",
    )
    allowed_input_roots: str = Field(
        ...,  # required
        description=(
            "Comma-separated list of allowed input root directories. "
            "Per D-013 allowlist. At least one root is required."
        ),
    )

    # --- App-state DB ---
    sqlite_db_path: str = Field(
        default="./data/ci_pipeline.db",
        description="Path to the application SQLite database.",
    )

    # --- External integrations ---
    jpmc_jira_base_url: str = Field(
        default="https://jira.jpmchase.net",
        description=(
            "Base URL for JPMC Jira. Used by GET /api/runs/{run_id}/jira-info "
            "to construct Epic and Story URLs server-side per D-073 Phase 5 "
            "resolution. Change here (not the frontend) to swap hosts; no "
            "rebuild required."
        ),
    )

    # --- Logging ---
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
    )

    # --- uvicorn ---
    api_host: str = Field(
        default="127.0.0.1",
        description=(
            "uvicorn bind host. Default is the safer dev-only loopback; "
            "production runs override to 0.0.0.0 via the uvicorn CLI flag "
            "per D-067. CLI flag wins over this env value."
        ),
    )
    api_port: int = Field(
        default=8000,
        description=(
            "uvicorn bind port. Must match the port referenced by "
            "VITE_API_BASE_URL in /web/.env per D-066 coordination."
        ),
    )

    # --- Computed properties ---
    @property
    def allowed_input_roots_list(self) -> list[Path]:
        """Parse the comma-separated allowed roots into resolved Path objects."""
        return [
            Path(r.strip()).resolve()
            for r in self.allowed_input_roots.split(",")
            if r.strip()
        ]

    @property
    def output_base_folder_path(self) -> Path:
        return Path(self.output_base_folder).resolve()

    @property
    def sqlite_db_path_resolved(self) -> Path:
        return Path(self.sqlite_db_path).resolve()

    # --- Validators ---
    @field_validator("allowed_input_roots")
    @classmethod
    def _validate_allowed_input_roots(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError(
                "ALLOWED_INPUT_ROOTS not set in /api/.env — at least one "
                "allowed input root is required (per D-013 allowlist). "
                "Example: ALLOWED_INPUT_ROOTS=C:\\Users\\...\\CI_Main\\CI_Vision\\input"
            )
        roots = [r.strip() for r in v.split(",") if r.strip()]
        if not roots:
            raise ValueError(
                "ALLOWED_INPUT_ROOTS was set but contained only empty entries. "
                "Provide at least one non-empty path."
            )
        return v

    @model_validator(mode="after")
    def _validate_conditional_pipeline_path(self) -> "Settings":
        """Enforce D-066 calibration: PIPELINE_MODULE_PATH required when real."""
        if self.adapter_profile == "real" and not self.pipeline_module_path:
            raise ValueError(
                "PIPELINE_MODULE_PATH is required when ADAPTER_PROFILE=real; "
                "not needed for mock. Set PIPELINE_MODULE_PATH in /api/.env "
                "to the absolute path of the pipeline package on this machine "
                "(typically ...\\CI_Main\\CI_Vision)."
            )
        if self.adapter_profile == "real" and self.pipeline_module_path:
            if not Path(self.pipeline_module_path).exists():
                raise ValueError(
                    f"PIPELINE_MODULE_PATH points to a path that does not "
                    f"exist: {self.pipeline_module_path}. Check the path in "
                    f"/api/.env."
                )
        return self


# Module-level singleton. Importing this module triggers env loading and
# validation. A startup failure here is intentional and visible.
settings = Settings()  # type: ignore[call-arg]
```

### Acceptance criteria

- [ ] `cd api && python -c "from api.config import settings; print(settings.adapter_profile)"` prints `mock` when `.env` contains only `ALLOWED_INPUT_ROOTS=C:\tmp` (defaults populate everything else)
- [ ] Removing `ALLOWED_INPUT_ROOTS` from `.env` and re-running the import raises `ValidationError` with a message naming the variable AND directing the operator to `/api/.env`
- [ ] Setting `ADAPTER_PROFILE=real` without `PIPELINE_MODULE_PATH` raises a `ValidationError` whose message reads literally `"PIPELINE_MODULE_PATH is required when ADAPTER_PROFILE=real; not needed for mock."` (the calibration message from D-066)
- [ ] Setting `ADAPTER_PROFILE=real` with a `PIPELINE_MODULE_PATH` that does not exist on disk raises a `ValidationError` naming the missing path
- [ ] `settings.allowed_input_roots_list` returns a `list[Path]` of resolved absolute paths
- [ ] `settings.jpmc_jira_base_url` returns `"https://jira.jpmchase.net"` when the env var is unset (the default)
- [ ] After T1's `main.py` is in place plus this T4, `uvicorn main:app --reload` starts cleanly with a minimal `.env` (just `ALLOWED_INPUT_ROOTS=C:\tmp`)

### Notes

The 13th variable (`JPMC_JIRA_BASE_URL`) lives on the **backend** intentionally per D-073 Phase 5 resolution — frontend `VITE_*` vars bake at build time per D-066 calibration, so moving the Jira host to the frontend would force a rebuild every time the host changes. Backend env var means a `.env` edit + uvicorn restart is the entire change.

The default `https://jira.jpmchase.net` is a guess at the on-prem JPMC Jira host. If V's environment uses a different host (e.g., Atlassian Cloud `jpmc.atlassian.net`), update the value in `/api/.env`. The default in code is preserved so the app boots even if `.env` doesn't override.

`extra="ignore"` lets `.env` files carry transitional or commented-out variables without breaking startup. This is friendlier than `extra="forbid"`; the trade-off is that typos like `ALLOWD_INPUT_ROOTS=...` will silently miss the required variable and fail validation with the "required" message rather than a "typo" hint. Acceptable since the validation message guides correction either way.

The `# type: ignore[call-arg]` on the singleton assignment is because pydantic-settings' `BaseSettings.__init__` accepts no positional args at the type level even though the env-loading machinery populates fields — a known pydantic-settings idiom.

---

## T5 — `.env.example` files for both packages

**Depends on:** T0, T4
**Touches files:** `/api/.env.example`, `/web/.env.example`
**Estimated effort:** small

### Goal

Create checked-in `.env.example` files for both packages with every variable documented inline. Per D-066 secrets handling: the actual `.env` files are gitignored (already in T0); the `.example` files give a new contributor or the production team a complete map of the configuration surface.

### Context

From D-066 (Configuration management):

> **Secrets handling — standard pattern.** Both `.env` files are gitignored. `.env.example` files are checked in with all variable names, example values, and per-variable inline comments. No secrets hardcoded anywhere in the codebase.

From D-066 calibration:

> *`API_PORT` and `VITE_API_BASE_URL` must stay coordinated.* Changing `API_PORT` to 8001 requires updating `VITE_API_BASE_URL` to match. Two separate `.env` files, two places to remember. Phase 5 should at minimum document the coordination explicitly in both `.env.example` files (inline comment on each variable pointing at the other).

From D-067 calibration:

> *`API_HOST` env default vs. production CLI override.* D-066 sets `API_HOST=127.0.0.1` as the safer dev default; this entry's production command uses `--host 0.0.0.0` to make the app reachable from peer operators' browsers. uvicorn's CLI flag overrides the env. Phase 5 should document this explicitly in `.env.example` (inline comment on `API_HOST`) and in the production startup runbook.

### Implementation

**File: `/api/.env.example`** — all 12 backend variables with inline documentation:

```dotenv
# ===========================================================================
# ci_ui backend configuration — copy this file to .env and edit as needed.
#
# .env is gitignored. .env.example is the canonical map of the config
# surface; keep it in sync with api/config.py.
#
# Per D-066: fail-fast validation runs at startup; the backend refuses to
# boot if a required variable is missing.
# ===========================================================================

# ---------------------------------------------------------------------------
# Adapter selection
# ---------------------------------------------------------------------------

# Which adapter implementations to use. "mock" reads fixtures from disk and
# simulates pipeline runs; "real" invokes the actual pipeline subprocess.
# Default: mock
ADAPTER_PROFILE=mock

# MockPipelineRunner event-cadence mode. "realistic" emits events on timers
# that approximate real pipeline pacing; "instant" fires all events at once.
# Used only when ADAPTER_PROFILE=mock.
# Default: realistic
MOCK_LATENCY=realistic

# MockPipelineRunner failure injection mode. "none" runs cleanly through;
# "staged" injects a failure during run_unified_pipeline; "approval" injects
# a failure during submit_to_jira. Used only when ADAPTER_PROFILE=mock.
# Default: none
MOCK_FAILURE=none

# ---------------------------------------------------------------------------
# Real-adapter requirements (only used when ADAPTER_PROFILE=real)
# ---------------------------------------------------------------------------

# Absolute path to the pipeline package on this machine. Required when
# ADAPTER_PROFILE=real; ignored when ADAPTER_PROFILE=mock.
# Typically points at the sibling CI_Vision repo.
# Example: PIPELINE_MODULE_PATH=C:\Users\you\CI_Main\CI_Vision
PIPELINE_MODULE_PATH=

# Python interpreter used to spawn pipeline subprocess. Useful when the
# pipeline lives in a different venv than the UI.
# Default: python3
PYTHON_INTERPRETER=python3

# ---------------------------------------------------------------------------
# Filesystem layout
# ---------------------------------------------------------------------------

# Root directory under which run output folders are created. The pipeline
# writes output/<merchant>_<timestamp>/ subdirectories here.
# For production with the sibling CI_Vision setup:
# OUTPUT_BASE_FOLDER=C:\Users\you\CI_Main\CI_Vision\output
# Default: ./output
OUTPUT_BASE_FOLDER=./output

# Allowed input root directories — operator can pick agreement folders only
# from beneath these roots per D-013. Comma-separated; at least one is
# REQUIRED. Paths are resolved to absolute at load time.
# Example: ALLOWED_INPUT_ROOTS=C:\Users\you\CI_Main\CI_Vision\input
ALLOWED_INPUT_ROOTS=

# Path to the application's SQLite database (locks, events, maid_index,
# audit_log). Per D-058: D-067's manual process management relies on this
# DB being readable across uvicorn restarts.
# Default: ./data/ci_pipeline.db
SQLITE_DB_PATH=./data/ci_pipeline.db

# ---------------------------------------------------------------------------
# External integrations
# ---------------------------------------------------------------------------

# Base URL for JPMC Jira. The backend constructs Epic and Story click-through
# URLs by appending /browse/<KEY> to this value (per D-073 Phase 5
# resolution). Change this here, not in the frontend bundle, when the Jira
# host changes — no rebuild required.
# Default: https://jira.jpmchase.net
JPMC_JIRA_BASE_URL=https://jira.jpmchase.net

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

# Python logging level. One of DEBUG / INFO / WARNING / ERROR / CRITICAL.
# Default: INFO
LOG_LEVEL=INFO

# ---------------------------------------------------------------------------
# uvicorn bind
# ---------------------------------------------------------------------------

# uvicorn bind host. The safe default 127.0.0.1 (loopback only) is
# appropriate for local dev. For production on VDI, override on the
# uvicorn CLI: `uvicorn main:app --host 0.0.0.0 --port 8000` (per D-067).
# The CLI flag wins over this env value.
# Default: 127.0.0.1
API_HOST=127.0.0.1

# uvicorn bind port. MUST stay coordinated with VITE_API_BASE_URL in
# /web/.env (per D-066 calibration). Changing 8000 here without changing
# /web/.env breaks the dev-time proxy and the production fetch base URL.
# Default: 8000
API_PORT=8000
```

**File: `/web/.env.example`**:

```dotenv
# ===========================================================================
# ci_ui frontend configuration — copy this file to .env and edit as needed.
#
# .env is gitignored. Only variables prefixed VITE_ are exposed to the
# React app at build time. Per D-066 calibration: VITE_* values are baked
# into the JS bundle during `npm run build`; the same bundle can't deploy
# to multiple environments without rebuilding.
# ===========================================================================

# Base URL of the backend API. In dev this is overridden by Vite's
# server.proxy config (see vite.config.ts) so fetch('/api/...') just works
# from the dev-server origin. In production (single-uvicorn deployment per
# D-067) this can stay as a relative origin or empty — the same uvicorn
# process serves both api and web.
#
# MUST stay coordinated with API_PORT in /api/.env (per D-066 calibration).
# Changing API_PORT to 8001 without updating this URL breaks the build's
# fetch base.
#
# Default: http://localhost:8000
VITE_API_BASE_URL=http://localhost:8000
```

### Acceptance criteria

- [ ] `/api/.env.example` contains exactly 12 variable assignments (12 `KEY=` lines)
- [ ] `/web/.env.example` contains exactly 1 variable assignment
- [ ] Both files are tracked in git (`git ls-files` shows them); the corresponding `.env` files are NOT tracked (gitignored per T0)
- [ ] `cd api && copy .env.example .env && echo ALLOWED_INPUT_ROOTS=C:\tmp >> .env && python -c "from api.config import settings; print(settings.api_port)"` prints `8000`
- [ ] `cd web && copy .env.example .env && npm run dev` starts cleanly with the Vite proxy pointing at the documented backend port
- [ ] Each variable in `/api/.env.example` has an inline `# ...` comment explaining purpose, default, and any cross-variable coordination

### Notes

`ALLOWED_INPUT_ROOTS` is left empty in `.env.example` — copying the example file as-is will fail validation per T4, which is the correct behavior. The operator must explicitly choose at least one root.

The `JPMC_JIRA_BASE_URL` default `https://jira.jpmchase.net` is a placeholder. If V's environment differs (Atlassian Cloud `jpmc.atlassian.net`, a different on-prem hostname, etc.), update the value in the operator's `.env` — the `.env.example` default can also be updated in a follow-up commit if the host is confirmed.

For production deployment on VDI per D-067, the production team typically copies `.env.example` to `.env` once and edits the values, then never touches the example file again. Keep the example file as the "what knobs exist" reference even after production rolls.

---

## T6 — Font vendoring (General Sans + JetBrains Mono)

**Depends on:** T2
**Touches files:** `/web/public/fonts/` (seven `.woff2` files), `/web/src/features/shared/styles/fonts.css`
**Estimated effort:** small

### Goal

Self-host General Sans and JetBrains Mono in `/web/public/fonts/` with `@font-face` declarations referencing local files. Per the Phase 5 directive resolving D-069's calibration note: do not rely on Fontshare CDN access from JPMC VDI. The `@font-face` family names match those referenced by the `--font-sans` and `--font-mono` CSS variables landing in T7.

### Context

From D-069 (Typography, Phase 4):

> **Choice:** General Sans for body and headings; JetBrains Mono for IDs, MAIDs, mnemonics, timestamps, match tags, JSON content, and tabular numerics.

From D-069 calibration:

> JPMC VDI may block Fontshare CDN access. The conservative play is to self-host both fonts (vendor the .woff2 files into the repo at `/web/public/fonts/` and reference them via `@font-face`) rather than wait to discover CDN blocks at deploy time. Cost: ~150 KB of bundled font files; benefit: VDI-deployment robustness independent of network policy.

Phase 5 bootstrap directive:

> **D-069 font availability:** self-host General Sans and JetBrains Mono in `/web/public/fonts/` with `@font-face` declarations referencing the local files. Do NOT rely on Fontshare CDN access from JPMC VDI. Generate the task to vendor the .woff2 files and the corresponding CSS.

### Implementation

**Step 1 — Acquire the `.woff2` files.**

The visual mockup uses these weight ranges:
- General Sans weights: 200, 300, 400, 500, 600, 700
- JetBrains Mono weights: 300, 400, 500, 600, 700

To save bundle size and match actual usage in the mockup, vendor only the weights that appear: General Sans 400 + 500 + 600 + 700 (regular, medium, semibold, bold used by `font-weight: 500` in `.h-display`, `.btn`, `.h-label`, etc.) and JetBrains Mono 400 + 500 + 600.

Acquisition sources (download once, commit to repo):

- **General Sans:** https://www.fontshare.com/fonts/general-sans (download "Free Download" → desktop bundle → extract Fonts/WEB/woff2/)
- **JetBrains Mono:** https://www.jetbrains.com/lp/mono/ (download → extract `fonts/webfonts/`)

Both fonts have permissive licenses (General Sans is free under the Fontshare license; JetBrains Mono is OFL-1.1).

**Step 2 — Place the files:**

```
web/public/fonts/
├── GeneralSans-Regular.woff2     (weight 400)
├── GeneralSans-Medium.woff2      (weight 500)
├── GeneralSans-Semibold.woff2    (weight 600)
├── GeneralSans-Bold.woff2        (weight 700)
├── JetBrainsMono-Regular.woff2   (weight 400)
├── JetBrainsMono-Medium.woff2    (weight 500)
└── JetBrainsMono-SemiBold.woff2  (weight 600)
```

Seven files. Approximate total size: ~120 KB. Acceptable per D-069 calibration (~150 KB ceiling).

**File: `/web/src/features/shared/styles/fonts.css`** — `@font-face` declarations:

```css
/*
 * Self-hosted fonts per resolved D-069 Phase 5 directive.
 *
 * General Sans is the body/heading typeface; JetBrains Mono is for IDs,
 * MAIDs, mnemonics, timestamps, match tags, JSON content, and tabular
 * numerics.
 *
 * Loaded from /public/fonts/ (Vite serves /public/* at the site root in
 * dev and copies to dist/ in production builds).
 *
 * `font-display: swap` prevents the FOIT (flash of invisible text) — the
 * fallback in --font-sans / --font-mono renders first, then swaps when
 * the woff2 lands. Acceptable per the brief.
 */

@font-face {
  font-family: 'General Sans';
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url('/fonts/GeneralSans-Regular.woff2') format('woff2');
}

@font-face {
  font-family: 'General Sans';
  font-style: normal;
  font-weight: 500;
  font-display: swap;
  src: url('/fonts/GeneralSans-Medium.woff2') format('woff2');
}

@font-face {
  font-family: 'General Sans';
  font-style: normal;
  font-weight: 600;
  font-display: swap;
  src: url('/fonts/GeneralSans-Semibold.woff2') format('woff2');
}

@font-face {
  font-family: 'General Sans';
  font-style: normal;
  font-weight: 700;
  font-display: swap;
  src: url('/fonts/GeneralSans-Bold.woff2') format('woff2');
}

@font-face {
  font-family: 'JetBrains Mono';
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url('/fonts/JetBrainsMono-Regular.woff2') format('woff2');
}

@font-face {
  font-family: 'JetBrains Mono';
  font-style: normal;
  font-weight: 500;
  font-display: swap;
  src: url('/fonts/JetBrainsMono-Medium.woff2') format('woff2');
}

@font-face {
  font-family: 'JetBrains Mono';
  font-style: normal;
  font-weight: 600;
  font-display: swap;
  src: url('/fonts/JetBrainsMono-SemiBold.woff2') format('woff2');
}
```

T7 will import this file alongside `tokens.css` into the app's root style chain.

### Acceptance criteria

- [ ] `/web/public/fonts/` contains exactly seven `.woff2` files matching the names above
- [ ] `/web/src/features/shared/styles/fonts.css` contains seven `@font-face` blocks (four General Sans, three JetBrains Mono) referencing the local files via `/fonts/...` paths
- [ ] All `@font-face` declarations use `font-display: swap`
- [ ] After T7 lands and imports `fonts.css`: opening DevTools → Network → filter "Font" while loading the app shows seven `200 OK` responses for the `.woff2` files (or fewer if the browser cache is populated)
- [ ] No requests to `api.fontshare.com` or `fonts.googleapis.com` appear in the Network tab (verifies no CDN leakage)
- [ ] `npm run build` produces a `dist/fonts/` directory mirroring `public/fonts/` contents
- [ ] Setting an element to `font-family: var(--font-mono)` (per T7's `:root` tokens) renders in JetBrains Mono visually distinct from the General Sans body

### Notes

Acquisition of the `.woff2` files is the only manual step in this task — they are not regenerable by Copilot from scratch. Once they land in the repo, they are checked in and survive the air-gap transfer cleanly. Re-vendoring is only necessary if a font weight that isn't in the seven is later needed.

If V's environment cannot accept the `.woff2` binary checkin (some Bitbucket configurations are picky about binary blobs), the alternative is to write a small build-time script that downloads them from Fontshare and Google Fonts at install time — but that re-introduces CDN dependency the resolved directive specifically rejects. Vendoring is the correct path.

The font fallback chain in `--font-sans` (T7) goes `'General Sans', ui-sans-serif, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`. If the `.woff2` files fail to load (e.g., permissions, network in dev), the fallback chain is acceptable and the app remains usable — the aesthetic degrades but functionality is intact.

---

## T7 — Aesthetic CSS variable tokens (deep oceanic palette)

**Depends on:** T2, T6
**Touches files:** `/web/src/features/shared/styles/tokens.css`, `/web/src/features/shared/styles/index.ts`, `/web/src/main.tsx` (import addition)
**Estimated effort:** small

### Goal

Establish the global CSS variable layer for the deep-oceanic palette per D-068. These tokens are consumed by every component built in Sections F through I. Import order: `fonts.css` (T6) → `tokens.css` (this task) → app component styles.

### Context

From D-068 (Aesthetic direction, Phase 4):

> Deep oceanic: near-black navy base, cyan/teal glass tints, pale amber accents.
> The Phosphor-terminal alternative was rejected specifically because its green tint would have fought D-047's green Add badge — confirming D-047's coloring system as the anchor that constrains the global palette choice rather than vice versa.

From D-047 (Action coloring):

> Base table coloring: Add → green, Remove → red, Rate Update → yellow / amber, MCC Expansion → blue.
> Drawer ETL Impact coloring: ADD → green, REMOVE → red, NO_CHANGE → gray, PEOPLESOFT_ONLY → blue or purple.

From the Phase 4 closing packet:

> Aesthetic carve-out on data tables — atmospheric glass material applies to chrome, drawer, timeline cards, run-context strip, toasts, and modals but NOT to the 18-column Results base table or the 12-column ETL Impact table (flat cells against the dark navy base). Per the design brief's readability-non-negotiable clause.

From `visual-mockup.jsx` `:root` block — the source-of-truth token values reproduced verbatim in Implementation below.

### Implementation

**File: `/web/src/features/shared/styles/tokens.css`** — exact token values from the mockup plus a documented carve-out utility for data-table flat rendering:

```css
/*
 * ci_ui global aesthetic tokens — deep oceanic palette per D-068.
 *
 * Token values are sourced verbatim from visual-mockup.jsx GlobalStyle.
 * Component styles in Sections F through I reference these variables
 * exclusively — no hex literals in component CSS.
 *
 * Two-tier action coloring per D-047:
 *   Base-table badges:  --add / --rate / --mcc / --remove
 *   Drawer ETL Impact:  --add / --remove / --nochange / --psonly
 *
 * State badges per D-045 filesystem-inferred states (Phase 2 + Phase 4):
 *   --state-pre / --state-sub / --state-stale / --state-prog / --state-fail
 *
 * Issue severity per D-049:  --crit / --err / --warn
 *
 * CARVE-OUT (D-068 + Phase 4 closing packet):
 * The atmospheric glass material applies to chrome, drawer panels,
 * timeline cards, run-context strip, toasts, and modals — but NOT to
 * the 18-column Results base table or the 12-column ETL Impact table.
 * Those render flat against the navy base for readability. Section H
 * tasks enforce this carve-out at component level; the .data-table-flat
 * utility class below is the surface the carve-out attaches to.
 */

:root {
  /* ---- Surface backgrounds ---- */
  --bg: #06090f;
  --bg-soft: #0a0f18;
  --bg-elev: #0e141f;

  /* ---- Ink (text) ---- */
  --ink: #e6ecf5;
  --ink-soft: rgba(230, 236, 245, 0.78);
  --ink-mute: rgba(230, 236, 245, 0.52);
  --ink-dim: rgba(230, 236, 245, 0.32);
  --ink-faint: rgba(230, 236, 245, 0.14);

  /* ---- Accent palette ---- */
  --cyan: #7dd3fc;
  --cyan-soft: rgba(125, 211, 252, 0.18);
  --teal: #5eead4;
  --amber: #f7d28f;
  --amber-soft: rgba(247, 210, 143, 0.16);

  /* ---- Glass material (chrome, drawer, modals — NOT data tables) ---- */
  --glass: rgba(255, 255, 255, 0.035);
  --glass-strong: rgba(255, 255, 255, 0.06);
  --glass-stroke: rgba(255, 255, 255, 0.08);
  --glass-stroke-strong: rgba(255, 255, 255, 0.14);
  --glass-highlight: rgba(255, 255, 255, 0.18);

  /* ---- Action badge colors per D-047 base-table tier ---- */
  --add: #6ee7a0;
  --add-bg: rgba(110, 231, 160, 0.14);
  --rate: #facc6b;
  --rate-bg: rgba(250, 204, 107, 0.14);
  --mcc: #93c5fd;
  --mcc-bg: rgba(147, 197, 253, 0.14);
  --remove: #fca5a5;
  --remove-bg: rgba(252, 165, 165, 0.14);

  /* ---- entry_type coloring per D-047 drawer-ETL-Impact tier ---- */
  --nochange: #94a3b8;
  --nochange-bg: rgba(148, 163, 184, 0.12);
  --psonly: #c4b5fd;
  --psonly-bg: rgba(196, 181, 253, 0.14);
  /* ADD and REMOVE reuse the badge tokens above (--add / --remove). */

  /* ---- State badges (D-045 filesystem-inferred states) ---- */
  --state-pre: #f7d28f;     /* Pre-approval */
  --state-sub: #6ee7a0;     /* Submitted */
  --state-stale: #94a3b8;   /* Stale */
  --state-prog: #7dd3fc;    /* In-progress (any phase, per V's single-lock model) */
  --state-fail: #fca5a5;    /* Failed */

  /* ---- Issue severity (D-049) ---- */
  --crit: #f87171;
  --err: #fb923c;
  --warn: #facc15;

  /* ---- Radius scale ---- */
  --radius-sm: 6px;
  --radius: 10px;
  --radius-lg: 14px;
  --radius-xl: 20px;

  /* ---- Typography (fonts loaded by fonts.css in T6) ---- */
  --font-sans: 'General Sans', ui-sans-serif, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-mono: 'JetBrains Mono', ui-monospace, 'SF Mono', monospace;
}

/* ---- Reset ---- */
*, *::before, *::after { box-sizing: border-box; }

html, body, #root { height: 100%; }

body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: var(--font-sans);
  font-weight: 400;
  font-feature-settings: "ss01", "ss02", "cv01";
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  letter-spacing: -0.005em;
  line-height: 1.5;
}

/* ---- Utility: mono + tabular nums ---- */
.mono { font-family: var(--font-mono); font-feature-settings: "tnum", "ss01"; }
.num  { font-family: var(--font-mono); font-variant-numeric: tabular-nums; }

/* ---- Utility: glass-flat — the carve-out surface for data tables ----
 * Use this on the 18-column Results base table and the 12-column ETL
 * Impact table per D-068 + Phase 4 closing packet. Other tables (e.g.,
 * Field Deltas panel within the drawer) are NOT data tables in this
 * sense; they live inside glass surfaces and inherit the parent's
 * material.
 */
.data-table-flat {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--glass-stroke);
  border-radius: var(--radius);
}
```

**File: `/web/src/features/shared/styles/index.ts`** — barrel for the styles directory:

```typescript
/**
 * Side-effect import of global stylesheets.
 *
 * Order matters: fonts must load before tokens so the @font-face
 * declarations are present when tokens.css's --font-sans / --font-mono
 * are first resolved.
 */
import './fonts.css'
import './tokens.css'
```

**Modification to `/web/src/main.tsx`** — add one import at the top:

```typescript
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter } from 'react-router-dom'

// Global styles (fonts.css + tokens.css). Import early so all components
// resolve --font-sans / --font-mono and palette tokens consistently.
import '@/features/shared/styles'

import App from './App'

// ... (rest unchanged from T2)
```

### Acceptance criteria

- [ ] `/web/src/features/shared/styles/tokens.css` exists and contains every variable from the mockup's `:root` block verbatim
- [ ] `/web/src/features/shared/styles/fonts.css` from T6 is imported by `/web/src/features/shared/styles/index.ts` before `tokens.css`
- [ ] `/web/src/main.tsx` imports `'@/features/shared/styles'` before its `App` import
- [ ] Loading the dev server in a browser: `getComputedStyle(document.documentElement).getPropertyValue('--bg')` in the console returns `#06090f` (or the resolved value with leading whitespace)
- [ ] `getComputedStyle(document.body).fontFamily` includes `"General Sans"` as the first entry
- [ ] `getComputedStyle(document.body).backgroundColor` resolves to a dark color near `rgb(6, 9, 15)`
- [ ] The `.data-table-flat` utility class is defined and applies a flat background rather than backdrop-filter glass
- [ ] No hex literals appear in any component CSS authored in Sections F-I (verify via `grep -rE "#[0-9a-fA-F]{3,6}" web/src/features/*/components` returning zero matches after Section F lands)

### Notes

The `.h-display`, `.h-label`, `.glass`, `.glass-strong`, `.glass-bar`, `.btn`, `.btn-primary` utility classes from the mockup's `GlobalStyle` are NOT defined here — they belong with the components that own them in Section F (where the AppShell, glass surfaces, and button primitives land). T7's scope is the variable layer plus the body reset plus the carve-out utility for data tables.

The animation keyframes (`ciDrift`) and atmospheric background classes (`.ci-bg`, `.ci-grain`) also belong with their components (the AppShell in Section F) rather than the global token layer.

Component CSS in Sections F-I must reference `var(--add)` etc., never `#6ee7a0` literals. The grep acceptance check in Section F closing will enforce this; flag any literal slipping in.

If V's environment has accessibility/contrast concerns flagged in operator testing, the most likely tuning targets are `--amber` (against `--bg`) and `--ink-dim`/`--ink-faint` (low-contrast secondary text). Per D-068's revisit trigger: those tokens are the places to adjust.
# Section B — Database & migrations

This section establishes the SQLite app-state database (`locks`, `events`, `maid_index`, `audit_log`) per D-058 + D-057, with migration tooling and write helpers. The single-lock model per V's Phase 5 directive (resolving D-057's §11.6 known-open) collapses D-050's two-phase model to a single row; the schema includes a nullable `phase` column for forward compatibility if the partner later confirms safe concurrency.

Section index:

- [ ] T-B1 — SQLite schema migration (001_initial.sql)
- [ ] T-B2 — Migration runner with startup hook
- [ ] T-B3 — Audit log writer helper
- [ ] T-B4 — MAID index post-run hook + startup backfill

---

## T-B1 — SQLite schema migration (001_initial.sql)

**Depends on:** T1
**Touches files:** `/api/db/migrations/001_initial.sql`
**Estimated effort:** small

### Goal

Define the four-table app-state schema per D-058 in a single declarative SQL migration. The locks table uses a single-row model per V's Phase 5 directive. The `phase` column is included as nullable to preserve forward compatibility if the partner later confirms safe per-phase concurrency, in which case a follow-up migration adds a second row.

### Context

From D-058 (Database schema, Phase 3):

> 1. **`events` table — narrow with JSON payload.** Columns: `id INTEGER PRIMARY KEY`, `run_id TEXT`, `ts TIMESTAMP`, `type TEXT`, `payload_json TEXT`. Event taxonomy lands in the Area H decision; this table absorbs new event types without schema migrations. SQLite's JSON functions handle in-payload queries when needed. Indexes: composite `(run_id, ts)` for Activity tab replay; `(type, ts)` for cross-run event queries.
> 2. **`issues` is derived from `events`, not a separate table.** Issues tab queries `SELECT * FROM events WHERE run_id = ? AND type IN ('validation_failure', 'warning', 'run_failed', ...) ORDER BY severity, ts`.
> 3. **`maid_index` — post-run hook + startup backfill.** Schema: `run_id TEXT, maid TEXT, PRIMARY KEY (run_id, maid)`; secondary index on `maid` for D-042 search.
> 4. **`audit_log` — state-changing actions + lock events; JSON details.** Schema: `id INTEGER PRIMARY KEY`, `ts TIMESTAMP`, `operator_id TEXT`, `action_type TEXT`, `run_id TEXT`, `lock_phase TEXT NULL`, `details_json TEXT`. Action types: `run_started`, `approve_clicked`, `retry_approve_clicked`, `rerun_from_scratch_clicked`, plus `lock_acquired` / `lock_released` per phase.

From D-057 (Run state machine, Phase 3):

> **Per-phase locks live in SQLite.** A `locks` table with two rows (one for `staged`, one for `approval`), each carrying `held_by_pid`, `held_by_operator`, `run_id`, `acquired_at`. Lock check + acquire happens in the FastAPI request handler before launching the `PipelineRunner` subprocess; release on subprocess exit (success or failure). Stale-lock mitigation: PID liveness check on lock-state queries.

From V's Phase 5 directive (resolving §11.6 known-open):

> **Single-instance-of-any-phase fallback.** The lock model collapses to ONE row, not two. Any operation blocks any other operation (Run blocks Approve; Approve blocks Run; Approve blocks other Approves; etc.). UI tooltip strings tighten to "An active operation is in progress" rather than separate staged/approval messaging. The `phase` column is preserved (nullable) so a future migration can split to two rows if the partner answers "safely concurrent."

### Implementation

**File: `/api/db/migrations/001_initial.sql`**:

```sql
-- ============================================================================
-- ci_ui — initial app-state schema
-- ============================================================================
-- Schemas per D-058 (Phase 3 Tech Spec), with locks table per D-057 narrowed
-- to V's Phase 5 single-lock directive.
--
-- Tables created here:
--   schema_migrations  — tracks which migrations have been applied
--   locks              — single-row lock for "any operation in progress"
--   events             — narrow JSON-payload event log (D-059 taxonomy)
--   maid_index         — per-run MAID index for Runs List search (D-042)
--   audit_log          — state-changing actions + lock events
--
-- No `runs` table — D-045's filesystem-inferred state model means the run
-- folder IS the run's state, and infer_state(folder_path) per D-057 is the
-- ground truth (implemented in Section C).
--
-- No `issues` table — derived from `events` filtered by type per D-058 #2.
-- ============================================================================

-- ---------------------------------------------------------------------------
-- schema_migrations
-- ---------------------------------------------------------------------------
-- Tracks applied migration files. The migration runner (T-B2) reads this on
-- startup to skip already-applied migrations.
CREATE TABLE IF NOT EXISTS schema_migrations (
    filename    TEXT PRIMARY KEY,
    applied_at  TEXT NOT NULL          -- ISO 8601 UTC
);

-- ---------------------------------------------------------------------------
-- locks
-- ---------------------------------------------------------------------------
-- Single-row global lock per V's Phase 5 directive. Row with id=1 always
-- exists; `held=0` when nothing is running, `held=1` when any operation is
-- in flight. Held-state columns are nullable for the un-held case.
--
-- The `phase` column is nullable for forward compatibility — if the partner
-- later answers §11.6 "safely concurrent," a follow-up migration adds a row
-- with id=2 and updates application code to acquire/release per phase. The
-- column itself doesn't need to change.
--
-- PID liveness check per D-057: lock-state queries verify the PID is still
-- alive before honoring a held lock; orphaned locks (uvicorn crashed mid-run)
-- get reaped via the lock helper in Section C.
CREATE TABLE IF NOT EXISTS locks (
    id                INTEGER PRIMARY KEY,
    held              INTEGER NOT NULL DEFAULT 0,    -- 0 | 1 (SQLite boolean idiom)
    held_by_pid       INTEGER,
    held_by_operator  TEXT,
    run_id            TEXT,
    phase             TEXT,                          -- 'staged' | 'approval' | NULL
    acquired_at       TEXT                           -- ISO 8601 UTC, nullable
);

-- Seed the single row. Subsequent migration runs are idempotent because
-- the runner skips already-applied migrations via schema_migrations.
INSERT INTO locks (id, held) VALUES (1, 0);

-- ---------------------------------------------------------------------------
-- events
-- ---------------------------------------------------------------------------
-- Narrow JSON-payload table per D-058 #1. Holds the full event stream from
-- the 13-type D-059 taxonomy plus any future additions (schema absorbs new
-- types without migration). Powers Activity tab replay per D-040 and Issues
-- tab queries per D-049.
CREATE TABLE IF NOT EXISTS events (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id        TEXT NOT NULL,
    ts            TEXT NOT NULL,                     -- ISO 8601 UTC
    type          TEXT NOT NULL,                     -- one of D-059's 13 types
    payload_json  TEXT NOT NULL                      -- JSON-serialized payload
);

-- Composite index for Activity tab replay: load all events for a single run
-- in chronological order.
CREATE INDEX IF NOT EXISTS idx_events_run_ts ON events(run_id, ts);

-- Composite index for cross-run event queries (e.g., "find all run_failed
-- events in the last week"). Less hot but cheap.
CREATE INDEX IF NOT EXISTS idx_events_type_ts ON events(type, ts);

-- ---------------------------------------------------------------------------
-- maid_index
-- ---------------------------------------------------------------------------
-- Per-run MAID index for Runs List search per D-042 + D-058 #3. Populated
-- by the post-run hook (when a staged run lands in pre-approval, the
-- extractor reads mod_file_entries.json) and the startup backfill (any
-- folders without maid_index entries get populated at app start). Both
-- live in T-B4.
CREATE TABLE IF NOT EXISTS maid_index (
    run_id  TEXT NOT NULL,
    maid    TEXT NOT NULL,
    PRIMARY KEY (run_id, maid)
);

-- Secondary index on maid for D-042 search ("find all runs touching MAID X").
CREATE INDEX IF NOT EXISTS idx_maid_index_maid ON maid_index(maid);

-- ---------------------------------------------------------------------------
-- audit_log
-- ---------------------------------------------------------------------------
-- State-changing actions + lock events per D-058 #4. Read actions (viewing
-- runs, opening drawers) are NOT logged — noise without an analytics surface.
--
-- Action types (enforced at write time by api/db/audit.py, not by DB CHECK
-- constraint — keeping schema simple):
--   run_started               (operator clicked Run on Run Detail)
--   approve_clicked           (operator clicked Approve)
--   retry_approve_clicked     (operator clicked Retry Approve)
--   rerun_from_scratch_clicked (operator clicked Re-run from scratch)
--   lock_acquired             (any of the above succeeded at lock acquire)
--   lock_released             (subprocess exit, lock released)
--
-- The lock_phase column is nullable; populated for lock_acquired /
-- lock_released events ('staged' | 'approval'); NULL for the operator-click
-- events (which don't have a phase distinction until lock acquire actually
-- happens).
CREATE TABLE IF NOT EXISTS audit_log (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    ts            TEXT NOT NULL,                     -- ISO 8601 UTC
    operator_id   TEXT NOT NULL,                     -- from X-Operator-ID per D-065
    action_type   TEXT NOT NULL,
    run_id        TEXT,                              -- nullable for system-level events
    lock_phase    TEXT,                              -- 'staged' | 'approval' | NULL
    details_json  TEXT                               -- JSON or NULL
);

-- Index for "what happened to this run" lookups.
CREATE INDEX IF NOT EXISTS idx_audit_run ON audit_log(run_id);

-- Index for "what happened in the last hour" forensic queries.
CREATE INDEX IF NOT EXISTS idx_audit_ts ON audit_log(ts);
```

### Acceptance criteria

- [ ] `/api/db/migrations/001_initial.sql` exists and is syntactically valid SQLite (test: `sqlite3 :memory: < api/db/migrations/001_initial.sql` succeeds)
- [ ] After T-B2's migration runner executes against a fresh database, `sqlite3 <db_path> ".tables"` lists exactly: `audit_log`, `events`, `locks`, `maid_index`, `schema_migrations`
- [ ] `sqlite3 <db_path> "SELECT id, held FROM locks"` returns `1|0` (the single seed row)
- [ ] `sqlite3 <db_path> ".indexes events"` lists `idx_events_run_ts` and `idx_events_type_ts`
- [ ] `sqlite3 <db_path> ".indexes maid_index"` lists `idx_maid_index_maid`
- [ ] `sqlite3 <db_path> ".indexes audit_log"` lists `idx_audit_run` and `idx_audit_ts`
- [ ] Running the migration twice (via T-B2) leaves the database in the same state — no duplicate locks row, no duplicate indexes

### Notes

The single-lock model is V's Phase 5 directive resolving D-057's §11.6 known-open. If the partner later answers "safely concurrent" — meaning `run_unified_pipeline(skip_jira=True)` and `submit_to_jira(output_folder)` can run as separate Python subprocesses without contention on module state, Snowflake auth, or registry writes — the migration path is:

1. Add `002_two_phase_locks.sql` containing `INSERT INTO locks (id, held, phase) VALUES (2, 0, 'approval');` and `UPDATE locks SET phase='staged' WHERE id=1;`
2. Update Section C's lock acquire/release helpers to take a `phase` parameter and operate on `id=1` for staged, `id=2` for approval.

Schema doesn't change in step 1; only data. The lock helper signature change in step 2 is the only application-level diff.

The `events.id` column uses `AUTOINCREMENT` rather than the simpler `INTEGER PRIMARY KEY` because some D-059 event-payload routing depends on monotonic event ordering — `AUTOINCREMENT` guarantees ids strictly increase even if rows are deleted, which matters for SSE's `Last-Event-ID` semantics if we ever enable browser-default reconnect cursor support (deferred per D-060).

SQLite stores `TEXT` ISO 8601 timestamps efficiently and supports comparison ordering as plain string compare. No need for the `datetime()` function in indexed predicates.

---

## T-B2 — Migration runner with startup hook

**Depends on:** T-B1, T1, T4
**Touches files:** `/api/db/connection.py`, `/api/db/migrate.py`, `/api/main.py` (modification to lifespan)
**Estimated effort:** small

### Goal

Implement the migration runner that applies pending SQL migrations in alphabetical order, tracks them via `schema_migrations`, and is called from FastAPI's lifespan startup hook. Provide a `get_connection()` helper so every other DB-touching module uses the same connection pattern.

### Context

From D-067 (Deployment shape):

> **Process management for MVP: manual invocation.** ... on uvicorn restart, the UI re-derives state from filesystem per D-057 and the `locks` table per D-058 (PID liveness check disambiguates stale from active locks).

Implication: the SQLite database file persists across uvicorn restarts (it lives at `SQLITE_DB_PATH` per T4); the migration runner must be idempotent so re-starting uvicorn doesn't break a working database.

From the FastAPI patterns in `main.py` (per T1):

> Startup work goes here (DB migrations, backfill jobs, etc.)

This task makes the migration call land inside the `lifespan` context manager.

### Implementation

**File: `/api/db/connection.py`** — single connection-creation helper:

```python
"""
SQLite connection helper.

A new connection is opened per request handler / per background task — SQLite
connections are cheap and the standard pattern is "open, use, close" per
operation rather than maintaining a long-lived shared connection. This avoids
the GIL-adjacent threading issues SQLite has with shared connections across
async contexts.

Per T4: settings.sqlite_db_path_resolved gives the absolute path; parent
directory is created on first open if it doesn't exist.
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path

from api.config import settings


def _ensure_parent_dir(db_path: Path) -> None:
    """Create the parent directory if it doesn't exist. Idempotent."""
    db_path.parent.mkdir(parents=True, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    """Open a new SQLite connection to the app-state database.

    Caller is responsible for closing (or using the `connection()` context
    manager below). Returns a connection with:
        - row_factory = sqlite3.Row (column-name access on rows)
        - foreign_keys pragma enabled
        - WAL journal mode (better concurrent read performance)
    """
    db_path = settings.sqlite_db_path_resolved
    _ensure_parent_dir(db_path)
    conn = sqlite3.connect(str(db_path), isolation_level=None)  # autocommit off; we use BEGIN/COMMIT
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


@contextmanager
def connection():
    """Context-manager wrapper for get_connection() that closes on exit.

    Usage:
        with connection() as conn:
            rows = conn.execute("SELECT * FROM events WHERE run_id=?", (run_id,)).fetchall()
    """
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()
```

**File: `/api/db/migrate.py`** — migration runner:

```python
"""
SQLite migration runner.

Reads `.sql` files from /api/db/migrations/ in alphabetical order, applies
any not already recorded in the schema_migrations table, and records each
on success. Idempotent — re-running is a no-op if no new migrations.

Called from FastAPI's lifespan startup hook (see api/main.py).
"""

import logging
from datetime import datetime, timezone
from pathlib import Path

from api.db.connection import get_connection

logger = logging.getLogger(__name__)

# Migration files live alongside this module.
MIGRATIONS_DIR = Path(__file__).parent / "migrations"


def apply_pending_migrations() -> list[str]:
    """Apply any migrations not yet recorded in schema_migrations.

    Returns the list of migration filenames that were applied (empty if all
    were already up to date). Each migration is executed inside a transaction;
    if a migration fails, that transaction rolls back and the runner raises.

    A migration that has already been applied (its filename is in
    schema_migrations) is skipped — files are NEVER re-applied. To re-run a
    migration, you have to delete its schema_migrations row manually and
    accept the consequences.
    """
    if not MIGRATIONS_DIR.exists():
        logger.warning(
            "Migrations directory %s does not exist; nothing to apply.",
            MIGRATIONS_DIR,
        )
        return []

    conn = get_connection()
    try:
        # Make sure schema_migrations exists even on the very first run.
        # The 001_initial.sql migration creates it too (idempotently via
        # CREATE TABLE IF NOT EXISTS), but we need it BEFORE we can query
        # for already-applied migrations.
        conn.execute(
            "CREATE TABLE IF NOT EXISTS schema_migrations ("
            "filename TEXT PRIMARY KEY, applied_at TEXT NOT NULL)"
        )

        applied: set[str] = {
            row["filename"]
            for row in conn.execute("SELECT filename FROM schema_migrations").fetchall()
        }

        sql_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
        if not sql_files:
            logger.info("No migration files found in %s", MIGRATIONS_DIR)
            return []

        newly_applied: list[str] = []
        for sql_file in sql_files:
            if sql_file.name in applied:
                logger.debug("Skipping already-applied migration: %s", sql_file.name)
                continue

            logger.info("Applying migration: %s", sql_file.name)
            sql_text = sql_file.read_text(encoding="utf-8")
            try:
                conn.execute("BEGIN")
                conn.executescript(sql_text)
                conn.execute(
                    "INSERT INTO schema_migrations (filename, applied_at) VALUES (?, ?)",
                    (sql_file.name, datetime.now(timezone.utc).isoformat()),
                )
                conn.execute("COMMIT")
            except Exception:
                conn.execute("ROLLBACK")
                logger.exception("Migration %s failed; rolled back.", sql_file.name)
                raise
            newly_applied.append(sql_file.name)

        if newly_applied:
            logger.info("Applied %d migrations: %s", len(newly_applied), newly_applied)
        else:
            logger.info("Database schema is up to date (no migrations to apply).")

        return newly_applied
    finally:
        conn.close()
```

**Modification to `/api/main.py`** — add the migration call to lifespan:

```python
"""
ci_ui FastAPI application.

(... unchanged docstring from T1 ...)
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.config import settings
from api.db.migrate import apply_pending_migrations
from api.routers import runs as runs_router
from api.routers import system as system_router

# Configure logging at startup based on settings.log_level (per T4).
logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown hooks."""
    # Migrations: apply any pending schema changes before serving traffic.
    logger.info("Applying database migrations...")
    applied = apply_pending_migrations()
    if applied:
        logger.info("Applied migrations: %s", applied)

    # Section B / Section C add more startup work here:
    # - MAID index startup backfill (T-B4)
    # - Stale-lock reaping via PID liveness (T-C2)
    # - PipelineRunner subprocess registry rehydration (Section D)

    yield

    # Shutdown work: nothing required for MVP. Pipeline subprocesses survive
    # uvicorn restarts per D-067; the next startup re-derives state from
    # filesystem + locks table.


# (rest of main.py from T1 unchanged: app = FastAPI(...), CORS, /api/health,
#  router includes, StaticFiles mount)
```

### Acceptance criteria

- [ ] `/api/db/connection.py` exports `get_connection()` and `connection()` (context manager); both open with `row_factory = sqlite3.Row` and WAL journal mode enabled
- [ ] `/api/db/migrate.py` exports `apply_pending_migrations()` returning a list of newly-applied filenames
- [ ] First-ever startup with an empty `SQLITE_DB_PATH`: uvicorn boots, log shows `Applying migration: 001_initial.sql`, then `Applied migrations: ['001_initial.sql']`
- [ ] Second startup with the same database: uvicorn boots, log shows `Database schema is up to date (no migrations to apply).`
- [ ] After first-ever startup, `sqlite3 <db_path> "SELECT filename FROM schema_migrations"` returns `001_initial.sql`
- [ ] A deliberately-broken migration file (`002_broken.sql` containing `CREATE TABLE foo (id NOT_A_TYPE)`) causes startup to fail with the exception logged; the database is left in its prior state (no `foo` table, no `002_broken.sql` row in schema_migrations). Delete the test file after verifying.
- [ ] Migration files are read in alphabetical order (sorted glob); naming convention `NNN_<description>.sql` makes order obvious

### Notes

The migration runner uses `executescript()` rather than `execute()` because `001_initial.sql` contains multiple statements separated by `;`. `executescript()` auto-commits inside SQLite, which is why we wrap the whole thing in an explicit BEGIN/COMMIT — to atomically include the `schema_migrations` insert with the schema changes.

Forward-compatibility note: this runner intentionally does NOT support down-migrations / rollbacks. The MVP scale (~50 runs/year, single VDI deployment) doesn't justify the operational complexity, and the production team's eventual ECS deployment will use a proper migration tool (Alembic) if needed. If a migration goes wrong, recovery is: restore from backup, fix the migration file, re-run.

The `journal_mode = WAL` pragma is set on every connection but only takes effect once (WAL is database-level state, not connection-level). Setting it idempotently is fine.

`isolation_level=None` puts the connection into "autocommit off" mode — every `BEGIN`/`COMMIT` is explicit. This is the safer pattern for transaction integrity than the default Python "smart" wrapper that opens implicit transactions on data-modifying statements.

---

## T-B3 — Audit log writer helper

**Depends on:** T-B1, T-B2
**Touches files:** `/api/db/audit.py`
**Estimated effort:** small

### Goal

Implement a single `write_audit()` helper that all state-changing endpoints (Section E) and lock helpers (Section C) call to append rows to the `audit_log` table. Centralize the action_type vocabulary as a typed enum so misspellings are caught at write-call sites rather than discovered later in audit queries.

### Context

From D-058 (Phase 3 Tech Spec):

> **`audit_log` — state-changing actions + lock events; JSON details.** Schema: `id INTEGER PRIMARY KEY`, `ts TIMESTAMP`, `operator_id TEXT`, `action_type TEXT`, `run_id TEXT`, `lock_phase TEXT NULL`, `details_json TEXT`. Action types: `run_started`, `approve_clicked`, `retry_approve_clicked`, `rerun_from_scratch_clicked`, plus `lock_acquired` / `lock_released` per phase. Read actions (viewing runs, opening drawers) are NOT logged — noise without an analytics surface. Joins against `locks` table provide forensic granularity ("who held the staged lock 9:03-9:31, failed; who retried at 9:32").

From D-065 calibration note:

> *Audit-log `operator_id` is browser-session-scoped, not person-scoped, in MVP.* Worth a schema-level comment on the `audit_log.operator_id` column noting this until production auth lands. Two operators sharing a workstation register as the same UUID; one operator on two browsers registers as two UUIDs. Anyone querying the audit log for "who did what" in MVP should know they're seeing browser sessions, not people.

### Implementation

**File: `/api/db/audit.py`**:

```python
"""
Audit log writer.

Centralized helper for appending rows to the audit_log table. Every
state-changing API endpoint (Section E) and lock acquire/release helper
(Section C) calls write_audit() to record the action.

NOT logged (intentionally): read actions like viewing runs, opening drawers,
loading the base table. These produce noise without an analytics surface
to consume them. If audit needs grow to include reads, add a SEPARATE
action_audit table — don't pollute this one.

MVP scope per D-065 calibration: operator_id is browser-session-scoped via
the localStorage UUID, not person-scoped. Two operators sharing a workstation
register as the same UUID; one operator on two browsers registers as two UUIDs.
Production team's RBAC swap (per D-067 swap surface) replaces the localStorage
source with real identity, but this writer's surface doesn't change.
"""

import json
import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from api.db.connection import connection

logger = logging.getLogger(__name__)


class AuditAction(str, Enum):
    """Canonical action types written to audit_log.action_type.

    Inherits from str so values are usable as plain strings at SQL-bind time
    without explicit `.value` access; the Enum constraint prevents typos at
    call sites.
    """

    # Operator-click actions (Section E endpoints).
    RUN_STARTED = "run_started"
    APPROVE_CLICKED = "approve_clicked"
    RETRY_APPROVE_CLICKED = "retry_approve_clicked"
    RERUN_FROM_SCRATCH_CLICKED = "rerun_from_scratch_clicked"

    # Lock lifecycle (Section C lock helpers).
    LOCK_ACQUIRED = "lock_acquired"
    LOCK_RELEASED = "lock_released"


# Valid lock_phase values when AuditAction is LOCK_ACQUIRED or LOCK_RELEASED.
# Under V's single-lock Phase 5 directive both values are recorded for
# audit-trail completeness, but the lock table itself only has id=1.
# If/when the partner answers safely-concurrent, two-phase locks come back
# without changing this enum.
_VALID_LOCK_PHASES = frozenset({"staged", "approval"})


def write_audit(
    operator_id: str,
    action_type: AuditAction,
    run_id: str | None = None,
    lock_phase: str | None = None,
    details: dict[str, Any] | None = None,
) -> None:
    """Append a row to audit_log.

    Args:
        operator_id: The X-Operator-ID header value per D-065 (or
                     server-generated fallback per T1 dependencies.py).
        action_type: One of AuditAction's canonical values.
        run_id: Optional run identifier. Always set for operator-click
                actions (RUN_STARTED, APPROVE_CLICKED, etc.); usually set
                for lock events too.
        lock_phase: Required for LOCK_ACQUIRED / LOCK_RELEASED; must be one
                    of 'staged' or 'approval'. None for operator-click events.
        details: Optional dict of action-specific context. Serialized to
                 JSON in details_json. Examples:
                   RUN_STARTED: {"input_folder": "...", "merchant": "..."}
                   LOCK_ACQUIRED: {"pid": 12345}
                   RERUN_FROM_SCRATCH_CLICKED: {"parent_run_id": "..."}

    Validation:
        - action_type must be an AuditAction instance (enforced by type hint
          + ValueError raise; misuse fails fast at call site).
        - For LOCK_* action types, lock_phase must be 'staged' or 'approval'.
        - operator_id must be non-empty.
    """
    if not operator_id:
        raise ValueError("write_audit: operator_id must be non-empty")

    if not isinstance(action_type, AuditAction):
        raise ValueError(
            f"write_audit: action_type must be AuditAction enum, got {type(action_type)}"
        )

    if action_type in (AuditAction.LOCK_ACQUIRED, AuditAction.LOCK_RELEASED):
        if lock_phase not in _VALID_LOCK_PHASES:
            raise ValueError(
                f"write_audit: lock_phase must be one of {_VALID_LOCK_PHASES} "
                f"for {action_type.value} events, got {lock_phase!r}"
            )

    ts = datetime.now(timezone.utc).isoformat()
    details_json = json.dumps(details, default=str) if details is not None else None

    with connection() as conn:
        conn.execute("BEGIN")
        try:
            conn.execute(
                "INSERT INTO audit_log "
                "(ts, operator_id, action_type, run_id, lock_phase, details_json) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (ts, operator_id, action_type.value, run_id, lock_phase, details_json),
            )
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            # Don't raise — audit writes should not break the request they're
            # logging. Log the failure and continue. This is a deliberate
            # design choice: a failed audit write is bad but not worse than
            # failing the operator's action because audit was unavailable.
            logger.exception(
                "Audit write failed (action_type=%s, run_id=%s, operator=%s)",
                action_type.value, run_id, operator_id,
            )


def read_audit_for_run(run_id: str) -> list[dict[str, Any]]:
    """Convenience reader for "what happened to this run" queries.

    Returns audit_log rows for the given run_id ordered chronologically.
    Used in Phase 5 by Section E's GET /api/runs/{run_id}/events response
    composition for the forensic-context display in Activity tab failure
    states.

    Each row is a dict with keys: id, ts, operator_id, action_type, run_id,
    lock_phase, details_json (deserialized to dict). NOT used by Issues tab
    (which reads `events` table per D-058 #2, not audit_log).
    """
    with connection() as conn:
        rows = conn.execute(
            "SELECT id, ts, operator_id, action_type, run_id, lock_phase, details_json "
            "FROM audit_log WHERE run_id = ? ORDER BY ts ASC",
            (run_id,),
        ).fetchall()
    return [
        {
            "id": r["id"],
            "ts": r["ts"],
            "operator_id": r["operator_id"],
            "action_type": r["action_type"],
            "run_id": r["run_id"],
            "lock_phase": r["lock_phase"],
            "details": json.loads(r["details_json"]) if r["details_json"] else None,
        }
        for r in rows
    ]
```

### Acceptance criteria

- [ ] `/api/db/audit.py` exports `AuditAction` (Enum), `write_audit()`, and `read_audit_for_run()`
- [ ] `write_audit("op-1", AuditAction.RUN_STARTED, run_id="r1", details={"merchant": "intuit"})` succeeds; `sqlite3 <db> "SELECT * FROM audit_log"` shows the row with `action_type='run_started'`, `details_json='{"merchant": "intuit"}'`, `lock_phase=NULL`
- [ ] `write_audit("op-1", AuditAction.LOCK_ACQUIRED, run_id="r1", lock_phase="staged", details={"pid": 12345})` succeeds; the row has `lock_phase='staged'`
- [ ] `write_audit("op-1", AuditAction.LOCK_ACQUIRED, run_id="r1")` (missing lock_phase) raises `ValueError` with a message naming the missing field
- [ ] `write_audit("op-1", "run_started", ...)` (passing a string instead of AuditAction) raises `ValueError`
- [ ] `write_audit("", AuditAction.RUN_STARTED, run_id="r1")` (empty operator_id) raises `ValueError`
- [ ] If the database file is deleted mid-app-life (simulating disk failure), `write_audit` logs the exception but does NOT raise — the operator-facing request continues; subsequent read_audit_for_run shows the audit row is missing but the run still completed

### Notes

The "swallow audit-write failures" behavior in the except block is deliberate. The trade-off: a failed audit write produces a missing-row hole in the log, but a propagated exception would fail the operator's action (Run, Approve, etc.) because audit was unavailable. The latter is worse — operator's productive work blocked by an audit-infrastructure problem. Logging the exception leaves a breadcrumb in uvicorn's stderr that surfaces in the runbook's "check the logs" step.

`AuditAction(str, Enum)` is the Python 3.11+ idiom for "enum whose values are also strings" — `AuditAction.RUN_STARTED == "run_started"` evaluates to True, and the value binds cleanly into SQL parameters without needing `.value` access. The type hint still constrains call sites to the enum.

`details_json` uses `default=str` in `json.dumps` so unexpected non-serializable values (Path objects, datetimes that slipped in) stringify rather than raise. Defensive against drift.

The Phase 5 calibration note from D-065 (operator_id browser-session-scoped) is reproduced in the module docstring rather than the schema — the SQL comments stay minimal; the application-layer file is where the "what does this mean operationally" discussion lives.

`read_audit_for_run` returns dict[str, Any] rather than typed Pydantic models because audit-log reads are operationally rare (forensics, not steady-state UI rendering). When Section E surfaces a forensic view it can layer typed models on top.

---

## T-B4 — MAID index post-run hook + startup backfill

**Depends on:** T-B1, T-B2
**Touches files:** `/api/db/maid_index.py`, `/api/main.py` (modification: add backfill to lifespan startup)
**Estimated effort:** medium

### Goal

Implement the MAID extractor + indexer that powers Runs List search by MAID per D-042. Three functions land here: `extract_maids_from_folder()` reads `mod_file_entries.json`; `populate_maid_index()` writes one row per distinct MAID for a single run; `backfill_maid_index_if_needed()` scans the output base directory at startup and populates any runs missing from the index. The post-run hook is wired in Section D when `PipelineRunner` exits cleanly; the startup backfill wires here in `lifespan()`.

### Context

From D-058 (Phase 3 Tech Spec):

> **`maid_index` — post-run hook + startup backfill.** Schema: `run_id TEXT, maid TEXT, PRIMARY KEY (run_id, maid)`; secondary index on `maid` for D-042 search. Population: a small extractor reads `mod_file_entries.json` when a staged run lands in pre-approval and writes one row per distinct MAID; at app startup, any folders that have no `maid_index` entries get backfilled (covers Phase 1 fixtures and any folder predating the index). UI search becomes `SELECT DISTINCT run_id FROM maid_index WHERE maid LIKE ?`.

From D-042 (Phase 2 Functional Spec):

> Last 10 reverse-chronological preserved. Search criteria revised to MAID OR merchant. V's exact words: "search by maid or merchant."

From `ui-approach.md` §3 (output anatomy):

> `output/<merchant>_<timestamp>/`
>   `comparison/mod_file_entries.json` — per-subtask payloads (UI base table source)

`mod_file_entries.json` is an array of records; each carries a `maid` field. The extractor harvests distinct MAID values from that file.

### Implementation

**File: `/api/db/maid_index.py`**:

```python
"""
MAID index maintenance.

Two write paths:
  1. Post-run hook  — Section D's PipelineRunner calls populate_maid_index()
                      when a staged run lands in pre-approval (i.e., when
                      mod_file_entries.json appears in the output folder).
  2. Startup backfill — backfill_maid_index_if_needed() scans the output
                      base directory at app startup and indexes any folders
                      not yet in the table. Covers Phase 1 fixtures and any
                      folder created while the app was offline.

One read path (Section E's GET /api/runs query, D-061):
    SELECT DISTINCT run_id FROM maid_index WHERE maid LIKE ?
"""

import json
import logging
from pathlib import Path

from api.config import settings
from api.db.connection import connection

logger = logging.getLogger(__name__)

# The pipeline writes mod_file_entries.json at this path within each run folder.
# Path matches ui-approach.md §3.
_MOD_FILE_RELATIVE_PATH = Path("comparison") / "mod_file_entries.json"


def extract_maids_from_folder(folder_path: Path) -> set[str]:
    """Extract distinct MAID values from a single run folder.

    Reads <folder_path>/comparison/mod_file_entries.json and returns the
    set of distinct `maid` field values. Returns empty set if:
        - the folder doesn't exist
        - the mod_file_entries.json doesn't exist (run hasn't reached
          pre-approval yet)
        - the file is malformed JSON
        - no records carry a `maid` field

    Defensive: never raises on read errors. Logs warnings on malformed
    input rather than failing — the caller can decide whether absence is
    okay (startup backfill: yes, log and skip) or not (post-run hook:
    yes, log and skip since the run still completed).
    """
    mod_file = folder_path / _MOD_FILE_RELATIVE_PATH
    if not mod_file.exists():
        return set()

    try:
        with mod_file.open("r", encoding="utf-8") as f:
            entries = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning(
            "Could not read mod_file_entries.json at %s: %s",
            mod_file, exc,
        )
        return set()

    if not isinstance(entries, list):
        logger.warning(
            "Expected mod_file_entries.json to be a JSON array, got %s at %s",
            type(entries).__name__, mod_file,
        )
        return set()

    maids: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        maid_val = entry.get("maid")
        if maid_val is None:
            continue
        # MAIDs are typically numeric strings (e.g., "411424") in the
        # pipeline output. Coerce to string defensively in case any
        # are int-typed.
        maids.add(str(maid_val))

    return maids


def populate_maid_index(run_id: str, folder_path: Path) -> int:
    """Populate maid_index rows for a single run.

    Reads MAIDs from the run folder and inserts one row per distinct MAID.
    Uses INSERT OR IGNORE so re-running on the same folder is a no-op
    (PK constraint on (run_id, maid) prevents duplicates).

    Returns the count of distinct MAIDs found (not the count of newly-
    inserted rows — for the caller's logging purposes, "this run has N
    MAIDs" is more useful than "we inserted N new rows" because the
    callers always treat existing entries as success).

    Called by:
        - Section D's PipelineRunner post-run hook (immediately after a
          staged run completes; the run folder is fully populated and
          mod_file_entries.json exists)
        - backfill_maid_index_if_needed() below (for any folder missing
          from the index at startup)
    """
    maids = extract_maids_from_folder(folder_path)
    if not maids:
        logger.debug(
            "No MAIDs found in run folder %s (run_id=%s)",
            folder_path, run_id,
        )
        return 0

    with connection() as conn:
        conn.execute("BEGIN")
        try:
            for maid in maids:
                conn.execute(
                    "INSERT OR IGNORE INTO maid_index (run_id, maid) VALUES (?, ?)",
                    (run_id, maid),
                )
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            logger.exception(
                "Failed to populate maid_index for run_id=%s", run_id,
            )
            raise

    logger.info(
        "Indexed %d MAIDs for run_id=%s: %s",
        len(maids), run_id, sorted(maids),
    )
    return len(maids)


def backfill_maid_index_if_needed() -> dict[str, int]:
    """Scan OUTPUT_BASE_FOLDER for run folders missing from maid_index; populate them.

    Called once at FastAPI lifespan startup. Idempotent — re-running on an
    already-up-to-date database is a no-op.

    Decision criterion for "needs backfilling": a folder under OUTPUT_BASE_FOLDER
    is considered un-indexed if there's no row in maid_index with that folder's
    name as run_id. We use folder name as run_id throughout (per D-045's
    filesystem-as-state model; the folder IS the run).

    Returns a dict mapping run_id -> MAID count for each backfilled run.
    Empty dict if nothing needed backfilling. Returned for logging /
    operational visibility; callers don't need to use the return value.
    """
    output_base = settings.output_base_folder_path
    if not output_base.exists():
        logger.info(
            "OUTPUT_BASE_FOLDER %s does not exist yet; skipping maid_index backfill.",
            output_base,
        )
        return {}

    # Get the set of run_ids already in maid_index.
    with connection() as conn:
        indexed: set[str] = {
            row["run_id"]
            for row in conn.execute("SELECT DISTINCT run_id FROM maid_index").fetchall()
        }

    backfilled: dict[str, int] = {}
    for run_folder in output_base.iterdir():
        if not run_folder.is_dir():
            continue
        run_id = run_folder.name

        # Skip folders we've already indexed.
        if run_id in indexed:
            continue

        # Skip folders that don't have mod_file_entries.json yet — those
        # are mid-run or failed-before-comparison; nothing to index.
        if not (run_folder / _MOD_FILE_RELATIVE_PATH).exists():
            logger.debug(
                "Skipping un-indexed folder %s — no mod_file_entries.json",
                run_folder.name,
            )
            continue

        try:
            count = populate_maid_index(run_id, run_folder)
            if count > 0:
                backfilled[run_id] = count
        except Exception:
            # Don't let one bad folder break the whole backfill — log it
            # and continue. The folder's run can still load (just won't be
            # MAID-searchable until manually re-indexed).
            logger.exception(
                "Backfill failed for folder %s; continuing with remaining folders.",
                run_folder.name,
            )

    if backfilled:
        logger.info(
            "MAID index backfilled for %d runs: %s",
            len(backfilled), backfilled,
        )
    else:
        logger.info("MAID index is up to date (nothing to backfill).")

    return backfilled
```

**Modification to `/api/main.py`** — add the backfill call to lifespan after migrations:

```python
"""
ci_ui FastAPI application.
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.config import settings
from api.db.maid_index import backfill_maid_index_if_needed
from api.db.migrate import apply_pending_migrations
from api.routers import runs as runs_router
from api.routers import system as system_router

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown hooks."""
    # 1. Schema migrations (T-B2).
    logger.info("Applying database migrations...")
    applied = apply_pending_migrations()
    if applied:
        logger.info("Applied migrations: %s", applied)

    # 2. MAID index backfill (T-B4). Runs every startup; idempotent.
    logger.info("Backfilling MAID index for any un-indexed run folders...")
    backfilled = backfill_maid_index_if_needed()
    if backfilled:
        logger.info("Backfilled %d runs into MAID index.", len(backfilled))

    # Section C will add stale-lock reaping here (T-C2).

    yield


# (rest of main.py unchanged — app, CORS, /api/health, routers, StaticFiles)
```

### Acceptance criteria

- [ ] `/api/db/maid_index.py` exports `extract_maids_from_folder()`, `populate_maid_index()`, `backfill_maid_index_if_needed()`
- [ ] `extract_maids_from_folder` on a folder with a valid `comparison/mod_file_entries.json` returns the set of distinct `maid` values; returns empty set on missing folder, missing file, malformed JSON, or non-list root
- [ ] `populate_maid_index("run-1", Path("/path/to/test_fixture"))` inserts one row per distinct MAID; calling twice on the same folder leaves the same row count (INSERT OR IGNORE)
- [ ] After T-B4 lands and first uvicorn startup: log shows `Backfilling MAID index...` followed by either `MAID index is up to date` (empty OUTPUT_BASE_FOLDER) or `Backfilled N runs into MAID index.`
- [ ] With one of the Phase 1 fixture folders (e.g., `intuit_20260511_155829/`) under OUTPUT_BASE_FOLDER, after startup `sqlite3 <db> "SELECT * FROM maid_index"` shows rows for that run's MAIDs
- [ ] Folders without `comparison/mod_file_entries.json` (mid-run or failed-early) are silently skipped during backfill — no error, just a debug log line
- [ ] A deliberately-malformed `mod_file_entries.json` (e.g., overwrite with `not json`) doesn't break startup — the affected folder gets a warning log line and backfill continues with other folders
- [ ] Running `populate_maid_index("run-1", Path("/test_fixture"))` twice in a row inserts no duplicate rows

### Notes

The post-run hook integration (calling `populate_maid_index(run_id, folder_path)` after a staged run completes) lives in Section D's `SubprocessPipelineRunner` and `MockPipelineRunner`. T-B4 only provides the helper; the call site is downstream. This separation matches the dependency direction: the adapters depend on the DB layer, not vice versa.

The startup backfill covers two scenarios:
- **Phase 1 fixtures preserved per D-026.** The two `intuit_20260511_*` folders exist before this index ever ran; backfill ensures they're searchable.
- **Recovery from app downtime.** If a run completes while uvicorn is down (the pipeline subprocess survives uvicorn restarts per D-067), the next startup re-indexes anything that landed in the interim.

`INSERT OR IGNORE` rather than `INSERT OR REPLACE` because the (run_id, maid) tuple identity is the natural key — there's no field on a row that can change between writes. If a folder's `mod_file_entries.json` gets edited to add a new MAID later (unusual but possible), the next backfill picks up the new MAID via INSERT OR IGNORE on the new row without touching existing rows.

The `_MOD_FILE_RELATIVE_PATH = Path("comparison") / "mod_file_entries.json"` constant mirrors `ui-approach.md` §3's output anatomy. If the pipeline ever moves the file (unlikely), this is the single point of update.

Performance note: at ~50 runs/year × ~5-15 MAIDs/run, the `maid_index` table holds ~250-750 rows lifetime. SQLite scans this in microseconds; no query plan tuning needed. The secondary index on `maid` helps when the LIKE query has a leading constant (`WHERE maid LIKE '411%'`); LIKE patterns starting with `%` force a full scan which is still fine at this size.
# Section C — State derivation & lifecycle plumbing

This section implements the runtime spine that bridges filesystem reality to API responses: the `infer_state()` function powering every state-aware endpoint per D-045, the lock helpers with PID liveness per D-057, the `failure.json` writer per D-046, the event ingestion pipeline that lands subprocess events into the `events` table, the in-memory SSE broadcaster per D-060, and a stale-lock reaper startup hook that recovers cleanly from uvicorn crashes.

Section index:

- [ ] T-C1 — `infer_state()` filesystem state inference
- [ ] T-C2 — Lock acquire/release helpers with PID liveness
- [ ] T-C3 — `failure.json` writer and schema
- [ ] T-C4 — Event ingestion (parser + writer to `events` table)
- [ ] T-C5 — In-memory SSE event broadcaster
- [ ] T-C6 — Stale-lock reaper startup hook

---

## T-C1 — `infer_state()` filesystem state inference

**Depends on:** T-B1, T-B2
**Touches files:** `/api/state/__init__.py`, `/api/state/inference.py`, `/api/state/sentinels.py`
**Estimated effort:** medium

### Goal

Implement the single state-inference function that every endpoint calls to derive a run's current state from filesystem sentinels + the locks table per D-045 + D-057. Return one of five states from a canonical `RunState` enum. Centralize sentinel-filename constants in a separate module so the integration with partner's pipeline outputs has exactly one update point.

### Context

From D-045 (Filesystem as state, Phase 2):

> Run state is derived from filesystem inspection — the presence/absence of specific sentinel files within a run's output folder, plus the locks table for in-flight signaling. No `runs` table. The folder IS the run. Five states: `pre_approval`, `submitted`, `stale`, `in_progress`, `failed`.

From D-057 (Run state machine, Phase 3):

> PID liveness check on lock-state queries disambiguates "actively running" (process alive, lock held) from "uvicorn crashed mid-run" (process gone, lock orphaned). The reaper in T-C6 cleans orphans at startup; queries during steady-state get the right answer because PID liveness is checked at read time, not just write time.

From D-046 (Failure visibility, Phase 2):

> Failure produces a `failure.json` sentinel in the run folder identifying the stage (`staged` vs `approval`) and message. The Run Detail header shows the failure state; available actions depend on the stage (failed-staged → Re-run from scratch only; failed-approval → Retry Approve OR Re-run from scratch).

### Implementation

**File: `/api/state/__init__.py`** — empty marker.

**File: `/api/state/sentinels.py`** — single-source-of-truth for sentinel filenames:

```python
"""
Filesystem sentinel filenames that drive state inference.

These constants name files the partner's pipeline writes (or that this UI
writes — failure.json — in T-C3). Centralized here so the integration
contract with the pipeline has exactly one update point if a filename ever
changes.

Per the agreement with the partner (verified during Section D adapter
integration): the pipeline writes `mod_file_entries.json` in the
`comparison/` subdirectory when the staged run reaches pre-approval, and
writes `jira_submission_complete.json` at the run-folder root when Jira +
SharePoint submission completes successfully. Both names are matched
case-sensitively on Windows VDI (NTFS is case-insensitive but the
pipeline preserves case; we match what's documented to keep the contract
visible).

`failure.json` is written by THIS UI's subprocess wrapper (T-C3), not by
the partner's pipeline. The pipeline raising an exception triggers our
wrapper to write the failure file.
"""

from pathlib import Path

# Pre-approval sentinel — written by the pipeline when comparison completes.
# Path relative to the run folder root.
SENTINEL_PRE_APPROVAL = Path("comparison") / "mod_file_entries.json"

# Submitted sentinel — written by the pipeline when Jira + SharePoint
# submission completes successfully.
SENTINEL_SUBMITTED = Path("jira_submission_complete.json")

# Failed sentinel — written by THIS UI's subprocess wrapper (T-C3) when
# the pipeline exits non-zero. The pipeline itself does not write this.
SENTINEL_FAILED = Path("failure.json")
```

**File: `/api/state/inference.py`**:

```python
"""
Run state inference per D-045 + D-057.

The single function infer_state(folder_path) is the ground truth for "what
state is this run in?" — called by every endpoint that needs to make a
state-dependent decision (Runs List rows, Run Detail header, action
button availability, lock acquisition pre-checks).

State precedence (highest to lowest):
    in_progress  — locks table says held and PID is alive
    failed       — failure.json sentinel present
    submitted    — jira_submission_complete.json sentinel present
    pre_approval — mod_file_entries.json sentinel present
    stale        — folder exists but none of the above sentinels do

Precedence matters: a run that BOTH has mod_file_entries.json AND a
held lock is in_progress (mid-approval), not pre_approval. A failed run
keeps its failure.json forever — re-running creates a new run folder per
D-046's "no in-place retry" model, so failure.json is terminal for the
folder it lives in.
"""

import logging
from enum import Enum
from pathlib import Path

from api.state.sentinels import (
    SENTINEL_FAILED,
    SENTINEL_PRE_APPROVAL,
    SENTINEL_SUBMITTED,
)

logger = logging.getLogger(__name__)


class RunState(str, Enum):
    """Canonical run states per D-045.

    Inherits from str so values bind cleanly into JSON serialization
    (FastAPI's response_model picks up the string value automatically).
    """

    PRE_APPROVAL = "pre_approval"
    SUBMITTED = "submitted"
    STALE = "stale"
    IN_PROGRESS = "in_progress"
    FAILED = "failed"


def infer_state(
    folder_path: Path,
    *,
    held_run_id: str | None = None,
) -> RunState:
    """Derive a run's state from filesystem sentinels + the lock state.

    Args:
        folder_path: Absolute path to the run folder. Folder name is treated
                     as the run_id per D-045's filesystem-as-state model.
        held_run_id: If a lock is currently held AND the holding PID is alive,
                     the caller passes the held run_id here. This is the lock
                     state contribution to inference — IN_PROGRESS supersedes
                     any filesystem-derived state. Callers that don't have
                     lock state handy should call get_lock_state() (T-C2)
                     first and pass the result. Passing None means "no lock
                     is held" (equivalent to lock state being not-held or
                     held by a dead PID).

    Returns:
        One of RunState's five values. Never raises — a missing folder
        returns STALE rather than throwing.

    Precedence:
        1. If held_run_id matches folder name → IN_PROGRESS.
        2. If failure.json exists → FAILED.
        3. If jira_submission_complete.json exists → SUBMITTED.
        4. If mod_file_entries.json (under comparison/) exists → PRE_APPROVAL.
        5. Otherwise → STALE.

    Defensive: if folder_path doesn't exist, returns STALE (rather than
    raising). The caller is responsible for filtering non-folder entries
    before calling.
    """
    run_id = folder_path.name

    # In-progress: lock-derived, supersedes all filesystem signals.
    if held_run_id is not None and held_run_id == run_id:
        return RunState.IN_PROGRESS

    # Folder not present at all → stale (e.g., deleted between list and inspect).
    if not folder_path.exists():
        return RunState.STALE

    # Terminal: failed.
    if (folder_path / SENTINEL_FAILED).exists():
        return RunState.FAILED

    # Terminal: submitted.
    if (folder_path / SENTINEL_SUBMITTED).exists():
        return RunState.SUBMITTED

    # Reached pre-approval (comparison artifacts present).
    if (folder_path / SENTINEL_PRE_APPROVAL).exists():
        return RunState.PRE_APPROVAL

    # Folder exists but nothing in it. Either mid-run with no output yet
    # (handled by held_run_id check above) or genuinely abandoned.
    return RunState.STALE
```

### Acceptance criteria

- [ ] `/api/state/sentinels.py` exports `SENTINEL_PRE_APPROVAL`, `SENTINEL_SUBMITTED`, `SENTINEL_FAILED` as `Path` constants
- [ ] `/api/state/inference.py` exports `RunState` enum and `infer_state()` function
- [ ] `infer_state(Path('/tmp/nonexistent'))` returns `RunState.STALE` without raising
- [ ] `infer_state(Path('/tmp/empty_dir'))` (folder exists but empty) returns `RunState.STALE`
- [ ] Folder with only `comparison/mod_file_entries.json` → `PRE_APPROVAL`
- [ ] Folder with `mod_file_entries.json` + `jira_submission_complete.json` → `SUBMITTED` (submitted supersedes pre_approval)
- [ ] Folder with `mod_file_entries.json` + `failure.json` → `FAILED` (failure supersedes pre_approval)
- [ ] Folder with `mod_file_entries.json` + `failure.json` + `jira_submission_complete.json` → `FAILED` (failure beats submitted; this combination is anomalous but the precedence rule defines behavior)
- [ ] `infer_state(Path('/runs/intuit_20260511_155829'), held_run_id='intuit_20260511_155829')` returns `IN_PROGRESS` even if the folder contains all three terminal sentinels (in-progress wins)
- [ ] `infer_state(Path('/runs/foo'), held_run_id='bar')` ignores the lock (different run_id) and falls through to filesystem precedence

### Notes

The `held_run_id` parameter is intentionally a single string rather than the full `LockState` object — this keeps `infer_state` decoupled from the lock module's internal shape. Callers in Section E who need to render many runs in one response will fetch lock state once and pass the held run_id (or None) per row, avoiding redundant DB hits.

The anomalous "both `failure.json` and `jira_submission_complete.json` exist" case shouldn't happen in steady state but is possible if a partner-pipeline bug writes both. The precedence rule (failure wins) is deliberate: the operator needs to see the failure even if a subsequent retry's success sentinel landed in the same folder — but D-046's "no in-place retry" model means retries produce new folders, so this combination is genuinely a bug indicator worth surfacing. The Issues tab (Section H) will show the `failure.json` content; the operator can investigate.

The sentinel filenames (`mod_file_entries.json`, `jira_submission_complete.json`) are V's best understanding of the partner's pipeline output contract at Phase 1 verification. If Copilot finds the real pipeline writes different names when integrating Section D, update `sentinels.py` and re-run the verification suite (Section K).

Path objects use forward slashes throughout — Windows VDI accepts forward slashes in Python pathlib operations even though Explorer shows backslashes.

---

## T-C2 — Lock acquire/release helpers with PID liveness

**Depends on:** T-B1, T-B2, T-B3
**Touches files:** `/api/state/locks.py`
**Estimated effort:** medium

### Goal

Implement the lock acquire/release/query helpers backed by the `locks` table per D-057, with PID liveness checking that returns "not held" when the recorded PID is dead. Single-lock model per V's Phase 5 directive — all calls operate on row `id=1`. Audit-log every acquire and release per D-058.

### Context

From D-057 (Run state machine, Phase 3):

> Per-phase locks live in SQLite. ... Lock check + acquire happens in the FastAPI request handler before launching the `PipelineRunner` subprocess; release on subprocess exit (success or failure). Stale-lock mitigation: PID liveness check on lock-state queries.

From V's Phase 5 directive:

> Single-lock model: one row in the locks table (id=1). Any operation blocks any other operation. Tooltip strings tighten to "An active operation is in progress." Schema preserves a nullable `phase` column for forward migration to two-lock if the partner confirms safe concurrency.

From D-058 (Database schema):

> `audit_log` ... `lock_acquired` / `lock_released` per phase.

The `phase` audit value is preserved under the single-lock model — every lock event records WHICH phase the operator was attempting (staged or approval) for forensic completeness. Only the lock-table contention behavior tightens, not the audit granularity.

### Implementation

**File: `/api/state/locks.py`**:

```python
"""
Single-row lock helpers per V's Phase 5 directive resolving D-057 §11.6.

Three operations:
    acquire_lock — atomic compare-and-set on the locks.held column; fails
                   cleanly if a lock is already held by a live process.
    release_lock — clears the held state; idempotent (releasing an already-
                   free lock is a no-op).
    get_lock_state — read-only query that returns the current state plus
                     resolved PID liveness for the caller's display use.

Audit logging: every successful acquire writes LOCK_ACQUIRED; every release
writes LOCK_RELEASED. The phase parameter on acquire/release records the
operator's INTENT (staged vs approval) even under single-lock — the
contention is global, but audit-log granularity preserves which phase was
running for forensic clarity.

PID liveness check uses os.kill(pid, 0) on POSIX-like and a Windows-specific
fallback. The "lock is held by a dead PID" case is treated as "not held"
by callers; the reaper (T-C6) clears the dead row at startup.
"""

import logging
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Literal

from api.db.audit import AuditAction, write_audit
from api.db.connection import connection

logger = logging.getLogger(__name__)

LockPhase = Literal["staged", "approval"]

# Single-lock model: all operations target the row with id = 1.
_LOCK_ID = 1


@dataclass(frozen=True)
class LockState:
    """Current state of the single global lock, with PID liveness resolved."""

    held: bool                     # True iff held AND holder PID is alive
    held_by_pid: int | None        # the PID recorded in the lock row (may be dead)
    held_by_operator: str | None
    run_id: str | None
    phase: str | None              # 'staged' | 'approval' | None
    acquired_at: str | None        # ISO 8601 UTC

    @property
    def is_stale(self) -> bool:
        """True iff a held flag is set but the recorded PID is dead."""
        return (
            self.held_by_pid is not None
            and self.run_id is not None
            and not self.held
        )


def _is_pid_alive(pid: int) -> bool:
    """Check whether a process exists.

    POSIX: os.kill(pid, 0) raises ProcessLookupError if dead, PermissionError
    if we lack permission to signal (treated as alive — process exists but
    is owned by someone else). Any other OSError is also treated as alive
    (defensive: don't reap a lock based on a flaky kernel call).

    Windows: subprocess.run('tasklist /FI "PID eq %d"') is the official path
    but launches a subprocess every check. Use a lighter ctypes path via
    OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION).
    """
    if pid <= 0:
        return False

    if sys.platform == "win32":
        return _is_pid_alive_windows(pid)
    return _is_pid_alive_posix(pid)


def _is_pid_alive_posix(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        # Process exists but we can't signal it. Treat as alive.
        return True
    except OSError as exc:
        logger.warning("Unexpected OSError checking PID %d: %s; treating as alive.", pid, exc)
        return True


def _is_pid_alive_windows(pid: int) -> bool:
    try:
        import ctypes
        # PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        SYNCHRONIZE = 0x00100000
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        handle = ctypes.windll.kernel32.OpenProcess(
            PROCESS_QUERY_LIMITED_INFORMATION | SYNCHRONIZE, False, pid
        )
        if handle == 0:
            return False
        # Check if the process has exited.
        STILL_ACTIVE = 259
        exit_code = ctypes.c_ulong(0)
        if ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
            alive = exit_code.value == STILL_ACTIVE
        else:
            alive = True  # defensive
        ctypes.windll.kernel32.CloseHandle(handle)
        return alive
    except Exception as exc:
        logger.warning("Windows PID-liveness check failed for %d: %s; treating as alive.", pid, exc)
        return True


def get_lock_state() -> LockState:
    """Read the current lock state, resolving PID liveness.

    Returns a LockState where `held` is True iff the row's held=1 AND the
    recorded PID is alive. If held=1 but PID is dead, the returned state
    has `held=False` but the other fields (held_by_pid, run_id, etc.)
    populated for the caller's inspection — useful for the reaper (T-C6)
    which detects exactly this stale state and clears it.
    """
    with connection() as conn:
        row = conn.execute(
            "SELECT id, held, held_by_pid, held_by_operator, run_id, phase, acquired_at "
            "FROM locks WHERE id = ?",
            (_LOCK_ID,),
        ).fetchone()

    if row is None:
        # Schema migration didn't run, or the row was deleted somehow.
        # Treat as not-held; T-B1 seeds the row on migration so this is
        # an unexpected state worth logging.
        logger.warning("locks table has no row with id=%d; treating as not held.", _LOCK_ID)
        return LockState(False, None, None, None, None, None)

    held_in_db = bool(row["held"])
    pid = row["held_by_pid"]

    if held_in_db and pid is not None:
        # PID-resolved "actually held".
        actually_held = _is_pid_alive(pid)
        return LockState(
            held=actually_held,
            held_by_pid=pid,
            held_by_operator=row["held_by_operator"],
            run_id=row["run_id"],
            phase=row["phase"],
            acquired_at=row["acquired_at"],
        )

    # Not held in DB.
    return LockState(False, None, None, None, None, None)


def acquire_lock(
    operator_id: str,
    run_id: str,
    phase: LockPhase,
) -> bool:
    """Attempt to acquire the global lock for an operation.

    Returns True if acquired, False if a live holder already has it.
    Audit-logs LOCK_ACQUIRED on success.

    Atomic semantics: the UPDATE statement uses a WHERE clause filtering
    on held=0 (or held=1 with a dead PID). Only one concurrent caller can
    flip the row; the rest see rows_affected=0 and get False.

    Stale-lock auto-reap: if the lock is held=1 but the PID is dead, this
    function takes it over (atomically). The reaper (T-C6) is the cleaner
    long-form recovery for app restarts, but inline reap here covers the
    "PID died between two requests" case.
    """
    pid = os.getpid()
    ts = datetime.now(timezone.utc).isoformat()

    with connection() as conn:
        conn.execute("BEGIN IMMEDIATE")
        try:
            # Read current state under lock.
            row = conn.execute(
                "SELECT held, held_by_pid FROM locks WHERE id = ?",
                (_LOCK_ID,),
            ).fetchone()

            if row is None:
                # Defensive: seed the row if somehow absent.
                conn.execute(
                    "INSERT INTO locks (id, held) VALUES (?, 0)", (_LOCK_ID,)
                )
                held_in_db, holder_pid = False, None
            else:
                held_in_db, holder_pid = bool(row["held"]), row["held_by_pid"]

            # If held by a live process, fail.
            if held_in_db and holder_pid is not None and _is_pid_alive(holder_pid):
                conn.execute("ROLLBACK")
                logger.info(
                    "acquire_lock rejected — lock held by live PID %d (run %s)",
                    holder_pid, run_id,
                )
                return False

            # Either not held, or held by a dead PID — take it over.
            if held_in_db and holder_pid is not None:
                logger.warning(
                    "Stealing stale lock from dead PID %d (was holding for run %s)",
                    holder_pid, row["run_id"] if "run_id" in row.keys() else "?",
                )

            conn.execute(
                "UPDATE locks SET held=1, held_by_pid=?, held_by_operator=?, "
                "run_id=?, phase=?, acquired_at=? WHERE id=?",
                (pid, operator_id, run_id, phase, ts, _LOCK_ID),
            )
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            logger.exception("acquire_lock failed unexpectedly")
            return False

    # Audit-log outside the DB transaction so an audit-write failure
    # doesn't roll back the lock acquisition.
    write_audit(
        operator_id=operator_id,
        action_type=AuditAction.LOCK_ACQUIRED,
        run_id=run_id,
        lock_phase=phase,
        details={"pid": pid},
    )
    logger.info(
        "Lock acquired by operator=%s run=%s phase=%s pid=%d",
        operator_id, run_id, phase, pid,
    )
    return True


def release_lock(
    operator_id: str,
    run_id: str,
    phase: LockPhase,
) -> None:
    """Release the global lock.

    Idempotent — releasing an already-free lock is logged and audited but
    does not raise. Audit-logs LOCK_RELEASED.

    The (operator_id, run_id, phase) parameters are for the audit row;
    they do NOT have to match what's currently in the locks table.
    Mismatch is logged as a warning and the release proceeds (defensive:
    we want the lock released even if a stale row identifier slipped in).
    """
    with connection() as conn:
        conn.execute("BEGIN IMMEDIATE")
        try:
            row = conn.execute(
                "SELECT held, run_id FROM locks WHERE id = ?", (_LOCK_ID,)
            ).fetchone()
            if row is None or not row["held"]:
                conn.execute("ROLLBACK")
                logger.info("release_lock called but lock was not held; no-op.")
            else:
                stored_run_id = row["run_id"]
                if stored_run_id != run_id:
                    logger.warning(
                        "release_lock called with run_id=%s but lock holds run_id=%s; "
                        "releasing anyway.",
                        run_id, stored_run_id,
                    )
                conn.execute(
                    "UPDATE locks SET held=0, held_by_pid=NULL, held_by_operator=NULL, "
                    "run_id=NULL, phase=NULL, acquired_at=NULL WHERE id=?",
                    (_LOCK_ID,),
                )
                conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            logger.exception("release_lock failed unexpectedly")
            return

    write_audit(
        operator_id=operator_id,
        action_type=AuditAction.LOCK_RELEASED,
        run_id=run_id,
        lock_phase=phase,
        details=None,
    )
    logger.info(
        "Lock released by operator=%s run=%s phase=%s",
        operator_id, run_id, phase,
    )
```

### Acceptance criteria

- [ ] `/api/state/locks.py` exports `LockState`, `LockPhase`, `acquire_lock()`, `release_lock()`, `get_lock_state()`
- [ ] After migrations run, `get_lock_state()` returns `LockState(held=False, held_by_pid=None, ...)`
- [ ] `acquire_lock("op-1", "run-1", "staged")` returns True; subsequent `get_lock_state()` returns `LockState(held=True, held_by_pid=<current pid>, run_id='run-1', phase='staged', ...)`
- [ ] Second concurrent `acquire_lock("op-2", "run-2", "approval")` returns False (live holder)
- [ ] `release_lock("op-1", "run-1", "staged")` succeeds; subsequent `get_lock_state()` returns held=False
- [ ] Releasing an already-free lock is a no-op (logged but no raise)
- [ ] PID-liveness simulation: manually `UPDATE locks SET held=1, held_by_pid=99999` (a PID that doesn't exist); `get_lock_state()` returns `held=False, held_by_pid=99999, run_id=...` (the stale row's metadata is preserved for the reaper)
- [ ] After the stale-PID scenario above, `acquire_lock("op-3", "run-3", "staged")` succeeds (steals the stale lock) and logs a warning
- [ ] After each successful acquire, `sqlite3 <db> "SELECT action_type, lock_phase, run_id FROM audit_log ORDER BY id DESC LIMIT 1"` returns the LOCK_ACQUIRED row with correct phase
- [ ] After each successful release, the latest audit_log row is LOCK_RELEASED with correct phase

### Notes

`BEGIN IMMEDIATE` is used instead of plain `BEGIN` because SQLite's deferred locking would let two concurrent readers race past the held-check before either commits. `IMMEDIATE` acquires a write-reservation on the database immediately, serializing the acquire path. The cost is brief contention on the global lock-read; benefit is correctness on simultaneous acquire attempts.

The audit-log writes happen OUTSIDE the lock transaction. This is intentional: an audit-write failure should not roll back a successful lock acquire. The trade-off is a small window where the lock is acquired but no audit row exists — acceptable per the audit-write-failure design from T-B3.

PID liveness on Windows uses ctypes rather than the `subprocess + tasklist` approach. The ctypes path is faster (no subprocess overhead) and works in JPMC VDI without requiring shell-out. If the ctypes import or the kernel32 calls fail (extremely unusual), the fallback is "treat as alive" — better to refuse a lock acquisition than to steal a live one based on a flaky liveness check.

The `phase` parameter under the single-lock model is purely for audit clarity. If the partner later confirms safe concurrency and a two-lock migration lands, this parameter starts driving WHICH row to operate on without changing the function signatures. Callers in Section E pass `phase="staged"` for `/runs/start` and `phase="approval"` for `/runs/{id}/approve` regardless of current single-lock semantics.

The `LockState.is_stale` property is a convenience for the reaper in T-C6; it returns True iff the row indicates `held` data but `held` resolved to False due to PID liveness — exactly the condition the reaper cleans.

---

## T-C3 — `failure.json` writer and schema

**Depends on:** T-C1
**Touches files:** `/api/state/failure.py`, `/api/state/sentinels.py` (modification: add SENTINEL_FAILED — already in T-C1)
**Estimated effort:** small

### Goal

Implement the `write_failure_json()` helper that subprocess wrappers (Section D adapters) call when the pipeline exits non-zero or raises an uncaught exception. The schema captures the stage, error context, and a retry strategy hint that the UI uses to decide which action buttons to show per D-046.

### Context

From D-046 (Failure visibility, Phase 2):

> Failed-during-staged → operator can only Re-run from scratch (partial filesystem state can't be trusted).
> Failed-during-approval → operator can Retry Approve (the staged outputs are still intact and a retry can pick up from there) OR Re-run from scratch.
> Failure UX shows: where it failed (staged vs approval), what the error was, and what the operator can do.

From `ui-approach.md` §9 (partner's subprocess pattern guidance):

> Subprocess invocation: `run_unified_pipeline(skip_jira=True)` for staged; `submit_to_jira(output_folder)` for approval. The wrapper that spawns either subprocess is also the one that writes failure.json when the subprocess exits non-zero — the pipeline functions themselves don't know about UI sentinels.

### Implementation

**File: `/api/state/failure.py`**:

```python
"""
failure.json writer per D-046.

Called by Section D's PipelineRunner adapters (both subprocess and mock)
when a pipeline invocation fails — either by non-zero exit code, raised
exception, or by emitting a run_failed event the wrapper observes.

Schema (this UI's contract; not from the partner's pipeline):

    {
      "stage": "staged" | "approval",
      "ts": "<ISO 8601 UTC>",
      "exit_code": <int> | null,
      "error_message": "<short, operator-facing>",
      "technical_details": "<longer, includes stack trace if any>" | null,
      "retry_strategy": "rerun_only" | "retry_or_rerun"
    }

retry_strategy maps directly to which action buttons the UI renders on
Run Detail per D-046:
    rerun_only      → only "Re-run from scratch"   (failed during staged)
    retry_or_rerun  → "Retry Approve" + "Re-run from scratch" (failed during approval)

The mapping (stage → retry_strategy) is deterministic, so the strategy
field is derivable. We still write it explicitly so the UI doesn't need
to know the mapping rule — it just reads the strategy and renders the
corresponding buttons. This keeps the rule in one place (here).
"""

import json
import logging
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from api.state.sentinels import SENTINEL_FAILED

logger = logging.getLogger(__name__)

FailureStage = Literal["staged", "approval"]
RetryStrategy = Literal["rerun_only", "retry_or_rerun"]


def _strategy_for_stage(stage: FailureStage) -> RetryStrategy:
    """Map stage to retry-strategy per D-046."""
    if stage == "staged":
        return "rerun_only"
    return "retry_or_rerun"


def write_failure_json(
    folder_path: Path,
    stage: FailureStage,
    error_message: str,
    *,
    exit_code: int | None = None,
    technical_details: str | None = None,
    exc: BaseException | None = None,
) -> None:
    """Write failure.json into a run folder.

    Args:
        folder_path: The run folder. Must exist (caller responsible for
                     verifying). failure.json is written at the folder root.
        stage: 'staged' or 'approval' — drives retry_strategy per D-046.
        error_message: Short, operator-facing one-liner. Shown in the Run
                       Detail header failure state per the visual mockup.
        exit_code: Subprocess exit code if available; None if the failure
                   came from a raised exception with no exit code.
        technical_details: Longer-form context (stderr tail, custom message).
                           If None and `exc` is provided, the formatted
                           traceback is used here automatically.
        exc: Optional exception. If provided, its formatted traceback
             populates technical_details (unless technical_details was
             passed explicitly, which wins).

    Defensive: never raises. If the write fails (disk full, permission),
    the exception is logged but the calling subprocess wrapper continues.
    The run is still in a failed state from the subprocess's exit code;
    the missing failure.json just means the UI can't show the rich error
    context (falls back to a generic "this run failed" header).
    """
    target = folder_path / SENTINEL_FAILED

    if technical_details is None and exc is not None:
        technical_details = "".join(
            traceback.format_exception(type(exc), exc, exc.__traceback__)
        )

    payload = {
        "stage": stage,
        "ts": datetime.now(timezone.utc).isoformat(),
        "exit_code": exit_code,
        "error_message": error_message,
        "technical_details": technical_details,
        "retry_strategy": _strategy_for_stage(stage),
    }

    try:
        # Write atomically: write to .tmp then rename. Prevents a half-written
        # failure.json being read by infer_state during the write.
        tmp = target.with_suffix(target.suffix + ".tmp")
        tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        tmp.replace(target)
        logger.info(
            "Wrote failure.json for %s: stage=%s error=%s",
            folder_path.name, stage, error_message,
        )
    except Exception:
        logger.exception(
            "Failed to write failure.json at %s; run remains in failed state "
            "but rich error context will not be available in UI.",
            target,
        )


def read_failure_json(folder_path: Path) -> dict | None:
    """Read failure.json from a run folder.

    Returns the parsed payload as a dict, or None if the file doesn't exist
    or is malformed. Used by Section E's GET /api/runs/{run_id} endpoint
    to surface failure context to the UI.
    """
    target = folder_path / SENTINEL_FAILED
    if not target.exists():
        return None
    try:
        with target.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("Could not read %s: %s", target, exc)
        return None
```

### Acceptance criteria

- [ ] `/api/state/failure.py` exports `write_failure_json()` and `read_failure_json()`
- [ ] `write_failure_json(Path('/test/run-1'), 'staged', 'Pipeline crashed')` writes a valid JSON file at `/test/run-1/failure.json` containing all six fields with `retry_strategy='rerun_only'`
- [ ] `write_failure_json(Path('/test/run-1'), 'approval', 'Jira down')` produces `retry_strategy='retry_or_rerun'`
- [ ] Passing `exc=exception_instance` populates `technical_details` with the formatted traceback
- [ ] Explicit `technical_details=` overrides the traceback fallback
- [ ] Write is atomic — interrupting the write process (e.g., simulated disk-full halfway) does not leave a partial `failure.json` (it leaves the `.tmp` file at most, which `infer_state` will not match)
- [ ] `read_failure_json(Path('/test/missing'))` returns `None` without raising
- [ ] `read_failure_json` on a malformed file returns `None` with a warning logged

### Notes

The atomic-write pattern (`.tmp` + `replace`) matters because `infer_state` polls for the existence of `failure.json` and a partial write would race. The `Path.replace` call is atomic on the same filesystem on both Windows and POSIX.

The schema does NOT include a `run_id` field because failure.json lives INSIDE the run folder — its location identifies the run. Adding a redundant run_id would create the possibility of inconsistency (folder name says one thing, internal field says another).

Per D-046's "no in-place retry" model: a successful re-run from scratch creates a NEW run folder. The failed folder is preserved as-is, including its `failure.json`. This is why we don't need a "this failure was retried; here's the successor run_id" pointer in the schema — the operator clicks Re-run from scratch, a new folder is created, the relationship is captured in audit_log via the `parent_run_id` in details_json (Section E will set this on rerun_from_scratch_clicked audit writes).

The `retry_strategy` field is intentionally redundant with `stage` for the API contract — the UI doesn't have to know the mapping rule. If D-046's mapping ever changes (e.g., partner adds a third stage), this module is the single update point.

---

## T-C4 — Event ingestion (parser + writer to `events` table)

**Depends on:** T-B1, T-B2
**Touches files:** `/api/state/events.py`
**Estimated effort:** medium

### Goal

Implement `record_event()` — the single write path for the `events` table consumed by every pipeline integration adapter in Section D. Validate event payloads against the 13-type D-059 taxonomy at write time so malformed event drift surfaces early rather than in Activity tab rendering.

### Context

From D-058 (Database schema):

> events table — narrow with JSON payload. Columns: id, run_id, ts, type, payload_json. Event taxonomy lands in the Area H decision; this table absorbs new event types without schema migrations.

From D-059 (Event taxonomy, Phase 3 — referenced from the spec docs; the 13 types):

> The canonical event taxonomy (13 types) covers: `run_started`, `stage_started`, `stage_progress`, `stage_completed`, `validation_failure`, `warning`, `comparison_ready`, `pre_approval_reached`, `approval_submitted`, `jira_created`, `sharepoint_synced`, `submission_complete`, `run_failed`. Each type's payload schema is documented in D-059 and reproduced in T-C4's implementation.

From D-058 #2:

> issues is derived from events, not a separate table. Issues tab queries `SELECT * FROM events WHERE run_id=? AND type IN ('validation_failure','warning','run_failed',...)`

This dual-purpose use (Activity replay + Issues filter) is why the type field must use canonical strings — the Issues query depends on exact string match.

### Implementation

**File: `/api/state/events.py`**:

```python
"""
Event ingestion per D-058 + D-059.

Single write path: record_event() inserts a row into the events table.
Section D's PipelineRunner adapters call this for every event emitted by
the pipeline subprocess; the SSE broadcaster (T-C5) is notified post-insert
so connected subscribers see the event in real time.

The 13-type canonical taxonomy is enforced at write time via the EventType
enum — passing an unknown type raises ValueError. This catches drift early
(the Issues tab query depends on exact match).

Event payload schemas are documented per-type in EventType comments below.
The payload_json column stores the JSON-serialized payload; schema evolution
is forward-compatible (adding payload fields doesn't break old rows) but
type renames require a migration.
"""

import json
import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from api.db.connection import connection

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Canonical event taxonomy per D-059.

    Payload schemas (the dict passed to record_event's `payload` parameter):

        RUN_STARTED:
            {"input_folder": "...", "merchant": "...", "operator_id": "..."}

        STAGE_STARTED / STAGE_PROGRESS / STAGE_COMPLETED:
            {"stage_name": "...", "message": "..." (optional),
             "percent": <int 0-100> (optional, STAGE_PROGRESS only)}

        VALIDATION_FAILURE:
            {"field": "...", "value": "...", "rule": "...",
             "severity": "critical" | "error" | "warning"}

        WARNING:
            {"message": "...", "context": {...} (optional)}

        COMPARISON_READY:
            {"changes_summary": {"add": <int>, "remove": <int>,
                                  "rate_update": <int>, "mcc_expansion": <int>}}

        PRE_APPROVAL_REACHED:
            {"output_folder": "...", "artifacts": [...]}

        APPROVAL_SUBMITTED:
            {"target_systems": ["jira", "sharepoint"]}

        JIRA_CREATED:
            {"epic_key": "...", "story_key": "..."}

        SHAREPOINT_SYNCED:
            {"folder_path": "..."}

        SUBMISSION_COMPLETE:
            {"epic_key": "...", "story_key": "...",
             "sharepoint_path": "..."}

        RUN_FAILED:
            {"stage": "staged" | "approval", "message": "...",
             "exit_code": <int> | null}
    """

    RUN_STARTED = "run_started"
    STAGE_STARTED = "stage_started"
    STAGE_PROGRESS = "stage_progress"
    STAGE_COMPLETED = "stage_completed"
    VALIDATION_FAILURE = "validation_failure"
    WARNING = "warning"
    COMPARISON_READY = "comparison_ready"
    PRE_APPROVAL_REACHED = "pre_approval_reached"
    APPROVAL_SUBMITTED = "approval_submitted"
    JIRA_CREATED = "jira_created"
    SHAREPOINT_SYNCED = "sharepoint_synced"
    SUBMISSION_COMPLETE = "submission_complete"
    RUN_FAILED = "run_failed"


# Event types that appear in the Issues tab per D-049 + D-058 #2.
# Section E's GET /api/runs/{id}/issues endpoint queries
# `WHERE type IN <this set>`.
ISSUE_EVENT_TYPES = frozenset({
    EventType.VALIDATION_FAILURE.value,
    EventType.WARNING.value,
    EventType.RUN_FAILED.value,
})


def record_event(
    run_id: str,
    event_type: EventType,
    payload: dict[str, Any],
    *,
    ts: str | None = None,
) -> int:
    """Insert an event into the events table.

    Args:
        run_id: The run this event belongs to.
        event_type: One of EventType's canonical values (enum-enforced).
        payload: Dict matching the per-type schema in EventType's docstring.
                 Serialized to JSON; non-serializable values stringify via
                 default=str (defensive).
        ts: Optional ISO 8601 UTC timestamp. Defaults to now() — pass an
            explicit ts only when replaying recorded events from an external
            source (e.g., the subprocess stdout timestamps).

    Returns:
        The inserted row's primary-key id (useful for SSE broadcast).

    Validation:
        - event_type must be an EventType instance.
        - payload must be a dict.
        - run_id must be non-empty.

    The SSE broadcaster (T-C5) is NOT called from here — record_event is
    the persistence path; subscribers are notified separately by the
    caller. This keeps the DB write loop tight and lets adapters batch
    SSE notifications independently from DB writes if needed.
    """
    if not isinstance(event_type, EventType):
        raise ValueError(
            f"record_event: event_type must be EventType enum, got {type(event_type)}"
        )
    if not isinstance(payload, dict):
        raise ValueError(
            f"record_event: payload must be dict, got {type(payload)}"
        )
    if not run_id:
        raise ValueError("record_event: run_id must be non-empty")

    if ts is None:
        ts = datetime.now(timezone.utc).isoformat()

    payload_json = json.dumps(payload, default=str)

    with connection() as conn:
        conn.execute("BEGIN")
        try:
            cur = conn.execute(
                "INSERT INTO events (run_id, ts, type, payload_json) "
                "VALUES (?, ?, ?, ?)",
                (run_id, ts, event_type.value, payload_json),
            )
            event_id = cur.lastrowid
            conn.execute("COMMIT")
            return event_id
        except Exception:
            conn.execute("ROLLBACK")
            logger.exception("record_event failed for run_id=%s type=%s", run_id, event_type)
            raise


def read_events_for_run(run_id: str) -> list[dict[str, Any]]:
    """Read all events for a run in chronological order.

    Returns a list of dicts with keys: id, run_id, ts, type, payload
    (deserialized from payload_json). Used by Section E's GET
    /api/runs/{run_id}/events endpoint for Activity tab replay per D-040.

    Returns empty list if the run has no events (e.g., a folder that exists
    but never had a UI-initiated run, or a folder predating the events
    table).
    """
    with connection() as conn:
        rows = conn.execute(
            "SELECT id, run_id, ts, type, payload_json FROM events "
            "WHERE run_id = ? ORDER BY ts ASC, id ASC",
            (run_id,),
        ).fetchall()

    result: list[dict[str, Any]] = []
    for r in rows:
        try:
            payload = json.loads(r["payload_json"])
        except json.JSONDecodeError:
            logger.warning(
                "Malformed payload_json for event id=%d run_id=%s; using empty dict.",
                r["id"], run_id,
            )
            payload = {}
        result.append({
            "id": r["id"],
            "run_id": r["run_id"],
            "ts": r["ts"],
            "type": r["type"],
            "payload": payload,
        })
    return result


def read_issues_for_run(run_id: str) -> list[dict[str, Any]]:
    """Read only Issues-tab events for a run per D-049 + D-058 #2.

    Filters by type IN ISSUE_EVENT_TYPES. Used by Section E's GET
    /api/runs/{run_id}/issues endpoint.

    Sort order: by severity (critical → error → warning), then by ts ASC.
    Severity is read from the payload's `severity` field for
    VALIDATION_FAILURE and from a derived rule for the other types:
      - RUN_FAILED → severity="critical"
      - WARNING → severity defaults to "warning" unless payload says otherwise
    """
    placeholders = ",".join("?" for _ in ISSUE_EVENT_TYPES)
    with connection() as conn:
        rows = conn.execute(
            f"SELECT id, run_id, ts, type, payload_json FROM events "
            f"WHERE run_id = ? AND type IN ({placeholders}) "
            f"ORDER BY ts ASC, id ASC",
            (run_id, *ISSUE_EVENT_TYPES),
        ).fetchall()

    severity_order = {"critical": 0, "error": 1, "warning": 2}

    def _severity_of(event_dict: dict[str, Any]) -> int:
        payload = event_dict["payload"]
        if event_dict["type"] == EventType.RUN_FAILED.value:
            return severity_order["critical"]
        sev = payload.get("severity", "warning")
        return severity_order.get(sev, severity_order["warning"])

    parsed: list[dict[str, Any]] = []
    for r in rows:
        try:
            payload = json.loads(r["payload_json"])
        except json.JSONDecodeError:
            payload = {}
        parsed.append({
            "id": r["id"],
            "run_id": r["run_id"],
            "ts": r["ts"],
            "type": r["type"],
            "payload": payload,
        })

    # Sort by severity, then ts ASC. (read order is already ts ASC; this
    # promotes higher-severity events to the top within the chronological flow.)
    parsed.sort(key=lambda e: (_severity_of(e), e["ts"]))
    return parsed
```

### Acceptance criteria

- [ ] `/api/state/events.py` exports `EventType`, `ISSUE_EVENT_TYPES`, `record_event()`, `read_events_for_run()`, `read_issues_for_run()`
- [ ] `EventType` has exactly 13 members matching D-059's taxonomy
- [ ] `record_event("r1", EventType.RUN_STARTED, {"input_folder": "/tmp"})` returns an integer id; subsequent `sqlite3 <db> "SELECT * FROM events WHERE id=<id>"` shows the row
- [ ] `record_event("r1", "run_started", {})` (string instead of EventType) raises ValueError
- [ ] `record_event("", EventType.RUN_STARTED, {})` (empty run_id) raises ValueError
- [ ] `read_events_for_run("r1")` returns events ordered by `ts ASC`, then `id ASC` (so same-millisecond events stay in insertion order)
- [ ] `read_issues_for_run("r1")` returns only events of type validation_failure / warning / run_failed
- [ ] `read_issues_for_run` sort order: critical first (RUN_FAILED), then errors (VALIDATION_FAILURE with severity="error"), then warnings; ties broken by ts ASC
- [ ] Inserting a non-JSON-serializable payload field (e.g., a Path object) succeeds — the `default=str` fallback stringifies it; `read_events_for_run` shows the field as a string

### Notes

The `record_event` function intentionally does NOT broadcast to SSE subscribers — that's the caller's responsibility, handled by Section D's PipelineRunner adapters after the DB write returns. Decoupling means a DB-write failure doesn't prevent the SSE notification (or vice versa), and the SSE broadcaster (T-C5) stays unaware of persistence concerns.

The `ISSUE_EVENT_TYPES` set is exposed module-level (frozenset) so other code that wants to "filter events to issues" can reuse the same definition rather than re-listing types. If new event types should appear in Issues later, update this single constant.

`json.dumps(payload, default=str)` is the defensive serialization. A pure-data payload (strings, numbers, lists, nested dicts) serializes losslessly. A payload that accidentally contains a non-serializable object (datetime, Path, numpy type) stringifies rather than raising — preferable to a record_event call failing because of an adapter mistake.

`read_issues_for_run` does the severity sorting in Python rather than SQL because the severity comes from inside payload_json (no indexed column). At ~50-150 events per run scale, sorting in Python is microseconds.

The `payload_json` text could be parsed once and joined with the row dict at SQL time using SQLite's JSON1 extension, but that requires the SQLite build to include JSON1 — true on modern macOS/Linux but not guaranteed on older Windows Python distributions. Python-side parsing is portable.

---

## T-C5 — In-memory SSE event broadcaster

**Depends on:** T-C4, T1
**Touches files:** `/api/state/sse.py`
**Estimated effort:** medium

### Goal

Implement a per-process `EventBroadcaster` singleton that holds subscriber queues for each SSE connection and pushes events to all subscribers when an adapter calls `broadcast()`. The broadcaster lives in memory only — events are persisted by `record_event()` in T-C4 separately. On reconnect, the SSE client requests a backlog via `GET /api/runs/{run_id}/events` (Section E) rather than relying on broker durability.

### Context

From D-060 (SSE design, Phase 3):

> Server-driven cadence (no client polling). FastAPI emits SSE events as the pipeline subprocess produces them, multiplexed by run_id. Backpressure: in-memory bounded queue per subscriber; on overflow, drop the oldest event for that subscriber and log (subscriber should reconnect to resync via `GET /api/runs/{run_id}/events` which returns the full event history from the DB).

From D-060 calibration:

> Reconnection model: browser's default EventSource reconnect with a fresh subscription (server doesn't durably replay; client triggers GET /api/runs/{run_id}/events on reconnect to backfill). The Last-Event-ID semantic is documented but unused at MVP scale — adding it is a Phase 7 enhancement.

From the partner's pipeline note in `ui-approach.md` §9:

> Adapters call into the API layer after each parsed event. The API layer is responsible for both persistence (events table) and broadcast (SSE subscribers).

### Implementation

**File: `/api/state/sse.py`**:

```python
"""
In-memory SSE event broadcaster per D-060.

Single per-process EventBroadcaster singleton. Adapters call broadcast()
after each successful record_event() to fan out the event to all currently-
connected SSE subscribers. New subscribers (HTTP GET to /api/events handled
by Section E's SSE endpoint) register a queue here and consume from it
asynchronously.

Persistence is OUT OF SCOPE here — record_event() (T-C4) is the persistence
path. This module is pure in-memory pub/sub. Subscribers that miss events
(disconnect / overflow) reconnect and call GET /api/runs/{run_id}/events
to backfill from the DB; the broadcaster doesn't replay.

Backpressure per D-060:
    Per-subscriber queue size = 100 events
    On full: drop oldest, log, continue. The dropped event still exists
    in the DB; the subscriber will pick it up via reconnect-backfill.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

logger = logging.getLogger(__name__)

# Per-subscriber queue size. At ~50-150 events/run and ~5 sec event spacing,
# a 100-event queue tolerates a 500-second processing stall before dropping.
_MAX_QUEUE_SIZE = 100


@dataclass
class _Subscriber:
    """A single SSE subscriber's state."""

    subscriber_id: str
    queue: asyncio.Queue
    # Optional filter: if run_id is set, only events for that run are
    # forwarded. None means "all runs" (the global /api/events stream).
    run_id_filter: str | None = None
    # Counter of dropped events for this subscriber, surfaced in logs
    # when the subscriber disconnects.
    dropped_count: int = 0


class EventBroadcaster:
    """In-memory pub/sub fan-out for pipeline events.

    Singleton per process; instantiate via get_broadcaster() at module
    import time. FastAPI's lifespan (T1) holds the reference implicitly
    via the module-level _broadcaster.
    """

    def __init__(self) -> None:
        self._subscribers: dict[str, _Subscriber] = {}
        self._lock = asyncio.Lock()  # guards _subscribers dict mutation

    async def subscribe(self, run_id: str | None = None) -> _Subscriber:
        """Register a new subscriber and return its handle.

        Args:
            run_id: If provided, only events with matching run_id are
                    forwarded to this subscriber. None = all events.

        The subscriber consumes from `subscriber.queue` (await get()).
        Caller is responsible for calling unsubscribe() when the SSE
        connection closes.
        """
        sub = _Subscriber(
            subscriber_id=str(uuid4()),
            queue=asyncio.Queue(maxsize=_MAX_QUEUE_SIZE),
            run_id_filter=run_id,
        )
        async with self._lock:
            self._subscribers[sub.subscriber_id] = sub
        logger.info(
            "SSE subscriber connected: %s (run_id_filter=%s); total=%d",
            sub.subscriber_id, run_id, len(self._subscribers),
        )
        return sub

    async def unsubscribe(self, subscriber: _Subscriber) -> None:
        """Remove a subscriber. Idempotent."""
        async with self._lock:
            self._subscribers.pop(subscriber.subscriber_id, None)
        if subscriber.dropped_count > 0:
            logger.warning(
                "SSE subscriber %s disconnected with %d dropped events "
                "(client should backfill via GET /api/runs/<id>/events)",
                subscriber.subscriber_id, subscriber.dropped_count,
            )
        logger.info(
            "SSE subscriber disconnected: %s; remaining=%d",
            subscriber.subscriber_id, len(self._subscribers),
        )

    async def broadcast(
        self,
        run_id: str,
        event_type: str,
        payload: dict[str, Any],
        *,
        event_id: int | None = None,
        ts: str | None = None,
    ) -> int:
        """Fan out an event to all matching subscribers.

        Args:
            run_id: The run this event belongs to. Used for subscriber filtering.
            event_type: Canonical event type string (EventType.X.value).
            payload: Event payload dict (already JSON-serializable).
            event_id: Database row id from record_event() (used for SSE
                      message id, future Last-Event-ID support per D-060
                      calibration).
            ts: Optional ISO 8601 timestamp string.

        Returns:
            Number of subscribers the event was delivered to (post-filter,
            excluding dropped overflows). Logged but not used by callers
            in steady state.
        """
        message = {
            "id": event_id,
            "run_id": run_id,
            "type": event_type,
            "payload": payload,
            "ts": ts,
        }

        delivered = 0
        async with self._lock:
            subscribers = list(self._subscribers.values())

        for sub in subscribers:
            # Apply per-subscriber run_id filter.
            if sub.run_id_filter is not None and sub.run_id_filter != run_id:
                continue
            try:
                sub.queue.put_nowait(message)
                delivered += 1
            except asyncio.QueueFull:
                # Backpressure: drop oldest, then enqueue new.
                try:
                    sub.queue.get_nowait()
                except asyncio.QueueEmpty:
                    pass
                try:
                    sub.queue.put_nowait(message)
                    delivered += 1
                    sub.dropped_count += 1
                except asyncio.QueueFull:
                    # Pathological — queue full after dequeue. Skip.
                    logger.warning(
                        "SSE subscriber %s queue still full after dequeue; skipping event.",
                        sub.subscriber_id,
                    )

        return delivered

    def subscriber_count(self) -> int:
        """For instrumentation / debugging."""
        return len(self._subscribers)


# Module-level singleton. Importing this module gives every caller the
# same instance.
_broadcaster: EventBroadcaster | None = None


def get_broadcaster() -> EventBroadcaster:
    """Return the process-wide EventBroadcaster singleton."""
    global _broadcaster
    if _broadcaster is None:
        _broadcaster = EventBroadcaster()
    return _broadcaster
```

### Acceptance criteria

- [ ] `/api/state/sse.py` exports `EventBroadcaster`, `get_broadcaster()`
- [ ] `get_broadcaster()` returns the same instance across calls within a single Python process
- [ ] A subscribed coroutine that awaits `sub.queue.get()` receives a message dispatched via `broadcast()` for a matching run_id
- [ ] A subscriber with `run_id_filter='r1'` does NOT receive events broadcast for run_id='r2'
- [ ] A subscriber with `run_id_filter=None` receives ALL broadcasts regardless of run_id
- [ ] Filling a subscriber's queue past `_MAX_QUEUE_SIZE` triggers oldest-event drop; `sub.dropped_count` increments; the latest event is enqueued
- [ ] `unsubscribe(sub)` is idempotent — calling twice doesn't raise
- [ ] `broadcaster.subscriber_count()` reflects active subscriptions accurately

### Notes

The broadcaster uses asyncio primitives (Queue, Lock) because FastAPI's request handlers are async. SSE endpoints in Section E will call `await broadcaster.subscribe()` and then `async for` over the queue inside an `EventSourceResponse` (from sse-starlette pinned in T1).

There is no global rate limit or priority queue — all subscribers get the same fan-out behavior. At ~50 runs/year and rarely more than 1-2 concurrent SSE connections (the operator viewing a single Run Detail), this is well within capacity.

The `event_id` parameter is plumbed through but not yet used for client-side resume. Per D-060 calibration: future Phase 7 enhancement may use SSE's `id:` field for Last-Event-ID-driven catchup. Until then, clients reconnect → call GET `/api/runs/{run_id}/events` for backfill, and the field is logged in dev tools but not consumed.

This module is process-local. If the production team ever shards uvicorn workers (multiple processes), each worker has its own broadcaster — subscribers connected to worker A miss events broadcast from worker B. The MVP single-uvicorn-process model per D-067 sidesteps this; ECS production deployment with horizontal scaling would need a Redis pub/sub backplane (out of scope for ci_ui).

The drop-oldest-on-overflow policy matches D-060's design: stale events are less valuable than fresh, and the client's reconnect-backfill flow recovers anything lost.

---

## T-C6 — Stale-lock reaper startup hook

**Depends on:** T-C2, T1, T-B2, T-B4
**Touches files:** `/api/state/reaper.py`, `/api/main.py` (modification: add reap call to lifespan)
**Estimated effort:** small

### Goal

Implement `reap_stale_locks()` and wire it into FastAPI's lifespan startup after migrations and MAID backfill. Detects locks held by PIDs that don't exist (uvicorn crashed mid-run), clears them, writes audit_log entries documenting the reap, and writes failure.json for the orphaned run folder so the UI shows the right state.

### Context

From D-057 (Phase 3 Tech Spec):

> Stale-lock mitigation: PID liveness check on lock-state queries.

From D-067 (Deployment shape):

> Process management for MVP: manual invocation. uvicorn process is the entire app — if it dies, V or the operator restarts it. ... On uvicorn restart, the UI re-derives state from filesystem per D-057 and the locks table per D-058 (PID liveness check disambiguates stale from active locks).

The PID liveness check in `get_lock_state()` (T-C2) reports stale locks correctly to queries, but the row stays in `held=1` state until something clears it. The reaper is what clears it at startup so the audit-log shows the cleanup and the failed run's folder gets a `failure.json` reflecting the orphan.

### Implementation

**File: `/api/state/reaper.py`**:

```python
"""
Stale-lock reaper.

Runs once at FastAPI lifespan startup, after migrations + MAID backfill.

Scenario: uvicorn was killed (Ctrl+C in production VDI, host shutdown,
crash) while a pipeline subprocess was running. The locks table still
shows held=1 with the dead PID; if the subprocess was a child of the
dying uvicorn, it also died — leaving an incomplete output folder.

The reaper:
  1. Reads the locks table.
  2. If held=1 AND the recorded PID is dead, clears the lock row.
  3. Writes audit_log: LOCK_RELEASED with details {"reason": "reaper",
     "stale_pid": <pid>}.
  4. Writes failure.json into the orphaned run folder (if it still exists)
     so infer_state() returns FAILED for that run. Stage and message are
     inferred from the lock's phase column.

If the orphaned run folder no longer exists (operator deleted it, or it
was a stale lock against a never-existing folder), the failure.json write
is skipped silently.
"""

import logging
from pathlib import Path

from api.config import settings
from api.db.audit import AuditAction, write_audit
from api.db.connection import connection
from api.state.failure import write_failure_json
from api.state.locks import _is_pid_alive

logger = logging.getLogger(__name__)

_LOCK_ID = 1


def reap_stale_locks() -> dict[str, str] | None:
    """Detect and clear stale locks at startup.

    Returns:
        None if no stale lock found.
        Otherwise a dict describing what was reaped: {
            "run_id": "...",
            "phase": "staged" | "approval",
            "stale_pid": <int as str>,
            "operator_id": "...",
            "folder_exists": "true" | "false",
        }

    Defensive: never raises. A failure here is logged but doesn't prevent
    uvicorn from starting — the operator's first action after restart will
    surface any leftover issues.
    """
    try:
        with connection() as conn:
            row = conn.execute(
                "SELECT held, held_by_pid, held_by_operator, run_id, phase, acquired_at "
                "FROM locks WHERE id = ?",
                (_LOCK_ID,),
            ).fetchone()
    except Exception:
        logger.exception("Reaper: could not read locks table; skipping reap.")
        return None

    if row is None or not row["held"] or row["held_by_pid"] is None:
        return None

    pid = row["held_by_pid"]
    if _is_pid_alive(pid):
        # Held by a live process — not stale, leave it alone. The likely
        # scenario: uvicorn restarted but the pipeline subprocess survived
        # (it was started detached or daemonized). The UI will reconcile
        # state via filesystem + lock-state-with-liveness on the next request.
        logger.info(
            "Reaper: lock held by live PID %d (run %s); leaving alone.",
            pid, row["run_id"],
        )
        return None

    # Stale.
    run_id = row["run_id"]
    operator_id = row["held_by_operator"] or "unknown"
    phase = row["phase"] or "staged"

    logger.warning(
        "Reaper: clearing stale lock — pid=%d run_id=%s phase=%s operator=%s",
        pid, run_id, phase, operator_id,
    )

    # Clear the lock row.
    try:
        with connection() as conn:
            conn.execute("BEGIN IMMEDIATE")
            try:
                conn.execute(
                    "UPDATE locks SET held=0, held_by_pid=NULL, held_by_operator=NULL, "
                    "run_id=NULL, phase=NULL, acquired_at=NULL WHERE id=?",
                    (_LOCK_ID,),
                )
                conn.execute("COMMIT")
            except Exception:
                conn.execute("ROLLBACK")
                raise
    except Exception:
        logger.exception("Reaper: failed to clear stale lock row; aborting reap.")
        return None

    # Audit-log the reap.
    write_audit(
        operator_id=operator_id,
        action_type=AuditAction.LOCK_RELEASED,
        run_id=run_id,
        lock_phase=phase,
        details={"reason": "reaper", "stale_pid": pid},
    )

    # Write failure.json into the orphaned folder, if it still exists.
    folder_exists = False
    if run_id:
        folder = settings.output_base_folder_path / run_id
        if folder.exists() and folder.is_dir():
            folder_exists = True
            try:
                write_failure_json(
                    folder_path=folder,
                    stage=phase if phase in ("staged", "approval") else "staged",
                    error_message=(
                        "The previous run was interrupted "
                        "(application restart or crash)."
                    ),
                    technical_details=(
                        f"Lock was held by PID {pid} which is no longer alive. "
                        f"Reaper cleared the lock and marked this run as failed "
                        f"so its filesystem state reflects reality."
                    ),
                )
            except Exception:
                logger.exception(
                    "Reaper: failed to write failure.json for orphaned run %s.",
                    run_id,
                )

    return {
        "run_id": run_id or "",
        "phase": phase,
        "stale_pid": str(pid),
        "operator_id": operator_id,
        "folder_exists": "true" if folder_exists else "false",
    }
```

**Modification to `/api/main.py`** — append reaper call to lifespan after MAID backfill:

```python
"""
ci_ui FastAPI application.
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.config import settings
from api.db.maid_index import backfill_maid_index_if_needed
from api.db.migrate import apply_pending_migrations
from api.routers import runs as runs_router
from api.routers import system as system_router
from api.state.reaper import reap_stale_locks

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown hooks."""
    # 1. Schema migrations (T-B2).
    logger.info("Applying database migrations...")
    applied = apply_pending_migrations()
    if applied:
        logger.info("Applied migrations: %s", applied)

    # 2. MAID index backfill (T-B4).
    logger.info("Backfilling MAID index for any un-indexed run folders...")
    backfilled = backfill_maid_index_if_needed()
    if backfilled:
        logger.info("Backfilled %d runs into MAID index.", len(backfilled))

    # 3. Stale-lock reaper (T-C6).
    logger.info("Checking for stale locks...")
    reaped = reap_stale_locks()
    if reaped:
        logger.warning(
            "Reaped stale lock: run=%s phase=%s stale_pid=%s folder_exists=%s",
            reaped["run_id"], reaped["phase"], reaped["stale_pid"], reaped["folder_exists"],
        )
    else:
        logger.info("No stale locks found.")

    yield


# (rest of main.py unchanged)
```

### Acceptance criteria

- [ ] `/api/state/reaper.py` exports `reap_stale_locks()`
- [ ] `main.py`'s lifespan calls `reap_stale_locks()` after `backfill_maid_index_if_needed()`
- [ ] Fresh startup (locks table has held=0): log shows `No stale locks found.`; nothing reaped
- [ ] After manually `UPDATE locks SET held=1, held_by_pid=99999, run_id='test_run', held_by_operator='op-x', phase='staged'` then restart: log shows `Reaping stale lock`; audit_log row appears with action_type=lock_released and details containing `"reason": "reaper"`
- [ ] If the run folder for the orphaned run exists, after reaping it contains a `failure.json` with `stage='staged'` and an operator-facing error message
- [ ] If the run folder does not exist, the reap completes without raising; the lock is still cleared
- [ ] Reaper is idempotent across restarts — after one reap, the second restart finds nothing to reap

### Notes

The reaper only runs at startup, not continuously. The PID liveness check on per-request `get_lock_state()` (T-C2) handles steady-state stale detection without needing a periodic timer. The startup reap is specifically about cleaning up audit-trail integrity and writing failure.json sentinels so the UI accurately reflects the orphaned state — which the per-request liveness check alone doesn't do (it returns held=False to the query but doesn't persist that fact).

Inline lock-stealing in T-C2's `acquire_lock` also handles the "PID died between two requests" scenario without needing the reaper. The startup reap is the comprehensive cleanup; the inline steal is the fast-path optimization. Both write audit entries.

The error_message in the orphaned run's failure.json — "The previous run was interrupted" — is intentionally generic. The operator probably knows what happened (Ctrl+C, host reboot); a more specific message would require knowing why uvicorn stopped, which we don't.

The reaper does NOT delete the orphaned run folder. Per D-046's "no in-place retry" model, the failed folder stays as the historical record. Operator can choose to re-run from scratch (creates a new folder) or leave the failed run as-is.

If the production team's eventual ECS deployment uses multiple uvicorn workers, the reaper runs once per worker startup. Multiple concurrent reaper runs on the same locks row are serialized by the IMMEDIATE transaction; the second to arrive sees held=0 and returns None. Safe.
# Section D — Adapter layer

This section implements the two adapter interfaces (`StorageClient`, `PipelineRunner`) and their real + mock implementations per Rule 7 (mocks first-class). The mock adapters are the DEFAULT (`ADAPTER_PROFILE=mock`); flipping to real requires only `.env` changes, no code change. Section E endpoints consume the adapters via FastAPI dependency injection wired in T-D6.

Three integration seams with the partner's pipeline live here:
1. `LocalStorageClient` reads pipeline output files from `OUTPUT_BASE_FOLDER`.
2. `SubprocessPipelineRunner` spawns the pipeline subprocess calling `run_unified_pipeline(skip_jira=True)` and `submit_to_jira(folder)`.
3. Fixture data in `MockStorageClient` mirrors the pipeline's output schema closely enough to exercise every UI rendering path.

Section index:

- [ ] T-D1 — Adapter interfaces + shared data models
- [ ] T-D2 — `LocalStorageClient` (real filesystem adapter)
- [ ] T-D3 — `MockStorageClient` + fixture files
- [ ] T-D4 — `SubprocessPipelineRunner` (real pipeline adapter)
- [ ] T-D5 — `MockPipelineRunner` + synthetic event sequence
- [ ] T-D6 — Adapter factory + FastAPI dependency wiring

---

## T-D1 — Adapter interfaces + shared data models

**Depends on:** T1, T4
**Touches files:** `/api/adapters/interfaces.py`, `/api/adapters/models.py`
**Estimated effort:** small

### Goal

Define abstract base classes for `StorageClient` and `PipelineRunner`, plus the shared Pydantic models that cross the adapter boundary into Section E's endpoints. These ABCs are the contract: real and mock implementations both conform to the same method signatures. The data models ensure type-safe serialization from adapter → endpoint → frontend.

### Context

From D-061 (API contract, Phase 3):

> 16 endpoints across three router groups. All data-read endpoints consume a `StorageClient` that abstracts the filesystem. All action endpoints consume a `PipelineRunner` that abstracts the subprocess invocation.

From D-066 (Configuration management):

> `ADAPTER_PROFILE` controls which implementations are active globally. `mock` is the default; `real` requires `PIPELINE_MODULE_PATH`.

From D-073 (Jira URL construction):

> Backend constructs full URLs server-side. `GET /api/runs/{run_id}/jira-info` returns `{epic_key, epic_url, story_key, story_url, sharepoint_path}`.

### Implementation

**File: `/api/adapters/models.py`**:

```python
"""
Shared data models for the adapter layer.

These Pydantic models cross the adapter → endpoint boundary. Section E's
response schemas reference these directly (or wrap them). Using Pydantic
v2 models ensures JSON serialization, type validation, and OpenAPI schema
generation are handled consistently.
"""

from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class RunFolderSummary(BaseModel):
    """Summary of a single run folder for the Runs List screen.

    Populated by StorageClient.list_run_folders(). The `state` field is
    NOT set by the adapter — it's injected by the endpoint after calling
    infer_state() per D-045. The adapter sets everything else from the
    folder's filesystem metadata + name parsing.
    """

    run_id: str = Field(description="Folder name = run identity per D-045")
    folder_path: str = Field(description="Absolute path to the run folder")
    merchant: str = Field(description="Merchant name extracted from folder name pattern merchant_YYYYMMDD_HHMMSS")
    created_at: str = Field(description="ISO 8601 UTC timestamp; parsed from folder name or fallback to OS ctime")
    state: str | None = Field(default=None, description="RunState value; injected by endpoint, not adapter")
    has_base_table: bool = Field(default=False, description="True if comparison/mod_file_entries.json exists")
    issue_count: int | None = Field(default=None, description="Number of issues; injected by endpoint from events table")


class InputFolderInfo(BaseModel):
    """An input folder available for a new run.

    Listed by GET /api/input-folders. Each entry represents a directory
    under one of the ALLOWED_INPUT_ROOTS that the operator can select
    as input for a staged run.
    """

    path: str = Field(description="Absolute path to the input folder")
    name: str = Field(description="Folder display name (basename)")
    root: str = Field(description="Which ALLOWED_INPUT_ROOT this folder lives under")
    has_old: bool = Field(default=False, description="True if an 'old' subdirectory exists")
    has_new: bool = Field(default=False, description="True if a 'new' subdirectory exists")


class JiraInfo(BaseModel):
    """Jira + SharePoint metadata for a submitted run.

    Populated by StorageClient.read_jira_info() from the pipeline's
    jira_submission_complete.json. The URLs are constructed server-side
    per D-073 using JPMC_JIRA_BASE_URL.
    """

    epic_key: str | None = None
    epic_url: str | None = None
    story_key: str | None = None
    story_url: str | None = None
    sharepoint_path: str | None = None


class BaseTableRow(BaseModel):
    """A single row from the Results base table.

    Populated from comparison/mod_file_entries.json. Field names match
    the pipeline's output schema. The frontend renders these in the
    18-column base table per the visual mockup.

    This is a permissive model (extra fields allowed) because the
    pipeline may add fields between releases; the UI renders the known
    columns and ignores extras.
    """

    model_config = {"extra": "allow"}

    match_tag: str = Field(description="Unique identifier for this comparison pair")
    maid: str | None = None
    mnemonic: str | None = None
    action: str | None = Field(default=None, description="Add | Remove | Rate Update | MCC Expansion")
    change_type: str | None = Field(default=None, description="pricing_change | mnemonic_change | no_change")
    system_update: str | None = Field(default=None, description="peoplesoft | etl | both | none")
    # Additional fields from the pipeline's 34-field schema are captured
    # by extra="allow" and forwarded to the frontend as-is.


class DrawerRecord(BaseModel):
    """Detailed comparison record for the drawer panel.

    Populated from comparison/comparison_results.json, filtered by match_tag.
    Contains old vs new field values, correlated_fields mapping, and
    ETL impact entries.
    """

    model_config = {"extra": "allow"}

    match_tag: str
    old_record: dict[str, Any] | None = None
    new_record: dict[str, Any] | None = None
    change_type: str | None = None
    correlated_fields: dict[str, Any] | None = Field(
        default=None,
        description="Field correlation mapping per D-057 correction (was incorrectly 'unrelated_fields')"
    )
    etl_entries: list[dict[str, Any]] | None = None
    mod_file_entry: dict[str, Any] | None = None
```

**File: `/api/adapters/interfaces.py`**:

```python
"""
Adapter abstract base classes.

StorageClient reads from the pipeline's output filesystem.
PipelineRunner spawns (or simulates) pipeline invocations.

Both have real + mock implementations (Sections T-D2/T-D3, T-D4/T-D5).
The factory in T-D6 selects which implementation to inject based on
ADAPTER_PROFILE.
"""

from abc import ABC, abstractmethod
from pathlib import Path

from api.adapters.models import (
    BaseTableRow,
    DrawerRecord,
    InputFolderInfo,
    JiraInfo,
    RunFolderSummary,
)


class StorageClient(ABC):
    """Reads pipeline output artifacts from the filesystem (or fixtures).

    Every method returns data models or None — never raises on missing data.
    The endpoint layer (Section E) maps None to appropriate HTTP responses
    (404 for single-record, empty list for collections).
    """

    @abstractmethod
    def list_run_folders(self) -> list[RunFolderSummary]:
        """List all run folders under OUTPUT_BASE_FOLDER.

        Returns newest-first by convention (sorted by created_at descending).
        State is NOT populated — the endpoint injects it via infer_state().
        """
        ...

    @abstractmethod
    def get_run_folder(self, run_id: str) -> RunFolderSummary | None:
        """Get metadata for a single run folder. None if not found."""
        ...

    @abstractmethod
    def read_base_table(self, run_id: str) -> list[BaseTableRow]:
        """Read the base table (mod_file_entries.json) for a run.

        Returns an empty list if the file doesn't exist (run hasn't reached
        pre-approval yet).
        """
        ...

    @abstractmethod
    def read_drawer_record(self, run_id: str, match_tag: str) -> DrawerRecord | None:
        """Read a single comparison record for the drawer panel.

        Filters comparison_results.json by match_tag. None if not found.
        """
        ...

    @abstractmethod
    def read_raw_extract(self, run_id: str, match_tag: str) -> dict | None:
        """Read the raw extraction data for a specific match_tag.

        Used by the Artifact Preview's raw-extract sub-pane. Returns a
        dict with the step 1/2 extraction fields, or None if not available.
        """
        ...

    @abstractmethod
    def get_pdf_path(self, run_id: str) -> Path | None:
        """Return the absolute path to the agreement PDF for a run.

        Used by GET /api/runs/{run_id}/pdf to serve the file. None if
        no PDF is available (the run's input folder may not have been
        preserved, or the PDF conversion step failed).
        """
        ...

    @abstractmethod
    def read_jira_info(self, run_id: str) -> JiraInfo | None:
        """Read Jira + SharePoint metadata for a submitted run.

        Reads from jira_submission_complete.json in the run folder.
        Returns None if the file doesn't exist (run not yet submitted).
        URLs are constructed server-side per D-073.
        """
        ...

    @abstractmethod
    def list_input_folders(self) -> list[InputFolderInfo]:
        """List available input folders from ALLOWED_INPUT_ROOTS.

        Scans each root for subdirectories that look like agreement input
        folders (contain old/ and/or new/ subdirectories). Returns them
        for the operator's folder-selection UI in the new-run flow.
        """
        ...


class PipelineRunner(ABC):
    """Spawns (or simulates) pipeline invocations.

    Both methods are async because real invocations involve subprocess
    I/O streaming. Lock acquire/release is handled INSIDE the runner
    (not by the endpoint) because the lock lifecycle is tightly coupled
    to the subprocess lifecycle.

    Event persistence (record_event) and SSE broadcast happen inside
    the runner. The endpoint's job is just to call the runner and return
    a 202 Accepted.
    """

    @abstractmethod
    async def run_staged(
        self,
        run_id: str,
        input_folder: str,
        operator_id: str,
    ) -> None:
        """Start a staged pipeline run (run_unified_pipeline with skip_jira=True).

        The method acquires the lock, spawns the subprocess, streams events,
        and releases the lock on exit. On failure, writes failure.json.
        On success, populates the MAID index.

        Callers should NOT await this directly in the request handler — it
        runs as a background task so the POST endpoint can return 202
        immediately.
        """
        ...

    @abstractmethod
    async def run_approval(
        self,
        run_id: str,
        operator_id: str,
    ) -> None:
        """Start an approval run (submit_to_jira).

        Same lifecycle as run_staged: lock → subprocess → events → release.
        On failure, writes failure.json with stage='approval'.
        """
        ...
```

### Acceptance criteria

- [ ] `/api/adapters/models.py` exports `RunFolderSummary`, `InputFolderInfo`, `JiraInfo`, `BaseTableRow`, `DrawerRecord`
- [ ] `/api/adapters/interfaces.py` exports `StorageClient` (ABC) and `PipelineRunner` (ABC)
- [ ] `StorageClient` has 8 abstract methods matching the interface above
- [ ] `PipelineRunner` has 2 abstract methods (`run_staged`, `run_approval`), both `async`
- [ ] `BaseTableRow` and `DrawerRecord` use `model_config = {"extra": "allow"}` so unknown pipeline fields pass through
- [ ] `DrawerRecord.correlated_fields` uses the CORRECT field name per the Phase 1 correction (NOT `unrelated_fields`)
- [ ] All models are importable and JSON-serializable via `.model_dump()` / `.model_dump_json()`

### Notes

The `RunFolderSummary.state` field is intentionally set to `None` by the adapter — the endpoint layer injects the state via `infer_state()` after the adapter returns the folder list. This decouples the filesystem-reading concern (adapter) from the state-derivation concern (state module in Section C). Same for `issue_count` — injected from the events table.

`BaseTableRow` and `DrawerRecord` use `extra="allow"` because the pipeline's output schema has more fields than the UI needs to know about by name. The UI's base table renders ~18 named columns; any additional fields in the JSON pass through to the frontend as extra props, future-proofing against pipeline schema additions.

The `correlated_fields` naming follows the Phase 1 critical correction (was `unrelated_fields` in OCR-damaged spec — opposite meaning, high impact). Every reference to this field must use `correlated_fields`.

---

## T-D2 — `LocalStorageClient` (real filesystem adapter)

**Depends on:** T-D1, T4, T-C1
**Touches files:** `/api/adapters/local_storage.py`
**Estimated effort:** medium

### Goal

Implement the real filesystem adapter that reads pipeline outputs from `OUTPUT_BASE_FOLDER`. Each method maps to a specific file path convention documented in `ui-approach.md` §3. Defensive throughout — missing files return None/empty rather than raising.

### Context

From `ui-approach.md` §3 (output anatomy):

> ```
> output/<merchant>_<timestamp>/
>   comparison/
>     mod_file_entries.json     — per-record base table data
>     comparison_results.json   — per-match comparison + correlated fields
>   raw_extracts/               — step 1/2 extraction outputs per record
>   input/                      — copy of original agreement PDFs
>   jira_submission_complete.json — written on successful Jira submission
>   failure.json                — written by UI on pipeline failure
> ```

From D-073 (Jira URL construction):

> Backend constructs full URLs: `{JPMC_JIRA_BASE_URL}/browse/{epic_key}`.

### Implementation

**File: `/api/adapters/local_storage.py`**:

```python
"""
LocalStorageClient — reads pipeline outputs from the real filesystem.

Used when ADAPTER_PROFILE=real. Every method is purely read-only;
writes to the filesystem happen via PipelineRunner (subprocess output)
or the failure/lock modules in Section C.

File-path conventions follow ui-approach.md §3. If the partner's pipeline
ever changes the output structure, update the path constants at the top
of this file.
"""

import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from api.adapters.interfaces import StorageClient
from api.adapters.models import (
    BaseTableRow,
    DrawerRecord,
    InputFolderInfo,
    JiraInfo,
    RunFolderSummary,
)
from api.config import settings

logger = logging.getLogger(__name__)

# --- File path conventions (relative to run folder root) ---
_COMPARISON_DIR = "comparison"
_MOD_FILE = Path(_COMPARISON_DIR) / "mod_file_entries.json"
_COMPARISON_RESULTS = Path(_COMPARISON_DIR) / "comparison_results.json"
_RAW_EXTRACTS_DIR = "raw_extracts"
_INPUT_DIR = "input"
_JIRA_COMPLETE = "jira_submission_complete.json"

# Folder name pattern: merchant_YYYYMMDD_HHMMSS
_FOLDER_NAME_RE = re.compile(r"^(.+?)_(\d{8}_\d{6})$")


def _parse_folder_name(name: str) -> tuple[str, str]:
    """Extract merchant and timestamp from folder name.

    Returns (merchant, iso_timestamp). If the name doesn't match the
    expected pattern, merchant = full name, timestamp = folder OS ctime.
    """
    m = _FOLDER_NAME_RE.match(name)
    if m:
        merchant = m.group(1)
        ts_str = m.group(2)
        try:
            dt = datetime.strptime(ts_str, "%Y%m%d_%H%M%S").replace(tzinfo=timezone.utc)
            return merchant, dt.isoformat()
        except ValueError:
            pass
    return name, ""


def _safe_read_json(path: Path) -> Any | None:
    """Read and parse a JSON file. Returns None on any error."""
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        logger.warning("Could not read %s: %s", path, exc)
        return None


class LocalStorageClient(StorageClient):
    """Real filesystem adapter for pipeline outputs."""

    def __init__(self) -> None:
        self._output_base = settings.output_base_folder_path
        self._input_roots = settings.allowed_input_roots_list
        self._jira_base_url = settings.jpmc_jira_base_url.rstrip("/")

    def list_run_folders(self) -> list[RunFolderSummary]:
        if not self._output_base.exists():
            return []

        folders: list[RunFolderSummary] = []
        for entry in self._output_base.iterdir():
            if not entry.is_dir():
                continue
            merchant, created_at = _parse_folder_name(entry.name)
            if not created_at:
                # Fallback to OS creation time.
                try:
                    stat = entry.stat()
                    created_at = datetime.fromtimestamp(
                        stat.st_ctime, tz=timezone.utc
                    ).isoformat()
                except OSError:
                    created_at = datetime.now(timezone.utc).isoformat()

            has_bt = (entry / _MOD_FILE).exists()
            folders.append(RunFolderSummary(
                run_id=entry.name,
                folder_path=str(entry),
                merchant=merchant,
                created_at=created_at,
                has_base_table=has_bt,
            ))

        # Newest first.
        folders.sort(key=lambda f: f.created_at, reverse=True)
        return folders

    def get_run_folder(self, run_id: str) -> RunFolderSummary | None:
        folder = self._output_base / run_id
        if not folder.is_dir():
            return None
        merchant, created_at = _parse_folder_name(run_id)
        if not created_at:
            try:
                created_at = datetime.fromtimestamp(
                    folder.stat().st_ctime, tz=timezone.utc
                ).isoformat()
            except OSError:
                created_at = datetime.now(timezone.utc).isoformat()
        return RunFolderSummary(
            run_id=run_id,
            folder_path=str(folder),
            merchant=merchant,
            created_at=created_at,
            has_base_table=(folder / _MOD_FILE).exists(),
        )

    def read_base_table(self, run_id: str) -> list[BaseTableRow]:
        data = _safe_read_json(self._output_base / run_id / _MOD_FILE)
        if not isinstance(data, list):
            return []
        rows: list[BaseTableRow] = []
        for entry in data:
            if isinstance(entry, dict):
                try:
                    rows.append(BaseTableRow(**entry))
                except Exception as exc:
                    logger.warning("Skipping malformed base-table row: %s", exc)
        return rows

    def read_drawer_record(self, run_id: str, match_tag: str) -> DrawerRecord | None:
        data = _safe_read_json(
            self._output_base / run_id / _COMPARISON_RESULTS
        )
        if not isinstance(data, list):
            return None
        for record in data:
            if isinstance(record, dict) and record.get("match_tag") == match_tag:
                try:
                    return DrawerRecord(**record)
                except Exception as exc:
                    logger.warning("Malformed drawer record for match_tag=%s: %s", match_tag, exc)
                    return None
        return None

    def read_raw_extract(self, run_id: str, match_tag: str) -> dict | None:
        extract_dir = self._output_base / run_id / _RAW_EXTRACTS_DIR
        if not extract_dir.is_dir():
            return None
        # Convention: raw extract files named by match_tag.
        extract_file = extract_dir / f"{match_tag}.json"
        return _safe_read_json(extract_file)

    def get_pdf_path(self, run_id: str) -> Path | None:
        input_dir = self._output_base / run_id / _INPUT_DIR
        if not input_dir.is_dir():
            return None
        # Find the first PDF in the input directory.
        for f in input_dir.iterdir():
            if f.suffix.lower() == ".pdf" and f.is_file():
                return f
        return None

    def read_jira_info(self, run_id: str) -> JiraInfo | None:
        data = _safe_read_json(self._output_base / run_id / _JIRA_COMPLETE)
        if not isinstance(data, dict):
            return None

        epic_key = data.get("epic_key")
        story_key = data.get("story_key")

        return JiraInfo(
            epic_key=epic_key,
            epic_url=f"{self._jira_base_url}/browse/{epic_key}" if epic_key else None,
            story_key=story_key,
            story_url=f"{self._jira_base_url}/browse/{story_key}" if story_key else None,
            sharepoint_path=data.get("sharepoint_path"),
        )

    def list_input_folders(self) -> list[InputFolderInfo]:
        result: list[InputFolderInfo] = []
        for root in self._input_roots:
            if not root.is_dir():
                logger.debug("ALLOWED_INPUT_ROOT %s is not a directory; skipping.", root)
                continue
            for entry in root.iterdir():
                if not entry.is_dir():
                    continue
                result.append(InputFolderInfo(
                    path=str(entry),
                    name=entry.name,
                    root=str(root),
                    has_old=(entry / "old").is_dir(),
                    has_new=(entry / "new").is_dir(),
                ))
        result.sort(key=lambda f: f.name)
        return result
```

### Acceptance criteria

- [ ] `/api/adapters/local_storage.py` exports `LocalStorageClient` implementing all 8 `StorageClient` methods
- [ ] With a run folder `output/intuit_20260511_155829/` containing `comparison/mod_file_entries.json`, `list_run_folders()` returns a list including that folder with `merchant='intuit'`, `created_at` parsed from the folder name, `has_base_table=True`
- [ ] `read_base_table("intuit_20260511_155829")` returns a list of `BaseTableRow` instances from the JSON
- [ ] `read_drawer_record("intuit_20260511_155829", "some_tag")` returns a `DrawerRecord` when that match_tag exists in comparison_results.json, or `None` when it doesn't
- [ ] `read_jira_info` constructs URLs using `JPMC_JIRA_BASE_URL` — e.g., epic_url = `https://jira.jpmchase.net/browse/CMRPEE-123`
- [ ] `list_input_folders` scans each `ALLOWED_INPUT_ROOT` and returns `InputFolderInfo` with `has_old`/`has_new` flags
- [ ] Missing files return `None` or empty lists — no exceptions propagate to callers

### Notes

The `_FOLDER_NAME_RE` pattern (`merchant_YYYYMMDD_HHMMSS`) matches the observed naming in Phase 1 fixtures. If the partner uses a different convention (e.g., underscores within the merchant name like `visa_inc_20260511_155829`), the regex captures everything up to the last `_YYYYMMDD_HHMMSS` suffix. The greedy `(.+?)_(\d{8}_\d{6})$` pattern handles this correctly.

The `read_raw_extract` method assumes raw extract files are named `{match_tag}.json` under `raw_extracts/`. This convention is V's best understanding; verify against the partner's actual output when integrating Section D on VDI.

`get_pdf_path` returns the first `.pdf` found in the `input/` subdirectory. If multiple PDFs exist (e.g., old and new agreements), the Artifact Preview screen (Section I) may need a more nuanced selection. For MVP, the first-found behavior is documented and acceptable.

---

## T-D3 — `MockStorageClient` + fixture files

**Depends on:** T-D1
**Touches files:** `/api/adapters/mock_storage.py`, `/api/adapters/fixtures/` (directory + fixture files)
**Estimated effort:** medium

### Goal

Implement the mock filesystem adapter per Rule 7 (mocks first-class). Returns deterministic fixture data from bundled JSON files. The fixtures exercise every rendering path in the UI: multiple run folders with different states (pre_approval, submitted, failed), a variety of action types (Add, Remove, Rate Update, MCC Expansion), mixed change_types, and realistic field values for drawer and base table rendering.

### Context

From D-026 (Phase 1 fixture preservation):

> Phase 1 fixture folders (`intuit_20260511_155829`, `intuit_20260511_160142`) are preserved as the canonical reference for output structure. Mock fixtures should mirror this structure closely.

From Rule 7 (Project Rulebook):

> Mocks and stubs are first-class deliverables. The mock adapter is the DEFAULT development surface and must exercise every UI code path, not just the happy path.

### Implementation

**Step 1 — Create fixture directory and fixture files.**

```
api/adapters/fixtures/
├── runs.json                 — list of mock run folders
├── mod_file_entries.json     — base table fixture (shared across mock runs)
├── comparison_results.json   — drawer fixture
├── raw_extract_sample.json   — raw extract fixture
├── jira_info.json            — Jira submission fixture
└── input_folders.json        — input folder listing fixture
```

**File: `/api/adapters/fixtures/runs.json`** — three mock runs at different states:

```json
[
  {
    "run_id": "intuit_20260511_155829",
    "merchant": "intuit",
    "created_at": "2026-05-11T15:58:29Z",
    "has_base_table": true,
    "mock_state": "pre_approval"
  },
  {
    "run_id": "visa_20260510_093012",
    "merchant": "visa",
    "created_at": "2026-05-10T09:30:12Z",
    "has_base_table": true,
    "mock_state": "submitted"
  },
  {
    "run_id": "amex_20260509_140000",
    "merchant": "amex",
    "created_at": "2026-05-09T14:00:00Z",
    "has_base_table": true,
    "mock_state": "failed"
  }
]
```

**File: `/api/adapters/fixtures/mod_file_entries.json`** — 8 representative rows covering all action types:

```json
[
  {
    "match_tag": "MT001",
    "maid": "411424",
    "mnemonic": "US CPS RETAIL",
    "action": "Add",
    "change_type": "mnemonic_change",
    "system_update": "both",
    "interchange_rate_percent": "1.65",
    "interchange_rate_per_item": "0.10",
    "product_type": "Credit",
    "channel": "Card Present",
    "regulation_status": "Non-Regulated",
    "mcc_group": "General Retail"
  },
  {
    "match_tag": "MT002",
    "maid": "411424",
    "mnemonic": "US CPS E-COMMERCE",
    "action": "Add",
    "change_type": "pricing_change",
    "system_update": "etl",
    "interchange_rate_percent": "1.80",
    "interchange_rate_per_item": "0.10",
    "product_type": "Credit",
    "channel": "Card Not Present",
    "regulation_status": "Non-Regulated",
    "mcc_group": "General Retail"
  },
  {
    "match_tag": "MT003",
    "maid": "523891",
    "mnemonic": "US MERIT III",
    "action": "Remove",
    "change_type": "mnemonic_change",
    "system_update": "both",
    "interchange_rate_percent": "1.58",
    "interchange_rate_per_item": "0.10",
    "product_type": "Debit",
    "channel": "Card Present",
    "regulation_status": "Regulated",
    "mcc_group": "Supermarkets"
  },
  {
    "match_tag": "MT004",
    "maid": "411424",
    "mnemonic": "US CPS SUPERMARKET",
    "action": "Rate Update",
    "change_type": "pricing_change",
    "system_update": "peoplesoft",
    "interchange_rate_percent": "1.48",
    "interchange_rate_per_item": "0.05",
    "product_type": "Credit",
    "channel": "Card Present",
    "regulation_status": "Non-Regulated",
    "mcc_group": "Supermarkets"
  },
  {
    "match_tag": "MT005",
    "maid": "523891",
    "mnemonic": "US MERIT III",
    "action": "MCC Expansion",
    "change_type": "no_change",
    "system_update": "etl",
    "interchange_rate_percent": "1.58",
    "interchange_rate_per_item": "0.10",
    "product_type": "Debit",
    "channel": "Card Present",
    "regulation_status": "Regulated",
    "mcc_group": "Restaurants"
  },
  {
    "match_tag": "MT006",
    "maid": "667234",
    "mnemonic": "US STANDARD",
    "action": "Add",
    "change_type": "mnemonic_change",
    "system_update": "none",
    "interchange_rate_percent": "2.10",
    "interchange_rate_per_item": "0.10",
    "product_type": "Credit",
    "channel": "Card Not Present",
    "regulation_status": "Non-Regulated",
    "mcc_group": "General Merchandise"
  },
  {
    "match_tag": "MT007",
    "maid": "411424",
    "mnemonic": "US CPS RETAIL",
    "action": "Remove",
    "change_type": "pricing_change",
    "system_update": "both",
    "interchange_rate_percent": "1.65",
    "interchange_rate_per_item": "0.10",
    "product_type": "Credit",
    "channel": "Card Present",
    "regulation_status": "Non-Regulated",
    "mcc_group": "General Retail"
  },
  {
    "match_tag": "MT008",
    "maid": "523891",
    "mnemonic": "US MERIT III",
    "action": "Rate Update",
    "change_type": "pricing_change",
    "system_update": "etl",
    "interchange_rate_percent": "1.60",
    "interchange_rate_per_item": "0.10",
    "product_type": "Debit",
    "channel": "Card Present",
    "regulation_status": "Regulated",
    "mcc_group": "Supermarkets"
  }
]
```

**File: `/api/adapters/fixtures/comparison_results.json`** — drawer-level detail for MT001 and MT004 (representative subset):

```json
[
  {
    "match_tag": "MT001",
    "old_record": null,
    "new_record": {
      "mnemonic": "US CPS RETAIL",
      "interchange_rate_percent": "1.65",
      "interchange_rate_per_item": "0.10",
      "product_type": "Credit",
      "channel": "Card Present"
    },
    "change_type": "mnemonic_change",
    "correlated_fields": {},
    "etl_entries": [
      {"entry_type": "ADD", "mnemonic": "US CPS RETAIL", "rate": "1.65 + 0.10"}
    ],
    "mod_file_entry": {
      "action": "Add",
      "maid": "411424",
      "mnemonic": "US CPS RETAIL"
    }
  },
  {
    "match_tag": "MT004",
    "old_record": {
      "mnemonic": "US CPS SUPERMARKET",
      "interchange_rate_percent": "1.54",
      "interchange_rate_per_item": "0.05"
    },
    "new_record": {
      "mnemonic": "US CPS SUPERMARKET",
      "interchange_rate_percent": "1.48",
      "interchange_rate_per_item": "0.05"
    },
    "change_type": "pricing_change",
    "correlated_fields": {
      "interchange_rate_percent": {"old": "1.54", "new": "1.48"}
    },
    "etl_entries": [
      {"entry_type": "REMOVE", "mnemonic": "US CPS SUPERMARKET", "rate": "1.54 + 0.05"},
      {"entry_type": "ADD", "mnemonic": "US CPS SUPERMARKET", "rate": "1.48 + 0.05"}
    ],
    "mod_file_entry": {
      "action": "Rate Update",
      "maid": "411424",
      "mnemonic": "US CPS SUPERMARKET"
    }
  }
]
```

**File: `/api/adapters/fixtures/jira_info.json`**:

```json
{
  "epic_key": "CMRPEE-142",
  "story_key": "CMRPEE-143",
  "sharepoint_path": "\\\\sharepoint\\CustomInterchange\\visa\\2026-05"
}
```

**File: `/api/adapters/fixtures/input_folders.json`**:

```json
[
  {
    "path": "/mock/input/intuit_q2_2026",
    "name": "intuit_q2_2026",
    "root": "/mock/input",
    "has_old": true,
    "has_new": true
  },
  {
    "path": "/mock/input/visa_annual_2026",
    "name": "visa_annual_2026",
    "root": "/mock/input",
    "has_old": true,
    "has_new": true
  },
  {
    "path": "/mock/input/amex_partial",
    "name": "amex_partial",
    "root": "/mock/input",
    "has_old": true,
    "has_new": false
  }
]
```

**File: `/api/adapters/fixtures/raw_extract_sample.json`**:

```json
{
  "match_tag": "MT001",
  "step1_vision_output": {
    "raw_text_blocks": [
      "Visa Core Value — Credit — US CPS Retail",
      "Rate: 1.65% + $0.10 per item",
      "Card Present — Non-Regulated"
    ],
    "confidence": 0.94
  },
  "step2_field_mapping": {
    "mnemonic": "US CPS RETAIL",
    "interchange_rate_percent": "1.65",
    "interchange_rate_per_item": "0.10",
    "product_type": "Credit",
    "channel": "Card Present",
    "regulation_status": "Non-Regulated"
  }
}
```

**File: `/api/adapters/mock_storage.py`**:

```python
"""
MockStorageClient — fixture-backed adapter per Rule 7.

Used when ADAPTER_PROFILE=mock (the default). Returns deterministic data
from bundled JSON fixture files. Exercises every UI rendering path:
multiple states, all four action types, mixed change_types and
system_update values.

Fixture files live in /api/adapters/fixtures/ and are loaded once at
construction time.
"""

import json
import logging
from pathlib import Path

from api.adapters.interfaces import StorageClient
from api.adapters.models import (
    BaseTableRow,
    DrawerRecord,
    InputFolderInfo,
    JiraInfo,
    RunFolderSummary,
)
from api.config import settings

logger = logging.getLogger(__name__)

_FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _load_fixture(filename: str):
    """Load a JSON fixture file from the fixtures directory."""
    path = _FIXTURES_DIR / filename
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


class MockStorageClient(StorageClient):
    """Fixture-backed storage adapter."""

    def __init__(self) -> None:
        self._runs = _load_fixture("runs.json")
        self._base_table = _load_fixture("mod_file_entries.json")
        self._comparison = _load_fixture("comparison_results.json")
        self._raw_extract = _load_fixture("raw_extract_sample.json")
        self._jira = _load_fixture("jira_info.json")
        self._inputs = _load_fixture("input_folders.json")
        self._jira_base_url = settings.jpmc_jira_base_url.rstrip("/")

    def list_run_folders(self) -> list[RunFolderSummary]:
        return [
            RunFolderSummary(
                run_id=r["run_id"],
                folder_path=f"/mock/output/{r['run_id']}",
                merchant=r["merchant"],
                created_at=r["created_at"],
                has_base_table=r.get("has_base_table", True),
            )
            for r in self._runs
        ]

    def get_run_folder(self, run_id: str) -> RunFolderSummary | None:
        for r in self._runs:
            if r["run_id"] == run_id:
                return RunFolderSummary(
                    run_id=r["run_id"],
                    folder_path=f"/mock/output/{r['run_id']}",
                    merchant=r["merchant"],
                    created_at=r["created_at"],
                    has_base_table=r.get("has_base_table", True),
                )
        return None

    def read_base_table(self, run_id: str) -> list[BaseTableRow]:
        # All mock runs share the same base table fixture.
        if not any(r["run_id"] == run_id for r in self._runs):
            return []
        return [BaseTableRow(**row) for row in self._base_table]

    def read_drawer_record(self, run_id: str, match_tag: str) -> DrawerRecord | None:
        for record in self._comparison:
            if record.get("match_tag") == match_tag:
                return DrawerRecord(**record)
        return None

    def read_raw_extract(self, run_id: str, match_tag: str) -> dict | None:
        # Return the sample extract for any match_tag; enrich with the
        # requested match_tag for realism.
        sample = dict(self._raw_extract)
        sample["match_tag"] = match_tag
        return sample

    def get_pdf_path(self, run_id: str) -> Path | None:
        # No real PDF in mock mode. Section E returns 404; Section I
        # handles the "no PDF available" state gracefully.
        return None

    def read_jira_info(self, run_id: str) -> JiraInfo | None:
        # Only the "submitted" mock run has Jira info.
        for r in self._runs:
            if r["run_id"] == run_id and r.get("mock_state") == "submitted":
                epic_key = self._jira.get("epic_key")
                story_key = self._jira.get("story_key")
                return JiraInfo(
                    epic_key=epic_key,
                    epic_url=f"{self._jira_base_url}/browse/{epic_key}" if epic_key else None,
                    story_key=story_key,
                    story_url=f"{self._jira_base_url}/browse/{story_key}" if story_key else None,
                    sharepoint_path=self._jira.get("sharepoint_path"),
                )
        return None

    def list_input_folders(self) -> list[InputFolderInfo]:
        return [InputFolderInfo(**item) for item in self._inputs]
```

### Acceptance criteria

- [ ] `/api/adapters/fixtures/` contains six JSON fixture files
- [ ] `/api/adapters/mock_storage.py` exports `MockStorageClient` implementing all 8 `StorageClient` methods
- [ ] `MockStorageClient().list_run_folders()` returns 3 runs (intuit pre_approval, visa submitted, amex failed)
- [ ] `read_base_table("intuit_20260511_155829")` returns 8 `BaseTableRow` instances with all four action types represented (Add, Remove, Rate Update, MCC Expansion)
- [ ] `read_drawer_record("intuit_20260511_155829", "MT001")` returns a `DrawerRecord` with non-null `etl_entries` and `mod_file_entry`
- [ ] `read_drawer_record("intuit_20260511_155829", "NONEXISTENT")` returns None
- [ ] `read_jira_info("visa_20260510_093012")` returns `JiraInfo` with constructed URLs; `read_jira_info("intuit_20260511_155829")` returns None
- [ ] `get_pdf_path` returns None for all mock runs (no real PDF in mock mode)
- [ ] Fixture files use `correlated_fields` (NOT `unrelated_fields`) everywhere

### Notes

The fixtures are intentionally compact (~8 base-table rows, 2 comparison records). They exercise the critical rendering paths (all four action types, both change_type values with content, one no_change, drawer with ETL entries) without creating large files that slow fixture loading.

V can replace these fixtures with real data extracted from the Phase 1 intuit folders once on VDI — the fixture file format matches the pipeline's output format exactly. The mock implementation just reads from `fixtures/` instead of `output/`.

The `mock_state` field in `runs.json` is consumed ONLY by MockStorageClient methods that need state-dependent behavior (e.g., `read_jira_info` only returns data for the "submitted" run). The `state` field on `RunFolderSummary` is still set by the endpoint via `infer_state()`, not by the mock — this preserves the endpoint-injects-state contract even in mock mode. For mock state inference to work correctly, the MockPipelineRunner (T-D5) should set up appropriate sentinel conditions (or the endpoint should short-circuit for mock mode).

---

## T-D4 — `SubprocessPipelineRunner` (real pipeline adapter)

**Depends on:** T-D1, T-C2, T-C3, T-C4, T-C5, T-B4
**Touches files:** `/api/adapters/subprocess_runner.py`
**Estimated effort:** large

### Goal

Implement the real pipeline adapter that spawns the partner's Python code as a subprocess, streams stdout line-by-line for event parsing, acquires and releases the global lock, writes `failure.json` on non-zero exit, and populates the MAID index on staged-run success. The subprocess invocation uses the inline-import pattern as the default (option b from the Phase 5 coordination question); a CLI wrapper flag is documented for option (a) if the partner provides one.

### Context

From `ui-approach.md` §9 (partner's subprocess pattern guidance):

> ```
> run_unified_pipeline(skip_jira=True)  — staged run
> submit_to_jira(output_folder)          — approval run
> ```
> The pipeline functions live in the CI_Vision codebase at `PIPELINE_MODULE_PATH`.

From the Phase 5 coordination question (default to option b):

> UI constructs `python -c "import sys; sys.path.insert(0, '<PIPELINE_MODULE_PATH>'); from CI_LLM.claude_agent_process.mpp_pipeline.CI_LLM_unified_pipeline import run_unified_pipeline; run_unified_pipeline(skip_jira=True, input_path='<input_folder>', output_path='<output_folder>')"`.

If partner provides option (a): `python pipeline_cli.py staged --input <folder> --output <folder>` — switch the command construction but keep everything else the same.

From D-057 (Run state machine):

> Lock acquire before subprocess start; lock release on subprocess exit (success or failure). PID recorded in the lock row for liveness checking.

### Implementation

**File: `/api/adapters/subprocess_runner.py`**:

```python
"""
SubprocessPipelineRunner — real pipeline adapter.

Spawns the partner's pipeline as a subprocess, streaming stdout for
event parsing. Lock lifecycle + failure sentinel + MAID index hook
all happen here.

The subprocess command construction uses the inline-import pattern
(option b from Phase 5 coordination). If the partner provides a CLI
wrapper (option a), update _build_staged_command / _build_approval_command
and leave everything else unchanged.

Event protocol: the pipeline subprocess should print JSON lines to stdout
in the format:
    {"type": "<EventType>", "payload": {...}}
Each line is parsed and forwarded to record_event() + broadcaster.
Non-JSON lines (raw pipeline logs) are logged as debug and ignored.
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from api.adapters.interfaces import PipelineRunner
from api.config import settings
from api.db.audit import AuditAction, write_audit
from api.db.maid_index import populate_maid_index
from api.state.events import EventType, record_event
from api.state.failure import write_failure_json
from api.state.locks import acquire_lock, release_lock
from api.state.sse import get_broadcaster

logger = logging.getLogger(__name__)


def _build_staged_command(input_folder: str, output_folder: str) -> list[str]:
    """Build the subprocess command for a staged run.

    Option (b) — inline import:
        python -c "import sys; sys.path.insert(0, '<path>'); ..."

    If the partner provides option (a) — CLI wrapper:
        python pipeline_cli.py staged --input <folder> --output <folder>
    Change only this function.
    """
    module_path = settings.pipeline_module_path or ""
    python = settings.python_interpreter

    inline_code = (
        f"import sys; "
        f"sys.path.insert(0, r'{module_path}'); "
        f"from CI_LLM.claude_agent_process.mpp_pipeline.CI_LLM_unified_pipeline "
        f"import run_unified_pipeline; "
        f"run_unified_pipeline("
        f"skip_jira=True, "
        f"input_path=r'{input_folder}', "
        f"output_path=r'{output_folder}')"
    )
    return [python, "-c", inline_code]


def _build_approval_command(output_folder: str) -> list[str]:
    """Build the subprocess command for an approval run."""
    module_path = settings.pipeline_module_path or ""
    python = settings.python_interpreter

    inline_code = (
        f"import sys; "
        f"sys.path.insert(0, r'{module_path}'); "
        f"from CI_LLM.claude_agent_process.mpp_pipeline.CI_LLM_unified_pipeline "
        f"import submit_to_jira; "
        f"submit_to_jira(r'{output_folder}')"
    )
    return [python, "-c", inline_code]


async def _stream_subprocess(
    cmd: list[str],
    run_id: str,
    phase: str,
    operator_id: str,
) -> int:
    """Spawn a subprocess and stream its stdout for event parsing.

    Returns the subprocess exit code.
    """
    broadcaster = get_broadcaster()

    logger.info("Spawning subprocess: %s", " ".join(cmd))
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    # Stream stdout line-by-line.
    stderr_lines: list[str] = []
    if proc.stdout:
        async for line_bytes in proc.stdout:
            line = line_bytes.decode("utf-8", errors="replace").strip()
            if not line:
                continue
            try:
                event_data = json.loads(line)
                event_type_str = event_data.get("type", "")
                payload = event_data.get("payload", {})

                # Validate event type against taxonomy.
                try:
                    event_type = EventType(event_type_str)
                except ValueError:
                    logger.warning(
                        "Unknown event type from subprocess: %s (run=%s)",
                        event_type_str, run_id,
                    )
                    continue

                # Persist event.
                event_id = record_event(
                    run_id=run_id,
                    event_type=event_type,
                    payload=payload,
                )

                # Broadcast to SSE subscribers.
                await broadcaster.broadcast(
                    run_id=run_id,
                    event_type=event_type.value,
                    payload=payload,
                    event_id=event_id,
                    ts=datetime.now(timezone.utc).isoformat(),
                )

            except json.JSONDecodeError:
                # Non-JSON line — raw pipeline log output. Debug-log it.
                logger.debug("Non-JSON stdout (run=%s): %s", run_id, line)

    # Collect stderr for failure context.
    if proc.stderr:
        stderr_data = await proc.stderr.read()
        stderr_text = stderr_data.decode("utf-8", errors="replace")
        if stderr_text.strip():
            stderr_lines = stderr_text.strip().splitlines()
            for sl in stderr_lines[-10:]:  # last 10 lines
                logger.warning("Subprocess stderr (run=%s): %s", run_id, sl)

    exit_code = await proc.wait()
    logger.info(
        "Subprocess exited: run=%s phase=%s exit_code=%d",
        run_id, phase, exit_code,
    )
    return exit_code


class SubprocessPipelineRunner(PipelineRunner):
    """Real pipeline adapter using subprocess invocation."""

    async def run_staged(
        self,
        run_id: str,
        input_folder: str,
        operator_id: str,
    ) -> None:
        output_folder = str(settings.output_base_folder_path / run_id)
        phase = "staged"

        # Audit the operator action.
        write_audit(
            operator_id=operator_id,
            action_type=AuditAction.RUN_STARTED,
            run_id=run_id,
            details={"input_folder": input_folder, "output_folder": output_folder},
        )

        # Acquire lock.
        acquired = acquire_lock(operator_id, run_id, phase)
        if not acquired:
            logger.error(
                "Could not acquire lock for staged run %s — another operation is in progress.",
                run_id,
            )
            # Record a run_failed event so the UI sees the failure.
            record_event(
                run_id=run_id,
                event_type=EventType.RUN_FAILED,
                payload={
                    "stage": phase,
                    "message": "Could not start — another operation is in progress.",
                    "exit_code": None,
                },
            )
            return

        try:
            # Emit run_started event.
            event_id = record_event(
                run_id=run_id,
                event_type=EventType.RUN_STARTED,
                payload={
                    "input_folder": input_folder,
                    "merchant": run_id.rsplit("_", 2)[0] if "_" in run_id else run_id,
                    "operator_id": operator_id,
                },
            )
            broadcaster = get_broadcaster()
            await broadcaster.broadcast(
                run_id=run_id,
                event_type=EventType.RUN_STARTED.value,
                payload={"input_folder": input_folder},
                event_id=event_id,
            )

            # Create output directory.
            Path(output_folder).mkdir(parents=True, exist_ok=True)

            # Spawn subprocess.
            cmd = _build_staged_command(input_folder, output_folder)
            exit_code = await _stream_subprocess(cmd, run_id, phase, operator_id)

            if exit_code != 0:
                write_failure_json(
                    folder_path=Path(output_folder),
                    stage=phase,
                    error_message=f"Pipeline exited with code {exit_code}.",
                    exit_code=exit_code,
                )
                record_event(
                    run_id=run_id,
                    event_type=EventType.RUN_FAILED,
                    payload={
                        "stage": phase,
                        "message": f"Pipeline exited with code {exit_code}.",
                        "exit_code": exit_code,
                    },
                )
            else:
                # Success: populate MAID index.
                populate_maid_index(run_id, Path(output_folder))

        except Exception as exc:
            logger.exception("Unexpected error in staged run %s", run_id)
            write_failure_json(
                folder_path=Path(output_folder),
                stage=phase,
                error_message="Unexpected error during staged run.",
                exc=exc,
            )
            record_event(
                run_id=run_id,
                event_type=EventType.RUN_FAILED,
                payload={"stage": phase, "message": str(exc), "exit_code": None},
            )
        finally:
            release_lock(operator_id, run_id, phase)

    async def run_approval(
        self,
        run_id: str,
        operator_id: str,
    ) -> None:
        output_folder = str(settings.output_base_folder_path / run_id)
        phase = "approval"

        write_audit(
            operator_id=operator_id,
            action_type=AuditAction.APPROVE_CLICKED,
            run_id=run_id,
        )

        acquired = acquire_lock(operator_id, run_id, phase)
        if not acquired:
            logger.error(
                "Could not acquire lock for approval run %s — another operation is in progress.",
                run_id,
            )
            record_event(
                run_id=run_id,
                event_type=EventType.RUN_FAILED,
                payload={
                    "stage": phase,
                    "message": "Could not start approval — another operation is in progress.",
                    "exit_code": None,
                },
            )
            return

        try:
            event_id = record_event(
                run_id=run_id,
                event_type=EventType.APPROVAL_SUBMITTED,
                payload={"target_systems": ["jira", "sharepoint"]},
            )
            broadcaster = get_broadcaster()
            await broadcaster.broadcast(
                run_id=run_id,
                event_type=EventType.APPROVAL_SUBMITTED.value,
                payload={"target_systems": ["jira", "sharepoint"]},
                event_id=event_id,
            )

            cmd = _build_approval_command(output_folder)
            exit_code = await _stream_subprocess(cmd, run_id, phase, operator_id)

            if exit_code != 0:
                write_failure_json(
                    folder_path=Path(output_folder),
                    stage=phase,
                    error_message=f"Approval pipeline exited with code {exit_code}.",
                    exit_code=exit_code,
                )
                record_event(
                    run_id=run_id,
                    event_type=EventType.RUN_FAILED,
                    payload={
                        "stage": phase,
                        "message": f"Approval exited with code {exit_code}.",
                        "exit_code": exit_code,
                    },
                )
            else:
                record_event(
                    run_id=run_id,
                    event_type=EventType.SUBMISSION_COMPLETE,
                    payload={},
                )

        except Exception as exc:
            logger.exception("Unexpected error in approval run %s", run_id)
            write_failure_json(
                folder_path=Path(output_folder),
                stage=phase,
                error_message="Unexpected error during approval.",
                exc=exc,
            )
            record_event(
                run_id=run_id,
                event_type=EventType.RUN_FAILED,
                payload={"stage": phase, "message": str(exc), "exit_code": None},
            )
        finally:
            release_lock(operator_id, run_id, phase)
```

### Acceptance criteria

- [ ] `/api/adapters/subprocess_runner.py` exports `SubprocessPipelineRunner` implementing `run_staged` and `run_approval`
- [ ] `_build_staged_command` produces a Python subprocess command that imports from `PIPELINE_MODULE_PATH`
- [ ] Lock is acquired BEFORE subprocess spawn and released in `finally` (even on exception)
- [ ] Non-zero exit code triggers both `failure.json` and a `run_failed` event
- [ ] Successful staged run calls `populate_maid_index(run_id, folder_path)` after subprocess exits 0
- [ ] Successful approval run records a `submission_complete` event
- [ ] `lock_acquire_fail` path records a `run_failed` event immediately (no subprocess spawned)
- [ ] Stderr is captured and last 10 lines logged at WARNING level
- [ ] JSON stdout lines are parsed and forwarded to `record_event` + `broadcaster.broadcast`; non-JSON lines are debug-logged

### Notes

The inline-import pattern in `_build_staged_command` uses raw strings (`r'...'`) for Windows VDI path safety. The command is a single `-c` invocation — no temporary files, no shell=True (which would open a security hole).

If the partner provides a CLI wrapper (option a from the Phase 5 coordination question):

```python
def _build_staged_command(input_folder, output_folder):
    cli_script = str(Path(settings.pipeline_module_path) / "pipeline_cli.py")
    return [settings.python_interpreter, cli_script, "staged",
            "--input", input_folder, "--output", output_folder]
```

Only `_build_staged_command` and `_build_approval_command` need to change — everything else (streaming, events, locks, MAID index) stays identical.

The subprocess is launched with `asyncio.create_subprocess_exec` (not `exec_shell`). This avoids shell injection risks from folder names containing special characters.

The `run_staged` method creates the output directory before spawning the subprocess. The pipeline is expected to write INTO this directory rather than creating it — if the pipeline also creates the directory, `exist_ok=True` on our `mkdir` prevents collisions.

The lock-acquire-fail case does NOT write `failure.json` — the folder may not exist yet (new run that couldn't start), and a failure.json would create a phantom folder. Instead, the UI detects the lock-held condition via `GET /api/locks` and shows the "An active operation is in progress" tooltip per V's single-lock directive.

---

## T-D5 — `MockPipelineRunner` + synthetic event sequence

**Depends on:** T-D1, T-C2, T-C3, T-C4, T-C5
**Touches files:** `/api/adapters/mock_runner.py`
**Estimated effort:** medium

### Goal

Implement the mock pipeline adapter per Rule 7. Simulates pipeline execution with configurable latency (`MOCK_LATENCY`) and failure injection (`MOCK_FAILURE`) per D-066. Emits a realistic event sequence matching the D-059 taxonomy so the Activity tab, Issues tab, and SSE-driven live updates all exercise their rendering paths during development.

### Context

From D-066 (Configuration management):

> `MOCK_LATENCY` — "realistic" (events on timers ~2-5s apart) | "instant" (all events at once).
> `MOCK_FAILURE` — "none" (clean run) | "staged" (fail during run_unified_pipeline) | "approval" (fail during submit_to_jira).

From Rule 7 (Project Rulebook):

> The mock adapter exercises every UI code path, not just the happy path. Failure injection and variable latency are required features.

### Implementation

**File: `/api/adapters/mock_runner.py`**:

```python
"""
MockPipelineRunner — synthetic event simulation per Rule 7.

DEFAULT adapter (ADAPTER_PROFILE=mock). Emits a realistic sequence of
D-059 events with configurable timing and failure injection so the UI's
Activity tab, Issues tab, state badges, action buttons, and SSE-driven
invalidation all work correctly during development.

Event sequence (staged):
    run_started → stage_started(extraction) → stage_progress(30%) →
    stage_progress(60%) → stage_completed(extraction) →
    stage_started(comparison) → validation_failure (mock issue) →
    warning (mock warning) → comparison_ready → stage_completed(comparison) →
    pre_approval_reached

Event sequence (approval):
    approval_submitted → stage_started(jira) → jira_created →
    stage_started(sharepoint) → sharepoint_synced →
    submission_complete

Failure injection (MOCK_FAILURE=staged):
    Sequence proceeds through stage_started(extraction) → stage_progress(30%)
    → run_failed (simulated crash).

Failure injection (MOCK_FAILURE=approval):
    Approval sequence proceeds through approval_submitted → stage_started(jira)
    → run_failed (simulated Jira timeout).
"""

import asyncio
import logging
from datetime import datetime, timezone

from api.adapters.interfaces import PipelineRunner
from api.config import settings
from api.db.audit import AuditAction, write_audit
from api.db.maid_index import populate_maid_index
from api.state.events import EventType, record_event
from api.state.failure import write_failure_json
from api.state.locks import acquire_lock, release_lock
from api.state.sse import get_broadcaster

logger = logging.getLogger(__name__)


def _delay() -> float:
    """Return the inter-event delay based on MOCK_LATENCY setting."""
    if settings.mock_latency == "instant":
        return 0.05  # near-instant but still yields to event loop
    return 2.5  # realistic: ~2.5 seconds between events


async def _emit(
    run_id: str,
    event_type: EventType,
    payload: dict,
) -> None:
    """Record event + broadcast to SSE subscribers."""
    event_id = record_event(
        run_id=run_id,
        event_type=event_type,
        payload=payload,
    )
    broadcaster = get_broadcaster()
    await broadcaster.broadcast(
        run_id=run_id,
        event_type=event_type.value,
        payload=payload,
        event_id=event_id,
        ts=datetime.now(timezone.utc).isoformat(),
    )


class MockPipelineRunner(PipelineRunner):
    """Mock adapter with synthetic event simulation."""

    async def run_staged(
        self,
        run_id: str,
        input_folder: str,
        operator_id: str,
    ) -> None:
        phase = "staged"
        delay = _delay()

        write_audit(
            operator_id=operator_id,
            action_type=AuditAction.RUN_STARTED,
            run_id=run_id,
            details={"input_folder": input_folder, "mock": True},
        )

        acquired = acquire_lock(operator_id, run_id, phase)
        if not acquired:
            await _emit(run_id, EventType.RUN_FAILED, {
                "stage": phase,
                "message": "Could not start — another operation is in progress.",
            })
            return

        try:
            # --- Staged event sequence ---
            await _emit(run_id, EventType.RUN_STARTED, {
                "input_folder": input_folder,
                "merchant": run_id.rsplit("_", 2)[0] if "_" in run_id else run_id,
                "operator_id": operator_id,
            })
            await asyncio.sleep(delay)

            await _emit(run_id, EventType.STAGE_STARTED, {
                "stage_name": "extraction",
                "message": "Starting document extraction...",
            })
            await asyncio.sleep(delay)

            await _emit(run_id, EventType.STAGE_PROGRESS, {
                "stage_name": "extraction",
                "percent": 30,
                "message": "Processing page images...",
            })
            await asyncio.sleep(delay)

            # --- Failure injection: staged ---
            if settings.mock_failure == "staged":
                await _emit(run_id, EventType.RUN_FAILED, {
                    "stage": phase,
                    "message": "Mock failure: pipeline crashed during extraction.",
                    "exit_code": 1,
                })
                write_failure_json(
                    folder_path=settings.output_base_folder_path / run_id,
                    stage=phase,
                    error_message="Mock failure: pipeline crashed during extraction.",
                    exit_code=1,
                )
                return

            await _emit(run_id, EventType.STAGE_PROGRESS, {
                "stage_name": "extraction",
                "percent": 60,
                "message": "Applying field mappings...",
            })
            await asyncio.sleep(delay)

            await _emit(run_id, EventType.STAGE_COMPLETED, {
                "stage_name": "extraction",
                "message": "Extraction complete.",
            })
            await asyncio.sleep(delay)

            await _emit(run_id, EventType.STAGE_STARTED, {
                "stage_name": "comparison",
                "message": "Starting old vs new comparison...",
            })
            await asyncio.sleep(delay)

            # Issue events for Issues tab exercise.
            await _emit(run_id, EventType.VALIDATION_FAILURE, {
                "field": "interchange_rate_percent",
                "value": "0.00",
                "rule": "rate_must_be_positive",
                "severity": "warning",
            })
            await asyncio.sleep(delay * 0.5)

            await _emit(run_id, EventType.WARNING, {
                "message": "MCC group 'Restaurants' has no breakeven threshold defined.",
                "context": {"mcc_group": "Restaurants"},
            })
            await asyncio.sleep(delay)

            await _emit(run_id, EventType.COMPARISON_READY, {
                "changes_summary": {
                    "add": 3,
                    "remove": 2,
                    "rate_update": 2,
                    "mcc_expansion": 1,
                },
            })
            await asyncio.sleep(delay)

            await _emit(run_id, EventType.STAGE_COMPLETED, {
                "stage_name": "comparison",
                "message": "Comparison complete.",
            })
            await asyncio.sleep(delay)

            await _emit(run_id, EventType.PRE_APPROVAL_REACHED, {
                "output_folder": str(settings.output_base_folder_path / run_id),
                "artifacts": ["mod_file_entries.json", "comparison_results.json"],
            })

            # Post-run: MAID index population (skipped for mock since
            # no real files exist; logs a debug message).
            try:
                populate_maid_index(run_id, settings.output_base_folder_path / run_id)
            except Exception:
                logger.debug("Mock run: MAID index population skipped (no real folder).")

        except Exception as exc:
            logger.exception("MockPipelineRunner.run_staged error: %s", exc)
            await _emit(run_id, EventType.RUN_FAILED, {
                "stage": phase,
                "message": f"Unexpected mock error: {exc}",
            })
        finally:
            release_lock(operator_id, run_id, phase)

    async def run_approval(
        self,
        run_id: str,
        operator_id: str,
    ) -> None:
        phase = "approval"
        delay = _delay()

        write_audit(
            operator_id=operator_id,
            action_type=AuditAction.APPROVE_CLICKED,
            run_id=run_id,
        )

        acquired = acquire_lock(operator_id, run_id, phase)
        if not acquired:
            await _emit(run_id, EventType.RUN_FAILED, {
                "stage": phase,
                "message": "Could not start approval — another operation is in progress.",
            })
            return

        try:
            await _emit(run_id, EventType.APPROVAL_SUBMITTED, {
                "target_systems": ["jira", "sharepoint"],
            })
            await asyncio.sleep(delay)

            await _emit(run_id, EventType.STAGE_STARTED, {
                "stage_name": "jira_submission",
                "message": "Creating Jira Epic and Story...",
            })
            await asyncio.sleep(delay)

            # --- Failure injection: approval ---
            if settings.mock_failure == "approval":
                await _emit(run_id, EventType.RUN_FAILED, {
                    "stage": phase,
                    "message": "Mock failure: Jira API timeout.",
                    "exit_code": 1,
                })
                write_failure_json(
                    folder_path=settings.output_base_folder_path / run_id,
                    stage=phase,
                    error_message="Mock failure: Jira API timeout.",
                    exit_code=1,
                )
                return

            await _emit(run_id, EventType.JIRA_CREATED, {
                "epic_key": "CMRPEE-142",
                "story_key": "CMRPEE-143",
            })
            await asyncio.sleep(delay)

            await _emit(run_id, EventType.STAGE_STARTED, {
                "stage_name": "sharepoint_sync",
                "message": "Syncing to SharePoint...",
            })
            await asyncio.sleep(delay)

            await _emit(run_id, EventType.SHAREPOINT_SYNCED, {
                "folder_path": "\\\\sharepoint\\CustomInterchange\\mock\\2026-05",
            })
            await asyncio.sleep(delay)

            await _emit(run_id, EventType.SUBMISSION_COMPLETE, {
                "epic_key": "CMRPEE-142",
                "story_key": "CMRPEE-143",
                "sharepoint_path": "\\\\sharepoint\\CustomInterchange\\mock\\2026-05",
            })

        except Exception as exc:
            logger.exception("MockPipelineRunner.run_approval error: %s", exc)
            await _emit(run_id, EventType.RUN_FAILED, {
                "stage": phase,
                "message": f"Unexpected mock error: {exc}",
            })
        finally:
            release_lock(operator_id, run_id, phase)
```

### Acceptance criteria

- [ ] `/api/adapters/mock_runner.py` exports `MockPipelineRunner` implementing `run_staged` and `run_approval`
- [ ] With `MOCK_LATENCY=instant`, `MOCK_FAILURE=none`: `run_staged` completes in <1s; `sqlite3 <db> "SELECT type FROM events WHERE run_id='test' ORDER BY id"` shows the full 11-event sequence
- [ ] With `MOCK_LATENCY=realistic`: events are ~2.5s apart (verify with `ts` column differences)
- [ ] With `MOCK_FAILURE=staged`: event sequence stops after `stage_progress(30%)` with a `run_failed` event; `failure.json` exists with `stage='staged'` and `retry_strategy='rerun_only'`
- [ ] With `MOCK_FAILURE=approval`: approval sequence stops after `stage_started(jira)` with `run_failed`; `failure.json` has `stage='approval'` and `retry_strategy='retry_or_rerun'`
- [ ] Lock is acquired before events start and released in `finally` (even on failure injection)
- [ ] SSE subscribers receive events in real time during the run (verify with a test subscriber)
- [ ] Issues tab events: at least one `validation_failure` and one `warning` appear in the staged sequence

### Notes

The mock event sequence is intentionally rich — it includes `validation_failure` and `warning` events so the Issues tab has content to render during development. Without these, the Issues tab would appear empty in mock mode, making it impossible to style or debug.

`MOCK_FAILURE` injection happens mid-sequence (not before the first event) to exercise the "run started, then failed" state transition — the Run Detail header shows "In Progress" → "Failed" with the right visual flicker.

The `populate_maid_index` call at the end of `run_staged` will likely log "no real folder" in mock mode because no actual output folder exists on disk. This is expected — the mock doesn't create real files. In production (`ADAPTER_PROFILE=real`), `SubprocessPipelineRunner` creates the output folder and the pipeline populates it with real files.

The Jira keys in the mock approval sequence (`CMRPEE-142`, `CMRPEE-143`) match the fixture in `jira_info.json` (T-D3). This consistency matters for the Jira Info panel in Run Detail's Activity tab.

---

## T-D6 — Adapter factory + FastAPI dependency wiring

**Depends on:** T-D1, T-D2, T-D3, T-D4, T-D5, T1
**Touches files:** `/api/adapters/factory.py`, `/api/dependencies.py` (modification)
**Estimated effort:** small

### Goal

Implement factory functions that return the correct adapter implementation based on `ADAPTER_PROFILE`. Wire them as FastAPI dependencies so Section E endpoints declare `storage: StorageClient = Depends(get_storage_client)` and get the right implementation injected.

### Context

From D-066 (Configuration management):

> `ADAPTER_PROFILE=mock` is the default. Flipping to `real` requires only `.env` edits, no code change.

### Implementation

**File: `/api/adapters/factory.py`**:

```python
"""
Adapter factory functions.

Called via FastAPI's Depends() system by Section E endpoints. The factory
reads ADAPTER_PROFILE once and returns a cached instance for the process
lifetime (both adapters are stateless reads, so sharing an instance is safe).
"""

import logging
from functools import lru_cache

from api.adapters.interfaces import PipelineRunner, StorageClient
from api.config import settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_storage_client() -> StorageClient:
    """Return the StorageClient implementation matching ADAPTER_PROFILE."""
    profile = settings.adapter_profile
    if profile == "real":
        from api.adapters.local_storage import LocalStorageClient
        logger.info("StorageClient: using LocalStorageClient (ADAPTER_PROFILE=real)")
        return LocalStorageClient()
    else:
        from api.adapters.mock_storage import MockStorageClient
        logger.info("StorageClient: using MockStorageClient (ADAPTER_PROFILE=mock)")
        return MockStorageClient()


@lru_cache(maxsize=1)
def get_pipeline_runner() -> PipelineRunner:
    """Return the PipelineRunner implementation matching ADAPTER_PROFILE."""
    profile = settings.adapter_profile
    if profile == "real":
        from api.adapters.subprocess_runner import SubprocessPipelineRunner
        logger.info("PipelineRunner: using SubprocessPipelineRunner (ADAPTER_PROFILE=real)")
        return SubprocessPipelineRunner()
    else:
        from api.adapters.mock_runner import MockPipelineRunner
        logger.info("PipelineRunner: using MockPipelineRunner (ADAPTER_PROFILE=mock)")
        return MockPipelineRunner()
```

**Modification to `/api/dependencies.py`** — add the adapter dependencies alongside the existing auth stubs:

```python
"""
FastAPI dependency stubs per D-065 + adapter factory per T-D6.

Section E endpoints declare these as Depends() parameters to get the right
adapter implementation injected automatically.
"""

import uuid
from fastapi import Depends, Header

from api.adapters.factory import get_pipeline_runner, get_storage_client
from api.adapters.interfaces import PipelineRunner, StorageClient


def require_operator(x_operator_id: str | None = Header(default=None)) -> str:
    """Extract operator identity from the X-Operator-ID header.
    (... docstring from T1, unchanged ...)
    """
    if not x_operator_id:
        return f"server-{uuid.uuid4()}"
    return x_operator_id


def require_admin(x_operator_id: str | None = Header(default=None)) -> str:
    """No-op in MVP per D-030.
    (... docstring from T1, unchanged ...)
    """
    return require_operator(x_operator_id)


# Adapter dependencies — Section E endpoints use these:
#
#   @router.get("/runs")
#   def list_runs(storage: StorageClient = Depends(get_storage_client)):
#       ...
#
#   @router.post("/runs/start")
#   async def start_run(runner: PipelineRunner = Depends(get_pipeline_runner)):
#       ...

# Re-export for clean imports in Section E.
# Usage: from api.dependencies import get_storage_client, get_pipeline_runner
```

### Acceptance criteria

- [ ] `/api/adapters/factory.py` exports `get_storage_client()` and `get_pipeline_runner()`
- [ ] With `ADAPTER_PROFILE=mock` (default): `get_storage_client()` returns `MockStorageClient`; `get_pipeline_runner()` returns `MockPipelineRunner`
- [ ] With `ADAPTER_PROFILE=real`: returns `LocalStorageClient` and `SubprocessPipelineRunner`
- [ ] Factory functions are cached (`lru_cache`) — second call returns the same instance
- [ ] `/api/dependencies.py` re-exports the factory functions alongside `require_operator` / `require_admin`
- [ ] Log output on first call shows which implementation was selected
- [ ] Changing `ADAPTER_PROFILE` requires a uvicorn restart (lru_cache is per-process)

### Notes

The lazy imports inside the factory functions (`from api.adapters.local_storage import ...`) are intentional. The real adapters depend on `PIPELINE_MODULE_PATH` existing (checked at Settings validation in T4) and on the partner's codebase being importable. Lazy importing means mock mode never touches real-adapter code paths, avoiding import-time errors when `PIPELINE_MODULE_PATH` isn't set.

`lru_cache(maxsize=1)` gives us singleton behavior without explicit module-level state. The trade-off: changing `ADAPTER_PROFILE` at runtime (which is not a supported operation anyway) would require clearing the cache or restarting uvicorn.

Section E endpoints will declare dependencies like:

```python
from api.dependencies import get_storage_client, get_pipeline_runner, require_operator

@router.get("/runs")
def list_runs(
    storage: StorageClient = Depends(get_storage_client),
    operator_id: str = Depends(require_operator),
):
    ...
```

This pattern makes the adapter injection invisible to the endpoint implementation — the code inside `list_runs` calls `storage.list_run_folders()` without caring whether it's hitting the real filesystem or fixtures.
# Section E — FastAPI endpoints

This section wires the 16 D-061 endpoints (plus error-envelope middleware and the SSE stream) to the adapter layer (Section D) and state-derivation plumbing (Section C). Each endpoint task is focused: call the adapter, transform the result, return the response. The business logic lives upstream in Sections C/D; these endpoints are thin composition glue.

Section index:

- [ ] T-E1 — Error envelope middleware
- [ ] T-E2 — Response models + shared schemas
- [ ] T-E3 — POST /api/runs/start
- [ ] T-E4 — POST /api/runs/{run_id}/approve
- [ ] T-E5 — POST /api/runs/{run_id}/retry-approve
- [ ] T-E6 — POST /api/runs/{run_id}/rerun
- [ ] T-E7 — GET /api/runs (list with search, filter, pagination)
- [ ] T-E8 — GET /api/runs/{run_id} (run detail summary)
- [ ] T-E9 — GET /api/runs/{run_id}/base-table
- [ ] T-E10 — GET /api/runs/{run_id}/drawer/{match_tag}
- [ ] T-E11 — GET /api/runs/{run_id}/raw-extract/{match_tag}
- [ ] T-E12 — GET /api/runs/{run_id}/issues
- [ ] T-E13 — GET /api/runs/{run_id}/events
- [ ] T-E14 — GET /api/runs/{run_id}/pdf
- [ ] T-E15 — GET /api/runs/{run_id}/jira-info
- [ ] T-E16 — GET /api/input-folders
- [ ] T-E17 — GET /api/locks
- [ ] T-E18 — GET /api/events (SSE stream)

---

## T-E1 — Error envelope middleware

**Depends on:** T1
**Touches files:** `/api/middleware/__init__.py`, `/api/middleware/error_envelope.py`, `/api/main.py` (modification)
**Estimated effort:** small

### Goal

Install FastAPI exception handlers that wrap all error responses in the D-061 §7.4 error envelope shape: `{"error": {"code": "...", "message": "...", "remediation_hint": "..."}}`. Covers HTTP exceptions raised by endpoints, validation errors from Pydantic, and unhandled 500s.

### Context

From D-061 (API contract):

> Error shape: `{"error": {"code": "LOCK_HELD", "message": "...", "remediation_hint": "..."}}`. All non-2xx responses use this envelope. The frontend's error rendering pipeline depends on this shape being consistent.

### Implementation

**File: `/api/middleware/__init__.py`** — empty marker.

**File: `/api/middleware/error_envelope.py`**:

```python
"""
Error envelope middleware per D-061 §7.4.

Intercepts all non-2xx responses and wraps them in the canonical
error envelope shape so the frontend can rely on a single error
rendering path.

Error codes are short UPPER_SNAKE_CASE identifiers:
    LOCK_HELD, NOT_FOUND, VALIDATION_ERROR, BAD_REQUEST, INTERNAL_ERROR
"""

import logging
import traceback

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


def _envelope(code: str, message: str, hint: str | None = None, status: int = 400) -> JSONResponse:
    body = {
        "error": {
            "code": code,
            "message": message,
        }
    }
    if hint:
        body["error"]["remediation_hint"] = hint
    return JSONResponse(status_code=status, content=body)


def install_error_handlers(app: FastAPI) -> None:
    """Attach exception handlers to the FastAPI app."""

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        code_map = {
            404: "NOT_FOUND",
            409: "LOCK_HELD",
            422: "VALIDATION_ERROR",
            403: "FORBIDDEN",
        }
        code = code_map.get(exc.status_code, "HTTP_ERROR")
        hint = None
        if exc.status_code == 409:
            hint = "Wait for the current operation to finish, then try again."
        return _envelope(code, str(exc.detail), hint=hint, status=exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        errors = exc.errors()
        msg = "; ".join(
            f"{'.'.join(str(l) for l in e.get('loc', []))}: {e.get('msg', '')}"
            for e in errors
        )
        return _envelope(
            "VALIDATION_ERROR", msg,
            hint="Check request parameters and try again.",
            status=422,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
        return _envelope(
            "INTERNAL_ERROR",
            "An unexpected error occurred.",
            hint="Check the server logs for details.",
            status=500,
        )
```

**Modification to `/api/main.py`** — install error handlers after app creation:

```python
from api.middleware.error_envelope import install_error_handlers

# ... (after app = FastAPI(...))
install_error_handlers(app)
```

### Acceptance criteria

- [ ] A 404 from any endpoint returns `{"error": {"code": "NOT_FOUND", "message": "..."}}`
- [ ] A Pydantic validation error returns `{"error": {"code": "VALIDATION_ERROR", ...}}` with field-level detail
- [ ] An unhandled exception returns `{"error": {"code": "INTERNAL_ERROR", ...}}` with status 500
- [ ] A 409 (lock held) returns the envelope with `remediation_hint` populated
- [ ] The response `Content-Type` is always `application/json` for error responses

### Notes

The error envelope is the contract between backend and frontend error rendering. The frontend's error-handling layer (Section F) depends on being able to read `response.error.code` and `response.error.message` from every non-2xx response without conditional parsing.

---

## T-E2 — Response models + shared schemas

**Depends on:** T-D1
**Touches files:** `/api/routers/schemas.py`
**Estimated effort:** small

### Goal

Define Pydantic response models used across multiple endpoints. Centralizes the API response shapes so OpenAPI docs are accurate and the frontend TypeScript types can be derived from them.

### Implementation

**File: `/api/routers/schemas.py`**:

```python
"""
API response schemas per D-061.

These Pydantic models define the JSON shapes returned by Section E endpoints.
Adapter models (Section D) are the internal representations; these schemas
are the HTTP-facing contract.
"""

from typing import Any

from pydantic import BaseModel, Field

from api.adapters.models import (
    BaseTableRow,
    DrawerRecord,
    InputFolderInfo,
    JiraInfo,
    RunFolderSummary,
)


class RunListResponse(BaseModel):
    """GET /api/runs response."""
    runs: list[RunFolderSummary]
    total: int = Field(description="Total matching runs before pagination")
    page: int = Field(default=1)
    page_size: int = Field(default=10)


class RunDetailResponse(BaseModel):
    """GET /api/runs/{run_id} response."""
    run: RunFolderSummary
    failure: dict[str, Any] | None = Field(
        default=None,
        description="Contents of failure.json if state is FAILED"
    )
    available_actions: list[str] = Field(
        default_factory=list,
        description="Which action buttons to enable: 'approve', 'retry_approve', 'rerun_from_scratch'"
    )


class BaseTableResponse(BaseModel):
    """GET /api/runs/{run_id}/base-table response."""
    rows: list[BaseTableRow]
    total: int


class IssueItem(BaseModel):
    """Single issue item for Issues tab."""
    id: int
    ts: str
    type: str
    severity: str | None = None
    message: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class IssuesResponse(BaseModel):
    """GET /api/runs/{run_id}/issues response."""
    issues: list[IssueItem]
    total: int


class EventItem(BaseModel):
    """Single event for Activity tab."""
    id: int
    ts: str
    type: str
    payload: dict[str, Any] = Field(default_factory=dict)


class EventsResponse(BaseModel):
    """GET /api/runs/{run_id}/events response."""
    events: list[EventItem]


class LockStateResponse(BaseModel):
    """GET /api/locks response."""
    held: bool
    held_by_operator: str | None = None
    run_id: str | None = None
    phase: str | None = None
    acquired_at: str | None = None


class InputFoldersResponse(BaseModel):
    """GET /api/input-folders response."""
    folders: list[InputFolderInfo]


class ActionAcceptedResponse(BaseModel):
    """POST mutation response (202 Accepted)."""
    status: str = "accepted"
    run_id: str
    message: str
```

### Acceptance criteria

- [ ] `/api/routers/schemas.py` exports all response models listed above
- [ ] All models serialize cleanly via `.model_dump_json()`
- [ ] `RunDetailResponse.available_actions` is a list of strings (not an enum — the frontend matches against string literals)
- [ ] `ActionAcceptedResponse` has `status="accepted"` as default

### Notes

`RunDetailResponse.available_actions` is computed by the endpoint based on `infer_state()` + `failure.json` stage per D-046. The list values match the frontend's action-button rendering logic: `'approve'`, `'retry_approve'`, `'rerun_from_scratch'`.

---

## T-E3 — POST /api/runs/start

**Depends on:** T-E1, T-E2, T-D6, T-C2
**Touches files:** `/api/routers/runs.py` (modification)
**Estimated effort:** medium

### Goal

Implement the staged-run initiation endpoint. Validates the input folder against `ALLOWED_INPUT_ROOTS`, generates a run_id from merchant + timestamp, launches `PipelineRunner.run_staged()` as a FastAPI background task, and returns 202 Accepted immediately.

### Context

From D-061:

> `POST /api/runs/start` — body: `{"input_folder": "..."}`. Validates input_folder against D-013 allowlist. Generates run_id. Returns 202 with run_id. Pipeline runs in background.

From D-013 (Input folder allowlist):

> Only folders under one of the `ALLOWED_INPUT_ROOTS` are accepted. Path traversal (../) is blocked.

### Implementation

Add to `/api/routers/runs.py`:

```python
import re
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from api.adapters.factory import get_pipeline_runner, get_storage_client
from api.adapters.interfaces import PipelineRunner, StorageClient
from api.config import settings
from api.dependencies import require_operator
from api.routers.schemas import ActionAcceptedResponse
from api.state.locks import get_lock_state

router = APIRouter(tags=["runs"])


class StartRunRequest(BaseModel):
    input_folder: str


@router.post("/runs/start", response_model=ActionAcceptedResponse, status_code=202)
async def start_run(
    body: StartRunRequest,
    background_tasks: BackgroundTasks,
    operator_id: str = Depends(require_operator),
    runner: PipelineRunner = Depends(get_pipeline_runner),
):
    """Start a new staged pipeline run per D-061.

    Validates input_folder against ALLOWED_INPUT_ROOTS (D-013).
    Generates run_id from merchant name + timestamp.
    Launches PipelineRunner.run_staged() as a background task.
    Returns 202 immediately — the frontend polls via SSE.
    """
    # 1. Validate input folder against allowlist per D-013.
    input_path = Path(body.input_folder).resolve()
    allowed = any(
        _is_under_root(input_path, root)
        for root in settings.allowed_input_roots_list
    )
    if not allowed:
        raise HTTPException(
            status_code=400,
            detail=f"Input folder is not under any allowed root. "
                   f"Allowed roots: {[str(r) for r in settings.allowed_input_roots_list]}",
        )
    if not input_path.is_dir():
        raise HTTPException(status_code=400, detail="Input folder does not exist.")

    # 2. Check lock — fail fast before background task.
    lock = get_lock_state()
    if lock.held:
        raise HTTPException(
            status_code=409,
            detail="An active operation is in progress. Wait for it to complete.",
        )

    # 3. Generate run_id.
    merchant = input_path.name.split("_")[0] if "_" in input_path.name else input_path.name
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_id = f"{merchant}_{ts}"

    # 4. Launch background task.
    background_tasks.add_task(
        runner.run_staged,
        run_id=run_id,
        input_folder=str(input_path),
        operator_id=operator_id,
    )

    return ActionAcceptedResponse(
        run_id=run_id,
        message=f"Staged run started for {merchant}.",
    )


def _is_under_root(path: Path, root: Path) -> bool:
    """Check that path is under root, preventing traversal attacks."""
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False
```

### Acceptance criteria

- [ ] `POST /api/runs/start` with a valid `input_folder` under an allowed root returns 202 with `{"status":"accepted","run_id":"...","message":"..."}`
- [ ] An `input_folder` not under any allowed root returns 400 with the error envelope
- [ ] A non-existent `input_folder` returns 400
- [ ] If the lock is held, returns 409 with `"An active operation is in progress"`
- [ ] The generated `run_id` follows the `merchant_YYYYMMDD_HHMMSS` pattern
- [ ] The endpoint returns immediately (202); the pipeline runs in the background
- [ ] `X-Operator-ID` header is passed through to the runner

### Notes

The lock check before `add_task` is a best-effort fast-fail — there's a TOCTOU race between the check and the `acquire_lock` inside the runner. The runner's own `acquire_lock` is the authoritative gate; this pre-check just gives a cleaner 409 instead of a background-task failure event.

The `from pydantic import BaseModel` import for `StartRunRequest` is needed — add it to the imports block alongside the existing imports from T1's stub.

---

## T-E4 — POST /api/runs/{run_id}/approve

**Depends on:** T-E1, T-E2, T-D6, T-C1
**Touches files:** `/api/routers/runs.py` (modification)
**Estimated effort:** small

### Goal

Implement the approval endpoint. Validates the run is in `pre_approval` state, launches `PipelineRunner.run_approval()` as a background task.

### Implementation

Add to `/api/routers/runs.py`:

```python
@router.post("/runs/{run_id}/approve", response_model=ActionAcceptedResponse, status_code=202)
async def approve_run(
    run_id: str,
    background_tasks: BackgroundTasks,
    operator_id: str = Depends(require_operator),
    runner: PipelineRunner = Depends(get_pipeline_runner),
    storage: StorageClient = Depends(get_storage_client),
):
    """Approve a pre-approval run for Jira + SharePoint submission."""
    folder = storage.get_run_folder(run_id)
    if not folder:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found.")

    lock = get_lock_state()
    if lock.held:
        raise HTTPException(status_code=409, detail="An active operation is in progress.")

    # State check: only pre_approval runs can be approved.
    from api.state.inference import infer_state, RunState
    state = infer_state(
        Path(folder.folder_path),
        held_run_id=lock.run_id if lock.held else None,
    )
    if state != RunState.PRE_APPROVAL:
        raise HTTPException(
            status_code=400,
            detail=f"Run {run_id} is in state '{state.value}', not 'pre_approval'. Cannot approve.",
        )

    background_tasks.add_task(runner.run_approval, run_id=run_id, operator_id=operator_id)
    return ActionAcceptedResponse(run_id=run_id, message="Approval started.")
```

### Acceptance criteria

- [ ] Approving a `pre_approval` run returns 202
- [ ] Approving a `submitted` or `failed` run returns 400 with state mismatch message
- [ ] 404 for non-existent run_id
- [ ] 409 if lock is held

---

## T-E5 — POST /api/runs/{run_id}/retry-approve

**Depends on:** T-E1, T-E2, T-D6, T-C1, T-C3
**Touches files:** `/api/routers/runs.py` (modification)
**Estimated effort:** small

### Goal

Retry approval on a run that failed during the approval stage. Validates state is `failed` and failure stage is `approval` per D-046. Removes the existing `failure.json` before re-launching approval.

### Implementation

Add to `/api/routers/runs.py`:

```python
@router.post("/runs/{run_id}/retry-approve", response_model=ActionAcceptedResponse, status_code=202)
async def retry_approve(
    run_id: str,
    background_tasks: BackgroundTasks,
    operator_id: str = Depends(require_operator),
    runner: PipelineRunner = Depends(get_pipeline_runner),
    storage: StorageClient = Depends(get_storage_client),
):
    """Retry approval on a run that failed during the approval stage per D-046."""
    folder = storage.get_run_folder(run_id)
    if not folder:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found.")

    lock = get_lock_state()
    if lock.held:
        raise HTTPException(status_code=409, detail="An active operation is in progress.")

    from api.state.inference import infer_state, RunState
    from api.state.failure import read_failure_json
    from api.state.sentinels import SENTINEL_FAILED
    from api.db.audit import AuditAction, write_audit

    state = infer_state(Path(folder.folder_path), held_run_id=None)
    if state != RunState.FAILED:
        raise HTTPException(
            status_code=400,
            detail=f"Run {run_id} is in state '{state.value}', not 'failed'. Cannot retry.",
        )

    failure_info = read_failure_json(Path(folder.folder_path))
    if not failure_info or failure_info.get("retry_strategy") != "retry_or_rerun":
        raise HTTPException(
            status_code=400,
            detail=f"Run {run_id} failed during staged processing. "
                   f"Only 'Re-run from scratch' is available (not retry).",
        )

    # Remove failure.json so infer_state won't return FAILED during the retry.
    failure_file = Path(folder.folder_path) / SENTINEL_FAILED
    if failure_file.exists():
        failure_file.unlink()

    write_audit(
        operator_id=operator_id,
        action_type=AuditAction.RETRY_APPROVE_CLICKED,
        run_id=run_id,
    )

    background_tasks.add_task(runner.run_approval, run_id=run_id, operator_id=operator_id)
    return ActionAcceptedResponse(run_id=run_id, message="Retry approval started.")
```

### Acceptance criteria

- [ ] Retrying a run that failed with `retry_strategy='retry_or_rerun'` returns 202 and removes failure.json
- [ ] Retrying a run that failed with `retry_strategy='rerun_only'` (staged failure) returns 400
- [ ] 404 for non-existent run, 409 if lock held
- [ ] Audit log entry with `RETRY_APPROVE_CLICKED` is written

---

## T-E6 — POST /api/runs/{run_id}/rerun

**Depends on:** T-E3, T-E1, T-E2
**Touches files:** `/api/routers/runs.py` (modification)
**Estimated effort:** small

### Goal

Re-run from scratch: create a NEW run folder (new run_id) using the same input folder as the failed run. The old failed run folder stays as-is per D-046's "no in-place retry" model.

### Implementation

Add to `/api/routers/runs.py`:

```python
class RerunRequest(BaseModel):
    input_folder: str  # The operator re-specifies or the UI pre-fills from the original


@router.post("/runs/{run_id}/rerun", response_model=ActionAcceptedResponse, status_code=202)
async def rerun_from_scratch(
    run_id: str,
    body: RerunRequest,
    background_tasks: BackgroundTasks,
    operator_id: str = Depends(require_operator),
    runner: PipelineRunner = Depends(get_pipeline_runner),
    storage: StorageClient = Depends(get_storage_client),
):
    """Re-run from scratch per D-046 — creates a NEW run folder."""
    folder = storage.get_run_folder(run_id)
    if not folder:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found.")

    lock = get_lock_state()
    if lock.held:
        raise HTTPException(status_code=409, detail="An active operation is in progress.")

    # Validate input folder (same as T-E3).
    input_path = Path(body.input_folder).resolve()
    allowed = any(
        _is_under_root(input_path, root) for root in settings.allowed_input_roots_list
    )
    if not allowed:
        raise HTTPException(status_code=400, detail="Input folder not under any allowed root.")
    if not input_path.is_dir():
        raise HTTPException(status_code=400, detail="Input folder does not exist.")

    # Generate NEW run_id.
    from api.db.audit import AuditAction, write_audit
    merchant = input_path.name.split("_")[0] if "_" in input_path.name else input_path.name
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    new_run_id = f"{merchant}_{ts}"

    write_audit(
        operator_id=operator_id,
        action_type=AuditAction.RERUN_FROM_SCRATCH_CLICKED,
        run_id=run_id,
        details={"new_run_id": new_run_id, "input_folder": str(input_path)},
    )

    background_tasks.add_task(
        runner.run_staged,
        run_id=new_run_id,
        input_folder=str(input_path),
        operator_id=operator_id,
    )

    return ActionAcceptedResponse(
        run_id=new_run_id,
        message=f"Re-run started as {new_run_id} (original: {run_id}).",
    )
```

### Acceptance criteria

- [ ] Rerun creates a NEW run_id; returns 202 with the new ID
- [ ] Original run folder is NOT modified (no deletion, no failure.json removal)
- [ ] Audit log captures both old run_id and new_run_id in details
- [ ] Input folder validation same as T-E3

---

## T-E7 — GET /api/runs (list with search, filter, pagination)

**Depends on:** T-E2, T-D6, T-C1, T-C2, T-B4
**Touches files:** `/api/routers/runs.py` (modification)
**Estimated effort:** medium

### Goal

Implement the Runs List data endpoint per D-042 + D-061. Supports search by MAID or merchant, filter by state, and pagination. Injects `state` and `issue_count` into each run summary. Newest-first ordering.

### Context

From D-042 (Runs List search):

> Search by MAID or merchant. MAID search queries the `maid_index` table. Merchant search is a substring match on the folder name's merchant component.

From D-061:

> `GET /api/runs?search=...&state=...&page=1&page_size=10`

### Implementation

Add to `/api/routers/runs.py`:

```python
from api.routers.schemas import RunListResponse
from api.state.inference import infer_state, RunState
from api.state.events import ISSUE_EVENT_TYPES
from api.db.connection import connection


@router.get("/runs", response_model=RunListResponse)
def list_runs(
    search: str | None = None,
    state: str | None = None,
    page: int = 1,
    page_size: int = 10,
    storage: StorageClient = Depends(get_storage_client),
):
    """List runs with optional search/filter/pagination per D-042 + D-061."""
    # 1. Get all run folders from storage.
    all_runs = storage.list_run_folders()

    # 2. Get lock state once for state injection.
    lock = get_lock_state()
    held_run_id = lock.run_id if lock.held else None

    # 3. Inject state into each run.
    for run in all_runs:
        run.state = infer_state(
            Path(run.folder_path),
            held_run_id=held_run_id,
        ).value

    # 4. Search filter.
    if search:
        search_lower = search.strip().lower()
        # MAID search via maid_index table.
        matching_run_ids = _search_maid_index(search_lower)
        # Merchant substring match.
        all_runs = [
            r for r in all_runs
            if search_lower in r.merchant.lower()
            or r.run_id in matching_run_ids
        ]

    # 5. State filter.
    if state:
        all_runs = [r for r in all_runs if r.state == state]

    # 6. Inject issue counts.
    _inject_issue_counts(all_runs)

    # 7. Paginate.
    total = len(all_runs)
    start = (page - 1) * page_size
    end = start + page_size
    page_runs = all_runs[start:end]

    return RunListResponse(runs=page_runs, total=total, page=page, page_size=page_size)


def _search_maid_index(query: str) -> set[str]:
    """Search maid_index for run_ids containing MAIDs matching the query."""
    with connection() as conn:
        rows = conn.execute(
            "SELECT DISTINCT run_id FROM maid_index WHERE maid LIKE ?",
            (f"%{query}%",),
        ).fetchall()
    return {r["run_id"] for r in rows}


def _inject_issue_counts(runs: list) -> None:
    """Inject issue_count into each run from the events table."""
    if not runs:
        return
    placeholders_types = ",".join("?" for _ in ISSUE_EVENT_TYPES)
    with connection() as conn:
        for run in runs:
            count = conn.execute(
                f"SELECT COUNT(*) as cnt FROM events "
                f"WHERE run_id = ? AND type IN ({placeholders_types})",
                (run.run_id, *ISSUE_EVENT_TYPES),
            ).fetchone()
            run.issue_count = count["cnt"] if count else 0
```

### Acceptance criteria

- [ ] `GET /api/runs` returns `{"runs": [...], "total": N, "page": 1, "page_size": 10}`
- [ ] Each run in the response has `state` populated (not null)
- [ ] `?search=411424` finds runs via MAID index (substring match on MAID)
- [ ] `?search=intuit` finds runs via merchant substring match
- [ ] `?state=pre_approval` filters to only pre-approval runs
- [ ] `?page=2&page_size=5` paginates correctly
- [ ] Newest runs appear first (sorted by `created_at` descending)
- [ ] `issue_count` is populated per run from the events table

---

## T-E8 — GET /api/runs/{run_id} (run detail summary)

**Depends on:** T-E2, T-D6, T-C1, T-C3
**Touches files:** `/api/routers/runs.py` (modification)
**Estimated effort:** small

### Goal

Return run metadata + state + failure context + available actions for the Run Detail header.

### Implementation

Add to `/api/routers/runs.py`:

```python
from api.routers.schemas import RunDetailResponse
from api.state.failure import read_failure_json


@router.get("/runs/{run_id}", response_model=RunDetailResponse)
def get_run_detail(
    run_id: str,
    storage: StorageClient = Depends(get_storage_client),
):
    """Run detail summary for the Run Detail header per D-061."""
    folder = storage.get_run_folder(run_id)
    if not folder:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found.")

    lock = get_lock_state()
    held_run_id = lock.run_id if lock.held else None
    state = infer_state(Path(folder.folder_path), held_run_id=held_run_id)
    folder.state = state.value

    # Failure context.
    failure = None
    if state == RunState.FAILED:
        failure = read_failure_json(Path(folder.folder_path))

    # Available actions per D-046 + state.
    actions = _compute_available_actions(state, failure, lock.held)

    return RunDetailResponse(run=folder, failure=failure, available_actions=actions)


def _compute_available_actions(
    state: RunState,
    failure: dict | None,
    lock_held: bool,
) -> list[str]:
    """Determine which action buttons to enable per D-046."""
    if lock_held:
        return []  # Everything disabled during active operation.

    if state == RunState.PRE_APPROVAL:
        return ["approve", "rerun_from_scratch"]
    elif state == RunState.FAILED:
        strategy = (failure or {}).get("retry_strategy", "rerun_only")
        if strategy == "retry_or_rerun":
            return ["retry_approve", "rerun_from_scratch"]
        return ["rerun_from_scratch"]
    elif state == RunState.STALE:
        return ["rerun_from_scratch"]
    else:
        # SUBMITTED and IN_PROGRESS: no actions available.
        return []
```

### Acceptance criteria

- [ ] Returns 200 with run metadata, state, failure context (if failed), and available actions
- [ ] `pre_approval` run: `available_actions = ["approve", "rerun_from_scratch"]`
- [ ] `failed` (staged): `available_actions = ["rerun_from_scratch"]`
- [ ] `failed` (approval): `available_actions = ["retry_approve", "rerun_from_scratch"]`
- [ ] `submitted` run: `available_actions = []`
- [ ] Lock held: `available_actions = []` for all states
- [ ] 404 for non-existent run

---

## T-E9 — GET /api/runs/{run_id}/base-table

**Depends on:** T-E2, T-D6
**Touches files:** `/api/routers/runs.py` (modification)
**Estimated effort:** small

### Goal

Return the base table data (mod_file_entries.json) for the Results tab.

### Implementation

Add to `/api/routers/runs.py`:

```python
from api.routers.schemas import BaseTableResponse


@router.get("/runs/{run_id}/base-table", response_model=BaseTableResponse)
def get_base_table(
    run_id: str,
    storage: StorageClient = Depends(get_storage_client),
):
    """Base table data for the Results tab per D-061."""
    folder = storage.get_run_folder(run_id)
    if not folder:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found.")

    rows = storage.read_base_table(run_id)
    return BaseTableResponse(rows=rows, total=len(rows))
```

### Acceptance criteria

- [ ] Returns `{"rows": [...], "total": N}` with `BaseTableRow` items
- [ ] Empty list if run exists but has no base table data yet
- [ ] 404 for non-existent run

---

## T-E10 — GET /api/runs/{run_id}/drawer/{match_tag}

**Depends on:** T-E2, T-D6
**Touches files:** `/api/routers/runs.py` (modification)
**Estimated effort:** small

### Goal

Return a single comparison record for the drawer panel.

### Implementation

Add to `/api/routers/runs.py`:

```python
@router.get("/runs/{run_id}/drawer/{match_tag}")
def get_drawer_record(
    run_id: str,
    match_tag: str,
    storage: StorageClient = Depends(get_storage_client),
):
    """Drawer record for a specific match_tag per D-061."""
    folder = storage.get_run_folder(run_id)
    if not folder:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found.")

    record = storage.read_drawer_record(run_id, match_tag)
    if not record:
        raise HTTPException(status_code=404, detail=f"Match tag '{match_tag}' not found in run {run_id}.")

    return record.model_dump()
```

### Acceptance criteria

- [ ] Returns the `DrawerRecord` JSON for a valid match_tag
- [ ] 404 if run or match_tag doesn't exist
- [ ] Response includes `correlated_fields` (correct naming)

---

## T-E11 — GET /api/runs/{run_id}/raw-extract/{match_tag}

**Depends on:** T-D6
**Touches files:** `/api/routers/runs.py` (modification)
**Estimated effort:** small

### Goal

Return raw extraction data for Artifact Preview's raw-extract sub-pane.

### Implementation

Add to `/api/routers/runs.py`:

```python
@router.get("/runs/{run_id}/raw-extract/{match_tag}")
def get_raw_extract(
    run_id: str,
    match_tag: str,
    storage: StorageClient = Depends(get_storage_client),
):
    """Raw extraction data for Artifact Preview per D-061."""
    folder = storage.get_run_folder(run_id)
    if not folder:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found.")

    extract = storage.read_raw_extract(run_id, match_tag)
    if not extract:
        raise HTTPException(status_code=404, detail=f"Raw extract for '{match_tag}' not found.")

    return extract
```

### Acceptance criteria

- [ ] Returns the raw extract dict for a valid match_tag
- [ ] 404 if run or match_tag not found

---

## T-E12 — GET /api/runs/{run_id}/issues

**Depends on:** T-E2, T-C4
**Touches files:** `/api/routers/runs.py` (modification)
**Estimated effort:** small

### Goal

Return Issues-tab events (validation_failure, warning, run_failed) sorted by severity.

### Implementation

Add to `/api/routers/runs.py`:

```python
from api.routers.schemas import IssuesResponse, IssueItem
from api.state.events import read_issues_for_run


@router.get("/runs/{run_id}/issues", response_model=IssuesResponse)
def get_issues(
    run_id: str,
    storage: StorageClient = Depends(get_storage_client),
):
    """Issues for the Issues tab per D-049 + D-058."""
    folder = storage.get_run_folder(run_id)
    if not folder:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found.")

    raw_issues = read_issues_for_run(run_id)
    items = [
        IssueItem(
            id=i["id"],
            ts=i["ts"],
            type=i["type"],
            severity=i["payload"].get("severity"),
            message=i["payload"].get("message") or i["payload"].get("rule"),
            payload=i["payload"],
        )
        for i in raw_issues
    ]
    return IssuesResponse(issues=items, total=len(items))
```

### Acceptance criteria

- [ ] Returns issues sorted by severity (critical first, then error, then warning)
- [ ] Empty list if no issue-type events exist for the run
- [ ] 404 for non-existent run

---

## T-E13 — GET /api/runs/{run_id}/events

**Depends on:** T-E2, T-C4
**Touches files:** `/api/routers/runs.py` (modification)
**Estimated effort:** small

### Goal

Return the full event history for the Activity tab replay.

### Implementation

Add to `/api/routers/runs.py`:

```python
from api.routers.schemas import EventsResponse, EventItem
from api.state.events import read_events_for_run


@router.get("/runs/{run_id}/events", response_model=EventsResponse)
def get_events(
    run_id: str,
    storage: StorageClient = Depends(get_storage_client),
):
    """Full event history for the Activity tab per D-040 + D-058."""
    folder = storage.get_run_folder(run_id)
    if not folder:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found.")

    raw_events = read_events_for_run(run_id)
    items = [
        EventItem(id=e["id"], ts=e["ts"], type=e["type"], payload=e["payload"])
        for e in raw_events
    ]
    return EventsResponse(events=items)
```

### Acceptance criteria

- [ ] Returns events in chronological order (ts ASC)
- [ ] Each event includes id, ts, type, payload
- [ ] Empty list for runs with no events
- [ ] 404 for non-existent run

---

## T-E14 — GET /api/runs/{run_id}/pdf

**Depends on:** T-D6
**Touches files:** `/api/routers/runs.py` (modification)
**Estimated effort:** small

### Goal

Serve the agreement PDF for Artifact Preview's PDF viewer pane.

### Implementation

Add to `/api/routers/runs.py`:

```python
from fastapi.responses import FileResponse


@router.get("/runs/{run_id}/pdf")
def get_pdf(
    run_id: str,
    storage: StorageClient = Depends(get_storage_client),
):
    """Serve the agreement PDF per D-061. Used by Artifact Preview."""
    folder = storage.get_run_folder(run_id)
    if not folder:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found.")

    pdf_path = storage.get_pdf_path(run_id)
    if not pdf_path or not pdf_path.exists():
        raise HTTPException(status_code=404, detail="No PDF available for this run.")

    return FileResponse(
        path=str(pdf_path),
        media_type="application/pdf",
        filename=pdf_path.name,
    )
```

### Acceptance criteria

- [ ] Returns the PDF file with `Content-Type: application/pdf`
- [ ] 404 if run exists but no PDF is available
- [ ] 404 for non-existent run

---

## T-E15 — GET /api/runs/{run_id}/jira-info

**Depends on:** T-E2, T-D6
**Touches files:** `/api/routers/runs.py` (modification)
**Estimated effort:** small

### Goal

Return Jira + SharePoint metadata with server-side URL construction per D-073.

### Implementation

Add to `/api/routers/runs.py`:

```python
@router.get("/runs/{run_id}/jira-info")
def get_jira_info(
    run_id: str,
    storage: StorageClient = Depends(get_storage_client),
):
    """Jira + SharePoint metadata with server-constructed URLs per D-073."""
    folder = storage.get_run_folder(run_id)
    if not folder:
        raise HTTPException(status_code=404, detail=f"Run {run_id} not found.")

    info = storage.read_jira_info(run_id)
    if not info:
        raise HTTPException(
            status_code=404,
            detail=f"No Jira submission info for run {run_id}. "
                   f"Run may not have been submitted yet.",
        )
    return info.model_dump()
```

### Acceptance criteria

- [ ] Returns `{epic_key, epic_url, story_key, story_url, sharepoint_path}`
- [ ] URLs use `JPMC_JIRA_BASE_URL` — e.g., `https://jira.jpmchase.net/browse/CMRPEE-142`
- [ ] 404 if run not found or not yet submitted

---

## T-E16 — GET /api/input-folders

**Depends on:** T-D6
**Touches files:** `/api/routers/system.py` (modification)
**Estimated effort:** small

### Goal

List available input folders for the new-run folder selection UI.

### Implementation

Add to `/api/routers/system.py`:

```python
from fastapi import APIRouter, Depends

from api.adapters.factory import get_storage_client
from api.adapters.interfaces import StorageClient
from api.routers.schemas import InputFoldersResponse

router = APIRouter(tags=["system"])


@router.get("/input-folders", response_model=InputFoldersResponse)
def list_input_folders(
    storage: StorageClient = Depends(get_storage_client),
):
    """List available input folders from ALLOWED_INPUT_ROOTS per D-013."""
    folders = storage.list_input_folders()
    return InputFoldersResponse(folders=folders)
```

### Acceptance criteria

- [ ] Returns `{"folders": [...]}` with `InputFolderInfo` items
- [ ] Each item includes `has_old` and `has_new` flags
- [ ] Empty list if no input folders exist under any allowed root

---

## T-E17 — GET /api/locks

**Depends on:** T-C2
**Touches files:** `/api/routers/system.py` (modification)
**Estimated effort:** small

### Goal

Return the current lock state (with PID liveness resolved) for the frontend's SmartFallback resolver and action-button disabling.

### Implementation

Add to `/api/routers/system.py`:

```python
from api.routers.schemas import LockStateResponse
from api.state.locks import get_lock_state


@router.get("/locks", response_model=LockStateResponse)
def get_locks():
    """Current lock state per D-057. PID liveness resolved server-side."""
    state = get_lock_state()
    return LockStateResponse(
        held=state.held,
        held_by_operator=state.held_by_operator,
        run_id=state.run_id,
        phase=state.phase,
        acquired_at=state.acquired_at,
    )
```

### Acceptance criteria

- [ ] Returns `{"held": false, ...}` when no lock is held
- [ ] Returns `{"held": true, "run_id": "...", ...}` when a live process holds the lock
- [ ] Returns `{"held": false, ...}` when the lock row says held=1 but PID is dead (liveness resolved)

---

## T-E18 — GET /api/events (SSE stream)

**Depends on:** T-C5, T1
**Touches files:** `/api/routers/system.py` (modification)
**Estimated effort:** medium

### Goal

Implement the SSE endpoint that streams pipeline events to connected frontend clients per D-060. Uses sse-starlette's `EventSourceResponse`. Supports optional `run_id` filter query parameter.

### Context

From D-060 (SSE design):

> Server-driven cadence. FastAPI emits SSE events as the pipeline subprocess produces them. The frontend subscribes at mount time (Run Detail screen) and receives events in real time.

### Implementation

Add to `/api/routers/system.py`:

```python
import asyncio
import json

from fastapi import Query
from sse_starlette.sse import EventSourceResponse

from api.state.sse import get_broadcaster


@router.get("/events")
async def sse_events(
    run_id: str | None = Query(default=None, description="Filter events to a specific run"),
):
    """SSE event stream per D-060.

    Subscribes to the in-memory EventBroadcaster. Events are pushed in
    real time as the pipeline produces them. On disconnect, the subscriber
    is cleaned up automatically.

    Optional run_id filter: if provided, only events for that run are
    forwarded. The default (no filter) streams all events — useful for
    the Runs List screen's live-update indicators.
    """
    broadcaster = get_broadcaster()
    sub = await broadcaster.subscribe(run_id=run_id)

    async def event_generator():
        try:
            while True:
                try:
                    # Wait for next event with a timeout for keepalive.
                    message = await asyncio.wait_for(sub.queue.get(), timeout=30.0)
                    yield {
                        "event": message.get("type", "message"),
                        "id": str(message.get("id", "")),
                        "data": json.dumps(message),
                    }
                except asyncio.TimeoutError:
                    # Send keepalive comment to prevent connection timeout.
                    yield {"comment": "keepalive"}
        except asyncio.CancelledError:
            pass
        finally:
            await broadcaster.unsubscribe(sub)

    return EventSourceResponse(event_generator())
```

### Acceptance criteria

- [ ] `GET /api/events` returns `Content-Type: text/event-stream`
- [ ] Events emitted by MockPipelineRunner appear in the SSE stream in real time
- [ ] `?run_id=intuit_20260511_155829` filters to only that run's events
- [ ] Without `?run_id`, all events from all runs appear
- [ ] A 30-second keepalive comment is sent when no events are available (prevents nginx/proxy timeout)
- [ ] Disconnecting the client (closing the browser tab) triggers `unsubscribe` cleanup
- [ ] Multiple concurrent SSE connections each receive the same events independently

### Notes

The `EventSourceResponse` from sse-starlette handles the HTTP mechanics: setting headers, encoding SSE frames, managing the generator lifecycle. The `event_generator` async generator yields dicts with `event`, `id`, and `data` keys — sse-starlette formats these into SSE frame text.

The 30-second keepalive timeout is chosen to be well under typical nginx/reverse-proxy timeouts (usually 60s). On JPMC VDI, the direct-connection case (no proxy) doesn't need keepalive, but including it is cheap and prevents surprises if a proxy is later introduced.

The `asyncio.CancelledError` catch handles the client-disconnect case: when the browser closes the connection, FastAPI cancels the response coroutine, which triggers the `finally` block for cleanup. This is the standard pattern for sse-starlette.

The SSE `event` field is set to the event type string (e.g., `"run_started"`, `"stage_progress"`). The frontend's `EventSource.addEventListener('run_started', ...)` can listen for specific types, or use `onmessage` for all events. Section F's SSE client will use the approach that best fits React Query's invalidation model.
# Section F — Frontend infrastructure & shared components

This section builds the frontend spine: API client, React Query hooks, SSE client with cache invalidation, Zustand UI store, Error Boundary, AppShell layout, SmartFallback resolver, BaseTableWithDrawer, shared primitives, and Toast notifications. Every component in Sections G-I depends on this infrastructure.

All components live under `web/src/features/shared/` per D-062's feature-based layout. CSS uses the `var(--token)` pattern from T7 exclusively — no hex literals.

Section index:

- [ ] T-F1 — API client (fetch wrapper + error envelope parsing)
- [ ] T-F2 — React Query hooks + query key factory
- [ ] T-F3 — SSE client + React Query invalidation mapping
- [ ] T-F4 — Zustand UI state store
- [ ] T-F5 — Frontend error catalog + Error Boundary
- [ ] T-F6 — AppShell (layout, gradient background, segmented toggle)
- [ ] T-F7 — SmartFallback route resolver
- [ ] T-F8 — BaseTableWithDrawer (prop-driven reusable table + drawer)
- [ ] T-F9 — Shared primitives (StateBadge, ActionPill, EntryPill, TabBar)
- [ ] T-F10 — Toast notification system

---

## T-F1 — API client (fetch wrapper + error envelope parsing)

**Depends on:** T2, T7
**Touches files:** `/web/src/features/shared/api/client.ts`
**Estimated effort:** small

### Goal

Create a thin fetch wrapper that attaches the `X-Operator-ID` header (from localStorage per D-065), parses the D-061 error envelope on non-2xx responses, and throws typed errors React Query hooks can catch. All endpoint calls in Sections G-I go through this client.

### Implementation

**File: `/web/src/features/shared/api/client.ts`**:

```typescript
/**
 * API client per D-061 + D-065.
 *
 * Every fetch goes through `api()` which:
 * 1. Prepends the base URL from VITE_API_BASE_URL (or defaults to relative origin).
 * 2. Attaches X-Operator-ID from localStorage (or generates one).
 * 3. On non-2xx, parses the D-061 error envelope and throws ApiError.
 */

const BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

// Operator ID per D-065: browser-session-scoped UUID stored in localStorage.
function getOperatorId(): string {
  const KEY = 'ci_ui_operator_id'
  let id = localStorage.getItem(KEY)
  if (!id) {
    id = crypto.randomUUID()
    localStorage.setItem(KEY, id)
  }
  return id
}

export interface ApiErrorBody {
  code: string
  message: string
  remediation_hint?: string
}

export class ApiError extends Error {
  public readonly status: number
  public readonly code: string
  public readonly hint?: string

  constructor(status: number, body: ApiErrorBody) {
    super(body.message)
    this.name = 'ApiError'
    this.status = status
    this.code = body.code
    this.hint = body.remediation_hint
  }
}

export async function api<T = unknown>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const url = `${BASE_URL}${path}`

  const headers = new Headers(options.headers)
  headers.set('X-Operator-ID', getOperatorId())
  if (options.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  const response = await fetch(url, { ...options, headers })

  if (!response.ok) {
    let errorBody: ApiErrorBody
    try {
      const json = await response.json()
      errorBody = json.error || { code: 'UNKNOWN', message: response.statusText }
    } catch {
      errorBody = { code: 'UNKNOWN', message: response.statusText }
    }
    throw new ApiError(response.status, errorBody)
  }

  // Handle 204 No Content or empty body.
  const contentType = response.headers.get('Content-Type') || ''
  if (response.status === 204 || !contentType.includes('application/json')) {
    return undefined as T
  }

  return response.json() as Promise<T>
}

// Convenience methods.
export const apiGet = <T>(path: string) => api<T>(path)

export const apiPost = <T>(path: string, body?: unknown) =>
  api<T>(path, {
    method: 'POST',
    body: body ? JSON.stringify(body) : undefined,
  })
```

### Acceptance criteria

- [ ] `api('/api/health')` returns `{status: 'ok'}` when the backend is running
- [ ] `X-Operator-ID` header is sent on every request (verify in DevTools → Network)
- [ ] On first visit, a UUID is generated and stored in localStorage under `ci_ui_operator_id`
- [ ] A 404 response throws `ApiError` with `code='NOT_FOUND'`, `message` from the envelope
- [ ] A 409 response throws `ApiError` with `code='LOCK_HELD'` and `hint` populated
- [ ] A 500 response throws `ApiError` with `code='INTERNAL_ERROR'`
- [ ] The base URL is read from `VITE_API_BASE_URL`; in dev (Vite proxy) an empty string works correctly

---

## T-F2 — React Query hooks + query key factory

**Depends on:** T-F1, T2
**Touches files:** `/web/src/features/shared/api/queryKeys.ts`, `/web/src/features/shared/api/hooks.ts`
**Estimated effort:** medium

### Goal

Define the query key factory (consistent cache keys mapping to D-061 endpoint URLs) and React Query hooks for each data-fetching endpoint. Mutation hooks for POST endpoints.

### Implementation

**File: `/web/src/features/shared/api/queryKeys.ts`**:

```typescript
/**
 * React Query cache key factory per D-062.
 *
 * Key structure mirrors the D-061 URL namespace:
 *   ['runs']                        → GET /api/runs (list)
 *   ['runs', runId]                 → GET /api/runs/{runId} (detail)
 *   ['runs', runId, 'base-table']   → GET /api/runs/{runId}/base-table
 *   ['runs', runId, 'drawer', tag]  → GET /api/runs/{runId}/drawer/{tag}
 *   ['runs', runId, 'issues']       → GET /api/runs/{runId}/issues
 *   ['runs', runId, 'events']       → GET /api/runs/{runId}/events
 *   ['runs', runId, 'jira-info']    → GET /api/runs/{runId}/jira-info
 *   ['input-folders']               → GET /api/input-folders
 *   ['locks']                       → GET /api/locks
 */

export const queryKeys = {
  runs: {
    all: ['runs'] as const,
    list: (params?: { search?: string; state?: string; page?: number }) =>
      ['runs', { ...params }] as const,
    detail: (runId: string) => ['runs', runId] as const,
    baseTable: (runId: string) => ['runs', runId, 'base-table'] as const,
    drawer: (runId: string, matchTag: string) =>
      ['runs', runId, 'drawer', matchTag] as const,
    rawExtract: (runId: string, matchTag: string) =>
      ['runs', runId, 'raw-extract', matchTag] as const,
    issues: (runId: string) => ['runs', runId, 'issues'] as const,
    events: (runId: string) => ['runs', runId, 'events'] as const,
    jiraInfo: (runId: string) => ['runs', runId, 'jira-info'] as const,
    pdf: (runId: string) => ['runs', runId, 'pdf'] as const,
  },
  inputFolders: ['input-folders'] as const,
  locks: ['locks'] as const,
} as const
```

**File: `/web/src/features/shared/api/hooks.ts`**:

```typescript
/**
 * React Query hooks for D-061 endpoints.
 *
 * Query hooks use the key factory above.
 * Mutation hooks use retry: false per D-064.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { api, apiGet, apiPost } from './client'
import { queryKeys } from './queryKeys'

// --- Types matching Section E response schemas ---

export interface RunSummary {
  run_id: string
  folder_path: string
  merchant: string
  created_at: string
  state: string | null
  has_base_table: boolean
  issue_count: number | null
}

export interface RunListResponse {
  runs: RunSummary[]
  total: number
  page: number
  page_size: number
}

export interface RunDetailResponse {
  run: RunSummary
  failure: Record<string, unknown> | null
  available_actions: string[]
}

export interface BaseTableRow {
  match_tag: string
  maid?: string
  mnemonic?: string
  action?: string
  change_type?: string
  system_update?: string
  [key: string]: unknown
}

export interface BaseTableResponse {
  rows: BaseTableRow[]
  total: number
}

export interface IssueItem {
  id: number
  ts: string
  type: string
  severity?: string
  message?: string
  payload: Record<string, unknown>
}

export interface EventItem {
  id: number
  ts: string
  type: string
  payload: Record<string, unknown>
}

export interface LockState {
  held: boolean
  held_by_operator?: string
  run_id?: string
  phase?: string
  acquired_at?: string
}

export interface InputFolder {
  path: string
  name: string
  root: string
  has_old: boolean
  has_new: boolean
}

export interface JiraInfo {
  epic_key?: string
  epic_url?: string
  story_key?: string
  story_url?: string
  sharepoint_path?: string
}

// --- Query hooks ---

export function useRunsList(params?: {
  search?: string
  state?: string
  page?: number
  pageSize?: number
}) {
  const qs = new URLSearchParams()
  if (params?.search) qs.set('search', params.search)
  if (params?.state) qs.set('state', params.state)
  if (params?.page) qs.set('page', String(params.page))
  if (params?.pageSize) qs.set('page_size', String(params.pageSize))
  const suffix = qs.toString() ? `?${qs}` : ''

  return useQuery({
    queryKey: queryKeys.runs.list(params),
    queryFn: () => apiGet<RunListResponse>(`/api/runs${suffix}`),
  })
}

export function useRunDetail(runId: string) {
  return useQuery({
    queryKey: queryKeys.runs.detail(runId),
    queryFn: () => apiGet<RunDetailResponse>(`/api/runs/${runId}`),
    enabled: !!runId,
  })
}

export function useBaseTable(runId: string) {
  return useQuery({
    queryKey: queryKeys.runs.baseTable(runId),
    queryFn: () => apiGet<BaseTableResponse>(`/api/runs/${runId}/base-table`),
    enabled: !!runId,
  })
}

export function useDrawerRecord(runId: string, matchTag: string) {
  return useQuery({
    queryKey: queryKeys.runs.drawer(runId, matchTag),
    queryFn: () => apiGet<Record<string, unknown>>(`/api/runs/${runId}/drawer/${matchTag}`),
    enabled: !!runId && !!matchTag,
  })
}

export function useRawExtract(runId: string, matchTag: string) {
  return useQuery({
    queryKey: queryKeys.runs.rawExtract(runId, matchTag),
    queryFn: () => apiGet<Record<string, unknown>>(`/api/runs/${runId}/raw-extract/${matchTag}`),
    enabled: !!runId && !!matchTag,
  })
}

export function useIssues(runId: string) {
  return useQuery({
    queryKey: queryKeys.runs.issues(runId),
    queryFn: () => apiGet<{ issues: IssueItem[]; total: number }>(`/api/runs/${runId}/issues`),
    enabled: !!runId,
  })
}

export function useEvents(runId: string) {
  return useQuery({
    queryKey: queryKeys.runs.events(runId),
    queryFn: () => apiGet<{ events: EventItem[] }>(`/api/runs/${runId}/events`),
    enabled: !!runId,
  })
}

export function useJiraInfo(runId: string) {
  return useQuery({
    queryKey: queryKeys.runs.jiraInfo(runId),
    queryFn: () => apiGet<JiraInfo>(`/api/runs/${runId}/jira-info`),
    enabled: !!runId,
  })
}

export function useInputFolders() {
  return useQuery({
    queryKey: queryKeys.inputFolders,
    queryFn: () => apiGet<{ folders: InputFolder[] }>('/api/input-folders'),
  })
}

export function useLockState() {
  return useQuery({
    queryKey: queryKeys.locks,
    queryFn: () => apiGet<LockState>('/api/locks'),
    refetchInterval: 5_000, // Poll every 5s for lock state changes
  })
}

// --- Mutation hooks (retry: false per D-064) ---

export function useStartRun() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (input: { input_folder: string }) =>
      apiPost<{ status: string; run_id: string; message: string }>(
        '/api/runs/start',
        input,
      ),
    retry: false,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.runs.all })
      qc.invalidateQueries({ queryKey: queryKeys.locks })
    },
  })
}

export function useApproveRun() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (runId: string) =>
      apiPost<{ status: string; run_id: string }>(`/api/runs/${runId}/approve`),
    retry: false,
    onSuccess: (_data, runId) => {
      qc.invalidateQueries({ queryKey: queryKeys.runs.detail(runId) })
      qc.invalidateQueries({ queryKey: queryKeys.locks })
    },
  })
}

export function useRetryApprove() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (runId: string) =>
      apiPost<{ status: string; run_id: string }>(`/api/runs/${runId}/retry-approve`),
    retry: false,
    onSuccess: (_data, runId) => {
      qc.invalidateQueries({ queryKey: queryKeys.runs.detail(runId) })
      qc.invalidateQueries({ queryKey: queryKeys.locks })
    },
  })
}

export function useRerunFromScratch() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (input: { runId: string; input_folder: string }) =>
      apiPost<{ status: string; run_id: string; message: string }>(
        `/api/runs/${input.runId}/rerun`,
        { input_folder: input.input_folder },
      ),
    retry: false,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.runs.all })
      qc.invalidateQueries({ queryKey: queryKeys.locks })
    },
  })
}
```

### Acceptance criteria

- [ ] `queryKeys` object produces stable, unique keys for every D-061 endpoint
- [ ] All query hooks use the key factory (no inline string arrays)
- [ ] All mutation hooks have `retry: false` per D-064
- [ ] Mutations invalidate the relevant queries on success (list + detail + locks)
- [ ] `useRunDetail(runId)` is disabled when runId is empty string
- [ ] `useLockState` polls every 5 seconds via `refetchInterval`
- [ ] TypeScript types match the Section E response schemas

---

## T-F3 — SSE client + React Query invalidation mapping

**Depends on:** T-F2, T2
**Touches files:** `/web/src/features/shared/sse/client.ts`, `/web/src/features/shared/sse/useSSE.ts`
**Estimated effort:** medium

### Goal

Create an EventSource wrapper that subscribes to `GET /api/events`, parses SSE frames, and invalidates the relevant React Query cache keys per D-062. The hook `useSSE(runId?)` is called from screen-level components to keep live data flowing.

### Context

From D-062 (Frontend architecture):

> SSE-driven invalidation: when an SSE event arrives, the React Query cache is invalidated for the affected queries. The frontend re-fetches the stale data automatically.

### Implementation

**File: `/web/src/features/shared/sse/client.ts`**:

```typescript
/**
 * SSE client wrapper per D-060.
 *
 * Manages EventSource lifecycle. On each event, calls the provided
 * onEvent callback with the parsed event data. Reconnects automatically
 * on disconnect (EventSource default behavior).
 */

export interface SSEEvent {
  id?: number
  run_id: string
  type: string
  payload: Record<string, unknown>
  ts?: string
}

export function createSSEClient(
  runId?: string,
  onEvent?: (event: SSEEvent) => void,
): { close: () => void } {
  const baseUrl = import.meta.env.VITE_API_BASE_URL || ''
  const url = runId
    ? `${baseUrl}/api/events?run_id=${encodeURIComponent(runId)}`
    : `${baseUrl}/api/events`

  const source = new EventSource(url)

  source.onmessage = (msg) => {
    try {
      const data: SSEEvent = JSON.parse(msg.data)
      onEvent?.(data)
    } catch {
      // Non-JSON message (keepalive comment) — ignore.
    }
  }

  source.onerror = () => {
    // EventSource reconnects automatically. Log for dev visibility.
    console.debug('[SSE] Connection error; EventSource will reconnect.')
  }

  return {
    close: () => source.close(),
  }
}
```

**File: `/web/src/features/shared/sse/useSSE.ts`**:

```typescript
/**
 * React hook that subscribes to SSE events and invalidates React Query
 * cache keys based on event type per D-062.
 *
 * Usage:
 *   useSSE()              — global subscription (Runs List live indicators)
 *   useSSE('run-123')     — filtered to a single run (Run Detail Activity)
 */

import { useEffect } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { createSSEClient, SSEEvent } from './client'
import { queryKeys } from '../api/queryKeys'

// Map event types to the cache keys they should invalidate.
// This is the single source of truth for the SSE → React Query bridge.
const INVALIDATION_MAP: Record<string, (runId: string) => readonly unknown[][]> = {
  // Run lifecycle events → refresh run detail + runs list + lock state.
  run_started: (runId) => [
    queryKeys.runs.all,
    queryKeys.runs.detail(runId),
    queryKeys.locks,
  ],
  run_failed: (runId) => [
    queryKeys.runs.all,
    queryKeys.runs.detail(runId),
    queryKeys.runs.issues(runId),
    queryKeys.runs.events(runId),
    queryKeys.locks,
  ],

  // Stage events → refresh events (Activity tab) + run detail (state badge).
  stage_started: (runId) => [queryKeys.runs.events(runId)],
  stage_progress: (runId) => [queryKeys.runs.events(runId)],
  stage_completed: (runId) => [queryKeys.runs.events(runId)],

  // Validation/warning → refresh issues + events.
  validation_failure: (runId) => [
    queryKeys.runs.issues(runId),
    queryKeys.runs.events(runId),
  ],
  warning: (runId) => [
    queryKeys.runs.issues(runId),
    queryKeys.runs.events(runId),
  ],

  // Comparison ready → refresh base table + events.
  comparison_ready: (runId) => [
    queryKeys.runs.baseTable(runId),
    queryKeys.runs.events(runId),
  ],

  // Pre-approval → refresh run detail (state change) + events + list.
  pre_approval_reached: (runId) => [
    queryKeys.runs.all,
    queryKeys.runs.detail(runId),
    queryKeys.runs.events(runId),
    queryKeys.locks,
  ],

  // Approval flow.
  approval_submitted: (runId) => [
    queryKeys.runs.detail(runId),
    queryKeys.runs.events(runId),
    queryKeys.locks,
  ],
  jira_created: (runId) => [
    queryKeys.runs.jiraInfo(runId),
    queryKeys.runs.events(runId),
  ],
  sharepoint_synced: (runId) => [queryKeys.runs.events(runId)],
  submission_complete: (runId) => [
    queryKeys.runs.all,
    queryKeys.runs.detail(runId),
    queryKeys.runs.jiraInfo(runId),
    queryKeys.runs.events(runId),
    queryKeys.locks,
  ],
}

export function useSSE(runId?: string) {
  const queryClient = useQueryClient()

  useEffect(() => {
    const client = createSSEClient(runId, (event: SSEEvent) => {
      const getKeys = INVALIDATION_MAP[event.type]
      if (!getKeys) return

      const keySets = getKeys(event.run_id)
      for (const key of keySets) {
        queryClient.invalidateQueries({ queryKey: key as readonly unknown[] })
      }
    })

    return () => client.close()
  }, [runId, queryClient])
}
```

### Acceptance criteria

- [ ] `useSSE()` subscribes to the global SSE stream on mount and closes on unmount
- [ ] `useSSE('run-123')` subscribes filtered to that run's events
- [ ] When a `run_started` event arrives, React Query invalidates `['runs']`, `['runs', runId]`, and `['locks']`
- [ ] When `pre_approval_reached` arrives, the Runs List and Run Detail both refetch
- [ ] When `validation_failure` arrives, the Issues tab query is invalidated
- [ ] The invalidation map covers all 13 D-059 event types
- [ ] No memory leaks — EventSource is closed on component unmount

---

## T-F4 — Zustand UI state store

**Depends on:** T2
**Touches files:** `/web/src/features/shared/stores/uiStore.ts`
**Estimated effort:** small

### Goal

Create the Zustand store for UI-only state per D-062: current filter chip selection, drawer open/closed + selected match_tag, search input value, Artifact Preview divider position, current Run Detail tab.

### Implementation

**File: `/web/src/features/shared/stores/uiStore.ts`**:

```typescript
/**
 * Zustand UI state store per D-062.
 *
 * This store holds ONLY client-side UI state. Server state (runs, events,
 * base table data) lives in React Query. The boundary is: if losing the
 * value on page refresh is acceptable, it goes in Zustand. If it must
 * survive refresh, it goes in React Query (which refetches from the API).
 */

import { create } from 'zustand'

export type RunDetailTab = 'activity' | 'results' | 'issues'

interface UIState {
  // Runs List filters
  searchQuery: string
  stateFilter: string | null
  currentPage: number

  // Run Detail
  activeTab: RunDetailTab
  drawerOpen: boolean
  drawerMatchTag: string | null

  // Artifact Preview
  dividerPosition: number  // 0-100 percentage (left pane width)

  // Actions
  setSearchQuery: (q: string) => void
  setStateFilter: (s: string | null) => void
  setCurrentPage: (p: number) => void
  setActiveTab: (tab: RunDetailTab) => void
  openDrawer: (matchTag: string) => void
  closeDrawer: () => void
  setDividerPosition: (pos: number) => void
  resetFilters: () => void
}

export const useUIStore = create<UIState>((set) => ({
  // Defaults
  searchQuery: '',
  stateFilter: null,
  currentPage: 1,
  activeTab: 'activity',
  drawerOpen: false,
  drawerMatchTag: null,
  dividerPosition: 50,

  // Setters
  setSearchQuery: (q) => set({ searchQuery: q, currentPage: 1 }),
  setStateFilter: (s) => set({ stateFilter: s, currentPage: 1 }),
  setCurrentPage: (p) => set({ currentPage: p }),
  setActiveTab: (tab) => set({ activeTab: tab }),
  openDrawer: (matchTag) => set({ drawerOpen: true, drawerMatchTag: matchTag }),
  closeDrawer: () => set({ drawerOpen: false, drawerMatchTag: null }),
  setDividerPosition: (pos) => set({ dividerPosition: pos }),
  resetFilters: () => set({ searchQuery: '', stateFilter: null, currentPage: 1 }),
}))
```

### Acceptance criteria

- [ ] `useUIStore` exports a Zustand hook with all listed state fields and actions
- [ ] `setSearchQuery` resets `currentPage` to 1 (new search = new pagination)
- [ ] `openDrawer('MT001')` sets both `drawerOpen: true` and `drawerMatchTag: 'MT001'`
- [ ] `closeDrawer()` clears both fields
- [ ] Default `activeTab` is `'activity'` per the mockup's initial tab state
- [ ] Default `dividerPosition` is `50` (equal split)

---

## T-F5 — Frontend error catalog + Error Boundary

**Depends on:** T3 (scaffold), T-F1
**Touches files:** `/web/src/features/shared/errors/messages.ts` (populate), `/web/src/features/shared/errors/ErrorBoundary.tsx`
**Estimated effort:** small

### Goal

Populate the error message catalog scaffolded in T3 and create the root-level Error Boundary per D-064.

### Implementation

**Populate `/web/src/features/shared/errors/messages.ts`**:

```typescript
export const FRONTEND_ERROR_MESSAGES: Record<string, { message: string; hint?: string }> = {
  NETWORK_UNREACHABLE: {
    message: 'Could not reach the server.',
    hint: 'Check that the backend is running and try again.',
  },
  SSE_DISCONNECTED: {
    message: 'Live event stream disconnected.',
    hint: 'The page will attempt to reconnect automatically.',
  },
  PDF_RENDER_FAILED: {
    message: 'Could not render the PDF.',
    hint: 'The file may be corrupted or too large. Try downloading it directly.',
  },
  UNEXPECTED_ERROR: {
    message: 'Something unexpected went wrong.',
    hint: 'Try refreshing the page. If this persists, check the server logs.',
  },
}
```

**File: `/web/src/features/shared/errors/ErrorBoundary.tsx`**:

```typescript
/**
 * Root Error Boundary per D-064.
 *
 * Catches unhandled React errors and renders a recovery UI.
 * Per D-064 calibration: one Error Boundary at the app root, not per-pane.
 */

import { Component, ReactNode } from 'react'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error('[ErrorBoundary] Caught:', error, info.componentStack)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          display: 'flex', flexDirection: 'column', alignItems: 'center',
          justifyContent: 'center', height: '100vh', gap: 16,
          background: 'var(--bg)', color: 'var(--ink)',
          fontFamily: 'var(--font-sans)', padding: 32,
        }}>
          <h2 style={{ color: 'var(--amber)', fontWeight: 600, fontSize: 20 }}>
            Something went wrong
          </h2>
          <p style={{ color: 'var(--ink-soft)', maxWidth: 400, textAlign: 'center' }}>
            {this.state.error?.message || 'An unexpected error occurred.'}
          </p>
          <button
            onClick={() => {
              this.setState({ hasError: false, error: null })
              window.location.reload()
            }}
            style={{
              padding: '8px 20px', borderRadius: 'var(--radius-sm)',
              background: 'var(--glass-strong)', border: '1px solid var(--glass-stroke)',
              color: 'var(--ink)', cursor: 'pointer', fontSize: 14,
            }}
          >
            Reload page
          </button>
        </div>
      )
    }
    return this.props.children
  }
}
```

### Acceptance criteria

- [ ] Error catalog has 4 entries: NETWORK_UNREACHABLE, SSE_DISCONNECTED, PDF_RENDER_FAILED, UNEXPECTED_ERROR
- [ ] ErrorBoundary catches thrown errors in child components and renders the recovery UI
- [ ] The "Reload page" button calls `window.location.reload()`
- [ ] All colors in the Error Boundary use `var(--token)` — no hex literals

---

## T-F6 — AppShell (layout, gradient background, segmented toggle)

**Depends on:** T7, T6, T-F5
**Touches files:** `/web/src/features/shared/components/AppShell.tsx`, `/web/src/features/shared/components/AppShell.css`
**Estimated effort:** medium

### Goal

Create the app-level layout shell: gradient animated background, top header bar with logo text and Run Status segmented toggle per the visual mockup. Wraps the route outlet (`<Outlet />`). Updated `App.tsx` to render `<AppShell>` with routes.

### Implementation

**File: `/web/src/features/shared/components/AppShell.css`**:

```css
/* AppShell layout per visual mockup GlobalStyle + AppLayout */

.app-shell {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  position: relative;
}

/* Animated gradient background per D-068 deep oceanic */
.app-bg {
  position: fixed;
  inset: 0;
  z-index: 0;
  background:
    radial-gradient(ellipse 120% 80% at 20% 100%, rgba(14, 165, 233, 0.07), transparent 50%),
    radial-gradient(ellipse 80% 60% at 80% 20%, rgba(94, 234, 212, 0.05), transparent 40%),
    var(--bg);
  animation: ciDrift 30s ease-in-out infinite alternate;
}

@keyframes ciDrift {
  0% { background-position: 0% 50%; }
  100% { background-position: 100% 50%; }
}

/* Film-grain overlay */
.app-grain {
  position: fixed;
  inset: 0;
  z-index: 1;
  opacity: 0.015;
  pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}

.app-header {
  position: relative;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 32px;
  border-bottom: 1px solid var(--glass-stroke);
  background: var(--glass);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
}

.app-logo {
  font-family: var(--font-sans);
  font-weight: 700;
  font-size: 18px;
  letter-spacing: -0.02em;
  color: var(--ink);
}

.app-logo span {
  color: var(--cyan);
}

.app-content {
  position: relative;
  z-index: 2;
  flex: 1;
  padding: 24px 32px;
  overflow-y: auto;
}

/* Segmented toggle (Runs List / Run Detail navigation) */
.seg-toggle {
  display: inline-flex;
  background: var(--glass);
  border: 1px solid var(--glass-stroke);
  border-radius: var(--radius);
  padding: 3px;
  gap: 2px;
}

.seg-toggle button {
  padding: 6px 16px;
  border: none;
  background: transparent;
  color: var(--ink-soft);
  font-family: var(--font-sans);
  font-size: 13px;
  font-weight: 500;
  border-radius: calc(var(--radius) - 3px);
  cursor: pointer;
  transition: all 0.15s;
}

.seg-toggle button:hover {
  color: var(--ink);
}

.seg-toggle button.active {
  background: var(--glass-strong);
  color: var(--ink);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}
```

**File: `/web/src/features/shared/components/AppShell.tsx`**:

```typescript
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import './AppShell.css'

export function AppShell() {
  const navigate = useNavigate()
  const location = useLocation()

  const isRunsList = location.pathname === '/runs' || location.pathname === '/'
  const isRunDetail = location.pathname.startsWith('/runs/') && location.pathname !== '/runs'

  return (
    <div className="app-shell">
      <div className="app-bg" />
      <div className="app-grain" />
      <header className="app-header">
        <div className="app-logo">
          Custom <span>Interchange</span>
        </div>
        <div className="seg-toggle">
          <button
            className={isRunsList ? 'active' : ''}
            onClick={() => navigate('/runs')}
          >
            Runs
          </button>
          <button
            className={isRunDetail ? 'active' : ''}
            onClick={() => {
              // If on a run detail already, stay. Otherwise do nothing
              // (can't navigate to "run detail" without a run_id).
              if (!isRunDetail) return
            }}
          >
            Detail
          </button>
        </div>
      </header>
      <main className="app-content">
        <Outlet />
      </main>
    </div>
  )
}
```

**Modification to `/web/src/App.tsx`** — replace scaffold placeholder:

```typescript
import { Routes, Route, Navigate } from 'react-router-dom'
import { ErrorBoundary } from '@/features/shared/errors/ErrorBoundary'
import { AppShell } from '@/features/shared/components/AppShell'

// Screens imported lazily in Sections G, H, I.
// For now, placeholder components until those sections land.
function RunsListPlaceholder() {
  return <div style={{ color: 'var(--ink-soft)' }}>Runs List — Section G</div>
}
function RunDetailPlaceholder() {
  return <div style={{ color: 'var(--ink-soft)' }}>Run Detail — Section H</div>
}

export default function App() {
  return (
    <ErrorBoundary>
      <Routes>
        <Route element={<AppShell />}>
          <Route path="/" element={<SmartFallbackPlaceholder />} />
          <Route path="/runs" element={<RunsListPlaceholder />} />
          <Route path="/runs/new" element={<RunDetailPlaceholder />} />
          <Route path="/runs/:id" element={<RunDetailPlaceholder />} />
          <Route path="/runs/:id/artifact" element={<div>Artifact Preview — Section I</div>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </ErrorBoundary>
  )
}

function SmartFallbackPlaceholder() {
  return <Navigate to="/runs" replace />
}
```

### Acceptance criteria

- [ ] AppShell renders the gradient background with animation
- [ ] Header shows "Custom Interchange" logo with "Interchange" in cyan
- [ ] Segmented toggle highlights "Runs" when on /runs and "Detail" when on /runs/:id
- [ ] `<Outlet />` renders the routed screen content
- [ ] All colors use CSS variables (no hex literals in .css or .tsx)
- [ ] Error Boundary wraps the entire route tree
- [ ] Route table matches D-062's route definitions

---

## T-F7 — SmartFallback route resolver

**Depends on:** T-F2, T-F6
**Touches files:** `/web/src/features/shared/components/SmartFallback.tsx`
**Estimated effort:** small

### Goal

Implement the `/` route resolver per D-038: query `GET /api/locks`; if a lock is held, redirect to `/runs/:held_run_id`; otherwise redirect to `/runs`.

### Implementation

**File: `/web/src/features/shared/components/SmartFallback.tsx`**:

```typescript
import { Navigate } from 'react-router-dom'
import { useLockState } from '@/features/shared/api/hooks'

export function SmartFallback() {
  const { data: lock, isLoading } = useLockState()

  if (isLoading) {
    return <div style={{ color: 'var(--ink-mute)', padding: 32 }}>Loading...</div>
  }

  if (lock?.held && lock.run_id) {
    return <Navigate to={`/runs/${lock.run_id}`} replace />
  }

  return <Navigate to="/runs" replace />
}
```

Update `App.tsx`: replace `<SmartFallbackPlaceholder />` with `<SmartFallback />` and import it.

### Acceptance criteria

- [ ] `/` redirects to `/runs` when no lock is held
- [ ] `/` redirects to `/runs/:run_id` when a lock is held (operator probably wants to see the active run)
- [ ] Shows a brief loading state while the lock query is in flight

---

## T-F8 — BaseTableWithDrawer (prop-driven reusable table + drawer)

**Depends on:** T7, T-F4
**Touches files:** `/web/src/features/shared/components/BaseTableWithDrawer.tsx`, `/web/src/features/shared/components/BaseTableWithDrawer.css`
**Estimated effort:** large

### Goal

Build the dumb, prop-driven table + sliding drawer component shared by Run Detail Results tab (Section H) and Artifact Preview (Section I) per D-062. The component receives data and callbacks via props; it has no data-fetching or global-store access. Parents own React Query hooks and pass data down.

### Context

From D-062 (Frontend component architecture):

> `BaseTableWithDrawer` is the dumb prop-driven component used by both Run Detail Results tab and Artifact Preview's artifact pane. Component contains no data-fetching or global-store access; parents own React Query hooks and pass data down.

From the Phase 4 closing packet:

> `.data-table-flat` carve-out applies to this table — flat cells against the dark navy base, NOT atmospheric glass.

### Implementation

**File: `/web/src/features/shared/components/BaseTableWithDrawer.css`**:

```css
.base-table-container {
  display: flex;
  height: 100%;
  position: relative;
  overflow: hidden;
}

.base-table-wrapper {
  flex: 1;
  overflow: auto;
}

/* Apply the flat carve-out per D-068 + Phase 4 closing */
.base-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  font-size: 13px;
  font-family: var(--font-sans);
}

.base-table thead {
  position: sticky;
  top: 0;
  z-index: 5;
}

.base-table th {
  padding: 10px 12px;
  text-align: left;
  font-weight: 600;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--ink-mute);
  background: var(--bg-elev);
  border-bottom: 1px solid var(--glass-stroke);
  white-space: nowrap;
}

.base-table td {
  padding: 10px 12px;
  color: var(--ink-soft);
  border-bottom: 1px solid var(--glass-stroke);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 200px;
}

.base-table tr {
  cursor: pointer;
  transition: background 0.1s;
}

.base-table tr:hover {
  background: var(--glass);
}

.base-table tr.selected {
  background: var(--cyan-soft);
}

/* Mono cells for IDs, MAIDs, mnemonics */
.base-table td.mono {
  font-family: var(--font-mono);
  font-size: 12px;
  font-feature-settings: "tnum", "ss01";
}

/* Drawer panel */
.drawer-overlay {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 420px;
  background: var(--bg-elev);
  border-left: 1px solid var(--glass-stroke);
  box-shadow: -8px 0 32px rgba(0, 0, 0, 0.3);
  transform: translateX(100%);
  transition: transform 0.2s ease;
  overflow-y: auto;
  z-index: 10;
}

.drawer-overlay.open {
  transform: translateX(0);
}

.drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-bottom: 1px solid var(--glass-stroke);
}

.drawer-header h3 {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  color: var(--ink);
}

.drawer-close {
  background: none;
  border: none;
  color: var(--ink-mute);
  cursor: pointer;
  font-size: 18px;
  padding: 4px;
}

.drawer-close:hover {
  color: var(--ink);
}

.drawer-body {
  padding: 16px 20px;
}
```

**File: `/web/src/features/shared/components/BaseTableWithDrawer.tsx`**:

```typescript
/**
 * BaseTableWithDrawer — dumb, prop-driven component per D-062.
 *
 * Renders a data table (flat, per D-068 carve-out) with a sliding
 * drawer panel. No data-fetching, no global-store access. Parents
 * pass data + callbacks.
 */

import { ReactNode } from 'react'
import './BaseTableWithDrawer.css'

export interface ColumnDef<T> {
  key: string
  header: string
  render?: (row: T) => ReactNode
  mono?: boolean   // Use monospace font for this column
  width?: string   // CSS width
}

interface Props<T> {
  columns: ColumnDef<T>[]
  rows: T[]
  getRowKey: (row: T) => string
  selectedKey?: string | null
  onRowClick?: (row: T) => void

  // Drawer
  drawerOpen?: boolean
  drawerTitle?: string
  drawerContent?: ReactNode
  onDrawerClose?: () => void
}

export function BaseTableWithDrawer<T extends Record<string, unknown>>({
  columns,
  rows,
  getRowKey,
  selectedKey,
  onRowClick,
  drawerOpen = false,
  drawerTitle,
  drawerContent,
  onDrawerClose,
}: Props<T>) {
  return (
    <div className="base-table-container data-table-flat">
      <div className="base-table-wrapper">
        <table className="base-table">
          <thead>
            <tr>
              {columns.map((col) => (
                <th key={col.key} style={col.width ? { width: col.width } : undefined}>
                  {col.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => {
              const key = getRowKey(row)
              return (
                <tr
                  key={key}
                  className={selectedKey === key ? 'selected' : ''}
                  onClick={() => onRowClick?.(row)}
                >
                  {columns.map((col) => (
                    <td
                      key={col.key}
                      className={col.mono ? 'mono' : ''}
                    >
                      {col.render
                        ? col.render(row)
                        : String(row[col.key] ?? '')}
                    </td>
                  ))}
                </tr>
              )
            })}
            {rows.length === 0 && (
              <tr>
                <td
                  colSpan={columns.length}
                  style={{ textAlign: 'center', color: 'var(--ink-dim)', padding: 32 }}
                >
                  No data available
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className={`drawer-overlay ${drawerOpen ? 'open' : ''}`}>
        <div className="drawer-header">
          <h3>{drawerTitle || 'Details'}</h3>
          <button className="drawer-close" onClick={onDrawerClose}>✕</button>
        </div>
        <div className="drawer-body">
          {drawerContent}
        </div>
      </div>
    </div>
  )
}
```

### Acceptance criteria

- [ ] `BaseTableWithDrawer` renders a table with configurable columns and rows
- [ ] Clicking a row calls `onRowClick` and highlights the row via `selectedKey`
- [ ] Drawer slides in from the right when `drawerOpen` is true
- [ ] Drawer close button calls `onDrawerClose`
- [ ] Table uses `.data-table-flat` carve-out class (flat background, no glass)
- [ ] Mono columns use `var(--font-mono)` for IDs, MAIDs, etc.
- [ ] Empty state shows "No data available" centered across all columns
- [ ] Component accepts no hooks or stores — pure props (verify: no `use*` calls in the file)

---

## T-F9 — Shared primitives (StateBadge, ActionPill, EntryPill, TabBar)

**Depends on:** T7
**Touches files:** `/web/src/features/shared/components/StateBadge.tsx`, `/web/src/features/shared/components/ActionPill.tsx`, `/web/src/features/shared/components/EntryPill.tsx`, `/web/src/features/shared/components/TabBar.tsx`
**Estimated effort:** medium

### Goal

Build the four shared primitive components used throughout Sections G, H, and I per D-045 / D-047 / D-049.

### Implementation

**File: `/web/src/features/shared/components/StateBadge.tsx`**:

```typescript
/**
 * StateBadge per D-045 state coloring.
 * Renders a small colored pill with the run state label.
 */

const STATE_CONFIG: Record<string, { label: string; color: string; bg: string }> = {
  pre_approval: { label: 'Pre-Approval', color: 'var(--state-pre)', bg: 'rgba(247,210,143,0.14)' },
  submitted:    { label: 'Submitted',    color: 'var(--state-sub)', bg: 'rgba(110,231,160,0.14)' },
  stale:        { label: 'Stale',        color: 'var(--state-stale)', bg: 'rgba(148,163,184,0.12)' },
  in_progress:  { label: 'In Progress',  color: 'var(--state-prog)', bg: 'rgba(125,211,252,0.14)' },
  failed:       { label: 'Failed',       color: 'var(--state-fail)', bg: 'rgba(252,165,165,0.14)' },
}

export function StateBadge({ state }: { state: string }) {
  const cfg = STATE_CONFIG[state] || STATE_CONFIG.stale
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 6,
      padding: '3px 10px', borderRadius: 'var(--radius-sm)',
      fontSize: 12, fontWeight: 600, letterSpacing: '0.02em',
      color: cfg.color, background: cfg.bg,
    }}>
      <span style={{
        width: 6, height: 6, borderRadius: '50%', background: cfg.color,
      }} />
      {cfg.label}
    </span>
  )
}
```

**File: `/web/src/features/shared/components/ActionPill.tsx`**:

```typescript
/**
 * ActionPill per D-047 base-table action coloring.
 * Maps action strings to colored pills: Add (green), Remove (red),
 * Rate Update (amber), MCC Expansion (blue).
 */

const ACTION_CONFIG: Record<string, { color: string; bg: string }> = {
  'Add':           { color: 'var(--add)',    bg: 'var(--add-bg)' },
  'Remove':        { color: 'var(--remove)', bg: 'var(--remove-bg)' },
  'Rate Update':   { color: 'var(--rate)',   bg: 'var(--rate-bg)' },
  'MCC Expansion': { color: 'var(--mcc)',    bg: 'var(--mcc-bg)' },
}

export function ActionPill({ action }: { action: string }) {
  const cfg = ACTION_CONFIG[action] || { color: 'var(--ink-mute)', bg: 'var(--glass)' }
  return (
    <span style={{
      display: 'inline-block', padding: '2px 8px',
      borderRadius: 'var(--radius-sm)', fontSize: 11,
      fontWeight: 600, color: cfg.color, background: cfg.bg,
    }}>
      {action}
    </span>
  )
}
```

**File: `/web/src/features/shared/components/EntryPill.tsx`**:

```typescript
/**
 * EntryPill per D-047 drawer ETL Impact tier.
 * Maps entry_type to colored pills: ADD (green), REMOVE (red),
 * NO_CHANGE (gray), PEOPLESOFT_ONLY (purple).
 */

const ENTRY_CONFIG: Record<string, { color: string; bg: string }> = {
  'ADD':             { color: 'var(--add)',      bg: 'var(--add-bg)' },
  'REMOVE':          { color: 'var(--remove)',   bg: 'var(--remove-bg)' },
  'NO_CHANGE':       { color: 'var(--nochange)', bg: 'var(--nochange-bg)' },
  'PEOPLESOFT_ONLY': { color: 'var(--psonly)',    bg: 'var(--psonly-bg)' },
}

export function EntryPill({ entryType }: { entryType: string }) {
  const cfg = ENTRY_CONFIG[entryType] || { color: 'var(--ink-mute)', bg: 'var(--glass)' }
  return (
    <span style={{
      display: 'inline-block', padding: '2px 8px',
      borderRadius: 'var(--radius-sm)', fontSize: 11,
      fontWeight: 600, color: cfg.color, background: cfg.bg,
    }}>
      {entryType}
    </span>
  )
}
```

**File: `/web/src/features/shared/components/TabBar.tsx`**:

```typescript
/**
 * TabBar — shared tab component for Run Detail's Activity/Results/Issues tabs.
 * Per D-062: tab state is in-session (Zustand), not in URL.
 */

interface Tab {
  key: string
  label: string
  badge?: number | null  // e.g., issue count
}

interface Props {
  tabs: Tab[]
  activeKey: string
  onChange: (key: string) => void
}

export function TabBar({ tabs, activeKey, onChange }: Props) {
  return (
    <div style={{
      display: 'flex', gap: 2,
      borderBottom: '1px solid var(--glass-stroke)',
      padding: '0 0 0 4px',
    }}>
      {tabs.map((tab) => (
        <button
          key={tab.key}
          onClick={() => onChange(tab.key)}
          style={{
            padding: '10px 18px',
            border: 'none',
            background: activeKey === tab.key ? 'var(--glass)' : 'transparent',
            color: activeKey === tab.key ? 'var(--ink)' : 'var(--ink-mute)',
            fontFamily: 'var(--font-sans)',
            fontSize: 13,
            fontWeight: activeKey === tab.key ? 600 : 400,
            cursor: 'pointer',
            borderBottom: activeKey === tab.key
              ? '2px solid var(--cyan)'
              : '2px solid transparent',
            transition: 'all 0.15s',
            display: 'flex',
            alignItems: 'center',
            gap: 6,
          }}
        >
          {tab.label}
          {tab.badge != null && tab.badge > 0 && (
            <span style={{
              fontSize: 10, fontWeight: 700,
              padding: '1px 6px', borderRadius: 8,
              background: 'var(--amber-soft)', color: 'var(--amber)',
            }}>
              {tab.badge}
            </span>
          )}
        </button>
      ))}
    </div>
  )
}
```

### Acceptance criteria

- [ ] `StateBadge` renders five distinct states with correct D-045 colors
- [ ] `ActionPill` renders Add (green), Remove (red), Rate Update (amber), MCC Expansion (blue)
- [ ] `EntryPill` renders ADD (green), REMOVE (red), NO_CHANGE (gray), PEOPLESOFT_ONLY (purple)
- [ ] `TabBar` highlights the active tab with a cyan bottom border and bold text
- [ ] `TabBar` renders an amber badge when `badge > 0`
- [ ] All colors use CSS variables — `grep -rE "#[0-9a-fA-F]{3,8}" web/src/features/shared/components/` returns only the one inline rgba in StateBadge's config (which references CSS vars for the foreground)

### Notes

The inline `rgba(...)` values in `StateBadge` and pill configs are backgrounds with explicit alpha — these complement the CSS variable foregrounds. They could be moved to CSS variables if the token count grows, but at 5 states + 4 actions + 4 entries the inline approach is clearer than 13 additional `--state-X-bg` variables.

---

## T-F10 — Toast notification system

**Depends on:** T7
**Touches files:** `/web/src/features/shared/components/Toast.tsx`, `/web/src/features/shared/stores/toastStore.ts`
**Estimated effort:** small

### Goal

Build a lightweight toast notification system for action confirmations ("Staged run started"), errors ("Could not acquire lock"), and SSE-driven alerts. Toasts auto-dismiss after 5 seconds. A Zustand store manages the toast queue.

### Implementation

**File: `/web/src/features/shared/stores/toastStore.ts`**:

```typescript
import { create } from 'zustand'

export interface Toast {
  id: string
  message: string
  type: 'success' | 'error' | 'info'
}

interface ToastState {
  toasts: Toast[]
  addToast: (message: string, type?: Toast['type']) => void
  removeToast: (id: string) => void
}

export const useToastStore = create<ToastState>((set) => ({
  toasts: [],

  addToast: (message, type = 'info') => {
    const id = crypto.randomUUID()
    set((s) => ({ toasts: [...s.toasts, { id, message, type }] }))
    // Auto-dismiss after 5 seconds.
    setTimeout(() => {
      set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) }))
    }, 5_000)
  },

  removeToast: (id) =>
    set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),
}))
```

**File: `/web/src/features/shared/components/Toast.tsx`**:

```typescript
import { useToastStore } from '../stores/toastStore'

const TYPE_STYLES: Record<string, { bg: string; border: string }> = {
  success: { bg: 'rgba(110,231,160,0.12)', border: 'var(--add)' },
  error:   { bg: 'rgba(252,165,165,0.12)', border: 'var(--remove)' },
  info:    { bg: 'var(--glass)',            border: 'var(--glass-stroke-strong)' },
}

export function ToastContainer() {
  const toasts = useToastStore((s) => s.toasts)
  const removeToast = useToastStore((s) => s.removeToast)

  if (toasts.length === 0) return null

  return (
    <div style={{
      position: 'fixed', bottom: 24, right: 24, zIndex: 1000,
      display: 'flex', flexDirection: 'column', gap: 8, maxWidth: 360,
    }}>
      {toasts.map((toast) => {
        const ts = TYPE_STYLES[toast.type] || TYPE_STYLES.info
        return (
          <div
            key={toast.id}
            style={{
              padding: '12px 16px',
              background: ts.bg,
              borderLeft: `3px solid ${ts.border}`,
              borderRadius: 'var(--radius-sm)',
              backdropFilter: 'blur(16px)',
              color: 'var(--ink)',
              fontSize: 13,
              fontFamily: 'var(--font-sans)',
              cursor: 'pointer',
              animation: 'fadeIn 0.2s ease',
            }}
            onClick={() => removeToast(toast.id)}
          >
            {toast.message}
          </div>
        )
      })}
    </div>
  )
}
```

Add `<ToastContainer />` to `AppShell.tsx` just before `</div>` (the closing `.app-shell` div).

### Acceptance criteria

- [ ] `addToast('Run started', 'success')` shows a green-bordered toast at bottom-right
- [ ] `addToast('Lock held', 'error')` shows a red-bordered toast
- [ ] Toasts auto-dismiss after 5 seconds
- [ ] Clicking a toast dismisses it immediately
- [ ] Multiple toasts stack vertically
- [ ] `<ToastContainer />` is rendered inside AppShell
# Section G — Runs List screen

This section builds the Runs List screen (`/runs` route) per the functional-integration-spec §3 and visual mockup. Components live in `web/src/features/runs/` per D-062's feature layout. Data flows through the React Query hooks and Zustand store from Section F.

Section index:

- [ ] T-G1 — RunsListScreen container + SSE subscription
- [ ] T-G2 — SearchBar (MAID/merchant search with debounce)
- [ ] T-G3 — StateFilterChips
- [ ] T-G4 — RunsTable (column definitions + row rendering)
- [ ] T-G5 — Pagination controls
- [ ] T-G6 — NewRunDialog (input folder selection)
- [ ] T-G7 — Loading, empty, and error states
- [ ] T-G8 — Route wiring in App.tsx

---

## T-G1 — RunsListScreen container + SSE subscription

**Depends on:** T-F2, T-F3, T-F4, T-F6
**Touches files:** `/web/src/features/runs/screens/RunsListScreen.tsx`
**Estimated effort:** medium

### Goal

Create the top-level Runs List screen component that composes the search bar, state filter chips, runs table, pagination, and new-run button. Subscribes to the global SSE stream for live state-badge updates.

### Implementation

**File: `/web/src/features/runs/screens/RunsListScreen.tsx`**:

```typescript
/**
 * RunsListScreen — /runs route per functional-integration-spec §3.
 *
 * Composition root for the Runs List. Owns the data query; passes
 * results to child components as props.
 */

import { useNavigate } from 'react-router-dom'
import { useRunsList, useLockState } from '@/features/shared/api/hooks'
import { useUIStore } from '@/features/shared/stores/uiStore'
import { useSSE } from '@/features/shared/sse/useSSE'
import { SearchBar } from '../components/SearchBar'
import { StateFilterChips } from '../components/StateFilterChips'
import { RunsTable } from '../components/RunsTable'
import { Pagination } from '../components/Pagination'
import { NewRunDialog } from '../components/NewRunDialog'

export function RunsListScreen() {
  const navigate = useNavigate()

  // UI state from Zustand.
  const searchQuery = useUIStore((s) => s.searchQuery)
  const stateFilter = useUIStore((s) => s.stateFilter)
  const currentPage = useUIStore((s) => s.currentPage)

  // Data from React Query.
  const { data, isLoading, isError, error } = useRunsList({
    search: searchQuery || undefined,
    state: stateFilter || undefined,
    page: currentPage,
    pageSize: 10,
  })

  const { data: lockState } = useLockState()

  // Global SSE for live updates (state badge changes, new runs appearing).
  useSSE()

  const handleRowClick = (runId: string) => {
    navigate(`/runs/${runId}`)
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Header row: title + new run button */}
      <div style={{
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
      }}>
        <h1 style={{
          margin: 0, fontSize: 22, fontWeight: 700, color: 'var(--ink)',
          letterSpacing: '-0.02em',
        }}>
          Pipeline Runs
        </h1>
        <NewRunDialog lockHeld={lockState?.held ?? false} />
      </div>

      {/* Search + filter row */}
      <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
        <SearchBar />
        <StateFilterChips />
      </div>

      {/* Table */}
      {isLoading && (
        <div style={{ padding: 48, textAlign: 'center', color: 'var(--ink-mute)' }}>
          Loading runs...
        </div>
      )}

      {isError && (
        <div style={{ padding: 48, textAlign: 'center', color: 'var(--state-fail)' }}>
          Failed to load runs: {(error as Error)?.message || 'Unknown error'}
        </div>
      )}

      {data && !isLoading && (
        <>
          <RunsTable
            runs={data.runs}
            lockHeld={lockState?.held ?? false}
            onRowClick={handleRowClick}
          />
          <Pagination
            page={data.page}
            pageSize={data.page_size}
            total={data.total}
          />
        </>
      )}
    </div>
  )
}
```

### Acceptance criteria

- [ ] RunsListScreen renders the full Runs List layout (title, search, filters, table, pagination)
- [ ] `useSSE()` is called at screen level for global live updates
- [ ] Row click navigates to `/runs/:run_id`
- [ ] Loading, error, and data states all render correctly

---

## T-G2 — SearchBar (MAID/merchant search with debounce)

**Depends on:** T-F4
**Touches files:** `/web/src/features/runs/components/SearchBar.tsx`
**Estimated effort:** small

### Implementation

**File: `/web/src/features/runs/components/SearchBar.tsx`**:

```typescript
import { useState, useEffect } from 'react'
import { useUIStore } from '@/features/shared/stores/uiStore'

export function SearchBar() {
  const setSearchQuery = useUIStore((s) => s.setSearchQuery)
  const searchQuery = useUIStore((s) => s.searchQuery)
  const [localValue, setLocalValue] = useState(searchQuery)

  // Debounce: update the store 300ms after the user stops typing.
  useEffect(() => {
    const timer = setTimeout(() => setSearchQuery(localValue), 300)
    return () => clearTimeout(timer)
  }, [localValue, setSearchQuery])

  // Sync if external reset happens.
  useEffect(() => { setLocalValue(searchQuery) }, [searchQuery])

  return (
    <input
      type="text"
      placeholder="Search by MAID or merchant..."
      value={localValue}
      onChange={(e) => setLocalValue(e.target.value)}
      style={{
        padding: '8px 14px', width: 260,
        background: 'var(--glass)', border: '1px solid var(--glass-stroke)',
        borderRadius: 'var(--radius-sm)', color: 'var(--ink)',
        fontFamily: 'var(--font-sans)', fontSize: 13,
        outline: 'none',
      }}
    />
  )
}
```

### Acceptance criteria

- [ ] Typing updates the Zustand search query after 300ms debounce
- [ ] Clearing the input resets the query
- [ ] Placeholder reads "Search by MAID or merchant..."

---

## T-G3 — StateFilterChips

**Depends on:** T-F4, T-F9
**Touches files:** `/web/src/features/runs/components/StateFilterChips.tsx`
**Estimated effort:** small

### Implementation

**File: `/web/src/features/runs/components/StateFilterChips.tsx`**:

```typescript
import { useUIStore } from '@/features/shared/stores/uiStore'

const FILTERS = [
  { key: null, label: 'All' },
  { key: 'pre_approval', label: 'Pre-Approval' },
  { key: 'in_progress', label: 'In Progress' },
  { key: 'submitted', label: 'Submitted' },
  { key: 'failed', label: 'Failed' },
  { key: 'stale', label: 'Stale' },
] as const

export function StateFilterChips() {
  const stateFilter = useUIStore((s) => s.stateFilter)
  const setStateFilter = useUIStore((s) => s.setStateFilter)

  return (
    <div style={{ display: 'flex', gap: 4 }}>
      {FILTERS.map((f) => (
        <button
          key={f.key ?? 'all'}
          onClick={() => setStateFilter(f.key)}
          style={{
            padding: '5px 12px', borderRadius: 'var(--radius-sm)',
            border: '1px solid var(--glass-stroke)', fontSize: 12, fontWeight: 500,
            cursor: 'pointer', fontFamily: 'var(--font-sans)',
            background: stateFilter === f.key ? 'var(--glass-strong)' : 'transparent',
            color: stateFilter === f.key ? 'var(--ink)' : 'var(--ink-mute)',
            transition: 'all 0.15s',
          }}
        >
          {f.label}
        </button>
      ))}
    </div>
  )
}
```

### Acceptance criteria

- [ ] Renders filter chips for All, Pre-Approval, In Progress, Submitted, Failed, Stale
- [ ] Clicking a chip updates the Zustand state filter
- [ ] Active chip is visually highlighted
- [ ] "All" chip sets filter to null (no filter)

---

## T-G4 — RunsTable (column definitions + row rendering)

**Depends on:** T-F9
**Touches files:** `/web/src/features/runs/components/RunsTable.tsx`
**Estimated effort:** medium

### Goal

Render the Runs List table with columns: Merchant, Run ID, Created, State, Issues, and a lock-aware status indicator.

### Implementation

**File: `/web/src/features/runs/components/RunsTable.tsx`**:

```typescript
import { RunSummary } from '@/features/shared/api/hooks'
import { StateBadge } from '@/features/shared/components/StateBadge'

interface Props {
  runs: RunSummary[]
  lockHeld: boolean
  onRowClick: (runId: string) => void
}

export function RunsTable({ runs, lockHeld, onRowClick }: Props) {
  if (runs.length === 0) {
    return (
      <div style={{
        padding: 48, textAlign: 'center', color: 'var(--ink-dim)',
        background: 'var(--glass)', borderRadius: 'var(--radius)',
        border: '1px solid var(--glass-stroke)',
      }}>
        No runs match the current filters.
      </div>
    )
  }

  return (
    <div className="data-table-flat" style={{ borderRadius: 'var(--radius)', overflow: 'hidden' }}>
      <table style={{
        width: '100%', borderCollapse: 'collapse', fontSize: 13,
        fontFamily: 'var(--font-sans)',
      }}>
        <thead>
          <tr>
            <th style={thStyle}>Merchant</th>
            <th style={thStyle}>Run ID</th>
            <th style={thStyle}>Created</th>
            <th style={thStyle}>State</th>
            <th style={{ ...thStyle, textAlign: 'right' }}>Issues</th>
          </tr>
        </thead>
        <tbody>
          {runs.map((run) => (
            <tr
              key={run.run_id}
              onClick={() => onRowClick(run.run_id)}
              style={{ cursor: 'pointer', transition: 'background 0.1s' }}
              onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--glass)')}
              onMouseLeave={(e) => (e.currentTarget.style.background = '')}
            >
              <td style={tdStyle}>
                <span style={{ fontWeight: 500, color: 'var(--ink)' }}>{run.merchant}</span>
              </td>
              <td style={{ ...tdStyle, fontFamily: 'var(--font-mono)', fontSize: 12 }}>
                {run.run_id}
              </td>
              <td style={{ ...tdStyle, color: 'var(--ink-mute)' }}>
                {formatDate(run.created_at)}
              </td>
              <td style={tdStyle}>
                <StateBadge state={run.state || 'stale'} />
              </td>
              <td style={{ ...tdStyle, textAlign: 'right' }}>
                {run.issue_count != null && run.issue_count > 0 ? (
                  <span style={{
                    fontSize: 11, fontWeight: 700, padding: '2px 7px',
                    borderRadius: 8, background: 'var(--amber-soft)', color: 'var(--amber)',
                  }}>
                    {run.issue_count}
                  </span>
                ) : (
                  <span style={{ color: 'var(--ink-dim)' }}>—</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

const thStyle: React.CSSProperties = {
  padding: '10px 14px', textAlign: 'left', fontWeight: 600, fontSize: 11,
  textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--ink-mute)',
  borderBottom: '1px solid var(--glass-stroke)', background: 'var(--bg-elev)',
}

const tdStyle: React.CSSProperties = {
  padding: '12px 14px', borderBottom: '1px solid var(--glass-stroke)',
  color: 'var(--ink-soft)',
}

function formatDate(iso: string): string {
  try {
    const d = new Date(iso)
    return d.toLocaleDateString('en-US', {
      month: 'short', day: 'numeric', year: 'numeric',
      hour: '2-digit', minute: '2-digit',
    })
  } catch {
    return iso
  }
}
```

### Acceptance criteria

- [ ] Table renders columns: Merchant, Run ID, Created, State, Issues
- [ ] Run ID uses monospace font
- [ ] State column renders `StateBadge` with correct colors
- [ ] Issue count > 0 shows an amber badge; 0 or null shows "—"
- [ ] Row hover highlights with glass background
- [ ] Row click calls `onRowClick` with the run_id
- [ ] Empty state shows "No runs match the current filters."
- [ ] Table uses `.data-table-flat` class (flat, no glass material)

---

## T-G5 — Pagination controls

**Depends on:** T-F4
**Touches files:** `/web/src/features/runs/components/Pagination.tsx`
**Estimated effort:** small

### Implementation

**File: `/web/src/features/runs/components/Pagination.tsx`**:

```typescript
import { useUIStore } from '@/features/shared/stores/uiStore'

interface Props {
  page: number
  pageSize: number
  total: number
}

export function Pagination({ page, pageSize, total }: Props) {
  const setCurrentPage = useUIStore((s) => s.setCurrentPage)
  const totalPages = Math.max(1, Math.ceil(total / pageSize))

  if (totalPages <= 1) return null

  return (
    <div style={{
      display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 12,
      color: 'var(--ink-mute)', fontSize: 13,
    }}>
      <button
        disabled={page <= 1}
        onClick={() => setCurrentPage(page - 1)}
        style={btnStyle(page <= 1)}
      >
        ← Prev
      </button>
      <span>
        Page {page} of {totalPages}
        <span style={{ marginLeft: 8, color: 'var(--ink-dim)' }}>
          ({total} runs)
        </span>
      </span>
      <button
        disabled={page >= totalPages}
        onClick={() => setCurrentPage(page + 1)}
        style={btnStyle(page >= totalPages)}
      >
        Next →
      </button>
    </div>
  )
}

function btnStyle(disabled: boolean): React.CSSProperties {
  return {
    padding: '6px 14px', borderRadius: 'var(--radius-sm)',
    border: '1px solid var(--glass-stroke)', background: 'var(--glass)',
    color: disabled ? 'var(--ink-dim)' : 'var(--ink-soft)', cursor: disabled ? 'default' : 'pointer',
    fontFamily: 'var(--font-sans)', fontSize: 12,
    opacity: disabled ? 0.5 : 1,
  }
}
```

### Acceptance criteria

- [ ] Hidden when total ≤ page_size (single page)
- [ ] Prev disabled on page 1; Next disabled on last page
- [ ] Shows "Page X of Y (Z runs)"

---

## T-G6 — NewRunDialog (input folder selection)

**Depends on:** T-F2, T-F10
**Touches files:** `/web/src/features/runs/components/NewRunDialog.tsx`
**Estimated effort:** medium

### Goal

Build the "New Run" button + modal dialog that lists available input folders from `GET /api/input-folders`, lets the operator select one, and calls `useStartRun` to initiate the staged run. Shows a toast on success.

### Implementation

**File: `/web/src/features/runs/components/NewRunDialog.tsx`**:

```typescript
import { useState } from 'react'
import { useInputFolders, useStartRun } from '@/features/shared/api/hooks'
import { useToastStore } from '@/features/shared/stores/toastStore'

interface Props {
  lockHeld: boolean
}

export function NewRunDialog({ lockHeld }: Props) {
  const [open, setOpen] = useState(false)
  const [selected, setSelected] = useState<string | null>(null)
  const { data } = useInputFolders()
  const startRun = useStartRun()
  const addToast = useToastStore((s) => s.addToast)

  const handleStart = async () => {
    if (!selected) return
    try {
      const result = await startRun.mutateAsync({ input_folder: selected })
      addToast(result.message, 'success')
      setOpen(false)
      setSelected(null)
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to start run'
      addToast(msg, 'error')
    }
  }

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        disabled={lockHeld}
        title={lockHeld ? 'An active operation is in progress' : 'Start a new pipeline run'}
        style={{
          padding: '8px 20px', borderRadius: 'var(--radius-sm)',
          border: 'none', fontFamily: 'var(--font-sans)', fontSize: 13,
          fontWeight: 600, cursor: lockHeld ? 'not-allowed' : 'pointer',
          background: lockHeld ? 'var(--glass)' : 'var(--cyan)',
          color: lockHeld ? 'var(--ink-dim)' : 'var(--bg)',
          opacity: lockHeld ? 0.5 : 1,
        }}
      >
        New Run
      </button>

      {open && (
        <div style={{
          position: 'fixed', inset: 0, zIndex: 100,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)',
        }}>
          <div style={{
            background: 'var(--bg-elev)', border: '1px solid var(--glass-stroke)',
            borderRadius: 'var(--radius-lg)', padding: 24, width: 440,
            maxHeight: '70vh', overflowY: 'auto',
          }}>
            <h2 style={{ margin: '0 0 16px', fontSize: 18, fontWeight: 600, color: 'var(--ink)' }}>
              Start New Run
            </h2>
            <p style={{ fontSize: 13, color: 'var(--ink-soft)', marginBottom: 16 }}>
              Select an input folder containing old and new agreement directories.
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
              {data?.folders.map((f) => (
                <button
                  key={f.path}
                  onClick={() => setSelected(f.path)}
                  style={{
                    padding: '10px 14px', textAlign: 'left',
                    borderRadius: 'var(--radius-sm)',
                    border: selected === f.path
                      ? '1px solid var(--cyan)'
                      : '1px solid var(--glass-stroke)',
                    background: selected === f.path ? 'var(--cyan-soft)' : 'var(--glass)',
                    color: 'var(--ink)', cursor: 'pointer',
                    fontFamily: 'var(--font-sans)', fontSize: 13,
                  }}
                >
                  <div style={{ fontWeight: 500 }}>{f.name}</div>
                  <div style={{ fontSize: 11, color: 'var(--ink-mute)', marginTop: 2 }}>
                    {f.path}
                    {f.has_old && f.has_new ? ' — old/ ✓ new/ ✓' : ''}
                    {f.has_old && !f.has_new ? ' — old/ ✓ new/ ✗' : ''}
                    {!f.has_old && f.has_new ? ' — old/ ✗ new/ ✓' : ''}
                  </div>
                </button>
              ))}
              {(!data?.folders || data.folders.length === 0) && (
                <div style={{ color: 'var(--ink-dim)', padding: 16, textAlign: 'center' }}>
                  No input folders found. Check ALLOWED_INPUT_ROOTS in /api/.env.
                </div>
              )}
            </div>

            <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end', marginTop: 20 }}>
              <button
                onClick={() => { setOpen(false); setSelected(null) }}
                style={{
                  padding: '8px 16px', borderRadius: 'var(--radius-sm)',
                  border: '1px solid var(--glass-stroke)', background: 'transparent',
                  color: 'var(--ink-soft)', cursor: 'pointer', fontSize: 13,
                }}
              >
                Cancel
              </button>
              <button
                onClick={handleStart}
                disabled={!selected || startRun.isPending}
                style={{
                  padding: '8px 16px', borderRadius: 'var(--radius-sm)',
                  border: 'none', background: selected ? 'var(--cyan)' : 'var(--glass)',
                  color: selected ? 'var(--bg)' : 'var(--ink-dim)',
                  cursor: selected ? 'pointer' : 'not-allowed', fontSize: 13, fontWeight: 600,
                }}
              >
                {startRun.isPending ? 'Starting...' : 'Start Run'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
```

### Acceptance criteria

- [ ] "New Run" button disabled with tooltip when lock is held
- [ ] Dialog lists input folders from `GET /api/input-folders`
- [ ] Each folder shows its name, path, and old/new directory presence
- [ ] Selecting a folder highlights it; clicking "Start Run" calls `useStartRun`
- [ ] Success toast appears; dialog closes
- [ ] Error toast appears on failure (e.g., lock acquired between dialog open and submit)
- [ ] Cancel closes the dialog without action

---

## T-G7 — Loading, empty, and error states

**Depends on:** T-G1
**Touches files:** (integrated into RunsListScreen from T-G1)
**Estimated effort:** small

### Goal

Verify and polish the three non-happy states in the Runs List screen. This is a review/polish task, not a new component — the states are already rendered in T-G1.

### Implementation

The three states from T-G1's RunsListScreen:

1. **Loading:** "Loading runs..." centered text while `isLoading` is true.
2. **Error:** Red-tinted message with the error text when `isError` is true.
3. **Empty (after filters):** "No runs match the current filters." via RunsTable's empty state.

Additionally, add a "first run" empty state when `data.total === 0` AND no search/filter is active:

Add to RunsListScreen, after the `{data && !isLoading && ...}` block:

```typescript
{data && !isLoading && data.total === 0 && !searchQuery && !stateFilter && (
  <div style={{
    padding: 64, textAlign: 'center', color: 'var(--ink-mute)',
    background: 'var(--glass)', borderRadius: 'var(--radius)',
    border: '1px solid var(--glass-stroke)',
  }}>
    <div style={{ fontSize: 16, fontWeight: 500, marginBottom: 8, color: 'var(--ink-soft)' }}>
      No pipeline runs yet
    </div>
    <div style={{ fontSize: 13 }}>
      Click "New Run" to start your first agreement processing run.
    </div>
  </div>
)}
```

### Acceptance criteria

- [ ] Loading state shows spinner/text while data is being fetched
- [ ] Error state shows the error message in a visible color
- [ ] Empty-with-filters state shows "No runs match the current filters."
- [ ] Empty-without-filters state shows "No pipeline runs yet" with guidance to click "New Run"

---

## T-G8 — Route wiring in App.tsx

**Depends on:** T-G1, T-F6
**Touches files:** `/web/src/App.tsx` (modification)
**Estimated effort:** small

### Goal

Replace the Runs List placeholder in App.tsx with the real `RunsListScreen` import.

### Implementation

Update `/web/src/App.tsx`:

```typescript
import { Routes, Route, Navigate } from 'react-router-dom'
import { ErrorBoundary } from '@/features/shared/errors/ErrorBoundary'
import { AppShell } from '@/features/shared/components/AppShell'
import { SmartFallback } from '@/features/shared/components/SmartFallback'
import { RunsListScreen } from '@/features/runs/screens/RunsListScreen'

// Section H / Section I placeholders remain until those sections land.
function RunDetailPlaceholder() {
  return <div style={{ color: 'var(--ink-soft)' }}>Run Detail — Section H</div>
}

export default function App() {
  return (
    <ErrorBoundary>
      <Routes>
        <Route element={<AppShell />}>
          <Route path="/" element={<SmartFallback />} />
          <Route path="/runs" element={<RunsListScreen />} />
          <Route path="/runs/new" element={<RunDetailPlaceholder />} />
          <Route path="/runs/:id" element={<RunDetailPlaceholder />} />
          <Route path="/runs/:id/artifact" element={<div>Artifact Preview — Section I</div>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </ErrorBoundary>
  )
}
```

Also update the `runs` feature's public API barrel:

**File: `/web/src/features/runs/index.ts`** (update from T3 scaffold):

```typescript
export { RunsListScreen } from './screens/RunsListScreen'
```

### Acceptance criteria

- [ ] Navigating to `/runs` renders the real RunsListScreen (not the placeholder)
- [ ] The SmartFallback at `/` correctly redirects to `/runs` or `/runs/:id`
- [ ] Run Detail and Artifact Preview routes still show their placeholders (populated in Sections H, I)
- [ ] `npm run lint` passes with zero boundary violations (RunsListScreen imports only from `runs/` and `shared/`)
# Section H — Run Detail screen

This section builds the Run Detail screen (`/runs/:id` route) per functional-integration-spec §5-§8 and the visual mockup. Three tabs (Activity, Results, Issues), action buttons per D-046 state rules, a sliding drawer for comparison record details, and live SSE-driven updates. Components live in `web/src/features/runs/`.

Section index:

- [ ] T-H1 — RunDetailScreen container + SSE
- [ ] T-H2 — RunHeader (merchant, state, timestamps)
- [ ] T-H3 — ActionButtonBar (Approve, Retry, Rerun with lock awareness)
- [ ] T-H4 — Tab integration (Activity / Results / Issues)
- [ ] T-H5 — ActivityTab container
- [ ] T-H6 — ActivityTimeline (event cards)
- [ ] T-H7 — StageProgressBar (live progress during in-progress)
- [ ] T-H8 — ResultsTab container
- [ ] T-H9 — Results column definitions (18-column base table)
- [ ] T-H10 — DrawerContent shell
- [ ] T-H11 — FieldDeltasPanel (old vs new comparison)
- [ ] T-H12 — ETLImpactPanel
- [ ] T-H13 — ModFilePanel
- [ ] T-H14 — IssuesTab container
- [ ] T-H15 — IssueCard (severity-colored issue rendering)
- [ ] T-H16 — JiraInfoPanel (for submitted runs)
- [ ] T-H17 — FailurePanel (for failed runs)
- [ ] T-H18 — Route wiring in App.tsx

---

## T-H1 — RunDetailScreen container + SSE

**Depends on:** T-F2, T-F3, T-F4, T-F6
**Touches files:** `/web/src/features/runs/screens/RunDetailScreen.tsx`
**Estimated effort:** medium

### Goal

Top-level Run Detail screen that reads `run_id` from route params, fetches run detail, subscribes to run-scoped SSE, and renders the header + tab container.

### Implementation

**File: `/web/src/features/runs/screens/RunDetailScreen.tsx`**:

```typescript
import { useParams } from 'react-router-dom'
import { useRunDetail, useLockState } from '@/features/shared/api/hooks'
import { useUIStore } from '@/features/shared/stores/uiStore'
import { useSSE } from '@/features/shared/sse/useSSE'
import { RunHeader } from '../components/RunHeader'
import { ActionButtonBar } from '../components/ActionButtonBar'
import { TabBar } from '@/features/shared/components/TabBar'
import { ActivityTab } from '../components/ActivityTab'
import { ResultsTab } from '../components/ResultsTab'
import { IssuesTab } from '../components/IssuesTab'
import { useIssues } from '@/features/shared/api/hooks'

export function RunDetailScreen() {
  const { id: runId } = useParams<{ id: string }>()
  const { data, isLoading, isError } = useRunDetail(runId || '')
  const { data: lockState } = useLockState()
  const { data: issuesData } = useIssues(runId || '')

  const activeTab = useUIStore((s) => s.activeTab)
  const setActiveTab = useUIStore((s) => s.setActiveTab)

  // Run-scoped SSE for live Activity tab updates.
  useSSE(runId)

  if (isLoading) {
    return <div style={{ padding: 48, color: 'var(--ink-mute)', textAlign: 'center' }}>Loading run details...</div>
  }
  if (isError || !data) {
    return <div style={{ padding: 48, color: 'var(--state-fail)', textAlign: 'center' }}>Run not found.</div>
  }

  const tabs = [
    { key: 'activity', label: 'Activity' },
    { key: 'results', label: 'Results' },
    { key: 'issues', label: 'Issues', badge: issuesData?.total ?? null },
  ]

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <RunHeader run={data.run} failure={data.failure} />
      <ActionButtonBar
        runId={runId || ''}
        availableActions={data.available_actions}
        lockHeld={lockState?.held ?? false}
        state={data.run.state || 'stale'}
        folderPath={data.run.folder_path}
      />

      <TabBar tabs={tabs} activeKey={activeTab} onChange={(k) => setActiveTab(k as typeof activeTab)} />

      <div style={{ flex: 1 }}>
        {activeTab === 'activity' && <ActivityTab runId={runId || ''} state={data.run.state || 'stale'} failure={data.failure} />}
        {activeTab === 'results' && <ResultsTab runId={runId || ''} />}
        {activeTab === 'issues' && <IssuesTab runId={runId || ''} />}
      </div>
    </div>
  )
}
```

### Acceptance criteria

- [ ] Route `/runs/:id` renders RunDetailScreen with run data
- [ ] SSE is scoped to the current run_id
- [ ] Tab bar shows Activity, Results, Issues with issue count badge
- [ ] Loading and error states render appropriately
- [ ] Tab switching is in-session only (Zustand, not URL per D-062)

---

## T-H2 — RunHeader

**Depends on:** T-F9
**Touches files:** `/web/src/features/runs/components/RunHeader.tsx`
**Estimated effort:** small

### Implementation

**File: `/web/src/features/runs/components/RunHeader.tsx`**:

```typescript
import { RunSummary } from '@/features/shared/api/hooks'
import { StateBadge } from '@/features/shared/components/StateBadge'

interface Props {
  run: RunSummary
  failure: Record<string, unknown> | null
}

export function RunHeader({ run, failure }: Props) {
  return (
    <div style={{
      padding: '20px 24px', background: 'var(--glass)',
      border: '1px solid var(--glass-stroke)', borderRadius: 'var(--radius)',
      backdropFilter: 'blur(16px)',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
        <div>
          <h2 style={{ margin: 0, fontSize: 20, fontWeight: 700, color: 'var(--ink)' }}>
            {run.merchant}
          </h2>
          <div style={{
            fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--ink-mute)', marginTop: 4,
          }}>
            {run.run_id}
          </div>
        </div>
        <StateBadge state={run.state || 'stale'} />
      </div>
      <div style={{
        marginTop: 12, fontSize: 12, color: 'var(--ink-dim)',
        display: 'flex', gap: 24,
      }}>
        <span>Created: {new Date(run.created_at).toLocaleString()}</span>
      </div>
      {failure && (
        <div style={{
          marginTop: 12, padding: '10px 14px', borderRadius: 'var(--radius-sm)',
          background: 'rgba(252,165,165,0.08)', border: '1px solid rgba(252,165,165,0.2)',
          fontSize: 13, color: 'var(--state-fail)',
        }}>
          {String(failure.error_message || 'Run failed.')}
        </div>
      )}
    </div>
  )
}
```

### Acceptance criteria

- [ ] Shows merchant name, run_id (mono), state badge, and created date
- [ ] Failed runs show the error_message from failure.json in a red-tinted banner

---

## T-H3 — ActionButtonBar

**Depends on:** T-F2, T-F10
**Touches files:** `/web/src/features/runs/components/ActionButtonBar.tsx`
**Estimated effort:** medium

### Goal

Render Approve, Retry Approve, and Re-run from Scratch buttons based on `available_actions` from the run detail response. Lock-aware disabling per V's single-lock model.

### Implementation

**File: `/web/src/features/runs/components/ActionButtonBar.tsx`**:

```typescript
import { useApproveRun, useRetryApprove, useRerunFromScratch } from '@/features/shared/api/hooks'
import { useToastStore } from '@/features/shared/stores/toastStore'
import { ApiError } from '@/features/shared/api/client'

interface Props {
  runId: string
  availableActions: string[]
  lockHeld: boolean
  state: string
  folderPath: string
}

export function ActionButtonBar({ runId, availableActions, lockHeld, state, folderPath }: Props) {
  const approve = useApproveRun()
  const retryApprove = useRetryApprove()
  const rerun = useRerunFromScratch()
  const addToast = useToastStore((s) => s.addToast)

  const isInProgress = state === 'in_progress'
  const disabled = lockHeld || isInProgress

  const handleAction = async (
    action: () => Promise<unknown>,
    successMsg: string,
  ) => {
    try {
      await action()
      addToast(successMsg, 'success')
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : 'Action failed'
      addToast(msg, 'error')
    }
  }

  if (availableActions.length === 0 && !isInProgress) return null

  const tooltip = disabled ? 'An active operation is in progress' : undefined

  return (
    <div style={{ display: 'flex', gap: 8 }}>
      {availableActions.includes('approve') && (
        <button
          disabled={disabled}
          title={tooltip}
          onClick={() => handleAction(
            () => approve.mutateAsync(runId),
            'Approval started.',
          )}
          style={actionBtnStyle('var(--add)', disabled)}
        >
          {approve.isPending ? 'Approving...' : 'Approve'}
        </button>
      )}

      {availableActions.includes('retry_approve') && (
        <button
          disabled={disabled}
          title={tooltip}
          onClick={() => handleAction(
            () => retryApprove.mutateAsync(runId),
            'Retry approval started.',
          )}
          style={actionBtnStyle('var(--amber)', disabled)}
        >
          {retryApprove.isPending ? 'Retrying...' : 'Retry Approve'}
        </button>
      )}

      {availableActions.includes('rerun_from_scratch') && (
        <button
          disabled={disabled}
          title={tooltip}
          onClick={() => handleAction(
            () => rerun.mutateAsync({ runId, input_folder: folderPath }),
            'Re-run from scratch started.',
          )}
          style={actionBtnStyle('var(--ink-soft)', disabled)}
        >
          {rerun.isPending ? 'Starting...' : 'Re-run from Scratch'}
        </button>
      )}

      {isInProgress && (
        <span style={{ fontSize: 12, color: 'var(--state-prog)', alignSelf: 'center' }}>
          Pipeline running...
        </span>
      )}
    </div>
  )
}

function actionBtnStyle(accentColor: string, disabled: boolean): React.CSSProperties {
  return {
    padding: '8px 18px', borderRadius: 'var(--radius-sm)',
    border: `1px solid ${disabled ? 'var(--glass-stroke)' : accentColor}`,
    background: disabled ? 'var(--glass)' : 'transparent',
    color: disabled ? 'var(--ink-dim)' : accentColor,
    fontFamily: 'var(--font-sans)', fontSize: 13, fontWeight: 600,
    cursor: disabled ? 'not-allowed' : 'pointer',
    opacity: disabled ? 0.5 : 1,
  }
}
```

### Acceptance criteria

- [ ] Buttons render based on `available_actions` list
- [ ] All buttons disabled when lock held; tooltip shows single-lock message
- [ ] "Approve" button uses green accent; "Retry Approve" amber; "Re-run" neutral
- [ ] Pending state shows loading text per button
- [ ] Success/error toasts on action completion
- [ ] In-progress state shows "Pipeline running..." indicator

---

## T-H4 — Tab integration

**Depends on:** T-F9, T-H1
**Touches files:** (integrated into RunDetailScreen in T-H1)
**Estimated effort:** small

### Goal

The TabBar is already rendered in T-H1's RunDetailScreen. This task verifies the tab switching, issue count badge, and default-tab behavior.

### Acceptance criteria

- [ ] Default tab on mount is "Activity" per D-062
- [ ] Switching tabs preserves Zustand state (no remount, no network refetch on tab re-entry)
- [ ] Issues tab badge shows the count from `useIssues` hook; hidden if 0
- [ ] Tab state is NOT in the URL per functional-integration-spec §9.5

---

## T-H5 — ActivityTab container

**Depends on:** T-F2
**Touches files:** `/web/src/features/runs/components/ActivityTab.tsx`
**Estimated effort:** small

### Implementation

**File: `/web/src/features/runs/components/ActivityTab.tsx`**:

```typescript
import { useEvents } from '@/features/shared/api/hooks'
import { ActivityTimeline } from './ActivityTimeline'
import { FailurePanel } from './FailurePanel'
import { JiraInfoPanel } from './JiraInfoPanel'

interface Props {
  runId: string
  state: string
  failure: Record<string, unknown> | null
}

export function ActivityTab({ runId, state, failure }: Props) {
  const { data, isLoading } = useEvents(runId)

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {state === 'failed' && failure && <FailurePanel failure={failure} />}
      {state === 'submitted' && <JiraInfoPanel runId={runId} />}

      {isLoading && (
        <div style={{ color: 'var(--ink-mute)', padding: 16 }}>Loading activity...</div>
      )}
      {data && <ActivityTimeline events={data.events} />}
      {data && data.events.length === 0 && !isLoading && (
        <div style={{ color: 'var(--ink-dim)', padding: 32, textAlign: 'center' }}>
          No events recorded yet.
        </div>
      )}
    </div>
  )
}
```

### Acceptance criteria

- [ ] Shows FailurePanel at top for failed runs, JiraInfoPanel for submitted runs
- [ ] Event timeline renders below contextual panels
- [ ] Empty state message for runs with no events

---

## T-H6 — ActivityTimeline (event cards)

**Depends on:** T-H5
**Touches files:** `/web/src/features/runs/components/ActivityTimeline.tsx`
**Estimated effort:** medium

### Implementation

**File: `/web/src/features/runs/components/ActivityTimeline.tsx`**:

```typescript
import { EventItem } from '@/features/shared/api/hooks'

const EVENT_LABELS: Record<string, string> = {
  run_started: 'Run Started',
  stage_started: 'Stage Started',
  stage_progress: 'Progress',
  stage_completed: 'Stage Completed',
  validation_failure: 'Validation Issue',
  warning: 'Warning',
  comparison_ready: 'Comparison Ready',
  pre_approval_reached: 'Pre-Approval Reached',
  approval_submitted: 'Approval Submitted',
  jira_created: 'Jira Created',
  sharepoint_synced: 'SharePoint Synced',
  submission_complete: 'Submission Complete',
  run_failed: 'Run Failed',
}

const EVENT_COLORS: Record<string, string> = {
  run_started: 'var(--cyan)',
  stage_started: 'var(--ink-soft)',
  stage_progress: 'var(--ink-mute)',
  stage_completed: 'var(--teal)',
  validation_failure: 'var(--err)',
  warning: 'var(--warn)',
  comparison_ready: 'var(--teal)',
  pre_approval_reached: 'var(--state-pre)',
  approval_submitted: 'var(--cyan)',
  jira_created: 'var(--add)',
  sharepoint_synced: 'var(--add)',
  submission_complete: 'var(--state-sub)',
  run_failed: 'var(--state-fail)',
}

interface Props {
  events: EventItem[]
}

export function ActivityTimeline({ events }: Props) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      {events.map((event) => {
        const color = EVENT_COLORS[event.type] || 'var(--ink-mute)'
        const label = EVENT_LABELS[event.type] || event.type
        const time = formatTime(event.ts)
        const detail = getEventDetail(event)

        return (
          <div key={event.id} style={{
            display: 'flex', gap: 12, alignItems: 'flex-start',
            padding: '10px 16px',
            background: 'var(--glass)', borderRadius: 'var(--radius-sm)',
            border: '1px solid var(--glass-stroke)',
          }}>
            {/* Timeline dot */}
            <div style={{
              width: 8, height: 8, borderRadius: '50%',
              background: color, marginTop: 5, flexShrink: 0,
            }} />

            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontWeight: 600, fontSize: 13, color: color }}>
                  {label}
                </span>
                <span style={{
                  fontFamily: 'var(--font-mono)', fontSize: 11,
                  color: 'var(--ink-dim)',
                }}>
                  {time}
                </span>
              </div>
              {detail && (
                <div style={{ fontSize: 12, color: 'var(--ink-mute)', marginTop: 4 }}>
                  {detail}
                </div>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}

function getEventDetail(event: EventItem): string | null {
  const p = event.payload
  switch (event.type) {
    case 'stage_started':
    case 'stage_completed':
      return p.stage_name ? `Stage: ${p.stage_name}` : null
    case 'stage_progress':
      return p.percent != null ? `${p.stage_name}: ${p.percent}%` : null
    case 'validation_failure':
      return p.rule ? `${p.field}: ${p.rule} (${p.severity})` : null
    case 'warning':
      return String(p.message || '')
    case 'comparison_ready': {
      const s = p.changes_summary as Record<string, number> | undefined
      if (!s) return null
      return `Add: ${s.add}, Remove: ${s.remove}, Rate Update: ${s.rate_update}, MCC: ${s.mcc_expansion}`
    }
    case 'run_failed':
      return String(p.message || 'Pipeline failed.')
    case 'jira_created':
      return `Epic: ${p.epic_key}, Story: ${p.story_key}`
    default:
      return null
  }
}

function formatTime(iso: string): string {
  try {
    return new Date(iso).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  } catch { return iso }
}
```

### Acceptance criteria

- [ ] Each event renders as a card with colored dot, label, timestamp, and detail text
- [ ] Events are ordered chronologically (server provides this order)
- [ ] `run_failed` events show in red; `stage_completed` in teal; etc.
- [ ] `comparison_ready` detail shows the change summary counts
- [ ] Timestamps use monospace font

---

## T-H7 — StageProgressBar

**Depends on:** T-H6
**Touches files:** `/web/src/features/runs/components/StageProgressBar.tsx`
**Estimated effort:** small

### Implementation

**File: `/web/src/features/runs/components/StageProgressBar.tsx`**:

```typescript
/**
 * Animated progress bar shown during in-progress runs.
 * Reads the latest stage_progress event's percent value.
 */

import { EventItem } from '@/features/shared/api/hooks'

interface Props {
  events: EventItem[]
}

export function StageProgressBar({ events }: Props) {
  const lastProgress = [...events]
    .reverse()
    .find((e) => e.type === 'stage_progress')

  if (!lastProgress) return null

  const percent = Number(lastProgress.payload.percent ?? 0)
  const stage = String(lastProgress.payload.stage_name ?? 'Processing')

  return (
    <div style={{ padding: '8px 0' }}>
      <div style={{ fontSize: 12, color: 'var(--ink-mute)', marginBottom: 6 }}>
        {stage}: {percent}%
      </div>
      <div style={{
        height: 4, borderRadius: 2, background: 'var(--glass-stroke)',
        overflow: 'hidden',
      }}>
        <div style={{
          height: '100%', width: `${percent}%`,
          background: 'var(--cyan)',
          borderRadius: 2,
          transition: 'width 0.5s ease',
        }} />
      </div>
    </div>
  )
}
```

### Acceptance criteria

- [ ] Shows the latest progress percentage with a cyan bar
- [ ] Hidden when no `stage_progress` events exist
- [ ] Smooth width transition when percentage updates via SSE

---

## T-H8 — ResultsTab container

**Depends on:** T-F2, T-F4, T-F8
**Touches files:** `/web/src/features/runs/components/ResultsTab.tsx`
**Estimated effort:** medium

### Goal

Wire `BaseTableWithDrawer` to the run's base table data and drawer record data.

### Implementation

**File: `/web/src/features/runs/components/ResultsTab.tsx`**:

```typescript
import { useBaseTable, useDrawerRecord } from '@/features/shared/api/hooks'
import { useUIStore } from '@/features/shared/stores/uiStore'
import { BaseTableWithDrawer, ColumnDef } from '@/features/shared/components/BaseTableWithDrawer'
import { DrawerContent } from './DrawerContent'
import { resultsColumns } from './resultsColumns'

interface Props {
  runId: string
}

export function ResultsTab({ runId }: Props) {
  const { data, isLoading } = useBaseTable(runId)
  const drawerOpen = useUIStore((s) => s.drawerOpen)
  const drawerMatchTag = useUIStore((s) => s.drawerMatchTag)
  const openDrawer = useUIStore((s) => s.openDrawer)
  const closeDrawer = useUIStore((s) => s.closeDrawer)

  const { data: drawerData } = useDrawerRecord(runId, drawerMatchTag || '')

  if (isLoading) {
    return <div style={{ color: 'var(--ink-mute)', padding: 24 }}>Loading results...</div>
  }

  return (
    <div style={{ height: 'calc(100vh - 300px)' }}>
      <BaseTableWithDrawer
        columns={resultsColumns}
        rows={data?.rows ?? []}
        getRowKey={(row) => String(row.match_tag)}
        selectedKey={drawerMatchTag}
        onRowClick={(row) => openDrawer(String(row.match_tag))}
        drawerOpen={drawerOpen}
        drawerTitle={drawerMatchTag ? `Details: ${drawerMatchTag}` : 'Details'}
        drawerContent={
          drawerMatchTag && drawerData ? (
            <DrawerContent record={drawerData} />
          ) : (
            <div style={{ color: 'var(--ink-dim)' }}>Loading...</div>
          )
        }
        onDrawerClose={closeDrawer}
      />
    </div>
  )
}
```

### Acceptance criteria

- [ ] Base table renders with data from `useBaseTable`
- [ ] Row click opens the drawer with the selected match_tag
- [ ] Drawer loads comparison record via `useDrawerRecord`
- [ ] Drawer close clears the Zustand drawer state

---

## T-H9 — Results column definitions

**Depends on:** T-F9, T-F8
**Touches files:** `/web/src/features/runs/components/resultsColumns.tsx`
**Estimated effort:** small

### Goal

Define the column configuration for the 18-column Results base table matching the mockup.

### Implementation

**File: `/web/src/features/runs/components/resultsColumns.tsx`**:

```typescript
import { ColumnDef } from '@/features/shared/components/BaseTableWithDrawer'
import { ActionPill } from '@/features/shared/components/ActionPill'
import { BaseTableRow } from '@/features/shared/api/hooks'

export const resultsColumns: ColumnDef<BaseTableRow>[] = [
  { key: 'match_tag', header: 'Match Tag', mono: true, width: '100px' },
  { key: 'maid', header: 'MAID', mono: true, width: '80px' },
  { key: 'mnemonic', header: 'Mnemonic', width: '160px' },
  {
    key: 'action', header: 'Action', width: '120px',
    render: (row) => row.action ? <ActionPill action={String(row.action)} /> : null,
  },
  { key: 'change_type', header: 'Change Type', width: '120px' },
  { key: 'system_update', header: 'System', width: '100px' },
  { key: 'interchange_rate_percent', header: 'Rate %', mono: true, width: '70px' },
  { key: 'interchange_rate_per_item', header: 'Per Item', mono: true, width: '70px' },
  { key: 'product_type', header: 'Product', width: '80px' },
  { key: 'channel', header: 'Channel', width: '120px' },
  { key: 'regulation_status', header: 'Regulation', width: '110px' },
  { key: 'mcc_group', header: 'MCC Group', width: '120px' },
]
```

### Acceptance criteria

- [ ] Column definitions produce a table with the expected headers
- [ ] MAID and Match Tag use mono font
- [ ] Action column renders `ActionPill` with D-047 coloring

### Notes

The full 18-column spec in the backend has additional fields (breakeven, IRD, etc.) — those exist in the data via `extra="allow"` but aren't rendered as named columns until V requests them. The 12 columns above cover the primary display columns from the mockup. Additional columns can be added by extending this array.

---

## T-H10 — DrawerContent shell

**Depends on:** T-H11, T-H12, T-H13
**Touches files:** `/web/src/features/runs/components/DrawerContent.tsx`
**Estimated effort:** small

### Implementation

**File: `/web/src/features/runs/components/DrawerContent.tsx`**:

```typescript
import { FieldDeltasPanel } from './FieldDeltasPanel'
import { ETLImpactPanel } from './ETLImpactPanel'
import { ModFilePanel } from './ModFilePanel'

interface Props {
  record: Record<string, unknown>
}

export function DrawerContent({ record }: Props) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      <FieldDeltasPanel
        oldRecord={record.old_record as Record<string, unknown> | null}
        newRecord={record.new_record as Record<string, unknown> | null}
        correlatedFields={record.correlated_fields as Record<string, unknown> | null}
      />
      <ETLImpactPanel
        entries={record.etl_entries as Array<Record<string, unknown>> | null}
      />
      <ModFilePanel
        entry={record.mod_file_entry as Record<string, unknown> | null}
      />
    </div>
  )
}
```

### Acceptance criteria

- [ ] Drawer content renders three panels vertically
- [ ] Props are passed from the comparison record to each panel

---

## T-H11 — FieldDeltasPanel

**Depends on:** T7
**Touches files:** `/web/src/features/runs/components/FieldDeltasPanel.tsx`
**Estimated effort:** medium

### Goal

Show old vs new field values side-by-side, highlighting changed fields per `correlated_fields`.

### Implementation

**File: `/web/src/features/runs/components/FieldDeltasPanel.tsx`**:

```typescript
interface Props {
  oldRecord: Record<string, unknown> | null
  newRecord: Record<string, unknown> | null
  correlatedFields: Record<string, unknown> | null
}

export function FieldDeltasPanel({ oldRecord, newRecord, correlatedFields }: Props) {
  if (!oldRecord && !newRecord) {
    return <div style={{ color: 'var(--ink-dim)', fontSize: 13 }}>No field data available.</div>
  }

  // Gather all field keys from both records.
  const allKeys = Array.from(new Set([
    ...Object.keys(oldRecord || {}),
    ...Object.keys(newRecord || {}),
  ])).sort()

  const changedKeys = new Set(Object.keys(correlatedFields || {}))

  return (
    <div>
      <h4 style={{ margin: '0 0 10px', fontSize: 13, fontWeight: 600, color: 'var(--ink)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
        Field Comparison
      </h4>
      <div style={{ fontSize: 12 }}>
        {allKeys.map((key) => {
          const oldVal = oldRecord?.[key]
          const newVal = newRecord?.[key]
          const isChanged = changedKeys.has(key)

          return (
            <div key={key} style={{
              display: 'grid', gridTemplateColumns: '140px 1fr 1fr', gap: 8,
              padding: '6px 0', borderBottom: '1px solid var(--glass-stroke)',
              background: isChanged ? 'rgba(247,210,143,0.06)' : 'transparent',
            }}>
              <div style={{
                color: isChanged ? 'var(--amber)' : 'var(--ink-mute)',
                fontWeight: isChanged ? 600 : 400,
              }}>
                {key}
              </div>
              <div style={{
                fontFamily: 'var(--font-mono)', fontSize: 11,
                color: oldVal != null ? 'var(--ink-soft)' : 'var(--ink-dim)',
              }}>
                {oldVal != null ? String(oldVal) : '—'}
              </div>
              <div style={{
                fontFamily: 'var(--font-mono)', fontSize: 11,
                color: newVal != null ? 'var(--ink)' : 'var(--ink-dim)',
                fontWeight: isChanged ? 600 : 400,
              }}>
                {newVal != null ? String(newVal) : '—'}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
```

### Acceptance criteria

- [ ] Shows a 3-column grid: field name, old value, new value
- [ ] Changed fields (in `correlated_fields`) highlighted with amber background
- [ ] Missing values show "—"
- [ ] Values use monospace font

---

## T-H12 — ETLImpactPanel

**Depends on:** T-F9
**Touches files:** `/web/src/features/runs/components/ETLImpactPanel.tsx`
**Estimated effort:** small

### Implementation

**File: `/web/src/features/runs/components/ETLImpactPanel.tsx`**:

```typescript
import { EntryPill } from '@/features/shared/components/EntryPill'

interface Props {
  entries: Array<Record<string, unknown>> | null
}

export function ETLImpactPanel({ entries }: Props) {
  if (!entries || entries.length === 0) {
    return <div style={{ color: 'var(--ink-dim)', fontSize: 13 }}>No ETL entries.</div>
  }

  return (
    <div>
      <h4 style={{ margin: '0 0 10px', fontSize: 13, fontWeight: 600, color: 'var(--ink)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
        ETL Impact
      </h4>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
        {entries.map((entry, i) => (
          <div key={i} style={{
            display: 'flex', alignItems: 'center', gap: 10,
            padding: '8px 12px', background: 'var(--glass)',
            borderRadius: 'var(--radius-sm)', border: '1px solid var(--glass-stroke)',
          }}>
            <EntryPill entryType={String(entry.entry_type || '')} />
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--ink-soft)' }}>
              {String(entry.mnemonic || '')}
            </span>
            <span style={{ fontSize: 11, color: 'var(--ink-mute)', marginLeft: 'auto' }}>
              {String(entry.rate || '')}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
```

### Acceptance criteria

- [ ] Each ETL entry renders with `EntryPill` (D-047 drawer tier coloring)
- [ ] Mnemonic in monospace; rate right-aligned
- [ ] Empty state shown when no entries

---

## T-H13 — ModFilePanel

**Depends on:** T7
**Touches files:** `/web/src/features/runs/components/ModFilePanel.tsx`
**Estimated effort:** small

### Implementation

**File: `/web/src/features/runs/components/ModFilePanel.tsx`**:

```typescript
interface Props {
  entry: Record<string, unknown> | null
}

export function ModFilePanel({ entry }: Props) {
  if (!entry) return null

  return (
    <div>
      <h4 style={{ margin: '0 0 10px', fontSize: 13, fontWeight: 600, color: 'var(--ink)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
        Mod File Entry
      </h4>
      <div style={{
        padding: '10px 14px', background: 'var(--glass)',
        borderRadius: 'var(--radius-sm)', border: '1px solid var(--glass-stroke)',
        fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--ink-soft)',
      }}>
        <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
          {JSON.stringify(entry, null, 2)}
        </pre>
      </div>
    </div>
  )
}
```

### Acceptance criteria

- [ ] Shows the mod file entry as formatted JSON
- [ ] Hidden when entry is null

---

## T-H14 — IssuesTab container

**Depends on:** T-F2
**Touches files:** `/web/src/features/runs/components/IssuesTab.tsx`
**Estimated effort:** small

### Implementation

**File: `/web/src/features/runs/components/IssuesTab.tsx`**:

```typescript
import { useIssues } from '@/features/shared/api/hooks'
import { IssueCard } from './IssueCard'

interface Props { runId: string }

export function IssuesTab({ runId }: Props) {
  const { data, isLoading } = useIssues(runId)

  if (isLoading) return <div style={{ color: 'var(--ink-mute)', padding: 24 }}>Loading issues...</div>

  if (!data || data.issues.length === 0) {
    return (
      <div style={{ padding: 48, textAlign: 'center', color: 'var(--ink-dim)' }}>
        No issues found for this run.
      </div>
    )
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
      <div style={{ fontSize: 12, color: 'var(--ink-mute)', marginBottom: 4 }}>
        {data.total} issue{data.total !== 1 ? 's' : ''} found
      </div>
      {data.issues.map((issue) => <IssueCard key={issue.id} issue={issue} />)}
    </div>
  )
}
```

### Acceptance criteria

- [ ] Shows issue count header
- [ ] Renders IssueCards sorted by severity (critical first, from server)
- [ ] Empty state for runs with no issues

---

## T-H15 — IssueCard

**Depends on:** T7
**Touches files:** `/web/src/features/runs/components/IssueCard.tsx`
**Estimated effort:** small

### Implementation

**File: `/web/src/features/runs/components/IssueCard.tsx`**:

```typescript
import { IssueItem } from '@/features/shared/api/hooks'

const SEVERITY_COLORS: Record<string, string> = {
  critical: 'var(--crit)',
  error: 'var(--err)',
  warning: 'var(--warn)',
}

export function IssueCard({ issue }: { issue: IssueItem }) {
  const sevColor = SEVERITY_COLORS[issue.severity || 'warning'] || 'var(--warn)'

  return (
    <div style={{
      padding: '12px 16px', borderRadius: 'var(--radius-sm)',
      background: 'var(--glass)', border: '1px solid var(--glass-stroke)',
      borderLeft: `3px solid ${sevColor}`,
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontSize: 13, fontWeight: 600, color: sevColor, textTransform: 'capitalize' }}>
          {issue.severity || issue.type}
        </span>
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--ink-dim)' }}>
          {new Date(issue.ts).toLocaleTimeString()}
        </span>
      </div>
      {issue.message && (
        <div style={{ fontSize: 12, color: 'var(--ink-soft)', marginTop: 6 }}>
          {issue.message}
        </div>
      )}
    </div>
  )
}
```

### Acceptance criteria

- [ ] Critical issues have red left border, error orange, warning yellow per D-049
- [ ] Severity label is colored and capitalized
- [ ] Timestamp in monospace

---

## T-H16 — JiraInfoPanel

**Depends on:** T-F2
**Touches files:** `/web/src/features/runs/components/JiraInfoPanel.tsx`
**Estimated effort:** small

### Implementation

**File: `/web/src/features/runs/components/JiraInfoPanel.tsx`**:

```typescript
import { useJiraInfo } from '@/features/shared/api/hooks'

interface Props { runId: string }

export function JiraInfoPanel({ runId }: Props) {
  const { data, isLoading } = useJiraInfo(runId)

  if (isLoading || !data) return null

  return (
    <div style={{
      padding: '14px 18px', borderRadius: 'var(--radius)',
      background: 'var(--glass)', border: '1px solid var(--glass-stroke)',
    }}>
      <h4 style={{ margin: '0 0 10px', fontSize: 13, fontWeight: 600, color: 'var(--ink)' }}>
        Jira Submission
      </h4>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 6, fontSize: 13 }}>
        {data.epic_key && (
          <div>
            <span style={{ color: 'var(--ink-mute)' }}>Epic: </span>
            <a href={data.epic_url || '#'} target="_blank" rel="noopener"
              style={{ color: 'var(--cyan)', textDecoration: 'none' }}>
              {data.epic_key}
            </a>
          </div>
        )}
        {data.story_key && (
          <div>
            <span style={{ color: 'var(--ink-mute)' }}>Story: </span>
            <a href={data.story_url || '#'} target="_blank" rel="noopener"
              style={{ color: 'var(--cyan)', textDecoration: 'none' }}>
              {data.story_key}
            </a>
          </div>
        )}
        {data.sharepoint_path && (
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: 11, color: 'var(--ink-mute)', marginTop: 4 }}>
            SharePoint: {data.sharepoint_path}
          </div>
        )}
      </div>
    </div>
  )
}
```

### Acceptance criteria

- [ ] Epic and Story keys render as clickable links using server-constructed URLs (D-073)
- [ ] SharePoint path shown in monospace
- [ ] Hidden when no Jira info available

---

## T-H17 — FailurePanel

**Depends on:** T7
**Touches files:** `/web/src/features/runs/components/FailurePanel.tsx`
**Estimated effort:** small

### Implementation

**File: `/web/src/features/runs/components/FailurePanel.tsx`**:

```typescript
interface Props {
  failure: Record<string, unknown>
}

export function FailurePanel({ failure }: Props) {
  return (
    <div style={{
      padding: '14px 18px', borderRadius: 'var(--radius)',
      background: 'rgba(252,165,165,0.06)', border: '1px solid rgba(252,165,165,0.15)',
    }}>
      <h4 style={{ margin: '0 0 8px', fontSize: 14, fontWeight: 600, color: 'var(--state-fail)' }}>
        Run Failed
      </h4>
      <div style={{ fontSize: 13, color: 'var(--ink-soft)' }}>
        {String(failure.error_message || 'An error occurred.')}
      </div>
      <div style={{ fontSize: 12, color: 'var(--ink-mute)', marginTop: 4 }}>
        Stage: {String(failure.stage || 'unknown')} · Strategy: {String(failure.retry_strategy || '—')}
      </div>
      {failure.technical_details && (
        <details style={{ marginTop: 10 }}>
          <summary style={{ fontSize: 12, color: 'var(--ink-mute)', cursor: 'pointer' }}>
            Technical details
          </summary>
          <pre style={{
            marginTop: 8, padding: 12, background: 'var(--bg)',
            borderRadius: 'var(--radius-sm)', fontSize: 11,
            fontFamily: 'var(--font-mono)', color: 'var(--ink-dim)',
            whiteSpace: 'pre-wrap', maxHeight: 200, overflowY: 'auto',
          }}>
            {String(failure.technical_details)}
          </pre>
        </details>
      )}
    </div>
  )
}
```

### Acceptance criteria

- [ ] Shows error_message, stage, and retry_strategy from failure.json
- [ ] Technical details collapsed by default behind a `<details>` toggle
- [ ] Red-tinted background matching the failure state

---

## T-H18 — Route wiring in App.tsx

**Depends on:** T-H1, T-G8
**Touches files:** `/web/src/App.tsx` (modification), `/web/src/features/runs/index.ts`
**Estimated effort:** small

### Goal

Replace the Run Detail placeholder with the real `RunDetailScreen` import.

### Implementation

Update `/web/src/App.tsx`:

```typescript
import { RunDetailScreen } from '@/features/runs/screens/RunDetailScreen'

// In the route table, replace RunDetailPlaceholder:
<Route path="/runs/new" element={<RunDetailScreen />} />
<Route path="/runs/:id" element={<RunDetailScreen />} />
```

Update `/web/src/features/runs/index.ts`:

```typescript
export { RunsListScreen } from './screens/RunsListScreen'
export { RunDetailScreen } from './screens/RunDetailScreen'
```

### Acceptance criteria

- [ ] `/runs/:id` renders the real RunDetailScreen with all three tabs
- [ ] `/runs/new` renders RunDetailScreen (pre-run state, empty events/data)
- [ ] `npm run lint` passes with zero boundary violations
# Section I — Artifact Preview screen

This section builds the Artifact Preview screen (`/runs/:id/artifact` route) per functional-integration-spec §10. A split-pane layout: PDF viewer on the left, base table + drawer on the right. The divider is draggable. PDF rendering uses `react-pdf` (lazy-loaded). The right pane reuses `BaseTableWithDrawer` from T-F8.

Section index:

- [ ] T-I1 — ArtifactPreviewScreen container (split pane layout)
- [ ] T-I2 — PDF viewer pane (react-pdf, lazy loaded)
- [ ] T-I3 — Artifact data pane (BaseTableWithDrawer reuse)
- [ ] T-I4 — Draggable divider
- [ ] T-I5 — Navigation between records (prev/next from base table)
- [ ] T-I6 — Route wiring with React.lazy()

---

## T-I1 — ArtifactPreviewScreen container

**Depends on:** T-F2, T-F4, T-I2, T-I3, T-I4
**Touches files:** `/web/src/features/artifact/screens/ArtifactPreviewScreen.tsx`
**Estimated effort:** medium

### Goal

Top-level split-pane layout: PDF left, data right, draggable divider in between. Reads `run_id` from route params. Divider position stored in Zustand.

### Implementation

**File: `/web/src/features/artifact/screens/ArtifactPreviewScreen.tsx`**:

```typescript
import { useParams, useNavigate } from 'react-router-dom'
import { useRunDetail, useBaseTable } from '@/features/shared/api/hooks'
import { useUIStore } from '@/features/shared/stores/uiStore'
import { PdfViewerPane } from '../components/PdfViewerPane'
import { ArtifactDataPane } from '../components/ArtifactDataPane'
import { Divider } from '../components/Divider'

export function ArtifactPreviewScreen() {
  const { id: runId } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data: runData, isLoading: runLoading } = useRunDetail(runId || '')
  const { data: tableData } = useBaseTable(runId || '')
  const dividerPosition = useUIStore((s) => s.dividerPosition)
  const setDividerPosition = useUIStore((s) => s.setDividerPosition)

  if (runLoading || !runData) {
    return <div style={{ padding: 48, color: 'var(--ink-mute)', textAlign: 'center' }}>Loading...</div>
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 120px)' }}>
      {/* Header bar with back button */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: 12,
        padding: '8px 0 12px', borderBottom: '1px solid var(--glass-stroke)',
        marginBottom: 12,
      }}>
        <button
          onClick={() => navigate(`/runs/${runId}`)}
          style={{
            padding: '4px 12px', borderRadius: 'var(--radius-sm)',
            border: '1px solid var(--glass-stroke)', background: 'var(--glass)',
            color: 'var(--ink-soft)', cursor: 'pointer', fontSize: 12,
          }}
        >
          ← Back to Run Detail
        </button>
        <span style={{ fontSize: 14, fontWeight: 600, color: 'var(--ink)' }}>
          Artifact Preview
        </span>
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: 12, color: 'var(--ink-mute)' }}>
          {runId}
        </span>
      </div>

      {/* Split pane */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        <div style={{ width: `${dividerPosition}%`, overflow: 'auto' }}>
          <PdfViewerPane runId={runId || ''} />
        </div>
        <Divider position={dividerPosition} onPositionChange={setDividerPosition} />
        <div style={{ width: `${100 - dividerPosition}%`, overflow: 'hidden' }}>
          <ArtifactDataPane runId={runId || ''} rows={tableData?.rows ?? []} />
        </div>
      </div>
    </div>
  )
}
```

### Acceptance criteria

- [ ] Split-pane layout renders with PDF on left, data on right
- [ ] Back button navigates to `/runs/:id`
- [ ] Divider position from Zustand controls the split ratio
- [ ] Default 50/50 split on first load

---

## T-I2 — PDF viewer pane (react-pdf, lazy loaded)

**Depends on:** T2 (react-pdf dependency)
**Touches files:** `/web/src/features/artifact/components/PdfViewerPane.tsx`
**Estimated effort:** medium

### Goal

Render the agreement PDF using react-pdf's `Document` and `Page` components. The PDF URL is `GET /api/runs/{run_id}/pdf`. Handles the "no PDF available" state gracefully.

### Context

From T2's Vite config: react-pdf is in the `pdfWorker` manual chunk. The PDF.js worker must be configured via `pdfjs.GlobalWorkerOptions.workerSrc`.

### Implementation

**File: `/web/src/features/artifact/components/PdfViewerPane.tsx`**:

```typescript
import { useState } from 'react'
import { Document, Page, pdfjs } from 'react-pdf'
import 'react-pdf/dist/esm/Page/AnnotationLayer.css'
import 'react-pdf/dist/esm/Page/TextLayer.css'

// Configure PDF.js worker (bundled via Vite manualChunks).
pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.mjs',
  import.meta.url,
).toString()

interface Props {
  runId: string
}

export function PdfViewerPane({ runId }: Props) {
  const [numPages, setNumPages] = useState<number>(0)
  const [loadError, setLoadError] = useState(false)

  const baseUrl = import.meta.env.VITE_API_BASE_URL || ''
  const pdfUrl = `${baseUrl}/api/runs/${encodeURIComponent(runId)}/pdf`

  if (loadError) {
    return (
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        height: '100%', color: 'var(--ink-dim)', fontSize: 13,
        padding: 32, textAlign: 'center',
      }}>
        No PDF available for this run.
        <br />
        The agreement document may not have been preserved.
      </div>
    )
  }

  return (
    <div style={{
      padding: 16, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8,
    }}>
      <Document
        file={pdfUrl}
        onLoadSuccess={({ numPages: n }) => setNumPages(n)}
        onLoadError={() => setLoadError(true)}
        loading={
          <div style={{ color: 'var(--ink-mute)', padding: 32 }}>Loading PDF...</div>
        }
      >
        {Array.from({ length: numPages }, (_, i) => (
          <Page
            key={i + 1}
            pageNumber={i + 1}
            width={500}
            renderTextLayer={true}
            renderAnnotationLayer={false}
          />
        ))}
      </Document>
      {numPages > 0 && (
        <div style={{ fontSize: 11, color: 'var(--ink-dim)' }}>
          {numPages} page{numPages !== 1 ? 's' : ''}
        </div>
      )}
    </div>
  )
}
```

### Acceptance criteria

- [ ] PDF renders when available via `GET /api/runs/{run_id}/pdf`
- [ ] "No PDF available" message when the endpoint returns 404
- [ ] Pages render sequentially with text layer enabled (for text selection)
- [ ] Loading indicator while PDF is being fetched
- [ ] PDF.js worker configured correctly (no console errors about worker)

---

## T-I3 — Artifact data pane (BaseTableWithDrawer reuse)

**Depends on:** T-F8, T-H9
**Touches files:** `/web/src/features/artifact/components/ArtifactDataPane.tsx`
**Estimated effort:** small

### Goal

Reuse `BaseTableWithDrawer` + `DrawerContent` from Sections F/H in the right pane of the artifact preview.

### Implementation

**File: `/web/src/features/artifact/components/ArtifactDataPane.tsx`**:

```typescript
import { useUIStore } from '@/features/shared/stores/uiStore'
import { useDrawerRecord, BaseTableRow } from '@/features/shared/api/hooks'
import { BaseTableWithDrawer } from '@/features/shared/components/BaseTableWithDrawer'
import { DrawerContent } from '@/features/runs/components/DrawerContent'
import { resultsColumns } from '@/features/runs/components/resultsColumns'

interface Props {
  runId: string
  rows: BaseTableRow[]
}

export function ArtifactDataPane({ runId, rows }: Props) {
  const drawerOpen = useUIStore((s) => s.drawerOpen)
  const drawerMatchTag = useUIStore((s) => s.drawerMatchTag)
  const openDrawer = useUIStore((s) => s.openDrawer)
  const closeDrawer = useUIStore((s) => s.closeDrawer)

  const { data: drawerData } = useDrawerRecord(runId, drawerMatchTag || '')

  return (
    <BaseTableWithDrawer
      columns={resultsColumns}
      rows={rows}
      getRowKey={(row) => String(row.match_tag)}
      selectedKey={drawerMatchTag}
      onRowClick={(row) => openDrawer(String(row.match_tag))}
      drawerOpen={drawerOpen}
      drawerTitle={drawerMatchTag ? `Details: ${drawerMatchTag}` : 'Details'}
      drawerContent={
        drawerMatchTag && drawerData
          ? <DrawerContent record={drawerData} />
          : <div style={{ color: 'var(--ink-dim)' }}>Loading...</div>
      }
      onDrawerClose={closeDrawer}
    />
  )
}
```

### Acceptance criteria

- [ ] Right pane renders the same base table as Run Detail's Results tab
- [ ] Row click opens the drawer with comparison details
- [ ] Reuses `resultsColumns` and `DrawerContent` from Section H (no duplication)

### Notes

The cross-feature import (`@/features/runs/components/DrawerContent`) is acceptable per D-062's boundary rules because `DrawerContent` is a pure presentational component. If V later wants stricter boundaries, these shared components can be promoted to `shared/`.

---

## T-I4 — Draggable divider

**Depends on:** T-F4
**Touches files:** `/web/src/features/artifact/components/Divider.tsx`
**Estimated effort:** small

### Implementation

**File: `/web/src/features/artifact/components/Divider.tsx`**:

```typescript
import { useCallback, useRef } from 'react'

interface Props {
  position: number  // 0-100 percentage
  onPositionChange: (pos: number) => void
}

export function Divider({ position, onPositionChange }: Props) {
  const containerRef = useRef<HTMLDivElement | null>(null)

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault()
    const startX = e.clientX

    const handleMouseMove = (moveEvent: MouseEvent) => {
      const parent = containerRef.current?.parentElement
      if (!parent) return
      const rect = parent.getBoundingClientRect()
      const newPos = ((moveEvent.clientX - rect.left) / rect.width) * 100
      // Clamp between 20% and 80%.
      onPositionChange(Math.min(80, Math.max(20, newPos)))
    }

    const handleMouseUp = () => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
      document.body.style.cursor = ''
      document.body.style.userSelect = ''
    }

    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)
    document.body.style.cursor = 'col-resize'
    document.body.style.userSelect = 'none'
  }, [onPositionChange])

  return (
    <div
      ref={containerRef}
      onMouseDown={handleMouseDown}
      style={{
        width: 6, cursor: 'col-resize', flexShrink: 0,
        background: 'var(--glass-stroke)',
        transition: 'background 0.15s',
      }}
      onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--cyan)')}
      onMouseLeave={(e) => (e.currentTarget.style.background = 'var(--glass-stroke)')}
    />
  )
}
```

### Acceptance criteria

- [ ] Dragging the divider changes the split ratio in real time
- [ ] Clamped between 20% and 80% (can't collapse either pane fully)
- [ ] Divider highlights cyan on hover
- [ ] Text selection disabled during drag (prevents accidental selection)

---

## T-I5 — Navigation between records

**Depends on:** T-I3, T-F4
**Touches files:** `/web/src/features/artifact/components/ArtifactDataPane.tsx` (modification)
**Estimated effort:** small

### Goal

When the drawer is open, add prev/next buttons to navigate between base table records without closing the drawer. This lets the operator step through records while viewing the PDF on the left.

### Implementation

Add to `ArtifactDataPane.tsx`, inside the `drawerContent` prop:

```typescript
// Compute prev/next match_tags from the rows array.
const currentIndex = rows.findIndex((r) => String(r.match_tag) === drawerMatchTag)
const prevTag = currentIndex > 0 ? String(rows[currentIndex - 1].match_tag) : null
const nextTag = currentIndex < rows.length - 1 ? String(rows[currentIndex + 1].match_tag) : null

// Add navigation buttons above DrawerContent:
drawerContent={
  drawerMatchTag ? (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 12 }}>
        <button
          disabled={!prevTag}
          onClick={() => prevTag && openDrawer(prevTag)}
          style={navBtnStyle(!prevTag)}
        >
          ← Prev
        </button>
        <span style={{ fontSize: 11, color: 'var(--ink-dim)' }}>
          {currentIndex + 1} / {rows.length}
        </span>
        <button
          disabled={!nextTag}
          onClick={() => nextTag && openDrawer(nextTag)}
          style={navBtnStyle(!nextTag)}
        >
          Next →
        </button>
      </div>
      {drawerData
        ? <DrawerContent record={drawerData} />
        : <div style={{ color: 'var(--ink-dim)' }}>Loading...</div>}
    </div>
  ) : null
}
```

Where `navBtnStyle` is:

```typescript
function navBtnStyle(disabled: boolean): React.CSSProperties {
  return {
    padding: '4px 10px', borderRadius: 'var(--radius-sm)',
    border: '1px solid var(--glass-stroke)', background: disabled ? 'transparent' : 'var(--glass)',
    color: disabled ? 'var(--ink-dim)' : 'var(--ink-soft)',
    cursor: disabled ? 'default' : 'pointer', fontSize: 11,
  }
}
```

### Acceptance criteria

- [ ] Prev/Next buttons navigate between records in the drawer
- [ ] Counter shows "N / total" position
- [ ] Prev disabled on first record; Next disabled on last
- [ ] Navigating updates the drawer content (new `useDrawerRecord` fetch)

---

## T-I6 — Route wiring with React.lazy()

**Depends on:** T-I1, T-G8
**Touches files:** `/web/src/App.tsx` (modification), `/web/src/features/artifact/index.ts`
**Estimated effort:** small

### Goal

Lazy-load the Artifact Preview screen to keep the main bundle small (react-pdf is large).

### Implementation

Update `/web/src/App.tsx`:

```typescript
import { Suspense, lazy } from 'react'

const ArtifactPreviewScreen = lazy(() =>
  import('@/features/artifact/screens/ArtifactPreviewScreen').then((m) => ({
    default: m.ArtifactPreviewScreen,
  }))
)

// In route table, replace the placeholder:
<Route
  path="/runs/:id/artifact"
  element={
    <Suspense fallback={<div style={{ padding: 48, color: 'var(--ink-mute)' }}>Loading Artifact Preview...</div>}>
      <ArtifactPreviewScreen />
    </Suspense>
  }
/>
```

**File: `/web/src/features/artifact/index.ts`**:

```typescript
export { ArtifactPreviewScreen } from './screens/ArtifactPreviewScreen'
```

### Acceptance criteria

- [ ] Navigating to `/runs/:id/artifact` lazy-loads the artifact chunk
- [ ] Suspense fallback shows while the chunk loads
- [ ] The `pdfWorker` manual chunk (from T2's Vite config) loads separately from the main bundle
- [ ] `npm run build` produces separate chunks for artifact + pdfWorker
# Section J — Production deployment

This section configures the single-process uvicorn deployment per D-070. No Docker, no NGINX — just `uvicorn` serving the FastAPI backend with the Vite-built frontend as static files. The JPMC VDI deployment model is a single machine running both the pipeline and the UI.

Section index:

- [ ] T-J1 — Single-uvicorn production config (static mount)
- [ ] T-J2 — Production .env template
- [ ] T-J3 — Startup runbook
- [ ] T-J4 — Health check / smoke test script

---

## T-J1 — Single-uvicorn production config (static mount)

**Depends on:** T1, T2
**Touches files:** `/api/main.py` (modification), `/scripts/build.sh`
**Estimated effort:** medium

### Goal

Configure the FastAPI app to serve the Vite-built frontend as static files from `/web/dist/` in production. In development, the Vite dev server proxies to FastAPI. In production, FastAPI serves everything.

### Implementation

**Modification to `/api/main.py`** — add static file mount after all API routes:

```python
import os
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# ... (after all router includes) ...

# Static file serving for production (Vite-built frontend).
# In development, Vite's dev server handles this via proxy.
_STATIC_DIR = Path(__file__).parent.parent / "web" / "dist"

if _STATIC_DIR.is_dir():
    # Serve static assets (JS, CSS, images, fonts).
    app.mount("/assets", StaticFiles(directory=str(_STATIC_DIR / "assets")), name="assets")
    app.mount("/fonts", StaticFiles(directory=str(_STATIC_DIR / "fonts")), name="fonts")

    # SPA fallback: serve index.html for any non-API route.
    @app.get("/{path:path}")
    async def spa_fallback(path: str):
        # Don't intercept API routes.
        if path.startswith("api/"):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="API route not found")
        # Serve the file if it exists (e.g., favicon.ico).
        file_path = _STATIC_DIR / path
        if file_path.is_file():
            return FileResponse(str(file_path))
        # Otherwise serve index.html for SPA routing.
        return FileResponse(str(_STATIC_DIR / "index.html"))
```

**File: `/scripts/build.sh`** — build script for production:

```bash
#!/usr/bin/env bash
# Build script for ci_ui production deployment.
# Run from the ci_ui repo root directory.
set -euo pipefail

echo "=== Building frontend ==="
cd web
npm ci --prefer-offline
npm run build
cd ..

echo "=== Frontend built to web/dist/ ==="
echo "=== Start with: uvicorn api.main:app --host 0.0.0.0 --port 8000 ==="
echo "=== Or:         python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 ==="
```

### Acceptance criteria

- [ ] `bash scripts/build.sh` builds the frontend into `web/dist/`
- [ ] `uvicorn api.main:app --port 8000` serves both the API and the frontend
- [ ] Navigating to `http://localhost:8000/` serves `index.html`
- [ ] Navigating to `http://localhost:8000/runs` serves `index.html` (SPA fallback)
- [ ] `http://localhost:8000/api/runs` returns the API response (not index.html)
- [ ] `http://localhost:8000/assets/main-xxx.js` serves the JS bundle
- [ ] `http://localhost:8000/fonts/GeneralSans-Variable.woff2` serves the font file
- [ ] In development (no `web/dist/`), the static mount is skipped; Vite proxy works normally

---

## T-J2 — Production .env template

**Depends on:** T4, T5
**Touches files:** `/api/.env.production.example`
**Estimated effort:** small

### Goal

Provide a production `.env` template with all 13 backend variables documented and set to realistic production values.

### Implementation

**File: `/api/.env.production.example`**:

```bash
# ci_ui Backend — Production Environment Variables
# Copy to /api/.env and fill in actual values before deployment.
# See backend-spec.md §4 for variable documentation.

# --- Adapter profile ---
# "real" for production (requires PIPELINE_MODULE_PATH).
# "mock" for development and demo (no pipeline dependency).
ADAPTER_PROFILE=real

# --- Pipeline integration ---
# Absolute path to the CI_Vision repo root (sibling of ci_ui in CI_Main/).
# Example: C:\Users\v123456\CI_Main\CI_Vision
PIPELINE_MODULE_PATH=C:\Users\REPLACE\CI_Main\CI_Vision

# Python interpreter path (must have pipeline dependencies installed).
PYTHON_INTERPRETER=python

# --- Filesystem paths ---
# Where pipeline output folders are written.
OUTPUT_BASE_FOLDER=C:\Users\REPLACE\CI_Main\CI_Vision\output

# Comma-separated list of directories the operator can select as input.
ALLOWED_INPUT_ROOTS=C:\Users\REPLACE\CI_Main\CI_Vision\input

# --- Database ---
# SQLite database file. Created automatically on first startup.
DATABASE_PATH=./ci_ui.db

# --- External services ---
# Jira base URL for constructing epic/story links (D-073).
JPMC_JIRA_BASE_URL=https://jira.jpmchase.net

# --- Mock adapter settings (ignored when ADAPTER_PROFILE=real) ---
MOCK_LATENCY=realistic
MOCK_FAILURE=none

# --- Auth (MVP stub per D-030) ---
# No auth variables needed for MVP. X-Operator-ID header is the only
# identity mechanism. Future phases may add SSO integration.

# --- CORS ---
# In production (static mount), CORS isn't needed because frontend and
# backend share the same origin. The CORS middleware in main.py can remain
# with allow_origins=["*"] since it only applies to cross-origin requests.
```

### Acceptance criteria

- [ ] All 13 environment variables are documented with examples
- [ ] `ADAPTER_PROFILE=real` is the production default
- [ ] File includes both Windows-style paths (VDI default) with `REPLACE` placeholders
- [ ] Comments explain each variable's purpose

---

## T-J3 — Startup runbook

**Depends on:** T-J1, T-J2
**Touches files:** `/RUNBOOK.md`
**Estimated effort:** small

### Goal

Concise startup guide for the operator or partner deploying ci_ui on VDI.

### Implementation

**File: `/RUNBOOK.md`**:

````markdown
# ci_ui — Startup Runbook

## Prerequisites

1. **Python 3.11+** with pip
2. **Node.js 18+** with npm
3. **CI_Vision repo** cloned alongside ci_ui in the `CI_Main/` workspace:
   ```
   CI_Main/
   ├── ci_ui/          ← this repo
   └── CI_Vision/      ← partner's pipeline repo
   ```

## First-time setup

```bash
# 1. Install backend dependencies.
cd ci_ui/api
pip install -r requirements.txt

# 2. Build the frontend.
cd ../
bash scripts/build.sh

# 3. Configure environment.
cp api/.env.production.example api/.env
# Edit api/.env — set PIPELINE_MODULE_PATH, OUTPUT_BASE_FOLDER, ALLOWED_INPUT_ROOTS.
```

## Start the server

```bash
cd ci_ui
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000` in Chrome.

## Development mode (mock adapter)

Terminal 1 — backend:
```bash
cd ci_ui/api
# Ensure .env has ADAPTER_PROFILE=mock
uvicorn api.main:app --reload --port 8000
```

Terminal 2 — frontend:
```bash
cd ci_ui/web
npm run dev
```

Open `http://localhost:5173` (Vite dev server proxies to :8000).

## Troubleshooting

| Symptom | Fix |
|---|---|
| `ModuleNotFoundError: CI_LLM` | Set `PIPELINE_MODULE_PATH` to CI_Vision repo root |
| Port 8000 in use | `netstat -ano | findstr :8000` then kill the PID |
| Frontend shows blank page | Run `bash scripts/build.sh` to rebuild |
| Database locked errors | Only one uvicorn instance should run at a time |
| SSE not updating | Check browser DevTools → Network for the `/api/events` stream |
````

### Acceptance criteria

- [ ] A new developer can follow the runbook to get ci_ui running on a fresh VDI
- [ ] Both production (single process) and development (two processes) modes documented
- [ ] Troubleshooting table covers the most common VDI issues
- [ ] No external network dependencies in the instructions (all deps pre-installed or vendored)

---

## T-J4 — Health check / smoke test script

**Depends on:** T-J1
**Touches files:** `/scripts/smoke_test.sh`
**Estimated effort:** small

### Goal

A simple script that verifies the server is running and the key endpoints respond correctly. Runs after deployment to confirm the system is healthy.

### Implementation

**File: `/scripts/smoke_test.sh`**:

```bash
#!/usr/bin/env bash
# Smoke test for ci_ui deployment.
# Usage: bash scripts/smoke_test.sh [BASE_URL]
set -euo pipefail

BASE=${1:-http://localhost:8000}
PASS=0
FAIL=0

check() {
  local desc="$1" url="$2" expect="$3"
  status=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
  if [ "$status" = "$expect" ]; then
    echo "  ✓ $desc ($status)"
    PASS=$((PASS + 1))
  else
    echo "  ✗ $desc (expected $expect, got $status)"
    FAIL=$((FAIL + 1))
  fi
}

echo "=== ci_ui smoke test ==="
echo "Target: $BASE"
echo ""

check "Health endpoint"          "$BASE/api/health"         "200"
check "Runs list"                "$BASE/api/runs"           "200"
check "Lock state"               "$BASE/api/locks"          "200"
check "Input folders"            "$BASE/api/input-folders"  "200"
check "SSE stream (connects)"    "$BASE/api/events"         "200"
check "SPA fallback (index.html)" "$BASE/"                  "200"
check "SPA route (/runs)"        "$BASE/runs"               "200"
check "Unknown API route"        "$BASE/api/nonexistent"    "404"

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] && echo "=== ALL CHECKS PASSED ===" || echo "=== SOME CHECKS FAILED ==="
exit $FAIL
```

### Acceptance criteria

- [ ] `bash scripts/smoke_test.sh` returns exit code 0 when all endpoints are healthy
- [ ] Non-zero exit code when any check fails
- [ ] Checks cover API, SPA fallback, and SSE stream connectivity
- [ ] No dependencies beyond `curl` and `bash`
# Section K — End-to-end verification

This section defines manual verification scenarios that exercise every major code path. These are NOT automated tests — they are structured walkthroughs the operator performs with the running system. Each scenario documents the preconditions, steps, and expected outcomes. Run them with `ADAPTER_PROFILE=mock` first, then with `ADAPTER_PROFILE=real` after partner integration.

Section index:

- [ ] T-K1 — Happy path: new run → pre-approval → approve → submitted
- [ ] T-K2 — Failure path: staged failure → re-run from scratch
- [ ] T-K3 — Failure path: approval failure → retry approve
- [ ] T-K4 — Concurrency UX: lock-held state across screens
- [ ] T-K5 — Mock adapter verification (all three MOCK_FAILURE modes)

---

## T-K1 — Happy path: new run → pre-approval → approve → submitted

**Depends on:** All of Sections A-I
**Estimated effort:** verification only (no code)

### Preconditions

- Server running with `ADAPTER_PROFILE=mock`, `MOCK_LATENCY=realistic`, `MOCK_FAILURE=none`.
- Browser open to `http://localhost:8000/runs` (or `:5173` in dev mode).

### Steps

1. **Runs List loads.**
   - [ ] Page shows "Pipeline Runs" header, search bar, state filter chips.
   - [ ] Three mock runs visible (intuit pre_approval, visa submitted, amex failed).
   - [ ] State badges show correct colors per D-045.
   - [ ] Issues badge shows counts for runs with validation/warning events.

2. **Start a new run.**
   - [ ] Click "New Run" button.
   - [ ] Modal shows input folders from `GET /api/input-folders`.
   - [ ] Select a folder and click "Start Run".
   - [ ] Toast: "Staged run started for {merchant}."
   - [ ] Modal closes. Runs List refreshes.
   - [ ] New run appears at top with state "In Progress" (cyan badge).

3. **Navigate to the new run.**
   - [ ] Click the new run row → navigates to `/runs/{run_id}`.
   - [ ] RunHeader shows merchant, run_id (mono), state "In Progress".
   - [ ] Action buttons are all disabled (lock held).
   - [ ] Tooltip on buttons: "An active operation is in progress".

4. **Activity tab updates in real time.**
   - [ ] Events appear one-by-one (~2.5s apart with realistic latency).
   - [ ] Timeline shows: run_started → stage_started → stage_progress(30%) → stage_progress(60%) → stage_completed → stage_started → validation_failure → warning → comparison_ready → stage_completed → pre_approval_reached.
   - [ ] Each event has correct color dot, label, and detail text.
   - [ ] SSE keeps the timeline updating without manual refresh.

5. **State transitions to pre-approval.**
   - [ ] After `pre_approval_reached`, state badge changes to "Pre-Approval" (amber).
   - [ ] "Approve" and "Re-run from Scratch" buttons become enabled.
   - [ ] Lock indicator disappears (operation complete).

6. **Verify Results tab.**
   - [ ] Switch to Results tab.
   - [ ] Base table shows 8 rows from mock fixtures.
   - [ ] Columns render: Match Tag (mono), MAID (mono), Mnemonic, Action (colored pill), etc.
   - [ ] Click a row → drawer slides in from right.
   - [ ] Drawer shows Field Deltas (3-column grid), ETL Impact (entry pills), Mod File Entry (JSON).
   - [ ] Changed fields highlighted in amber.
   - [ ] Close drawer → drawer slides out.

7. **Verify Issues tab.**
   - [ ] Switch to Issues tab.
   - [ ] Shows 2 issues (1 validation_failure, 1 warning) from mock events.
   - [ ] Issues sorted by severity (validation_failure first).
   - [ ] Issue cards have severity-colored left border.
   - [ ] Badge on Issues tab shows "2".

8. **Approve the run.**
   - [ ] Switch back to Activity tab.
   - [ ] Click "Approve".
   - [ ] Toast: "Approval started."
   - [ ] Buttons disable again (lock held).
   - [ ] Activity timeline shows: approval_submitted → stage_started(jira) → jira_created → stage_started(sharepoint) → sharepoint_synced → submission_complete.
   - [ ] State badge changes to "Submitted" (green).

9. **Verify Jira info.**
   - [ ] JiraInfoPanel appears in Activity tab for submitted run.
   - [ ] Epic and Story keys are clickable links.
   - [ ] URLs use `JPMC_JIRA_BASE_URL` (e.g., `https://jira.jpmchase.net/browse/CMRPEE-142`).
   - [ ] SharePoint path shown.

10. **Verify Artifact Preview (if PDF available).**
    - [ ] Navigate to `/runs/{run_id}/artifact`.
    - [ ] Split pane renders (PDF left, data right).
    - [ ] In mock mode, PDF pane shows "No PDF available" (expected — no real PDF).
    - [ ] Data pane renders the same base table + drawer as Results tab.
    - [ ] Divider is draggable between 20% and 80%.

11. **Return to Runs List.**
    - [ ] Click "← Back to Run Detail" then navigate to Runs List.
    - [ ] The new run now shows state "Submitted" with green badge.
    - [ ] Submitted run's action buttons are empty (no actions available).

### Pass criteria

All checkboxes above are checked. No console errors in DevTools. No unhandled exceptions.

---

## T-K2 — Failure path: staged failure → re-run from scratch

**Depends on:** All of Sections A-I
**Estimated effort:** verification only (no code)

### Preconditions

- Server running with `ADAPTER_PROFILE=mock`, `MOCK_LATENCY=realistic`, `MOCK_FAILURE=staged`.

### Steps

1. **Start a new run.**
   - [ ] Click "New Run", select folder, click "Start Run".
   - [ ] Toast confirms start.

2. **Watch the staged failure.**
   - [ ] Navigate to the new run's detail page.
   - [ ] Activity timeline shows: run_started → stage_started(extraction) → stage_progress(30%) → run_failed.
   - [ ] State badge changes to "Failed" (red).
   - [ ] FailurePanel appears: "Mock failure: pipeline crashed during extraction."
   - [ ] Stage shows "staged", retry_strategy shows "rerun_only".

3. **Verify available actions.**
   - [ ] Only "Re-run from Scratch" button is available (NOT "Retry Approve").
   - [ ] This matches D-046: staged failures can only rerun, not retry.

4. **Re-run from scratch.**
   - [ ] Click "Re-run from Scratch".
   - [ ] Toast: "Re-run started as {new_run_id} (original: {old_run_id})."
   - [ ] New run appears in Runs List with a new run_id and timestamp.
   - [ ] Original failed run remains in the list (not deleted).

5. **Return to Runs List.**
   - [ ] Both the failed run (red) and the new run (in progress or pre_approval) are visible.

### Pass criteria

Staged failure produces the correct state, action, and re-run behavior. No "Retry Approve" button appears for staged failures.

---

## T-K3 — Failure path: approval failure → retry approve

**Depends on:** All of Sections A-I
**Estimated effort:** verification only (no code)

### Preconditions

- Server running with `ADAPTER_PROFILE=mock`, `MOCK_FAILURE=none` initially.
- Complete a staged run to pre-approval (per T-K1 steps 1-5).
- Then change `MOCK_FAILURE=approval` in `.env` and restart the server.
  - *Alternatively:* use the amex failed run from the mock fixtures if its failure stage is set to "approval".

### Steps

1. **Approve the pre-approval run.**
   - [ ] Click "Approve" on the pre-approval run.
   - [ ] Activity shows: approval_submitted → stage_started(jira) → run_failed.
   - [ ] State badge: "Failed" (red).
   - [ ] FailurePanel: "Mock failure: Jira API timeout." Stage: "approval".

2. **Verify retry action is available.**
   - [ ] "Retry Approve" button IS available (amber).
   - [ ] "Re-run from Scratch" is ALSO available.
   - [ ] This matches D-046: approval failures offer both retry and rerun.

3. **Retry approval.**
   - [ ] Change `MOCK_FAILURE=none` and restart. (Or keep as-is if testing the failure retry loop.)
   - [ ] Click "Retry Approve".
   - [ ] Toast: "Retry approval started."
   - [ ] If MOCK_FAILURE=none now, approval succeeds → state becomes Submitted.
   - [ ] If MOCK_FAILURE=approval still, it fails again → same Failed state.

### Pass criteria

Approval failure shows "Retry Approve" (not just "Re-run"). Retry removes failure.json and re-attempts approval.

---

## T-K4 — Concurrency UX: lock-held state across screens

**Depends on:** All of Sections A-I
**Estimated effort:** verification only (no code)

### Preconditions

- Server running with `ADAPTER_PROFILE=mock`, `MOCK_LATENCY=realistic`, `MOCK_FAILURE=none`.
- A run is in progress (just started, pipeline events still streaming).

### Steps

1. **Verify Runs List lock indicator.**
   - [ ] While a run is in progress, navigate to `/runs`.
   - [ ] "New Run" button is disabled with single-lock tooltip.
   - [ ] The in-progress run shows "In Progress" state badge.

2. **Navigate to a DIFFERENT run while lock is held.**
   - [ ] Click on the intuit pre_approval run (not the in-progress one).
   - [ ] RunHeader shows the pre_approval state correctly.
   - [ ] Action buttons (Approve, Re-run) are DISABLED because lock is held by another run.
   - [ ] Tooltip: "An active operation is in progress".

3. **Wait for lock release.**
   - [ ] After the in-progress run completes (~25s with realistic latency), buttons re-enable.
   - [ ] `useLockState` poll (5s interval) detects the lock release.
   - [ ] The pre_approval run's "Approve" button becomes clickable.

4. **SmartFallback behavior.**
   - [ ] While a run is in progress, navigate to `/` (root).
   - [ ] SmartFallback should redirect to `/runs/{in_progress_run_id}`.
   - [ ] After completion, navigating to `/` redirects to `/runs` (list).

### Pass criteria

Lock-held state disables all action buttons across ALL runs, not just the active run. SmartFallback redirects to the active run during in-progress state. Buttons re-enable automatically after lock release via polling.

---

## T-K5 — Mock adapter verification (all three MOCK_FAILURE modes)

**Depends on:** T-D5
**Estimated effort:** verification only (no code)

### Preconditions

- Server running with `ADAPTER_PROFILE=mock`.

### Steps

1. **MOCK_FAILURE=none verification.**
   - Set `.env`: `MOCK_FAILURE=none`, `MOCK_LATENCY=instant`.
   - Restart server.
   - Start a new run.
   - [ ] Events appear rapidly (~50ms apart).
   - [ ] Full event sequence completes: run_started through pre_approval_reached (11 events).
   - [ ] `sqlite3 ci_ui.db "SELECT type FROM events WHERE run_id='<id>' ORDER BY id"` shows all 11 types.
   - [ ] Approve the run.
   - [ ] Approval sequence completes: approval_submitted through submission_complete (6 events).

2. **MOCK_FAILURE=staged verification.**
   - Set `.env`: `MOCK_FAILURE=staged`, `MOCK_LATENCY=instant`.
   - Restart server.
   - Start a new run.
   - [ ] Event sequence stops after stage_progress(30%) with run_failed.
   - [ ] `sqlite3 ci_ui.db "SELECT COUNT(*) FROM events WHERE run_id='<id>'"` = 4 (run_started, stage_started, stage_progress, run_failed).
   - [ ] `cat <output_folder>/failure.json` shows `stage: "staged"`, `retry_strategy: "rerun_only"`.

3. **MOCK_FAILURE=approval verification.**
   - Set `.env`: `MOCK_FAILURE=none` first. Start and complete a staged run to pre_approval.
   - Change `.env`: `MOCK_FAILURE=approval`. Restart.
   - Approve the pre_approval run.
   - [ ] Approval sequence stops after stage_started(jira) with run_failed.
   - [ ] `failure.json` shows `stage: "approval"`, `retry_strategy: "retry_or_rerun"`.

4. **Lock cleanup verification.**
   - [ ] After each scenario, `sqlite3 ci_ui.db "SELECT * FROM locks"` shows `held=0`.
   - [ ] No orphaned locks remain.

5. **Audit log verification.**
   - [ ] `sqlite3 ci_ui.db "SELECT action_type, run_id FROM audit_log ORDER BY id DESC LIMIT 10"` shows the expected action history.

### Pass criteria

All three MOCK_FAILURE modes produce the expected event sequences, failure.json contents, and state transitions. Lock is always released after each operation. Audit log captures all operator actions.
