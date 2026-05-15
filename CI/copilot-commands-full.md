# Copilot Commands — Per Task with Auto Commit

85 commands. Copy each one into Copilot Chat. Each command:
1. Sets the repo context (CI_Main/ci_ui/)
2. Points to the exact task in tasks.md
3. Auto-commits on completion

Work top-to-bottom. If a task fails, `git diff` to see what changed,
fix manually, then commit and continue.

---

## Section A — Setup & foundation

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section A, implement task T0 — Monorepo scaffold. Create every file with the exact content specified. When done, run: git add -A && git commit -m "T0: monorepo scaffold"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section A, implement task T1 — FastAPI backend scaffold. Create every file under ci_ui/api/ with the exact content specified. When done, run: git add -A && git commit -m "T1: FastAPI backend scaffold"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section A, implement task T2 — React + Vite + TypeScript scaffold. Create every file under ci_ui/web/ with the exact content specified. When done, run: git add -A && git commit -m "T2: React+Vite+TS scaffold"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section A, implement task T3 — Feature directories + ESLint boundaries. Create every file with the exact content specified. When done, run: git add -A && git commit -m "T3: feature directories + ESLint boundaries"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section A, implement task T4 — Pydantic Settings schema. Create ci_ui/api/config.py with the exact content specified. When done, run: git add -A && git commit -m "T4: pydantic settings schema"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section A, implement task T5 — .env.example files. Create every file with the exact content specified. When done, run: git add -A && git commit -m "T5: .env.example files"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section A, implement task T6 — Font vendoring. Create placeholder files under ci_ui/web/public/fonts/ with the exact content specified. When done, run: git add -A && git commit -m "T6: font vendoring"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section A, implement task T7 — CSS variable tokens. Create every file under ci_ui/web/src/styles/ with the exact content specified. When done, run: git add -A && git commit -m "T7: CSS variable tokens"
```

## Section B — Database & migrations

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section B, implement task T-B1 — Initial SQL migration. Create ci_ui/api/db/migrations/001_initial.sql with the exact content specified. When done, run: git add -A && git commit -m "T-B1: initial SQL migration"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section B, implement task T-B2 — connection.py + migrate.py + lifespan hook. Create every file under ci_ui/api/db/ with the exact content specified. When done, run: git add -A && git commit -m "T-B2: connection + migrate + lifespan"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section B, implement task T-B3 — audit.py. Create ci_ui/api/db/audit.py with the exact content specified. When done, run: git add -A && git commit -m "T-B3: audit module"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section B, implement task T-B4 — maid_index.py. Create ci_ui/api/db/maid_index.py with the exact content specified. When done, run: git add -A && git commit -m "T-B4: MAID index module"
```

## Section C — State derivation & lifecycle

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section C, implement task T-C1 — infer_state + RunState enum. Create every file under ci_ui/api/state/ with the exact content specified. When done, run: git add -A && git commit -m "T-C1: infer_state + RunState enum"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section C, implement task T-C2 — Lock helpers. Create ci_ui/api/state/locks.py with the exact content specified. When done, run: git add -A && git commit -m "T-C2: lock helpers"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section C, implement task T-C3 — failure.json writer. Create ci_ui/api/state/failure.py with the exact content specified. When done, run: git add -A && git commit -m "T-C3: failure.json writer"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section C, implement task T-C4 — Event ingestion. Create ci_ui/api/state/events.py with the exact content specified. When done, run: git add -A && git commit -m "T-C4: event ingestion"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section C, implement task T-C5 — SSE broadcaster. Create ci_ui/api/state/sse.py with the exact content specified. When done, run: git add -A && git commit -m "T-C5: SSE broadcaster"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section C, implement task T-C6 — Stale-lock reaper. Create ci_ui/api/state/reaper.py with the exact content specified. When done, run: git add -A && git commit -m "T-C6: stale-lock reaper"
```

## Section D — Adapter layer

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section D, implement task T-D1 — Adapter interfaces + shared data models. Create ci_ui/api/adapters/interfaces.py and ci_ui/api/adapters/models.py with the exact content specified. When done, run: git add -A && git commit -m "T-D1: adapter interfaces + data models"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section D, implement task T-D2 — LocalStorageClient. Create ci_ui/api/adapters/local_storage.py with the exact content specified. When done, run: git add -A && git commit -m "T-D2: LocalStorageClient"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section D, implement task T-D3 — MockStorageClient + fixture files. Create ci_ui/api/adapters/mock_storage.py and all JSON files under ci_ui/api/adapters/fixtures/ with the exact content specified. When done, run: git add -A && git commit -m "T-D3: MockStorageClient + fixtures"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section D, implement task T-D4 — SubprocessPipelineRunner. Create ci_ui/api/adapters/subprocess_runner.py with the exact content specified. When done, run: git add -A && git commit -m "T-D4: SubprocessPipelineRunner"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section D, implement task T-D5 — MockPipelineRunner. Create ci_ui/api/adapters/mock_runner.py with the exact content specified. When done, run: git add -A && git commit -m "T-D5: MockPipelineRunner"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section D, implement task T-D6 — Adapter factory + FastAPI dependency wiring. Create ci_ui/api/adapters/factory.py and update ci_ui/api/dependencies.py with the exact content specified. When done, run: git add -A && git commit -m "T-D6: adapter factory + dependency wiring"
```

