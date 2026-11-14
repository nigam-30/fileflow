import React, { useState } from 'react';
import { FlaskConical, Play, CheckCircle2, XCircle, FolderSearch } from 'lucide-react';
import { openFilePicker } from '../utils/filePicker';

export const RuleTester: React.FC = () => {
  const [filePath, setFilePath] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleBrowseFile = async () => {
    try {
      const selected = await openFilePicker();
      if (selected) {
        setFilePath(selected);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleTest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!filePath.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await fetch('/api/test-file', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ file_path: filePath.trim() }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Failed to inspect file');
      }

      const data = await res.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message || 'Error communicating with backend');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white dark:bg-neutral-950 border border-neutral-200 dark:border-neutral-800 rounded-xl p-6 space-y-4">
      <div className="flex items-center space-x-2">
        <FlaskConical className="w-5 h-5 text-blue-600 dark:text-blue-400" />
        <h2 className="text-sm font-bold text-neutral-900 dark:text-white">Live Rule Simulator & Inspector</h2>
      </div>
      <p className="text-xs text-neutral-500 dark:text-neutral-400">
        Test rules and preview extracted metadata without moving or modifying your files.
      </p>

      <form onSubmit={handleTest} className="flex flex-col sm:flex-row gap-2">
        <div className="relative flex-1">
          <input
            type="text"
            value={filePath}
            onChange={(e) => setFilePath(e.target.value)}
            placeholder="e.g. C:\Users\Downloads\sample_invoice.pdf"
            className="w-full px-3 py-2 pr-28 bg-neutral-50 dark:bg-black border border-neutral-300 dark:border-neutral-800 rounded-lg text-xs text-neutral-900 dark:text-white placeholder-neutral-400 focus:outline-none focus:border-blue-500"
          />
          <button
            type="button"
            onClick={handleBrowseFile}
            className="absolute right-1.5 top-1.5 px-3 py-1 bg-neutral-200 dark:bg-neutral-800 hover:bg-neutral-300 dark:hover:bg-neutral-700 text-neutral-800 dark:text-neutral-200 text-xs font-semibold rounded flex items-center space-x-1.5 transition"
          >
            <FolderSearch className="w-3.5 h-3.5" />
            <span>Browse...</span>
          </button>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="flex items-center justify-center space-x-1.5 px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg shadow-sm transition active:scale-95 disabled:opacity-50"
        >
          <Play className="w-3.5 h-3.5" />
          <span>{loading ? 'Testing...' : 'Simulate'}</span>
        </button>
      </form>

      {error && (
        <div className="p-3 bg-rose-500/10 border border-rose-500/20 rounded-lg text-xs text-rose-600 dark:text-rose-400">
          {error}
        </div>
      )}

      {result && (
        <div className="space-y-4 pt-3 border-t border-neutral-200 dark:border-neutral-800">
          {/* Rule Evaluations */}
          <div>
            <h3 className="text-xs font-bold text-neutral-700 dark:text-neutral-300 uppercase tracking-wider mb-2">
              Rule Match Results
            </h3>
            <div className="space-y-2">
              {result.evaluations.map((ev: any, idx: number) => (
                <div
                  key={idx}
                  className={`p-3 rounded-lg border flex items-center justify-between text-xs ${
                    ev.matched
                      ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-700 dark:text-emerald-300'
                      : 'bg-neutral-50 dark:bg-black border-neutral-200 dark:border-neutral-800 text-neutral-500'
                  }`}
                >
                  <div className="flex items-center space-x-2">
                    {ev.matched ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                    ) : (
                      <XCircle className="w-4 h-4 text-neutral-400" />
                    )}
                    <span className="font-semibold text-neutral-800 dark:text-neutral-200">{ev.rule_name}</span>
                  </div>
                  <span className="text-[11px] font-mono font-medium">
                    {ev.matched ? 'MATCHED (Would Trigger)' : 'NO MATCH'}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Extracted Variables Grid */}
          <div>
            <h3 className="text-xs font-bold text-neutral-700 dark:text-neutral-300 uppercase tracking-wider mb-2">
              Extracted Tokens & Metadata ({Object.keys(result.variables).length})
            </h3>
            <div className="bg-neutral-50 dark:bg-black p-3 rounded-lg border border-neutral-200 dark:border-neutral-800 max-h-56 overflow-y-auto font-mono text-xs space-y-1">
              {Object.entries(result.variables).map(([k, v]) => (
                <div key={k} className="flex justify-between py-0.5 border-b border-neutral-200 dark:border-neutral-900 last:border-0">
                  <span className="text-blue-600 dark:text-blue-400 font-semibold">{`{${k}}`}:</span>
                  <span className="text-neutral-700 dark:text-neutral-300 truncate max-w-md text-right">{String(v)}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
