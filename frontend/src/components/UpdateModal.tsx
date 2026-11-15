import React from 'react';
import { UpdateInfo } from '../types';
import { Sparkles, Download, ExternalLink, X, ArrowUpCircle } from 'lucide-react';

interface UpdateModalProps {
  isOpen: boolean;
  onClose: () => void;
  updateInfo: UpdateInfo | null;
}

export const UpdateModal: React.FC<UpdateModalProps> = ({
  isOpen,
  onClose,
  updateInfo,
}) => {
  if (!isOpen || !updateInfo) return null;

  const handleOpenUrl = async (url: string) => {
    try {
      await fetch('/api/open-external', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
      });
    } catch {
      window.open(url, '_blank');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-2xl max-w-lg w-full shadow-2xl overflow-hidden flex flex-col">
        {/* Header */}
        <div className="px-6 py-5 border-b border-neutral-200 dark:border-neutral-800 flex items-center justify-between bg-neutral-50/50 dark:bg-neutral-950/50">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-blue-500/10 dark:bg-blue-400/10 flex items-center justify-center text-blue-600 dark:text-blue-400">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="text-base font-bold text-neutral-900 dark:text-white">New Update Available</h3>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20">
                  v{updateInfo.latest_version}
                </span>
              </div>
              <p className="text-xs text-neutral-500 dark:text-neutral-400">
                You are on v{updateInfo.current_version} &bull; Latest: v{updateInfo.latest_version}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-neutral-400 hover:text-neutral-700 dark:hover:text-neutral-200 rounded-lg transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content & Release Notes */}
        <div className="p-6 space-y-4 max-h-[60vh] overflow-y-auto">
          <div>
            <h4 className="text-xs font-semibold text-neutral-500 dark:text-neutral-400 uppercase tracking-wider mb-2">
              What's New in {updateInfo.release_name || `v${updateInfo.latest_version}`}
            </h4>
            <div className="p-4 bg-neutral-50 dark:bg-black rounded-xl border border-neutral-200 dark:border-neutral-800 text-xs font-mono text-neutral-700 dark:text-neutral-300 whitespace-pre-wrap leading-relaxed max-h-48 overflow-y-auto">
              {updateInfo.release_notes || 'Performance improvements, bug fixes, and stability updates.'}
            </div>
          </div>

          <div className="p-3 bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-900/50 rounded-xl flex items-start space-x-2.5">
            <ArrowUpCircle className="w-4 h-4 text-blue-600 dark:text-blue-400 shrink-0 mt-0.5" />
            <p className="text-xs text-blue-700 dark:text-blue-300 leading-normal">
              Running the new installer replaces the older version automatically in seconds without losing any of your rules, folders, or settings.
            </p>
          </div>
        </div>

        {/* Actions */}
        <div className="px-6 py-4 border-t border-neutral-200 dark:border-neutral-800 flex items-center justify-between bg-neutral-50/50 dark:bg-neutral-950/50">
          <button
            onClick={() => handleOpenUrl(updateInfo.release_url)}
            className="flex items-center space-x-1.5 px-3 py-2 text-xs font-semibold text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-800 transition"
          >
            <ExternalLink className="w-3.5 h-3.5" />
            <span>View Release on GitHub</span>
          </button>

          <div className="flex items-center space-x-2">
            <button
              onClick={onClose}
              className="px-4 py-2 text-xs font-semibold text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white rounded-lg transition"
            >
              Later
            </button>
            <button
              onClick={() => handleOpenUrl(updateInfo.download_url)}
              className="flex items-center space-x-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg shadow-sm shadow-blue-600/30 transition active:scale-95"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download Update</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
