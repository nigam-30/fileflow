# Database

## 1. Database Engine
Database: SQLite 3
Hosting: Embedded Local Storage (File: `%APPDATA%\FileFlowData\fileflow.db`, fallback to local application directory if environment variables are missing)

## 2. Naming Conventions
Tables: `snake_case`, pluralized (e.g., `rules`, `monitored_folders`, `processed_files`, `audit_logs`)
Columns: `snake_case` (e.g., `created_at`, `source_path`, `destination_path`)
Primary Keys: Standard column naming (`id` for UUIDs/integers, or natural unique string keys like `path`, `file_path`)
Foreign Keys: Table singular name followed by `_id` (e.g., `rule_id`)
Timestamps: ISO-8601 strings or SQLite `CURRENT_TIMESTAMP` UTC datetimes

## 3. Tables

### `rules`
Purpose: Stores user-defined automation rules, condition trees, trigger origins, and action sequences.
Columns:
- `id` (TEXT, PRIMARY KEY): Unique UUIDv4 identifier string.
- `name` (TEXT, NOT NULL): Human-readable title for the rule.
- `enabled` (INTEGER, NOT NULL DEFAULT 1): Boolean flag indicating whether the rule is currently active (0 or 1).
- `data` (TEXT, NOT NULL): Full JSON-serialized payload conforming to Pydantic `Rule` schema (conditions, actions, match mode, origin folders).
- `created_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP): Timestamp when rule was created.
- `updated_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP): Timestamp when rule was last modified.

### `monitored_folders`
Purpose: Registers directory paths actively watched by the filesystem monitoring engine.
Columns:
- `path` (TEXT, PRIMARY KEY COLLATE NOCASE): Windows absolute directory path, case-insensitive.
- `recursive` (INTEGER, NOT NULL DEFAULT 0): Whether subdirectories should also be monitored (0 = top-level only, 1 = recursive).
- `enabled` (INTEGER, NOT NULL DEFAULT 1): Boolean flag indicating if active monitoring is enabled for this path.
- `added_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP): Timestamp when folder was registered.

### `processed_files`
Purpose: Tracks recently processed file events to prevent infinite loops, circular moves, and repeated triggers on identical files.
Columns:
- `file_path` (TEXT, PRIMARY KEY): Normalized canonical path of the processed file.
- `file_hash` (TEXT): SHA-256 or partial fingerprint of the file contents.
- `mtime` (REAL): Modification timestamp (`stat().st_mtime`) of the file when processed.
- `last_rule_id` (TEXT): ID of the rule that executed against this file.
- `processed_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP): Timestamp when processing was committed.

### `audit_logs`
Purpose: Maintains an immutable historical log of file automation actions, outcomes, and dry-run tests.
Columns:
- `id` (INTEGER PRIMARY KEY AUTOINCREMENT): Sequential log entry ID.
- `timestamp` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP): Timestamp when action was executed.
- `rule_id` (TEXT): Identifier of the executing rule (or null if manual/system operation).
- `rule_name` (TEXT): Name of the executing rule at the time of execution.
- `source_path` (TEXT NOT NULL): Original path of the processed file.
- `destination_path` (TEXT): Target destination path for move/copy/rename operations.
- `action_type` (TEXT): Name of the action (`move`, `copy`, `rename`, `recycle`, `zip`, etc.).
- `status` (TEXT NOT NULL): Execution outcome (`success`, `skipped`, `failed`, `info`).
- `details` (TEXT): Descriptive message, error trace, or reason for skipping.

## 4. Relationships
- `rules.id` → `audit_logs.rule_id`: Zero-to-many relationship. A rule can produce multiple audit log events. Audit logs persist even if a rule is deleted (records retain `rule_name`).
- `rules.id` → `processed_files.last_rule_id`: Loose reference to correlate loop prevention entries with the triggering rule.
- `monitored_folders.path` → `rules.monitored_folders`: Folders listed in rules correspond to active directories tracked by the directory watcher.

## 5. Constraints
Required:
- `rules.id`, `rules.name`, `rules.data`
- `monitored_folders.path`
- `processed_files.file_path`
- `audit_logs.source_path`, `audit_logs.status`
Unique:
- `rules.id` (PRIMARY KEY)
- `monitored_folders.path` (PRIMARY KEY COLLATE NOCASE)
- `processed_files.file_path` (PRIMARY KEY)
Foreign Keys:
- SQLite foreign key checks are intentionally decoupled with soft references in `audit_logs` so deleting a rule does not erase historical operational logs.

## 6. Indexes
- `rules(enabled)`: Fast filtering of active rules during real-time event processing.
- `audit_logs(timestamp DESC)`: High-performance retrieval for the UI Audit Log viewer.
- `audit_logs(rule_id)`: Fast indexing when filtering activity by specific rules.
- `processed_files(file_path, mtime)`: Rapid lookup to check if a file event was already handled.

## 7. Data Validation
- Pydantic models validate all JSON payloads prior to insertion into `rules.data`.
- Folder paths must be validated as absolute Windows paths (`os.path.isabs`) before saving into `monitored_folders`.
- Invalid JSON in `rules.data` causes validation failures caught at the API boundary, returning HTTP 422.

## 8. Soft Delete
Does the system use soft deletion? Yes for rules (via `enabled = 0` toggle); No for hard rule removals from the UI.
Implementation:
- Users can toggle `enabled` state on rules and monitored folders without deleting them.
- When an explicit rule deletion is confirmed by the user, the rule row is removed from `rules`, but associated entries in `audit_logs` remain intact with their descriptive `rule_name` preserved.

## 9. Auditing
Do we record:
- Created by? N/A (Single-user local desktop application; default local user identity).
- Updated by? N/A.
- Deleted by? N/A.
- Activity history? Yes, every file move, rename, copy, error, or recycle operation is recorded in `audit_logs`.
Retention & Pruning:
- Automatic background retention cleanup runs on engine startup: logs older than 12 hours (or user configurable limit) are purged using `DELETE FROM audit_logs WHERE timestamp < datetime('now', '-12 hours')`.

## 10. Sensitive Data
Sensitive fields:
- No passwords, financial credentials, or secret keys are stored in the database.
- File paths may contain personal usernames or directory structures; the database is restricted to the local user's `%APPDATA%` directory with OS-level user permissions.

## 11. Migration Rules
Schema changes must:
1. Be documented in this specification.
2. Use idempotent `CREATE TABLE IF NOT EXISTS` or safe `ALTER TABLE ... ADD COLUMN` statements inside `_init_db()`.
3. Check for and safely import legacy database files (`_migrate_legacy_db_if_needed()`) if migrating from earlier versions.
4. Never alter existing data or drop tables during routine updates.

## 12. Seed Data
For new installations, the system starts with an empty clean database and can auto-populate standard default monitored folder paths if consented:
- Origin folder: `%USERPROFILE%\Downloads` (recursive: false, enabled: true)
- Template default rules (e.g., "Sort Invoices to Documents", "Move Installers to Archives") can be created via the frontend UI preset templates.