## Section E — FastAPI endpoints

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section E, implement task T-E1 — Error envelope middleware. Create ci_ui/api/middleware/__init__.py and ci_ui/api/middleware/error_envelope.py, and update ci_ui/api/main.py with the exact content specified. When done, run: git add -A && git commit -m "T-E1: error envelope middleware"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section E, implement task T-E2 — Response models + shared schemas. Create ci_ui/api/routers/schemas.py with the exact content specified. When done, run: git add -A && git commit -m "T-E2: response schemas"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section E, implement task T-E3 — POST /api/runs/start. Add the endpoint to ci_ui/api/routers/runs.py with the exact content specified. Do not overwrite existing content in runs.py. When done, run: git add -A && git commit -m "T-E3: POST /api/runs/start"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section E, implement task T-E4 — POST /api/runs/{run_id}/approve. Add the endpoint to ci_ui/api/routers/runs.py. Do not overwrite existing content. When done, run: git add -A && git commit -m "T-E4: POST /api/runs/{run_id}/approve"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section E, implement task T-E5 — POST /api/runs/{run_id}/retry-approve. Add the endpoint to ci_ui/api/routers/runs.py. Do not overwrite existing content. When done, run: git add -A && git commit -m "T-E5: POST /api/runs/{run_id}/retry-approve"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section E, implement task T-E6 — POST /api/runs/{run_id}/rerun. Add the endpoint to ci_ui/api/routers/runs.py. Do not overwrite existing content. When done, run: git add -A && git commit -m "T-E6: POST /api/runs/{run_id}/rerun"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section E, implement task T-E7 — GET /api/runs. Add the endpoint to ci_ui/api/routers/runs.py. Do not overwrite existing content. When done, run: git add -A && git commit -m "T-E7: GET /api/runs"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section E, implement task T-E8 — GET /api/runs/{run_id}. Add the endpoint to ci_ui/api/routers/runs.py. Do not overwrite existing content. When done, run: git add -A && git commit -m "T-E8: GET /api/runs/{run_id}"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section E, implement task T-E9 — GET /api/runs/{run_id}/base-table. Add the endpoint to ci_ui/api/routers/runs.py. Do not overwrite existing content. When done, run: git add -A && git commit -m "T-E9: GET /api/runs/{run_id}/base-table"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section E, implement task T-E10 — GET /api/runs/{run_id}/drawer/{match_tag}. Add the endpoint to ci_ui/api/routers/runs.py. Do not overwrite existing content. When done, run: git add -A && git commit -m "T-E10: GET /api/runs/{run_id}/drawer/{match_tag}"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section E, implement task T-E11 — GET /api/runs/{run_id}/raw-extract/{match_tag}. Add the endpoint to ci_ui/api/routers/runs.py. Do not overwrite existing content. When done, run: git add -A && git commit -m "T-E11: GET /api/runs/{run_id}/raw-extract/{match_tag}"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section E, implement task T-E12 — GET /api/runs/{run_id}/issues. Add the endpoint to ci_ui/api/routers/runs.py. Do not overwrite existing content. When done, run: git add -A && git commit -m "T-E12: GET /api/runs/{run_id}/issues"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section E, implement task T-E13 — GET /api/runs/{run_id}/events. Add the endpoint to ci_ui/api/routers/runs.py. Do not overwrite existing content. When done, run: git add -A && git commit -m "T-E13: GET /api/runs/{run_id}/events"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section E, implement task T-E14 — GET /api/runs/{run_id}/pdf. Add the endpoint to ci_ui/api/routers/runs.py. Do not overwrite existing content. When done, run: git add -A && git commit -m "T-E14: GET /api/runs/{run_id}/pdf"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section E, implement task T-E15 — GET /api/runs/{run_id}/jira-info. Add the endpoint to ci_ui/api/routers/runs.py. Do not overwrite existing content. When done, run: git add -A && git commit -m "T-E15: GET /api/runs/{run_id}/jira-info"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section E, implement task T-E16 — GET /api/input-folders. Add the endpoint to ci_ui/api/routers/system.py with the exact content specified. When done, run: git add -A && git commit -m "T-E16: GET /api/input-folders"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section E, implement task T-E17 — GET /api/locks. Add the endpoint to ci_ui/api/routers/system.py. Do not overwrite existing content. When done, run: git add -A && git commit -m "T-E17: GET /api/locks"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section E, implement task T-E18 — GET /api/events SSE stream. Add the endpoint to ci_ui/api/routers/system.py. Do not overwrite existing content. When done, run: git add -A && git commit -m "T-E18: GET /api/events SSE stream"
```

## Section F — Frontend infrastructure & shared components

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section F, implement task T-F1 — API client. Create ci_ui/web/src/features/shared/api/client.ts with the exact content specified. When done, run: git add -A && git commit -m "T-F1: API client"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section F, implement task T-F2 — React Query hooks + query key factory. Create ci_ui/web/src/features/shared/api/queryKeys.ts and ci_ui/web/src/features/shared/api/hooks.ts with the exact content specified. When done, run: git add -A && git commit -m "T-F2: React Query hooks + query keys"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section F, implement task T-F3 — SSE client + React Query invalidation mapping. Create ci_ui/web/src/features/shared/sse/client.ts and ci_ui/web/src/features/shared/sse/useSSE.ts with the exact content specified. When done, run: git add -A && git commit -m "T-F3: SSE client + invalidation mapping"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section F, implement task T-F4 — Zustand UI state store. Create ci_ui/web/src/features/shared/stores/uiStore.ts with the exact content specified. When done, run: git add -A && git commit -m "T-F4: Zustand UI store"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section F, implement task T-F5 — Frontend error catalog + Error Boundary. Update ci_ui/web/src/features/shared/errors/messages.ts and create ci_ui/web/src/features/shared/errors/ErrorBoundary.tsx with the exact content specified. When done, run: git add -A && git commit -m "T-F5: error catalog + ErrorBoundary"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section F, implement task T-F6 — AppShell. Create ci_ui/web/src/features/shared/components/AppShell.tsx and AppShell.css, and update ci_ui/web/src/App.tsx with the exact content specified. When done, run: git add -A && git commit -m "T-F6: AppShell layout"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section F, implement task T-F7 — SmartFallback route resolver. Create ci_ui/web/src/features/shared/components/SmartFallback.tsx and update App.tsx with the exact content specified. When done, run: git add -A && git commit -m "T-F7: SmartFallback"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section F, implement task T-F8 — BaseTableWithDrawer. Create ci_ui/web/src/features/shared/components/BaseTableWithDrawer.tsx and BaseTableWithDrawer.css with the exact content specified. When done, run: git add -A && git commit -m "T-F8: BaseTableWithDrawer"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section F, implement task T-F9 — Shared primitives (StateBadge, ActionPill, EntryPill, TabBar). Create all four files under ci_ui/web/src/features/shared/components/ with the exact content specified. When done, run: git add -A && git commit -m "T-F9: shared primitives"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section F, implement task T-F10 — Toast notification system. Create ci_ui/web/src/features/shared/stores/toastStore.ts and ci_ui/web/src/features/shared/components/Toast.tsx with the exact content specified. Add ToastContainer to AppShell. When done, run: git add -A && git commit -m "T-F10: toast notification system"
```

