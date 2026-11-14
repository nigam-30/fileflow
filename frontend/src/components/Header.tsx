import React from 'react';
import { Layers, RefreshCw, Sun, Moon, ShieldCheck } from 'lucide-react';

interface HeaderProps {
  onScanNow: () => void;
  isScanning: boolean;
  foldersCount: number;
  rulesCount: number;
  darkMode: boolean;
  onToggleTheme: () => void;
  onOpenLegal: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  onScanNow,
  isScanning,
  foldersCount,
  rulesCount,
  darkMode,
  onToggleTheme,
  onOpenLegal,
}) => {
  return (
    <header className="border-b border-neutral-200 dark:border-neutral-800 bg-white/80 dark:bg-black/80 backdrop-blur sticky top-0 z-20 px-6 py-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <img src="/icon.png" alt="FileFlow Logo" className="w-10 h-10 object-contain drop-shadow" />
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-xl font-bold tracking-tight text-neutral-900 dark:text-white">FileFlow</h1>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/20 uppercase tracking-wider">
                100% Free & Local
              </span>
            </div>
            <p className="text-xs text-neutral-500 dark:text-neutral-400">Intelligent File Automation & Organization</p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <div className="hidden sm:flex items-center space-x-4 text-xs text-neutral-500 dark:text-neutral-400 border-r border-neutral-200 dark:border-neutral-800 pr-4">
            <div>
              <span className="font-semibold text-neutral-800 dark:text-neutral-200">{rulesCount}</span> Rules
            </div>
            <div>
              <span className="font-semibold text-neutral-800 dark:text-neutral-200">{foldersCount}</span> Folders
            </div>
          </div>

          {/* Privacy & Agreement Pill */}
          <button
            onClick={onOpenLegal}
            className="flex items-center space-x-1.5 px-3 py-1.5 text-xs font-medium text-neutral-600 dark:text-neutral-400 hover:text-blue-600 dark:hover:text-blue-400 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-900 transition"
            title="Privacy Policy & User Agreement"
          >
            <ShieldCheck className="w-4 h-4 text-blue-600 dark:text-blue-400" />
            <span className="hidden md:inline">Privacy & Terms</span>
          </button>

          {/* Theme Toggle */}
          <button
            onClick={onToggleTheme}
            className="p-2 text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white bg-neutral-100 dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-lg transition"
            title={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          >
            {darkMode ? <Sun className="w-4 h-4 text-amber-400" /> : <Moon className="w-4 h-4 text-neutral-600" />}
          </button>

          {/* Scan Now (Blue Button) */}
          <button
            onClick={onScanNow}
            disabled={isScanning}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg shadow-sm shadow-blue-600/20 transition active:scale-95 disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isScanning ? 'animate-spin' : ''}`} />
            <span>{isScanning ? 'Scanning...' : 'Scan Now'}</span>
          </button>
        </div>
      </div>
    </header>
  );
};
