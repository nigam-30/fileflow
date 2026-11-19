# Security Guidelines

## 1. Authentication
Authentication Provider: FileFlow Local Ephemeral Session Token Provider
Methods:
- Per-Session Local Bearer / API Token: On launch, the backend generates a cryptographically secure 32-byte hex token (`secrets.token_hex(32)`) or reads `FILEFLOW_API_TOKEN` from the process environment.
- Header Enforcement: Every HTTP request from the frontend to the backend `/api/*` endpoints must provide this token via the `X-API-Token` header.
- Desktop Shell Injection: The token is securely passed to the frontend WebView instance or local client window upon process initialization.

## 2. Authorization
Roles: Single Local Operator (Owner of the running desktop process)
Permissions:
### Desktop Operator
- Create, modify, and delete automation rules.
- Add and remove monitored directory paths.
- Execute dry-run simulations and trigger immediate folder scans.
- Run multi-stage duplicate scans and clean selected duplicates to the Recycle Bin.
- View and purge local operational audit logs.
Enforcement:
- Authorization is enforced server-side within the local FastAPI middleware. Requests originating outside localhost (`127.0.0.1` / `::1`) or lacking a valid token are immediately rejected with `403 Forbidden`.

## 3. Secrets
- Never hard-code credentials or tokens in source code or client builds.
- Never commit secrets to the Git repository.
- Never expose private tokens in client bundles, log files, or URL query parameters.
- Use environment variables (`FILEFLOW_API_TOKEN`) or ephemeral runtime generation for local IPC secrets.
- Store local application data strictly in the authenticated user's OS profile (`%APPDATA%\FileFlowData`).

## 4. Environment Variables
Public (Safe to expose / Client build variables):
- `VITE_APP_VERSION`: Current semantic version of FileFlow (e.g. `1.0.3`).
Private (Confidential / Process-only variables):
- `FILEFLOW_API_TOKEN`: Optional override for the local session authentication token.
- `FILEFLOW_PORT`: Port override for the local loopback server (defaults to dynamic free port).
- `FILEFLOW_DB_PATH`: Custom path override for the SQLite persistence database.

## 5. API Security
Input Validation:
- All request payloads are strictly validated using Pydantic v2 schemas.
- Path traversal prevention: Every folder and file path received from the API is normalized with `os.path.abspath(os.path.normpath(...))` and verified to prevent `../` traversal or access to prohibited system roots.
Rate Limiting:
- Loopback desktop calls have light concurrency limiting on expensive operations (e.g., maximum 1 concurrent full duplicate disk scan per session) to prevent CPU/IO thrashing.
CORS (Cross-Origin Resource Sharing):
- Strictly bound to localhost origins (`http://127.0.0.1:*`, `http://localhost:*`).
- Remote origins, external browsers, and public networks are blocked.
Authentication & Authorization:
- Custom middleware intercepts all non-static `/api/*` routes and checks `request.headers.get("X-API-Token") == API_TOKEN`.

## 6. Data Protection
Sensitive Data:
- User documents, invoices, bank statements, photos, and personal spreadsheets being organized.
Encryption:
- FileFlow operates strictly on local disk; OS-level disk encryption (e.g., Windows BitLocker) protects resting files.
- Local SQLite database resides in user-restricted `%APPDATA%` space.
Retention:
- Audit logs are maintained locally for 12 hours by default, with automatic pruning on engine start to minimize disk footprint.
Deletion:
- Destructive file actions prioritize non-destructive relocation to the native **Windows Recycle Bin** via `send2trash`. Hard deletion (`os.remove`) requires explicit confirmation.

## 7. Logging
Never log:
- Full text content of user documents or confidential files.
- Passwords or private API tokens.
- Personal data extracted from PDF or EXIF metadata.
Log:
- File operations (source path, destination path, action type, status).
- Rule execution milestones (rule matched, condition evaluated).
- Errors and exceptions with sanitized path strings.
- Security boundary violations (invalid API tokens, unauthorized network origins).

## 8. Local File Operations & Safety
Allowed Operations:
- Read metadata, PDF text previews, image EXIF tags.
- Move, copy, rename, zip, and send to Recycle Bin.
Maximum Extraction Bounds:
- PDF text extraction capped at the first 5 pages by default to prevent memory exhaustion.
- Head/Tail duplicate hashing restricted to 64 KB buffers per chunk.
Collision Safety:
- Default collision policy `rename_with_counter` prevents overwriting existing files with identical names.

## 9. Security Checklist
- [x] Ephemeral local API token authentication implemented
- [x] Host binding strictly restricted to loopback (`127.0.0.1`)
- [x] Path traversal protections and path normalization in place
- [x] Server-side Pydantic payload validation on all endpoints
- [x] Safe deletion routed to native Windows Recycle Bin (`send2trash`)
- [x] Process loop prevention prevents runaway cascading file events
- [x] Zero external network telemetry, analytics, or third-party cloud leaks
- [x] Automated log pruning avoids unbounded database growth
- [x] Error responses sanitize system internals and avoid leaking secret paths
