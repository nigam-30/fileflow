import React from 'react';
import { X, ShieldCheck, FileText, CheckCircle2 } from 'lucide-react';

interface LegalModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialTab?: 'privacy' | 'terms';
}

export const LegalModal: React.FC<LegalModalProps> = ({ isOpen, onClose, initialTab = 'privacy' }) => {
  const [tab, setTab] = React.useState<'privacy' | 'terms'>(initialTab);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
      <div className="bg-white dark:bg-black border border-neutral-200 dark:border-neutral-800 rounded-2xl w-full max-w-3xl max-h-[85vh] overflow-hidden shadow-2xl flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-neutral-200 dark:border-neutral-800">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-500/10 rounded-xl text-blue-600 dark:text-blue-400">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-neutral-900 dark:text-white">
                Transparency & Terms
              </h2>
              <p className="text-xs text-neutral-500 dark:text-neutral-400">
                100% Transparent, Open-Source & Private
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-neutral-400 hover:text-neutral-900 dark:hover:text-white rounded-lg transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Switcher */}
        <div className="flex border-b border-neutral-200 dark:border-neutral-800 px-6 pt-2 bg-neutral-50 dark:bg-neutral-950">
          <button
            onClick={() => setTab('privacy')}
            className={`flex items-center space-x-2 py-3 px-4 border-b-2 text-xs font-semibold transition ${
              tab === 'privacy'
                ? 'border-blue-600 text-blue-600 dark:text-blue-400'
                : 'border-transparent text-neutral-500 hover:text-neutral-800 dark:hover:text-neutral-200'
            }`}
          >
            <ShieldCheck className="w-4 h-4" />
            <span>Privacy Policy (100% Offline)</span>
          </button>
          <button
            onClick={() => setTab('terms')}
            className={`flex items-center space-x-2 py-3 px-4 border-b-2 text-xs font-semibold transition ${
              tab === 'terms'
                ? 'border-blue-600 text-blue-600 dark:text-blue-400'
                : 'border-transparent text-neutral-500 hover:text-neutral-800 dark:hover:text-neutral-200'
            }`}
          >
            <FileText className="w-4 h-4" />
            <span>User Agreement & Safety</span>
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto space-y-4 text-xs text-neutral-700 dark:text-neutral-300 leading-relaxed">
          {tab === 'privacy' ? (
            <div className="space-y-4">
              <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl text-emerald-800 dark:text-emerald-300 flex items-start space-x-3">
                <CheckCircle2 className="w-5 h-5 shrink-0 mt-0.5" />
                <div>
                  <h4 className="font-bold text-sm">Zero Telemetry & Absolute Local Privacy</h4>
                  <p className="text-xs mt-1">
                    FileFlow is an open-source, local-first utility. We do not track you, collect metrics, send analytics, or transmit your files over any network. Everything stays strictly on your machine.
                  </p>
                </div>
              </div>

              <h3 className="font-bold text-neutral-900 dark:text-white text-sm">1. Data Storage & Ownership</h3>
              <p>
                All rules, monitored folder lists, processed file histories, and execution logs are stored locally in an embedded SQLite database (<code>fileflow.db</code>) located in your application folder. No account, login, or internet connectivity is ever required.
              </p>

              <h3 className="font-bold text-neutral-900 dark:text-white text-sm">2. Document & File Content</h3>
              <p>
                When FileFlow evaluates file content (such as reading PDF text, invoice numbers, Word documents, or image EXIF metadata), parsing occurs entirely within your local Python process using open-source libraries (<code>pypdf</code>, <code>Pillow</code>). File data is never sent to third-party APIs or cloud endpoints.
              </p>

              <h3 className="font-bold text-neutral-900 dark:text-white text-sm">3. Network Access</h3>
              <p>
                FileFlow binds its REST API strictly to <code>localhost</code> (127.0.0.1) for internal UI communication. It makes zero outbound requests to external servers.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              <h3 className="font-bold text-neutral-900 dark:text-white text-sm">1. Safe Automation & File Protection</h3>
              <p>
                FileFlow is designed with multiple safeguard mechanisms:
              </p>
              <ul className="list-disc pl-5 space-y-1.5">
                <li>
                  <strong>Safe Recycle Bin Defaults:</strong> When configured to delete files, FileFlow routes them through the native Windows Recycle Bin by default, allowing you to restore any file if needed.
                </li>
                <li>
                  <strong>Collision Prevention:</strong> Moves and copies default to automatic renaming with counter suffixes (e.g. <code>invoice (1).pdf</code>) to prevent accidental overwriting.
                </li>
                <li>
                  <strong>Loop Protection:</strong> State hashes ensure an action moving a file within a monitored folder will not trigger an infinite recursive execution loop.
                </li>
              </ul>

              <h3 className="font-bold text-neutral-900 dark:text-white text-sm">2. User Responsibility & Custom Scripts</h3>
              <p>
                If you configure rules with arbitrary shell commands (<code>Run Script</code>) or permanent deletion policies (bypassing the Recycle Bin), please verify your commands and test them using the built-in <strong>Simulator</strong> first to ensure expected results.
              </p>

              <h3 className="font-bold text-neutral-900 dark:text-white text-sm">3. Open Source License</h3>
              <p>
                FileFlow is provided free of charge under the MIT License, without warranty of any kind. You are free to inspect, modify, and distribute the source code.
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-neutral-200 dark:border-neutral-800 bg-neutral-50 dark:bg-neutral-950 flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-lg text-xs transition active:scale-95 shadow-sm"
          >
            I Understand & Close
          </button>
        </div>
      </div>
    </div>
  );
};
