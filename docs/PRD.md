# Product Requirements Document (PRD)

## 1. Executive Summary
**FileFlow** is an intelligent, open-source, 100% offline desktop automation application for Windows designed to organize cluttered folders (such as `Downloads` and `Desktop`), eliminate duplicate files, and streamline digital workspaces without cloud dependencies or subscription fees. Combining a high-performance Python/FastAPI backend with a clean React + TypeScript interface, FileFlow monitors local folders in real-time, extracts file metadata and contents, evaluates configurable condition rules, and executes file operations safely and transparently.

## 2. Problem Statement
Windows users accumulate hundreds of downloaded files, installer binaries, receipts, and invoices in default folders like `Downloads` and `Desktop`. Over time, this leads to:
- **Productivity Drain**: Users waste minutes or hours manually sorting, searching for, and renaming files.
- **Accidental Clutter & Duplicates**: Repeatedly downloading the same documents wastes gigabytes of disk space and introduces confusion with filenames like `Invoice (1).pdf`.
- **Privacy & Security Risks with Cloud Tools**: Most modern automation or file-sorting tools require third-party cloud uploads, exposing confidential financial, personal, or corporate data.
- **Fragile Manual Scripts**: Standard automation scripts (PowerShell, batch files) are brittle, difficult for non-technical users to manage, and lack safety mechanisms like collision handling or Recycle Bin support.

## 3. Vision & Core Value Proposition
FileFlow delivers a frictionless, trustworthy, and enterprise-grade file automation utility with zero cloud reliance:
- **Instant Background Automation**: Monitors specified directories via filesystem events and immediately moves, renames, copies, or compresses incoming files.
- **Deep Extraction Intelligence**: Looks inside files (PDF body text/metadata, Image EXIF date/camera, file sizes, creation dates, regex patterns) to categorize accurately.
- **Safety by Design**: Features dry-run rule simulations, automatic debouncing for files still downloading, loop prevention, and deletion routed directly to the Windows Recycle Bin.
- **100% Offline & Private**: Zero telemetry, zero analytics, zero external network requests for processing. All data and logs remain strictly on the user's local machine.

## 4. Target Personas & Use Cases
- **Power Users & Professionals**: Developers, designers, writers, and consultants with constant downloads who need invoices, source assets, and contracts auto-sorted into client folders.
- **Casual / Home Users**: Non-technical users whose `Downloads` folders become unmanageable and want an install-and-forget solution.
- **Privacy-Conscious Individuals**: Users handling sensitive tax documents, medical forms, or proprietary data who refuse cloud-based automation tools.

## 5. Core Features & Functional Requirements

### 5.1 Real-Time Folder Monitoring & Origin Routing
- Users can assign one or more monitored origin folders (e.g. `C:\Users\<User>\Downloads`).
- System watches for filesystem events (`created`, `modified`, `moved`) using Windows file system notifications.
- Automatic debounce logic ensures incomplete downloads (e.g., `.crdownload`, `.part`, or locked write handles) are not touched until writes terminate.
- Option to perform an immediate retroactive scan of existing files upon saving or enabling a rule.

### 5.2 Rule Engine & Condition Evaluation
- Support for compound rule logic (`ALL` / AND vs. `ANY` / OR).
- Flexible condition matching:
  - **System Attributes**: File extension, file name stem, file size (MB/KB), creation date, modification date.
  - **PDF Extraction**: Title, author, page count, and full-text keyword matching (case-insensitive or regex).
  - **Image EXIF**: Date taken, camera model, resolution.
  - **Operators**: `equals`, `not_equals`, `contains`, `not_contains`, `starts_with`, `ends_with`, `greater_than`, `less_than`, `matches_regex`, `before`, `after`, `in_last_days`.
- Stop processing subsequent rules when a rule matches (`stop_processing_on_match`).

### 5.3 Safe Action Dispatcher
- Actions supported:
  - `move`: Relocate file to target folder (with dynamic folder creation and path templating, e.g. `{file.created_year}/{file.extension}`).
  - `copy`: Duplicate file to another target destination.
  - `rename`: Dynamic pattern renaming (e.g. `{file.created_date}_{vendor}_{file.name}`).
  - `recycle`: Send file to Windows Recycle Bin via `send2trash`.
  - `delete`: Direct permanent deletion (requires explicit confirmation).
  - `zip`: Compress matching files into an archive.
  - `run_command`: Execute custom local binaries or scripts safely.
- Collision handling policies: `rename_with_counter` (e.g., `file (1).pdf`), `skip`, or `overwrite`.

### 5.4 4-Stage Blazing Fast Duplicate Finder
- Multi-tier filtering to identify exact byte-for-byte duplicates with zero false positives:
  1. **Stage 1 (File Size Bucketing)**: Instant metadata comparison eliminates >90% of files.
  2. **Stage 2 (Head + Tail Dual Sample Hash)**: Reads first and last 64 KB of files to eliminate non-matching candidates with near-zero disk I/O.
  3. **Stage 3 (Full Parallel SHA-256)**: Multi-threaded cryptographic checksums across candidate pairs.
  4. **Stage 4 (Bit-for-Bit Verification)**: Direct binary stream comparison for candidate groups to ensure 100% collision immunity.
- Grouped UI display displaying SHA-256 badges, file paths, sizes, and one-click bulk deletion to Recycle Bin while keeping the newest or oldest file.

### 5.5 Rule Tester & Dry-Run Sandbox
- File simulation tab allows users to select any sample file and test active rules against it.
- Displays step-by-step condition evaluation results and predicted actions without modifying actual disk contents.

### 5.6 Audit Logs & Diagnostics
- Local SQLite logging recording every execution: timestamp, rule ID, source path, target path, action type, status (`success`, `skipped`, `failed`), and details.
- Auto-pruning mechanism to keep database lightweight (purges logs older than retention limits).

## 6. Non-Functional Requirements
- **Performance**: Rule evaluation latency < 50ms per file. Multi-threaded duplicate scanning capable of checking 50,000+ files in under 30 seconds on SSD storage.
- **Reliability & Loop Prevention**: File hash and modification time cache (`processed_files`) prevents infinite loops where moving a file triggers another rule.
- **Security**: Local-only API binding (`127.0.0.1`), per-session cryptographically random API token, path traversal guards (`Path.resolve`), and shell command restrictions.
- **Portability**: Native standalone Windows `.exe` packaged via PyInstaller; no prerequisites or external Python installation needed.

## 7. Assumptions & System Constraints
- Target OS: Windows 10 & Windows 11 (64-bit).
- Native dialogs require Windows shell APIs (`ctypes` integration for folder pickers).
- Users must have read/write permissions for monitored origin and destination folders.

## 8. Out of Scope / Future Roadmap
- Cloud sync (Dropbox, Google Drive, OneDrive cloud-only sync without local mounting).
- Mobile OS support (iOS / Android).
- Optical Character Recognition (OCR) for scanned image-only PDFs (planned for future major release).
