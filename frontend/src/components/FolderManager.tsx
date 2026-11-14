import React, { useState } from 'react';
import { MonitoredFolder } from '../types';
import { Folder, FolderPlus, Trash2, FolderSearch } from 'lucide-react';
import { openFolderPicker } from '../utils/filePicker';

interface FolderManagerProps {
  folders: MonitoredFolder[];
  onAddFolder: (path: string, recursive: boolean) => void;
  onRemoveFolder: (path: string) => void;
}

export const FolderManager: React.FC<FolderManagerProps> = ({
  folders,
  onAddFolder,
  onRemoveFolder,
}) => {
  const [newPath, setNewPath] = useState('');
  const [recursive, setRecursive] = useState(false);

  const handleBrowse = async () => {
    try {
      const selected = await openFolderPicker();
      if (selected) {
        setNewPath(selected);
      }
    } catch (err) {
      console.error('Failed to open native folder picker', err);
    }
  };

  const handleAdd = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newPath.trim()) return;
    onAddFolder(newPath.trim(), recursive);
    setNewPath('');
  };

  return (
    <div className="bg-white dark:bg-neutral-950 border border-neutral-200 dark:border-neutral-800 rounded-xl p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Folder className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          <h2 className="text-sm font-bold text-neutral-900 dark:text-white">Monitored Folders</h2>
        </div>
        <span className="text-xs text-neutral-500">{folders.length} watched</span>
      </div>

      <form onSubmit={handleAdd} className="space-y-3">
        <div className="flex flex-col sm:flex-row gap-2">
          <div className="relative flex-1">
            <input
              type="text"
              value={newPath}
              onChange={(e) => setNewPath(e.target.value)}
              placeholder="e.g. D:\Downloads or click Browse..."
              className="w-full px-3 py-2 pr-28 bg-neutral-50 dark:bg-black border border-neutral-300 dark:border-neutral-800 rounded-lg text-xs text-neutral-900 dark:text-white placeholder-neutral-400 focus:outline-none focus:border-blue-500"
            />
            <button
              type="button"
              onClick={handleBrowse}
              className="absolute right-1.5 top-1.5 px-3 py-1 bg-neutral-200 dark:bg-neutral-800 hover:bg-neutral-300 dark:hover:bg-neutral-700 text-neutral-800 dark:text-neutral-200 text-xs font-semibold rounded flex items-center space-x-1.5 transition"
            >
              <FolderSearch className="w-3.5 h-3.5" />
              <span>Browse...</span>
            </button>
          </div>

          <button
            type="submit"
            className="flex items-center justify-center space-x-1.5 px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg transition active:scale-95 shadow-sm"
          >
            <FolderPlus className="w-3.5 h-3.5" />
            <span>Add Folder</span>
          </button>
        </div>

        <label className="flex items-center space-x-2 text-xs text-neutral-600 dark:text-neutral-400 cursor-pointer">
          <input
            type="checkbox"
            checked={recursive}
            onChange={(e) => setRecursive(e.target.checked)}
            className="rounded bg-neutral-200 dark:bg-neutral-900 border-neutral-300 dark:border-neutral-800 text-blue-600 focus:ring-0"
          />
          <span>Include Subfolders</span>
        </label>
      </form>

      <div className="space-y-2 max-h-56 overflow-y-auto">
        {folders.length === 0 ? (
          <p className="text-xs text-neutral-400 dark:text-neutral-500 italic py-2">
            No folders monitored yet. Use Browse or paste a path above to watch for incoming files.
          </p>
        ) : (
          folders.map((f, idx) => (
            <div
              key={idx}
              className="flex items-center justify-between p-3 bg-neutral-50 dark:bg-black rounded-lg border border-neutral-200 dark:border-neutral-850 hover:border-neutral-300 dark:hover:border-neutral-700 transition"
            >
              <div className="flex items-center space-x-2.5 truncate">
                <Folder className="w-4 h-4 text-blue-500 shrink-0" />
                <span className="text-xs font-mono text-neutral-800 dark:text-neutral-200 truncate">{f.path}</span>
                {f.recursive && (
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-neutral-200 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-300 font-medium">
                    recursive
                  </span>
                )}
              </div>
              <button
                onClick={() => onRemoveFolder(f.path)}
                className="p-1.5 text-neutral-400 hover:text-rose-600 dark:hover:text-rose-400 rounded transition"
                title="Remove folder"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
