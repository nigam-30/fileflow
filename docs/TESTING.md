# Testing

## 1. Testing Goals
Critical functionality:
- Rule Condition Evaluation: Precision testing for all match operators (`equals`, `contains`, `matches_regex`, `greater_than`, `before`, `after`, etc.) and compound logic (`ALL` vs. `ANY`).
- 4-Stage Duplicate Finder Integrity: Guarantee 100% true duplicate matching with mathematical zero false positives across multi-tiered filters (Size, Head+Tail, SHA-256, Bit-for-bit).
- Safe File Dispatching & Collision Resolution: Verify `move`, `copy`, `rename`, `zip`, and `recycle` actions, ensuring `rename_with_counter` never overwrites files.
- Loop Prevention & Concurrency: Validate that moving or creating files inside watched folders does not trigger runaway recursive event loops.
- Local Security & Path Traversal: Ensure all API endpoints block unauthorized requests, reject directory traversal attempts (`../`), and sanitize inputs.

## 2. Test Types

### Unit Testing
- Test core business logic in isolation using mock filesystem objects:
  - Extractor parsers (PDF text, image EXIF, system attributes).
  - Condition match functions and date arithmetic.
  - Template string formatters (e.g., `{file.created_year}_{file.name}`).
  - Pydantic schema validation for incoming rule definitions.

### Integration Testing
- Test API endpoints and database operations using a test SQLite instance:
  - Rule persistence, updates, and query filters.
  - Monitored folder registration, toggling, and path normalization.
  - Audit log insertions, status queries, and auto-pruning.
  - FastAPI dependency injection and security token validation middleware.

### End-to-End Testing & Critical Journeys
Validate complete automated workflows:
- **Rule Creation & Auto-Scan**: Creating a rule with monitored folders immediately scans and organizes matching files.
- **Real-Time File Ingestion**: Dropping a file into a watched folder triggers the debouncer, evaluates conditions, and dispatches the action.
- **Duplicate Detection & Safe Cleanup**: Scanning a test directory finds byte-identical files, presents them in groups, and sends user-selected files safely to the Windows Recycle Bin.
- **Dry-Run Rule Simulation**: Testing a candidate file against active rules predicts exact transformations without modifying disk state.

## 3. Testing Tools
Unit: `pytest` (v8.0+), Python standard `unittest.mock`
Integration: `pytest`, `httpx` / FastAPI `TestClient`, SQLite in-memory / temporary database fixtures
Frontend Validation: TypeScript compiler (`tsc --noEmit`), Vite build validation
E2E / Functional Verification: Local automated test harnesses and simulated filesystem sandboxes (`tests/test_engine.py`, `tests/test_duplicate_finder.py`)

## 4. Test File Structure
```
fileflow/backend/tests/
├── conftest.py                   # Pytest fixtures, test database setup, and mock directories
├── test_engine.py                # Rule evaluation, condition matching, and action execution tests
├── test_duplicate_finder.py      # 4-stage duplicate detection, hashing, and bit-for-bit verification
├── test_security.py              # API token validation, path traversal prevention, origin checks
├── test_watcher_and_folders.py   # Watchdog directory monitoring, debouncing, and folder toggling
└── test_updater.py               # Update check parsing and version comparison tests
```

## 5. Critical User Flows

### Flow 1: Create Rule and Auto-Organize Existing Downloads
Steps:
1. User clicks "+ New Rule" in the UI.
2. User specifies Rule Name: "Invoices to Documents", selects Origin: `Downloads`.
3. Adds Condition: `file.extension == "pdf"` AND `content.text contains "Invoice"`.
4. Adds Action: Move to `Documents/Invoices/`, Collision: `rename_with_counter`.
5. User saves the rule.
Expected result:
- Rule is saved in SQLite database.
- Directory watcher registers origin path.
- Engine triggers immediate auto-scan on `Downloads`; matching invoice PDFs are moved to `Documents/Invoices/` with incremented names if duplicates exist.
- Each operation produces an entry in `audit_logs` marked as `success`.

### Flow 2: 4-Stage Duplicate Scan & Recycle Bin Deletion
Steps:
1. User opens "Duplicate Finder" tab.
2. Selects folder to scan (e.g., `D:\TestDuplicates`) and clicks "Start Scan".
3. Backend filters candidates through Size $\rightarrow$ Head+Tail $\rightarrow$ SHA-256 $\rightarrow$ Binary Comparison.
4. UI renders candidate duplicate groups with SHA-256 badges and timestamps.
5. User selects extra copies and clicks "Clean to Recycle Bin".
Expected result:
- True duplicates are accurately identified without false positives.
- Selected files are moved to the native Windows Recycle Bin via `send2trash`.
- Original file is retained intact; disk space reclaimed is reported to the user.

### Flow 3: Rule Dry-Run Testing
Steps:
1. User opens "Rule Tester" tab.
2. Selects a local test file using the file browser dialog.
3. Clicks "Simulate Rules".
Expected result:
- Backend runs extractors and tests active rules against the file.
- UI displays a step-by-step trace showing which conditions passed/failed and what actions would execute.
- The file is not moved, renamed, or modified on disk.

## 6. Coverage
Target: $\ge 85\%$ test coverage on backend core engine, security middleware, and duplicate finder modules.
Prioritize:
- Core business logic (`core/engine.py`, `actions/dispatcher.py`)
- Authentication & Path security (`api/server.py`, `test_security.py`)
- Duplicate detection algorithms (`core/duplicate_finder.py`)
- Database transactions and state loop prevention (`core/database.py`)

## 7. Commands
Test:
```powershell
pytest fileflow/backend/tests -v
```
Lint:
```powershell
flake8 fileflow/backend/src
```
Build (Frontend):
```powershell
cd fileflow/frontend; npm run build
```
Type Check (Frontend):
```powershell
cd fileflow/frontend; npx tsc --noEmit
```
Full Application Build (PyInstaller):
```powershell
pyinstaller FileFlow.spec --noconfirm
```

## 8. Definition of Done
- [ ] All unit and integration tests pass (`pytest` exits with code 0).
- [ ] Frontend builds with zero TypeScript compiler errors (`tsc --noEmit`).
- [ ] Frontend Vite bundle completes without missing assets or warnings.
- [ ] Security tests pass (API token enforcement and path traversal guards verified).
- [ ] Critical user flows manually or automatically verified against test directories.
- [ ] No regression or blocking errors in runtime logs.
