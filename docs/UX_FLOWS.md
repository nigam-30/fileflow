# UX Flows

This document details the critical user journeys, interactions, state transitions, and edge cases across FileFlow.

## Flow 1 - Application Launch & First-Run Experience
1. User launches FileFlow via the desktop shortcut or executable.
2. PyWebView / desktop window initializes at `1024x720` centered on screen.
3. React UI boots up and queries backend `/api/rules`, `/api/folders`, and `/api/logs`.
4. If no monitored folders exist, an onboarding banner or prompt suggests selecting the default Windows `Downloads` directory.
5. User confirms or adjusts default origin folder.
Loading State: Skeleton placeholder on rule list and statistics header.
Error State: Toast alert stating "Failed to connect to local FileFlow engine" with a retry button.
Empty State: Illustrated banner explaining "No rules active yet. Set up your first automated workflow to keep your files organized."

## Flow 2 - Add & Monitor an Origin Folder
1. User navigates to the "Monitored Folders" tab.
2. User clicks "+ Add Folder".
3. System invokes the native Windows Folder Browser dialog (`SHBrowseForFolderW`).
4. User selects a local folder (e.g., `D:\MyDownloads`) and confirms.
5. Frontend sends `POST /api/folders` with the absolute path and `recursive` toggle.
6. Backend validates path, persists it to `monitored_folders`, and attaches a `DirectoryWatcher` observer.
7. UI updates the folder card list immediately with active status badge.
Loading State: Native Windows dialog active; folder list shows disabled spinner while registering.
Error State: Modal banner stating "Folder does not exist or permission denied."
Empty State: Card indicating "No monitored folders. Add a folder to begin automatic background monitoring."

## Flow 3 - Create Automation Rule with Instant Auto-Scan
1. User clicks "+ New Rule" on the Rules tab.
2. `RuleBuilderModal` opens displaying:
   - Rule Name and Description inputs.
   - Monitored folder picker selector.
   - Match mode toggle (`Match ALL conditions` vs. `Match ANY condition`).
   - Condition Builder: field selector (`file.extension`, `file.size_mb`, `content.text`), operator selector, and value input.
   - Action Builder: action type (`move`, `copy`, `rename`, `recycle`), destination path picker, collision policy.
3. User completes configuration and clicks "Save & Scan".
4. Frontend sends `POST /api/rules`.
5. Backend validates rule schema, persists to SQLite `rules`, updates active engine rules, and triggers an immediate sweep of origin folders for existing matching files.
6. Modal closes, rule card appears in list, and auto-scan results stream into the Audit Log.
Loading State: "Saving and scanning..." spinner on submit button; inputs disabled.
Error State: Inline field validation errors (e.g. "Destination folder cannot be empty", "Invalid regex pattern").
Empty State: N/A.

## Flow 4 - 4-Stage Duplicate Scan & Safe Cleanup
1. User opens the "Duplicate Finder" tab.
2. User selects target directory to scan (or uses native Windows folder picker).
3. Clicks "Start Duplicate Scan".
4. Backend executes 4-stage filtering:
   - Stage 1: Size grouping.
   - Stage 2: Head+Tail 64 KB dual-sample hash.
   - Stage 3: Multi-threaded SHA-256 calculation.
   - Stage 4: Byte-for-byte binary verification.
5. Frontend receives grouped duplicates with SHA-256 checksums, modification dates, and file sizes.
6. User reviews items and clicks "Select All Except Oldest" or manually checks duplicates.
7. User clicks "Clean to Recycle Bin".
8. Confirmation modal appears detailing total files selected and disk space to be reclaimed.
9. User confirms; backend calls `send2trash` for each selected path and returns reclaimed bytes.
Loading State: Progress bar indicating scan phases ("Checking file sizes...", "Computing dual hashes...", "Verifying duplicates...").
Error State: Red notification stating "Unable to access file: locked by another process" with error list.
Empty State: Clean checkmark screen: "No duplicate files found in this directory. Your storage is clean!"

## Flow 5 - Rule Dry-Run Simulation (Rule Tester)
1. User navigates to the "Rule Tester" tab.
2. User clicks "Browse File" to select a sample file (`OpenFileNameW` native dialog).
3. The selected file's extracted metadata (extension, size, created date, PDF text snippet) is previewed.
4. User clicks "Test Against Rules".
5. Backend evaluates all enabled rules without making filesystem changes.
6. UI displays an interactive simulation trace showing:
   - Evaluated conditions with green checkmarks (passed) or red crosses (failed).
   - Matched rule name and predicted output path/name.
Loading State: Spinner on simulation button.
Error State: Alert explaining "File could not be read or extractor crashed."
Empty State: Prompt asking user to "Choose a file to test your automation rules in dry-run mode."

## Flow 6 - Audit Log Exploration & Diagnostics
1. User clicks the "Audit Logs" tab.
2. System displays a tabular history of actions: Timestamp, Rule Name, Source, Destination, Status Badge (`SUCCESS`, `SKIPPED`, `FAILED`).
3. User can filter logs by status (`All`, `Success`, `Failed`) or search by file name.
4. Clicking a log entry expands a drawer showing detailed error messages or execution stats.
5. User can click "Purge Logs" to clear the local history.
Loading State: Animated skeleton rows.
Error State: Banner stating "Could not load audit log history."
Empty State: "No activity recorded yet. File movements will appear here once rules trigger."
