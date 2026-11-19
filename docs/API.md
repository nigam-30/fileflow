# API Specification

## 1. Overview
The FileFlow Backend exposes a local loopback REST API running on `127.0.0.1`. All endpoints (except static assets and root health checks) require authentication via the `X-API-Token` header.

Base URL: `http://127.0.0.1:<PORT>`
Content-Type: `application/json`

## 2. Authentication
Header:
```http
X-API-Token: <32-byte-hex-session-token>
```
If the token is omitted or incorrect, the server returns:
```json
{
  "detail": "Unauthorized: Invalid or missing API token."
}
```
HTTP Status: `403 Forbidden`

---

## 3. Endpoints

### 3.1 Rule Management

#### `GET /api/rules`
Description: Retrieves all saved automation rules.
Response `200 OK`:
```json
[
  {
    "id": "b3e34b92-8094-4b5b-b924-42b7e51cfa8a",
    "name": "Organize Invoices",
    "description": "Moves incoming invoices to Documents/Invoices",
    "enabled": true,
    "monitored_folders": ["C:\\Users\\User\\Downloads"],
    "match_mode": "all",
    "conditions": [
      {
        "field": "file.extension",
        "operator": "equals",
        "value": "pdf"
      },
      {
        "field": "content.text",
        "operator": "contains",
        "value": "Invoice"
      }
    ],
    "actions": [
      {
        "type": "move",
        "destination": "C:\\Users\\User\\Documents\\Invoices",
        "collision_policy": "rename_with_counter"
      }
    ],
    "stop_processing_on_match": true,
    "created_at": "2026-11-19T10:00:00Z",
    "updated_at": "2026-11-19T10:00:00Z"
  }
]
```

#### `POST /api/rules`
Description: Creates or updates an automation rule.
Request Body: `Rule` object (matches schema above).
Response `200 OK`: Saved `Rule` object.
Error `422 Unprocessable Entity`: Validation failure on condition or action schema.

#### `GET /api/rules/{rule_id}`
Description: Retrieves a specific rule by UUID.
Response `200 OK`: `Rule` object.
Response `404 Not Found`: If rule ID does not exist.

#### `DELETE /api/rules/{rule_id}`
Description: Deletes a specific rule. Historical audit logs are retained.
Response `200 OK`:
```json
{
  "status": "success",
  "deleted_id": "b3e34b92-8094-4b5b-b924-42b7e51cfa8a"
}
```

#### `POST /api/rules/{rule_id}/toggle`
Description: Toggles the `enabled` state of a rule.
Request Body:
```json
{
  "enabled": true
}
```
Response `200 OK`: Updated `Rule` object.

---

### 3.2 Monitored Folders

#### `GET /api/folders`
Description: Lists all monitored directories and their current watcher states.
Response `200 OK`:
```json
[
  {
    "path": "C:\\Users\\User\\Downloads",
    "recursive": false,
    "enabled": true,
    "added_at": "2026-11-19T09:00:00Z"
  }
]
```

#### `POST /api/folders`
Description: Registers a new directory path for real-time monitoring.
Request Body:
```json
{
  "path": "C:\\Users\\User\\Downloads",
  "recursive": false
}
```
Response `200 OK`:
```json
{
  "status": "success",
  "path": "C:\\Users\\User\\Downloads"
}
```

#### `DELETE /api/folders`
Description: Removes a folder from monitored list and unbinds filesystem watchers.
Request Body:
```json
{
  "path": "C:\\Users\\User\\Downloads"
}
```
Response `200 OK`:
```json
{
  "status": "success",
  "removed_path": "C:\\Users\\User\\Downloads"
}
```

---

### 3.3 Rule Testing & Dry-Run Simulation

