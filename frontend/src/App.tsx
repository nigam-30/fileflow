import React, { useState, useEffect } from 'react';
import { Rule, MonitoredFolder, AuditLogEntry } from './types';
import { Header } from './components/Header';
import { RuleCard } from './components/RuleCard';
import { RuleBuilderModal } from './components/RuleBuilderModal';
import { FolderManager } from './components/FolderManager';
import { DuplicateFinderView } from './components/DuplicateFinderView';
import { AuditLogView } from './components/AuditLogView';
import { RuleTester } from './components/RuleTester';
import { LegalModal } from './components/LegalModal';
import { Plus, Sliders, Folder, History, FlaskConical, Copy, ShieldCheck } from 'lucide-react';

export function App() {
  const [rules, setRules] = useState<Rule[]>([]);
  const [folders, setFolders] = useState<MonitoredFolder[]>([]);
  const [logs, setLogs] = useState<AuditLogEntry[]>([]);
  const [activeTab, setActiveTab] = useState<'rules' | 'folders' | 'duplicates' | 'logs' | 'tester'>('rules');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingRule, setEditingRule] = useState<Rule | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [isLegalOpen, setIsLegalOpen] = useState(false);
  const [legalTab, setLegalTab] = useState<'privacy' | 'terms'>('privacy');

  // Dark/Light Theme state with localStorage persistence (Default: Light Mode)
  const [darkMode, setDarkMode] = useState<boolean>(() => {
    const saved = localStorage.getItem('fileflow_theme');
    return saved ? saved === 'dark' : false;
  });

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('fileflow_theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('fileflow_theme', 'light');
    }
  }, [darkMode]);

  const toggleTheme = () => {
    setDarkMode(!darkMode);
  };

  // Fetch initial data
  const fetchData = async () => {
    try {
      const [rulesRes, foldersRes, logsRes] = await Promise.all([
        fetch('/api/rules'),
        fetch('/api/folders'),
        fetch('/api/logs?limit=50'),
      ]);
      if (rulesRes.ok) setRules(await rulesRes.json());
      if (foldersRes.ok) setFolders(await foldersRes.json());
      if (logsRes.ok) setLogs(await logsRes.json());
    } catch (err) {
      console.error('Failed to connect to FileFlow backend', err);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 4000);
    return () => clearInterval(interval);
  }, []);

  const handleToggleRule = async (id: string) => {
    try {
      const res = await fetch(`/api/rules/${id}/toggle`, { method: 'PATCH' });
      if (res.ok) {
        setRules(rules.map((r) => (r.id === id ? { ...r, enabled: !r.enabled } : r)));
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleDeleteRule = async (id: string) => {
    if (!confirm('Are you sure you want to delete this rule?')) return;
    try {
      const res = await fetch(`/api/rules/${id}`, { method: 'DELETE' });
      if (res.ok) {
        setRules(rules.filter((r) => r.id !== id));
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleSaveRule = async (rule: Rule) => {
    try {
      const res = await fetch('/api/rules', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(rule),
      });
      if (res.ok) {
        const saved = await res.json();
        setRules((prev) => {
          const idx = prev.findIndex((r) => r.id === saved.id);
          if (idx >= 0) {
            const next = [...prev];
            next[idx] = saved;
            return next;
          }
          return [...prev, saved];
        });
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleAddFolder = async (path: string, recursive: boolean) => {
    try {
      const res = await fetch('/api/folders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path, recursive }),
      });
      if (res.ok) {
        setFolders([...folders, { path, recursive }]);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleRemoveFolder = async (path: string) => {
    try {
      const res = await fetch(`/api/folders?path=${encodeURIComponent(path)}`, {
        method: 'DELETE',
      });
      if (res.ok) {
        setFolders(folders.filter((f) => f.path !== path));
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleScanNow = async () => {
    setIsScanning(true);
    try {
      await fetch('/api/scan', { method: 'POST' });
      await fetchData();
    } catch (err) {
      console.error(err);
    } finally {
      setIsScanning(false);
    }
  };

  return (
    <div className="min-h-screen bg-white dark:bg-black text-neutral-900 dark:text-neutral-100 flex flex-col transition-colors duration-200">
      <Header
        onScanNow={handleScanNow}
        isScanning={isScanning}
        foldersCount={folders.length}
        rulesCount={rules.length}
        darkMode={darkMode}
        onToggleTheme={toggleTheme}
        onOpenLegal={() => {
          setLegalTab('privacy');
          setIsLegalOpen(true);
        }}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">
        {/* Navigation Tabs & Actions */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex flex-wrap items-center space-x-1 bg-neutral-100 dark:bg-neutral-950 p-1 rounded-xl border border-neutral-200 dark:border-neutral-850">
            <button
              onClick={() => setActiveTab('rules')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-semibold transition ${
                activeTab === 'rules'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white'
              }`}
            >
              <Sliders className="w-4 h-4" />
              <span>Rules ({rules.length})</span>
            </button>
            <button
              onClick={() => setActiveTab('folders')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-semibold transition ${
                activeTab === 'folders'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white'
              }`}
            >
              <Folder className="w-4 h-4" />
              <span>Folders ({folders.length})</span>
            </button>
            <button
              onClick={() => setActiveTab('duplicates')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-semibold transition ${
                activeTab === 'duplicates'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white'
              }`}
            >
              <Copy className="w-4 h-4" />
              <span>Duplicates</span>
            </button>
            <button
              onClick={() => setActiveTab('logs')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-semibold transition ${
                activeTab === 'logs'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white'
              }`}
            >
              <History className="w-4 h-4" />
              <span>Activity Log ({logs.length})</span>
            </button>
            <button
              onClick={() => setActiveTab('tester')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-semibold transition ${
                activeTab === 'tester'
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white'
              }`}
            >
              <FlaskConical className="w-4 h-4" />
              <span>Simulator</span>
            </button>
          </div>

          {activeTab === 'rules' && (
            <button
              onClick={() => {
                setEditingRule(null);
                setIsModalOpen(true);
              }}
              className="flex items-center justify-center space-x-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-xl shadow-md shadow-blue-600/20 transition active:scale-95"
            >
              <Plus className="w-4 h-4" />
              <span>Create Rule</span>
            </button>
          )}
        </div>

        {/* Tab Content */}
        {activeTab === 'rules' && (
          <div className="space-y-4">
            {rules.length === 0 ? (
              <div className="p-12 text-center rounded-2xl border border-dashed border-neutral-300 dark:border-neutral-800 bg-neutral-50 dark:bg-neutral-950 space-y-3">
                <Sliders className="w-8 h-8 text-neutral-400 mx-auto" />
                <h3 className="text-sm font-semibold text-neutral-800 dark:text-neutral-200">No automation rules configured</h3>
                <p className="text-xs text-neutral-500 max-w-sm mx-auto">
                  Click 'Create Rule' to organize your downloads, invoices, documents, and photos automatically.
                </p>
                <button
                  onClick={() => setIsModalOpen(true)}
                  className="px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg shadow-sm transition"
                >
                  Create Your First Rule
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-4">
                {rules.map((rule) => (
                  <RuleCard
                    key={rule.id}
                    rule={rule}
                    onToggle={handleToggleRule}
                    onDelete={handleDeleteRule}
                    onEdit={(r) => {
                      setEditingRule(r);
                      setIsModalOpen(true);
                    }}
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'folders' && (
          <FolderManager
            folders={folders}
            onAddFolder={handleAddFolder}
            onRemoveFolder={handleRemoveFolder}
          />
        )}

        {activeTab === 'duplicates' && <DuplicateFinderView />}

        {activeTab === 'logs' && (
          <AuditLogView logs={logs} onRefresh={fetchData} />
        )}

        {activeTab === 'tester' && <RuleTester />}
      </main>

      {/* Transparent Footer */}
      <footer className="border-t border-neutral-200 dark:border-neutral-850 px-6 py-4 mt-auto">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between text-xs text-neutral-500 gap-2">
          <div>
            FileFlow • Free, Open-Source & 100% Offline Automation Engine
          </div>
          <div className="flex items-center space-x-4">
            <button
              onClick={() => {
                setLegalTab('privacy');
                setIsLegalOpen(true);
              }}
              className="hover:text-blue-600 dark:hover:text-blue-400 transition"
            >
              Privacy Policy
            </button>
            <span>•</span>
            <button
              onClick={() => {
                setLegalTab('terms');
                setIsLegalOpen(true);
              }}
              className="hover:text-blue-600 dark:hover:text-blue-400 transition"
            >
              User Agreement & Safety
            </button>
          </div>
        </div>
      </footer>

      <RuleBuilderModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleSaveRule}
        initialRule={editingRule}
      />

      <LegalModal
        isOpen={isLegalOpen}
        onClose={() => setIsLegalOpen(false)}
        initialTab={legalTab}
      />
    </div>
  );
}
export default App;
