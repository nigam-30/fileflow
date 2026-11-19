# AI Coding Agent Instructions

## 1. Project Context
Project: FileFlow (Windows File Automation & Duplicate Cleaner)
Purpose: Automate local folder organization, eliminate duplicate clutter, and execute metadata-driven file workflows with zero cloud dependence.
Primary Users: Windows desktop users, developers, students, and professionals seeking private, offline, high-speed file management.

## 2. Source of Truth
Before significant changes, read relevant documentation inside `/docs`.
Core documentation:
- `PRD.md`: Functional scope, feature priorities, and requirements.
- `DESIGN_SYSTEM.md`: Visual language, Tailwind palette, typography, and component styling.
- `ARCHITECTURE.md`: Process boundaries, loopback REST IPC, and engine subsystems.
- `DATABASE.md`: SQLite tables (`rules`, `monitored_folders`, `processed_files`, `audit_logs`), schemas, and migration rules.
- `SECURITY.md`: Ephemeral API tokens, path traversal guards, and safe deletion protocols.
- `CODE_STYLE.md`: Naming rules, error handling conventions, and formatting guidelines.
- `TESTING.md`: Pytest suites, validation commands, and critical user journeys.
- `UX_FLOWS.md`: Step-by-step user journeys and UI state transitions.
- `API.md`: HTTP REST contracts, payload schemas, and response formats.

Do not contradict these documents without first identifying the conflict.

## 3. General Rules
- Understand existing code before modifying it.
- Reuse existing components, extractors, and utility functions.
- Follow the design system (strict Light/Dark mode compatibility, Lucide icons, 4px spacing grid).
- Follow the architecture (never allow frontend direct disk access; all actions pass through the FastAPI backend).
- Follow database conventions (parameterized SQLite queries, Pydantic JSON serialization).
- Follow security requirements (always route deletions through `send2trash` unless explicit override; enforce `X-API-Token`).
- Follow coding conventions (clean Python type hints, TypeScript strict typing).
- Do not invent business requirements or add features outside scope without confirmation.
- Do not expose secrets or log sensitive document contents.
- Avoid unnecessary dependencies; maintain a lightweight, standalone Windows application.
- Avoid unrelated changes; keep diffs focused and minimal.

## 4. Planning
Before implementing a non-trivial task:
1. Inspect relevant documentation in `/docs`.
2. Inspect relevant code across frontend and backend.
3. Identify affected files.
4. Identify dependencies and breaking changes.
5. Identify database/API changes (ensure schema migrations are backward compatible).
6. Identify tests required to validate changes.
7. Create a concise implementation plan before editing.

## 5. Implementation
- Make focused, atomic changes.
- Reuse established patterns (e.g., standard action dispatchers, extractor interfaces).
- Preserve existing behavior and edge-case protections (e.g., download debouncing, loop prevention).
- Avoid unnecessary rewrites or gratuitous refactoring.
- Keep code clean, readable, and maintainable.

## 6. Validation
After implementation:
1. Run backend unit and integration tests (`pytest fileflow/backend/tests -v`).
2. Run frontend type checking (`npx tsc --noEmit` in `fileflow/frontend`).
3. Run the frontend build (`npm run build` in `fileflow/frontend`).
4. Review changed files against Git status.
5. Check for unintended modifications or residual artifacts.

## 7. Documentation
Update documentation when implementation changes:
- Product behavior (`PRD.md`, `UX_FLOWS.md`)
- Architecture (`ARCHITECTURE.md`)
- Database schema (`DATABASE.md`)
- API contracts (`API.md`)
- Security rules (`SECURITY.md`)
- Coding conventions (`CODE_STYLE.md`)

## 8. Conflict Handling
If requirements conflict:
Do not guess. Identify the conflict and ask for clarification.

## 9. Completion Criteria
A task is complete only when:
- Requirements are satisfied.
- All tests pass without warnings or errors.
- Build succeeds cleanly.
- No unintended files are changed or generated in source trees.
- Security rules and safe deletion policies are respected.
- Documentation is updated when necessary.