#### `POST /api/test-rule`
Description: Evaluates a candidate file against active rules without modifying disk contents.
Request Body:
```json
{
  "file_path": "C:\\Users\\User\\Downloads\\sample_invoice.pdf",
  "rule": null
}
```
*(Note: Passing `rule: null` tests against all active rules; passing a specific rule tests only that rule).*
Response `200 OK`:
```json
{
  "matched": true,
  "matched_rule_id": "b3e34b92-8094-4b5b-b924-42b7e51cfa8a",
  "matched_rule_name": "Organize Invoices",
  "simulated_actions": [
    {
      "type": "move",
      "target_path": "C:\\Users\\User\\Documents\\Invoices\\sample_invoice.pdf"
    }
  ],
  "extracted_metadata": {
    "file.extension": "pdf",
    "file.size_mb": 0.45,
    "file.created_year": "2026",
    "content.text_sample": "INVOICE #40291... TOTAL DUE: $150.00"
  }
}
```

---

### 3.4 Duplicate Finder

#### `POST /api/duplicates/scan`
Description: Runs the 4-stage duplicate detection engine on a specified folder.
Request Body:
```json
{
  "target_folder": "C:\\Users\\User\\Downloads",
  "recursive": false
}
```
Response `200 OK`:
```json
{
  "status": "completed",
  "total_files_scanned": 1420,
  "duplicate_groups_count": 3,
  "groups": [
    {
      "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "size_bytes": 1048576,
      "files": [
        {
          "path": "C:\\Users\\User\\Downloads\\report.pdf",
          "mtime": 1731998400.0,
          "created_at": "2026-11-19T08:00:00Z"
        },
        {
          "path": "C:\\Users\\User\\Downloads\\report (1).pdf",
          "mtime": 1732002000.0,
          "created_at": "2026-11-19T09:00:00Z"
        }
      ]
    }
  ]
}
```

#### `POST /api/duplicates/clean`
Description: Sends specified duplicate file paths to the Windows Recycle Bin via `send2trash`.
Request Body:
```json
{
  "file_paths": [
    "C:\\Users\\User\\Downloads\\report (1).pdf"
  ]
}
```
Response `200 OK`:
```json
{
  "status": "success",
  "recycled_count": 1,
  "reclaimed_bytes": 1048576,
  "failed_paths": []
}
```

---

### 3.5 Audit Logs

#### `GET /api/logs`
Description: Returns paginated operational logs.
Query Parameters:
- `limit` (integer, default: 50): Number of records to return.
- `offset` (integer, default: 0): Pagination offset.
- `status` (string, optional): Filter by `success`, `skipped`, or `failed`.
Response `200 OK`:
```json
[
  {
    "id": 104,
    "timestamp": "2026-11-19T10:15:22Z",
    "rule_id": "b3e34b92-8094-4b5b-b924-42b7e51cfa8a",
    "rule_name": "Organize Invoices",
    "source_path": "C:\\Users\\User\\Downloads\\invoice_402.pdf",
    "destination_path": "C:\\Users\\User\\Documents\\Invoices\\invoice_402.pdf",
    "action_type": "move",
    "status": "success",
    "details": "Moved with collision policy rename_with_counter"
  }
]
```

#### `DELETE /api/logs`
Description: Purges historical audit logs.
Response `200 OK`:
```json
{
  "status": "success",
  "cleared_records": 104
}
```

---

### 3.6 Windows System Dialogs & Utilities

#### `POST /api/system/browse-folder`
Description: Opens the native Win32 `SHBrowseForFolderW` dialog on the host system to let the user pick a folder.
Response `200 OK`:
```json
{
  "path": "C:\\Users\\User\\Documents\\Invoices",
  "cancelled": false
}
```

#### `POST /api/system/browse-file`
Description: Opens the native Win32 `GetOpenFileNameW` dialog to let the user select a file for rule testing.
Response `200 OK`:
```json
{
  "path": "C:\\Users\\User\\Downloads\\sample.pdf",
  "cancelled": false
}
```

#### `GET /api/system/status`
Description: Reports health, active watcher thread status, memory consumption, and SQLite database path.
Response `200 OK`:
```json
{
  "status": "healthy",
  "version": "1.0.3",
  "active_watchers": 2,
  "database_path": "C:\\Users\\User\\AppData\\Roaming\\FileFlowData\\fileflow.db",
  "memory_rss_mb": 42.1
}
```