## Section G — Runs List screen

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section G, implement task T-G1 — RunsListScreen container. Create ci_ui/web/src/features/runs/screens/RunsListScreen.tsx with the exact content specified. When done, run: git add -A && git commit -m "T-G1: RunsListScreen container"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section G, implement task T-G2 — SearchBar. Create ci_ui/web/src/features/runs/components/SearchBar.tsx with the exact content specified. When done, run: git add -A && git commit -m "T-G2: SearchBar"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section G, implement task T-G3 — StateFilterChips. Create ci_ui/web/src/features/runs/components/StateFilterChips.tsx with the exact content specified. When done, run: git add -A && git commit -m "T-G3: StateFilterChips"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section G, implement task T-G4 — RunsTable. Create ci_ui/web/src/features/runs/components/RunsTable.tsx with the exact content specified. When done, run: git add -A && git commit -m "T-G4: RunsTable"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section G, implement task T-G5 — Pagination. Create ci_ui/web/src/features/runs/components/Pagination.tsx with the exact content specified. When done, run: git add -A && git commit -m "T-G5: Pagination"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section G, implement task T-G6 — NewRunDialog. Create ci_ui/web/src/features/runs/components/NewRunDialog.tsx with the exact content specified. When done, run: git add -A && git commit -m "T-G6: NewRunDialog"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section G, implement task T-G7 — Loading, empty, and error states. Update RunsListScreen.tsx to add the first-run empty state with the exact content specified. When done, run: git add -A && git commit -m "T-G7: loading/empty/error states"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section G, implement task T-G8 — Route wiring in App.tsx. Update ci_ui/web/src/App.tsx and create ci_ui/web/src/features/runs/index.ts with the exact content specified. When done, run: git add -A && git commit -m "T-G8: runs list route wiring"
```

## Section H — Run Detail screen

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section H, implement task T-H1 — RunDetailScreen container. Create ci_ui/web/src/features/runs/screens/RunDetailScreen.tsx with the exact content specified. When done, run: git add -A && git commit -m "T-H1: RunDetailScreen container"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section H, implement task T-H2 — RunHeader. Create ci_ui/web/src/features/runs/components/RunHeader.tsx with the exact content specified. When done, run: git add -A && git commit -m "T-H2: RunHeader"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section H, implement task T-H3 — ActionButtonBar. Create ci_ui/web/src/features/runs/components/ActionButtonBar.tsx with the exact content specified. When done, run: git add -A && git commit -m "T-H3: ActionButtonBar"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section H, implement task T-H4 — Tab integration verification. Verify TabBar renders in RunDetailScreen per the exact content specified. When done, run: git add -A && git commit -m "T-H4: tab integration verified"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section H, implement task T-H5 — ActivityTab container. Create ci_ui/web/src/features/runs/components/ActivityTab.tsx with the exact content specified. When done, run: git add -A && git commit -m "T-H5: ActivityTab"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section H, implement task T-H6 — ActivityTimeline. Create ci_ui/web/src/features/runs/components/ActivityTimeline.tsx with the exact content specified. When done, run: git add -A && git commit -m "T-H6: ActivityTimeline"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section H, implement task T-H7 — StageProgressBar. Create ci_ui/web/src/features/runs/components/StageProgressBar.tsx with the exact content specified. When done, run: git add -A && git commit -m "T-H7: StageProgressBar"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section H, implement task T-H8 — ResultsTab container. Create ci_ui/web/src/features/runs/components/ResultsTab.tsx with the exact content specified. When done, run: git add -A && git commit -m "T-H8: ResultsTab"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section H, implement task T-H9 — Results column definitions. Create ci_ui/web/src/features/runs/components/resultsColumns.tsx with the exact content specified. When done, run: git add -A && git commit -m "T-H9: results column definitions"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section H, implement task T-H10 — DrawerContent shell. Create ci_ui/web/src/features/runs/components/DrawerContent.tsx with the exact content specified. When done, run: git add -A && git commit -m "T-H10: DrawerContent shell"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section H, implement task T-H11 — FieldDeltasPanel. Create ci_ui/web/src/features/runs/components/FieldDeltasPanel.tsx with the exact content specified. When done, run: git add -A && git commit -m "T-H11: FieldDeltasPanel"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section H, implement task T-H12 — ETLImpactPanel. Create ci_ui/web/src/features/runs/components/ETLImpactPanel.tsx with the exact content specified. When done, run: git add -A && git commit -m "T-H12: ETLImpactPanel"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section H, implement task T-H13 — ModFilePanel. Create ci_ui/web/src/features/runs/components/ModFilePanel.tsx with the exact content specified. When done, run: git add -A && git commit -m "T-H13: ModFilePanel"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section H, implement task T-H14 — IssuesTab container. Create ci_ui/web/src/features/runs/components/IssuesTab.tsx with the exact content specified. When done, run: git add -A && git commit -m "T-H14: IssuesTab"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section H, implement task T-H15 — IssueCard. Create ci_ui/web/src/features/runs/components/IssueCard.tsx with the exact content specified. When done, run: git add -A && git commit -m "T-H15: IssueCard"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section H, implement task T-H16 — JiraInfoPanel. Create ci_ui/web/src/features/runs/components/JiraInfoPanel.tsx with the exact content specified. When done, run: git add -A && git commit -m "T-H16: JiraInfoPanel"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section H, implement task T-H17 — FailurePanel. Create ci_ui/web/src/features/runs/components/FailurePanel.tsx with the exact content specified. When done, run: git add -A && git commit -m "T-H17: FailurePanel"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section H, implement task T-H18 — Route wiring in App.tsx. Update ci_ui/web/src/App.tsx and ci_ui/web/src/features/runs/index.ts with the exact content specified. When done, run: git add -A && git commit -m "T-H18: run detail route wiring"
```

