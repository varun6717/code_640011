I'm preparing this codebase for a web UI build. I need a comprehensive Markdown summary that a separate engineer (who cannot see the source) can use to design the UI and the UI-to-backend integration.

Produce a SINGLE Markdown file with the following sections, in this exact order. Be exhaustive and precise. Include real code snippets for function signatures and data models. If something is unclear, ambiguous, or would need refactoring to expose to a UI, call it out explicitly in a "⚠ UI Concern" callout.

# 1. System Overview
- 2-3 paragraph plain-English description of what the system does end-to-end
- The high-level workflow (input → stages → output) as a numbered list
- Key domain concepts and terminology a UI designer must understand
- Who the intended users are (personas, if obvious from the code)

# 2. Repository Structure
- Tree view of the directory (depth 3+)
- Table with columns: file path | one-line purpose | role (entry point / core logic / utility / config / test / prompt asset)

# 3. Entry Points & Public API
For EVERY function, class method, or CLI command that a UI layer might trigger:
- Fully-qualified name and file:line location
- Full signature with type hints
- One-paragraph description
- Inputs: each parameter — name, type, description, example value, required/optional
- Outputs: return type, full structure, example return value (as JSON if applicable)
- Side effects: files written, state mutated, external services called
- Execution profile: sync/async, blocking/streaming, typical runtime, can it be cancelled
- Idempotency: safe to retry? produces same output for same input?

# 4. Data Models & Schemas
For every dataclass, Pydantic model, TypedDict, or important dict shape:
- Name and source location
- Full field list (name, type, default, description)
- Where it appears (which functions consume/produce it)
- A complete realistic JSON example

# 5. Workflow / Orchestration
- Step-by-step pipeline as a numbered list
- For each step: trigger, inputs, processing, outputs, persistence
- All decision points, branches, retry loops, validation gates
- A Mermaid sequence diagram of the happy path
- A Mermaid flowchart showing decision branches and retry loops

# 6. LLM and External Calls
- Every LLM invocation: which model, which prompt file/string, sync vs streaming, expected token cost, typical latency
- Every external API or service called (auth method, endpoint, purpose)
- For each: what would need to change or be mocked to run the UI locally without hitting real services

# 7. State, Persistence, and Files
- Every file path read or written, with: purpose, format, lifecycle (temp/permanent), naming convention
- Any database, cache, queue, or in-memory state
- How "runs" / "jobs" / "sessions" are identified, named, and tracked over time
- Anything that would need to become a database row to support a multi-run UI

# 8. Configuration
- Every environment variable, config file, secret, or credential
- Default values and where defaults live
- Anything currently hardcoded that should be configurable from a UI

# 9. Logging, Progress, and Errors
- How progress is currently reported (stdout, log files, callbacks, return values)
- Every exception type raised, with conditions
- What a UI could realistically display as live status during a run
- What information is captured when something fails, and where it's stored

# 10. UI Integration Concerns (most important section)
- Long-running operations that need progress indicators or streaming
- Intermediate artifacts a user would likely want to inspect mid-run
- Anything currently CLI-only or interactive that needs an HTTP wrapper
- Anything that assumes a terminal, local filesystem, or single-user environment
- Functions that are not currently safely callable from a web layer (global state, sys.exit, input(), etc.)
- Suggested HTTP endpoint shape for each user-triggerable operation (method, path, request body, response body, sync vs SSE/websocket)

# 11. Glossary
- Every domain-specific term, acronym, or system-specific name used anywhere in the code, with a one-line definition

End the document with an "Open Questions" section listing anything you couldn't determine from the code alone.