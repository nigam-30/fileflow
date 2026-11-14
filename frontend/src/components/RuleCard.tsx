import React from 'react';
import { Rule } from '../types';
import { Trash2, Edit3, ArrowRight, CircleDot, Folder } from 'lucide-react';

interface RuleCardProps {
  rule: Rule;
  onToggle: (id: string) => void;
  onDelete: (id: string) => void;
  onEdit: (rule: Rule) => void;
}

export const RuleCard: React.FC<RuleCardProps> = ({ rule, onToggle, onDelete, onEdit }) => {
  return (
    <div className={`p-5 rounded-xl border transition-all duration-200 ${
      rule.enabled 
        ? 'bg-white dark:bg-black border-neutral-200 dark:border-neutral-800 shadow-sm' 
        : 'bg-neutral-50 dark:bg-neutral-950 border-neutral-200 dark:border-neutral-900 opacity-60'
    }`}>
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <div className="flex items-center space-x-3">
            <h3 className="font-semibold text-base text-neutral-900 dark:text-white">{rule.name}</h3>
            <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider ${
              rule.match_mode === 'all' 
                ? 'bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/20' 
                : 'bg-amber-500/10 text-amber-600 dark:text-amber-400 border border-amber-500/20'
            }`}>
              Match {rule.match_mode.toUpperCase()}
            </span>
          </div>
          {rule.description && (
            <p className="text-xs text-neutral-500 dark:text-neutral-400">{rule.description}</p>
          )}
        </div>

        {/* Toggle & Actions */}
        <div className="flex items-center space-x-2">
          <button
            onClick={() => onToggle(rule.id)}
            className={`w-11 h-6 flex items-center rounded-full p-1 transition-colors duration-200 ease-in-out ${
              rule.enabled ? 'bg-blue-600 justify-end' : 'bg-neutral-300 dark:bg-neutral-700 justify-start'
            }`}
          >
            <div className="bg-white w-4 h-4 rounded-full shadow-md transform transition" />
          </button>
          <button
            onClick={() => onEdit(rule)}
            className="p-1.5 text-neutral-500 hover:text-neutral-900 dark:hover:text-white hover:bg-neutral-100 dark:hover:bg-neutral-900 rounded-lg transition"
            title="Edit Rule"
          >
            <Edit3 className="w-4 h-4" />
          </button>
          <button
            onClick={() => onDelete(rule.id)}
            className="p-1.5 text-neutral-500 hover:text-rose-600 dark:hover:text-rose-400 hover:bg-neutral-100 dark:hover:bg-neutral-900 rounded-lg transition"
            title="Delete Rule"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Monitored / Origin Folder Summary */}
      <div className="mt-4 pt-3 border-t border-neutral-100 dark:border-neutral-850 flex items-center space-x-2 text-xs">
        <Folder className="w-3.5 h-3.5 text-blue-600 dark:text-blue-400 shrink-0" />
        <span className="font-semibold text-neutral-600 dark:text-neutral-400 shrink-0">Watch & sort from:</span>
        {rule.monitored_folders && rule.monitored_folders.length > 0 ? (
          <div className="flex flex-wrap gap-1.5">
            {rule.monitored_folders.map((f, idx) => (
              <span
                key={idx}
                className="inline-flex items-center px-2 py-0.5 rounded bg-blue-50 dark:bg-blue-950/40 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-900 font-mono text-[11px]"
              >
                {f}
              </span>
            ))}
          </div>
        ) : (
          <span className="text-neutral-400 italic">All monitored folders</span>
        )}
      </div>

      {/* Conditions Summary */}
      <div className="mt-3 pt-3 border-t border-neutral-100 dark:border-neutral-850 grid gap-2">
        <div className="text-xs font-medium text-neutral-500 dark:text-neutral-400 flex items-center space-x-1.5">
          <CircleDot className="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" />
          <span>If file matches ({rule.conditions.length}):</span>
        </div>
        <div className="flex flex-wrap gap-1.5">
          {rule.conditions.length === 0 ? (
            <span className="text-xs text-neutral-400 italic">Matches all incoming files</span>
          ) : (
            rule.conditions.map((c, idx) => (
              <span
                key={idx}
                className="inline-flex items-center space-x-1 text-xs px-2.5 py-1 rounded-md bg-neutral-100 dark:bg-neutral-900 text-neutral-800 dark:text-neutral-200 border border-neutral-200 dark:border-neutral-800 font-mono"
              >
                <span className="text-blue-600 dark:text-blue-400 font-semibold">{c.field}</span>
                <span className="text-neutral-400">{c.operator}</span>
                <span className="text-emerald-600 dark:text-emerald-400">"{String(c.value)}"</span>
              </span>
            ))
          )}
        </div>
      </div>

      {/* Actions Summary */}
      <div className="mt-3 pt-3 border-t border-neutral-100 dark:border-neutral-850 grid gap-2">
        <div className="text-xs font-medium text-neutral-500 dark:text-neutral-400 flex items-center space-x-1.5">
          <ArrowRight className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
          <span>Then execute ({rule.actions.length}):</span>
        </div>
        <div className="flex flex-wrap gap-1.5">
          {rule.actions.map((a, idx) => (
            <span
              key={idx}
              className="inline-flex items-center space-x-1.5 text-xs px-2.5 py-1 rounded-md bg-emerald-500/10 text-emerald-700 dark:text-emerald-300 border border-emerald-500/20"
            >
              <span className="font-semibold uppercase text-[10px] tracking-wide text-emerald-600 dark:text-emerald-400">{a.type}</span>
              {a.destination && (
                <span className="text-neutral-700 dark:text-neutral-300 truncate max-w-xs" title={a.destination}>
                  → {a.destination}
                </span>
              )}
              {a.template && (
                <span className="text-amber-600 dark:text-amber-400 font-mono text-[11px]">
                  [{a.template}]
                </span>
              )}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
};