## Section I — Artifact Preview screen

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section I, implement task T-I1 — ArtifactPreviewScreen container. Create ci_ui/web/src/features/artifact/screens/ArtifactPreviewScreen.tsx with the exact content specified. When done, run: git add -A && git commit -m "T-I1: ArtifactPreviewScreen container"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section I, implement task T-I2 — PDF viewer pane. Create ci_ui/web/src/features/artifact/components/PdfViewerPane.tsx with the exact content specified. When done, run: git add -A && git commit -m "T-I2: PDF viewer pane"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section I, implement task T-I3 — Artifact data pane. Create ci_ui/web/src/features/artifact/components/ArtifactDataPane.tsx with the exact content specified. When done, run: git add -A && git commit -m "T-I3: artifact data pane"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section I, implement task T-I4 — Draggable divider. Create ci_ui/web/src/features/artifact/components/Divider.tsx with the exact content specified. When done, run: git add -A && git commit -m "T-I4: draggable divider"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section I, implement task T-I5 — Navigation between records. Update ArtifactDataPane.tsx with prev/next navigation per the exact content specified. When done, run: git add -A && git commit -m "T-I5: record navigation"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section I, implement task T-I6 — Route wiring with React.lazy(). Update ci_ui/web/src/App.tsx and create ci_ui/web/src/features/artifact/index.ts with the exact content specified. When done, run: git add -A && git commit -m "T-I6: artifact preview route wiring"
```

## Section J — Production deployment

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section J, implement task T-J1 — Single-uvicorn production config. Update ci_ui/api/main.py with static file mount and create ci_ui/scripts/build.sh with the exact content specified. When done, run: git add -A && git commit -m "T-J1: production static mount + build script"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section J, implement task T-J2 — Production .env template. Create ci_ui/api/.env.production.example with the exact content specified. When done, run: git add -A && git commit -m "T-J2: production .env template"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section J, implement task T-J3 — Startup runbook. Create ci_ui/RUNBOOK.md with the exact content specified. When done, run: git add -A && git commit -m "T-J3: startup runbook"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section J, implement task T-J4 — Health check / smoke test script. Create ci_ui/scripts/smoke_test.sh with the exact content specified. When done, run: git add -A && git commit -m "T-J4: smoke test script"
```

## Section K — Verification

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section K, review task T-K1 — Happy path verification. Summarize the steps I need to verify manually and flag any missing code. When done, run: git add -A && git commit -m "T-K1: happy path verification reviewed"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section K, review task T-K2 — Staged failure path. Summarize the steps I need to verify manually. When done, run: git add -A && git commit -m "T-K2: staged failure path reviewed"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section K, review task T-K3 — Approval failure path. Summarize the steps I need to verify manually. When done, run: git add -A && git commit -m "T-K3: approval failure path reviewed"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section K, review task T-K4 — Concurrency UX. Summarize the steps I need to verify manually. When done, run: git add -A && git commit -m "T-K4: concurrency UX reviewed"
```

```
You are working in the ci_ui repo at CI_Main/ci_ui/. Read #file:tasks.md, Section K, review task T-K5 — Mock adapter modes. Summarize the steps I need to verify manually. When done, run: git add -A && git commit -m "T-K5: mock adapter verification reviewed"
```
