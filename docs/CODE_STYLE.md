# Code Style & Conventions

## 1. General Principles
- Prefer readable code over clever one-liners.
- Keep functions focused and deterministic.
- Avoid unnecessary abstractions, premature indirection, or deep inheritance hierarchies.
- Reuse existing components and utilities across both frontend and backend.
- Prefer consistency over novelty; follow existing idioms established in the codebase.
- Maintain strict typing in both TypeScript and Python (Pydantic / Type Hints).

## 2. Naming
Components: `PascalCase` (e.g., `RuleBuilderModal.tsx`, `DuplicateFinderView.tsx`, `Header.tsx`)
Functions:
- TypeScript: `camelCase` (e.g., `fetchData`, `handleToggleRule`, `openFolderPicker`)
- Python: `snake_case` (e.g., `evaluate_conditions`, `find_duplicates`, `get_file_metadata`)
Variables:
- TypeScript: `camelCase` (e.g., `activeTab`, `isScanning`, `editingRule`)
- Python: `snake_case` (e.g., `source_path`, `match_mode`, `candidate_groups`)
Constants:
- TypeScript: `UPPER_SNAKE_CASE` for global constants (e.g., `API_BASE_URL`, `DEFAULT_DEBOUNCE_MS`)
- Python: `UPPER_SNAKE_CASE` (e.g., `BIF_RETURNONLYFSDIRS`, `CHUNK_SIZE_64KB`)
Files:
- TypeScript components: `PascalCase.tsx`
- TypeScript utilities/types: `camelCase.ts` (e.g., `filePicker.ts`, `index.ts`)
- Python modules: `snake_case.py` (e.g., `duplicate_finder.py`, `models.py`)
Database fields: `snake_case` (e.g., `rule_id`, `source_path`, `created_at`)
API routes: `kebab-case` or lowercase nouns with resource naming (e.g., `/api/rules`, `/api/test-rule`, `/api/duplicates/scan`, `/api/system/browse-folder`)

## 3. Folder Structure
- Backend code belongs under `fileflow/backend/src/` organized by domain responsibility:
  - `actions/`: File operations and collision resolution dispatchers.
  - `api/`: FastAPI route controllers, request/response models, and security middleware.
  - `core/`: State management, database client, directory watcher, and duplicate search engine.
  - `extractors/`: Modular file format metadata and content parsers.
- Frontend code belongs under `fileflow/frontend/src/` organized by architectural role:
  - `components/`: View containers and interactive UI modals.
  - `types/`: Shared TypeScript data models and interfaces.
  - `utils/`: Reusable helper functions and Win32 interop wrappers.
- Test suites must mirror module structure under `fileflow/backend/tests/`.

## 4. Imports
- Group imports logically in both Python and TypeScript:
  1. Standard library / Framework imports (`react`, `os`, `sys`, `typing`)
  2. Third-party dependencies (`fastapi`, `lucide-react`, `pydantic`)
  3. Internal application modules (`..core.models`, `./types`)
- Avoid wildcard imports (e.g., never use `from module import *`).
- Keep imports explicit and sort alphabetically where possible.

## 5. Components
Components should:
- Have a single, well-defined responsibility.
- Prefer composable, reusable UI patterns (e.g., standard button chips, modal containers).
- Extract complex form logic or sub-views into dedicated subcomponents.
- Use explicit TypeScript interfaces for props (avoid `any`).
- Avoid unnecessary duplication of styling or DOM elements.

## 6. Functions
Functions should:
- Do one logical thing and do it reliably.
- Have clear, self-explanatory names describing action and intent.
- Avoid unnecessary complexity and deep nested branching (prefer early returns / guard clauses).
- Include comprehensive type annotations on all inputs and return values.

## 7. Error Handling
Use:
- Python: Explicit `try ... except SpecificException:` blocks with descriptive error logs and appropriate HTTP status codes via `HTTPException`.
- TypeScript: Structured `try ... catch` with user-friendly error banners or fallback UI states.
- Clean resource cleanup using context managers (`with` statements in Python).
Do not:
- Use bare `except:` in Python without logging or re-raising.
- Silently swallow exceptions or ignore promise rejections.
- Expose raw internal Python stack traces directly to end users in the frontend UI.

## 8. Comments
Comments should explain:
- **Why** a non-obvious piece of logic exists (e.g., explaining a Win32 `ctypes` flag or a debounce delay).
- Important trade-offs made in algorithms (e.g., why Head+Tail hashing is performed before full SHA-256).
- Edge-case handling for Windows filesystem behavior (e.g., locked file handles during Chrome downloads).
Avoid comments that simply repeat what the code already says.

## 9. Logging
Use:
- Python standard `logging` module or structured SQLite entries via `Database.log_action()`.
Rules:
- Log at appropriate severity levels (`DEBUG` for granular extraction, `INFO` for rule matches, `WARNING` for collisions, `ERROR` for operation failures).
- Sanitize logged file paths to protect sensitive personal directories where required.
- Never log raw document body contents or secrets.

## 10. Formatting
Formatter: Prettier (Frontend), Black / Ruff (Python)
Linter: ESLint with `@typescript-eslint` (Frontend), Flake8 / Ruff (Python)
Type Checking: `tsc --noEmit` (TypeScript 5.x), `mypy` or Pydantic validation (Python 3.11+)

## 11. Do
- Reuse existing patterns and components.
- Keep changes focused and atomic.
- Follow existing project conventions and directory organization.
- Remove dead code, unused imports, and commented-out snippets.
- Verify both Light and Dark mode appearance when altering UI styles.
- Write unit tests for new condition operators or extraction logic.

## 12. Don't
- Create duplicate utility functions.
- Introduce heavy or unnecessary external dependencies (e.g., avoid pulling in lodash or bulky UI libraries when native JS/Tailwind suffices).
- Ignore existing architectural boundaries (e.g., do not call filesystem APIs directly from frontend).
- Modify unrelated files or reformat arbitrary code during targeted bug fixes.
