import React, { useState } from 'react';
import { Copy, Folder, FolderSearch, Trash2, CheckCircle2, AlertCircle, HardDrive, RefreshCw } from 'lucide-react';
import { openFolderPicker } from '../utils/filePicker';

interface DuplicateFile {
  path: string;
  name: string;
  directory: string;
  size_bytes: number;
  modified: number;
}

interface DuplicateGroup {
  hash: string;
  size_bytes: number;
  size_formatted: string;
  count: number;
  files: DuplicateFile[];
}

export const DuplicateFinderView: React.FC = () => {
  const [folderPath, setFolderPath] = useState('');
  const [recursive, setRecursive] = useState(true);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{
    folder: string;
    duplicate_groups: DuplicateGroup[];
    total_groups: number;
    total_wasted_formatted: string;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Call native Windows folder picker
  const handleBrowseFolder = async () => {
    try {
      const selected = await openFolderPicker();
      if (selected) {
        setFolderPath(selected);
      }
    } catch (err) {
      console.error('Failed to open native folder picker', err);
    }
  };

  const handleScan = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!folderPath.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const res = await fetch('/api/duplicates/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ folder_path: folderPath.trim(), recursive }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Scan failed');
      }

      const data = await res.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message || 'Error scanning for duplicates');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteFile = async (filePath: string, groupHash: string) => {
    if (!confirm(`Send this duplicate copy to the Recycle Bin?\n${filePath}`)) return;

    try {
      const res = await fetch('/api/duplicates/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ file_path: filePath, recycle: true }),
      });

      if (res.ok) {
        // Update local state by removing the deleted file from the group
        if (result) {
          const updatedGroups = result.duplicate_groups
            .map((g) => {
              if (g.hash === groupHash) {
                const remaining = g.files.filter((f) => f.path !== filePath);
                return { ...g, files: remaining, count: remaining.length };
              }
              return g;
            })
            .filter((g) => g.files.length > 1); // remove group if only 1 file remains

          setResult({
            ...result,
            duplicate_groups: updatedGroups,
            total_groups: updatedGroups.length,
          });
        }
      }
    } catch (err) {
      console.error('Failed to delete file', err);
    }
  };

  const handleKeepOne = async (group: DuplicateGroup, keep: 'newest' | 'oldest') => {
    const sorted = [...group.files].sort((a, b) => 
      keep === 'newest' ? b.modified - a.modified : a.modified - b.modified
    );
    const toKeep = sorted[0];
    const toDelete = sorted.slice(1);

    if (!confirm(`Keep "${toKeep.name}" (${new Date(toKeep.modified * 1000).toLocaleDateString()}) and send the other ${toDelete.length} duplicate copy(ies) to the Recycle Bin?`)) {
      return;
    }

    for (const f of toDelete) {
      try {
        await fetch('/api/duplicates/delete', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ file_path: f.path, recycle: true }),
        });
      } catch (err) {
        console.error(err);
      }
    }

    // Refresh groups
    if (result) {
      const updatedGroups = result.duplicate_groups.filter((g) => g.hash !== group.hash);
      setResult({
        ...result,
        duplicate_groups: updatedGroups,
        total_groups: updatedGroups.length,
      });
    }
  };

  return (
    <div className="bg-white dark:bg-neutral-950 border border-neutral-200 dark:border-neutral-800 rounded-xl p-6 space-y-6">
      <div className="flex items-center space-x-3">
        <div className="p-2.5 bg-blue-500/10 rounded-xl text-blue-600 dark:text-blue-400">
          <Copy className="w-5 h-5" />
        </div>
        <div>
          <h2 className="text-base font-bold text-neutral-900 dark:text-white">
            Duplicate File Finder
          </h2>
          <p className="text-xs text-neutral-500 dark:text-neutral-400">
            Identify exact duplicate files by size and SHA-256 hash, and safely reclaim wasted storage.
          </p>
        </div>
      </div>

      {/* Folder Picker Form */}
      <form onSubmit={handleScan} className="space-y-3">
        <div className="flex flex-col sm:flex-row gap-2">
          <div className="relative flex-1">
            <input
              type="text"
              value={folderPath}
              onChange={(e) => setFolderPath(e.target.value)}
              placeholder="Select folder to scan for duplicates..."
              className="w-full px-3 py-2 pr-28 bg-neutral-50 dark:bg-black border border-neutral-300 dark:border-neutral-800 rounded-lg text-xs text-neutral-900 dark:text-white placeholder-neutral-400 focus:outline-none focus:border-blue-500"
              required
            />
            <button
              type="button"
              onClick={handleBrowseFolder}
              className="absolute right-1.5 top-1.5 px-3 py-1 bg-neutral-200 dark:bg-neutral-800 hover:bg-neutral-300 dark:hover:bg-neutral-700 text-neutral-800 dark:text-neutral-200 text-xs font-semibold rounded flex items-center space-x-1.5 transition"
            >
              <FolderSearch className="w-3.5 h-3.5" />
              <span>Browse...</span>
            </button>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="flex items-center justify-center space-x-2 px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg shadow-md transition active:scale-95 disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>{loading ? 'Scanning Files...' : 'Scan for Duplicates'}</span>
          </button>
        </div>

        <label className="flex items-center space-x-2 text-xs text-neutral-600 dark:text-neutral-400 cursor-pointer">
          <input
            type="checkbox"
            checked={recursive}
            onChange={(e) => setRecursive(e.target.checked)}
            className="rounded bg-neutral-200 dark:bg-neutral-900 border-neutral-300 dark:border-neutral-800 text-blue-600 focus:ring-0"
          />
          <span>Include all subfolders recursively</span>
        </label>
      </form>

      {error && (
        <div className="p-3 bg-rose-500/10 border border-rose-500/20 rounded-lg text-xs text-rose-600 dark:text-rose-400">
          {error}
        </div>
      )}

      {/* Results Header */}
      {result && (
        <div className="space-y-4 pt-4 border-t border-neutral-200 dark:border-neutral-800">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="p-4 bg-neutral-50 dark:bg-black border border-neutral-200 dark:border-neutral-800 rounded-xl flex items-center space-x-3">
              <div className="p-2 bg-blue-500/10 text-blue-600 dark:text-blue-400 rounded-lg">
                <Copy className="w-5 h-5" />
              </div>
              <div>
                <p className="text-xs text-neutral-500 dark:text-neutral-400">Duplicate Groups Found</p>
                <p className="text-lg font-bold text-neutral-900 dark:text-white">{result.total_groups}</p>
              </div>
            </div>

            <div className="p-4 bg-neutral-50 dark:bg-black border border-neutral-200 dark:border-neutral-800 rounded-xl flex items-center space-x-3">
              <div className="p-2 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 rounded-lg">
                <HardDrive className="w-5 h-5" />
              </div>
              <div>
                <p className="text-xs text-neutral-500 dark:text-neutral-400">Wasted Storage Space</p>
                <p className="text-lg font-bold text-emerald-600 dark:text-emerald-400">{result.total_wasted_formatted}</p>
              </div>
            </div>
          </div>

          {/* Group List */}
          {result.duplicate_groups.length === 0 ? (
            <div className="text-center py-10 text-neutral-500 dark:text-neutral-400 text-xs">
              <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto mb-2" />
              <p className="font-semibold text-neutral-800 dark:text-neutral-200">No duplicate files found!</p>
              <p className="mt-1">All files in this folder are unique.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {result.duplicate_groups.map((group, gIdx) => (
                <div
                  key={gIdx}
                  className="bg-neutral-50 dark:bg-black border border-neutral-200 dark:border-neutral-800 rounded-xl p-4 space-y-3"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-2 border-b border-neutral-200 dark:border-neutral-800 gap-2">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-bold text-neutral-800 dark:text-neutral-200">
                        {group.files[0].name}
                      </span>
                      <span className="text-[11px] font-semibold text-blue-600 dark:text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded-full">
                        {group.count} copies ({group.size_formatted} each)
                      </span>
                    </div>

                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handleKeepOne(group, 'newest')}
                        className="text-[11px] font-medium text-neutral-600 dark:text-neutral-400 hover:text-blue-600 dark:hover:text-blue-400 transition"
                      >
                        Keep Newest
                      </button>
                      <span className="text-neutral-400 dark:text-neutral-600">|</span>
                      <button
                        onClick={() => handleKeepOne(group, 'oldest')}
                        className="text-[11px] font-medium text-neutral-600 dark:text-neutral-400 hover:text-blue-600 dark:hover:text-blue-400 transition"
                      >
                        Keep Oldest
                      </button>
                    </div>
                  </div>

                  <div className="space-y-2">
                    {group.files.map((file, fIdx) => (
                      <div
                        key={fIdx}
                        className="flex items-center justify-between p-2.5 bg-white dark:bg-neutral-900 rounded-lg border border-neutral-200 dark:border-neutral-800/80 text-xs"
                      >
                        <div className="truncate space-y-0.5 max-w-xl">
                          <p className="font-mono text-neutral-800 dark:text-neutral-200 truncate">
                            {file.path}
                          </p>
                          <p className="text-[11px] text-neutral-500">
                            Modified: {new Date(file.modified * 1000).toLocaleString()}
                          </p>
                        </div>

                        <button
                          onClick={() => handleDeleteFile(file.path, group.hash)}
                          className="p-1.5 text-neutral-400 hover:text-rose-600 dark:hover:text-rose-400 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded transition"
                          title="Send to Recycle Bin"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
