import React, { useState } from 'react';
import { AuditLogEntry } from '../types';
import { History, CheckCircle2, AlertCircle, AlertTriangle, Info, Search } from 'lucide-react';

interface AuditLogViewProps {
  logs: AuditLogEntry[];
  onRefresh: () => void;
}

export const AuditLogView: React.FC<AuditLogViewProps> = ({ logs, onRefresh }) => {
  const [search, setSearch] = useState('');

  const formatLogTime = (ts: string) => {
    try {
      let parseable = ts;
      if (parseable && parseable.includes(' ') && !parseable.includes('T')) {
        parseable = parseable.replace(' ', 'T') + 'Z';
      }
      const d = new Date(parseable);
      if (isNaN(d.getTime())) return ts;
      return d.toLocaleTimeString([], {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: true
      });
    } catch {
      return ts;
    }
  };

  const filtered = logs.filter((log) => {
    if (!search) return true;
    const s = search.toLowerCase();
    return (
      (log.rule_name || '').toLowerCase().includes(s) ||
      log.source_path.toLowerCase().includes(s) ||
      (log.destination_path || '').toLowerCase().includes(s) ||
      (log.details || '').toLowerCase().includes(s)
    );
  });

  const getStatusBadge = (status: AuditLogEntry['status']) => {
    switch (status) {
      case 'success':
        return (
          <span className="inline-flex items-center space-x-1 text-[11px] font-semibold text-emerald-600 dark:text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
            <CheckCircle2 className="w-3 h-3" />
            <span>Success</span>
          </span>
        );
      case 'skipped':
        return (
          <span className="inline-flex items-center space-x-1 text-[11px] font-semibold text-amber-600 dark:text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded-full border border-amber-500/20">
            <AlertTriangle className="w-3 h-3" />
            <span>Skipped</span>
          </span>
        );
      case 'failed':
        return (
          <span className="inline-flex items-center space-x-1 text-[11px] font-semibold text-rose-600 dark:text-rose-400 bg-rose-500/10 px-2 py-0.5 rounded-full border border-rose-500/20">
            <AlertCircle className="w-3 h-3" />
            <span>Failed</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center space-x-1 text-[11px] font-semibold text-neutral-600 dark:text-neutral-400 bg-neutral-500/10 px-2 py-0.5 rounded-full border border-neutral-500/20">
            <Info className="w-3 h-3" />
            <span>Info</span>
          </span>
        );
    }
  };

  return (
    <div className="bg-white dark:bg-neutral-950 border border-neutral-200 dark:border-neutral-800 rounded-xl p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <History className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          <h2 className="text-sm font-bold text-neutral-900 dark:text-white">Activity & Execution Logs</h2>
          <span className="text-[10px] text-neutral-400 dark:text-neutral-500 bg-neutral-100 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 px-2 py-0.5 rounded-full font-medium">
            Auto-purged after 12 hrs
          </span>
        </div>
        <div className="relative">
          <Search className="w-3.5 h-3.5 text-neutral-400 absolute left-2.5 top-2.5" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search logs..."
            className="pl-8 pr-3 py-1.5 bg-neutral-50 dark:bg-black border border-neutral-300 dark:border-neutral-800 rounded-lg text-xs text-neutral-900 dark:text-white placeholder-neutral-400 focus:outline-none focus:border-blue-500"
          />
        </div>
      </div>

      <div className="space-y-2 max-h-80 overflow-y-auto">
        {filtered.length === 0 ? (
          <p className="text-xs text-neutral-400 dark:text-neutral-500 italic py-4 text-center">
            No activity logs recorded yet.
          </p>
        ) : (
          filtered.map((log) => (
            <div
              key={log.id}
              className="p-3 bg-neutral-50 dark:bg-black rounded-lg border border-neutral-200 dark:border-neutral-850 flex flex-col sm:flex-row sm:items-center justify-between gap-2"
            >
              <div className="space-y-1 truncate">
                <div className="flex items-center space-x-2">
                  {getStatusBadge(log.status)}
                  <span className="text-xs font-semibold text-neutral-800 dark:text-neutral-200">
                    {log.rule_name || 'Manual Action'}
                  </span>
                  <span className="text-[10px] text-neutral-500 uppercase tracking-wider">
                    {log.action_type}
                  </span>
                </div>
                <div className="text-xs text-neutral-600 dark:text-neutral-400 font-mono truncate">
                  <span className="text-neutral-900 dark:text-neutral-200">{log.source_path}</span>
                  {log.destination_path && (
                    <span className="text-blue-600 dark:text-blue-400"> → {log.destination_path}</span>
                  )}
                </div>
                {log.details && (
                  <p className="text-[11px] text-neutral-500">{log.details}</p>
                )}
              </div>
              <div className="text-[11px] text-neutral-400 shrink-0 sm:text-right font-mono">
                {formatLogTime(log.timestamp)}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
