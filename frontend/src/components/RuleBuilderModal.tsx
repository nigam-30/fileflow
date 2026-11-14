import React, { useState, useEffect } from 'react';
import { Rule, Condition, Action, MatchMode, ConditionOperator, ActionType, CollisionPolicy } from '../types';
import { X, Plus, Trash2, FolderSearch, Sparkles, Folder } from 'lucide-react';
import { openFolderPicker } from '../utils/filePicker';

interface RuleBuilderModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (rule: Rule) => void;
  initialRule?: Rule | null;
}

const COMMON_FIELDS = [
  { value: 'file.extension', label: 'File Extension (e.g. pdf, jpg, txt)' },
  { value: 'file.name', label: 'File Name with extension' },
  { value: 'file.stem', label: 'File Name without extension' },
  { value: 'file.size_mb', label: 'File Size (MB)' },
  { value: 'file.created_year', label: 'Created Year (YYYY)' },
  { value: 'content.text', label: 'Document Content (Regex / Text)' },
  { value: 'pdf.title', label: 'PDF Document Title' },
  { value: 'pdf.author', label: 'PDF Author' },
  { value: 'image.camera_model', label: 'Image Camera Model' },
  { value: 'image.date_taken', label: 'Image Date Taken' }
];

const OPERATORS: { value: ConditionOperator; label: string }[] = [
  { value: 'equals', label: 'Equals' },
  { value: 'not_equals', label: 'Not Equals' },
  { value: 'contains', label: 'Contains' },
  { value: 'not_contains', label: 'Does Not Contain' },
  { value: 'starts_with', label: 'Starts With' },
  { value: 'ends_with', label: 'Ends With' },
  { value: 'greater_than', label: 'Greater Than (>)' },
  { value: 'less_than', label: 'Less Than (<)' },
  { value: 'matches_regex', label: 'Matches Regex (Captures Named Tokens)' },
];

const ACTION_TYPES: { value: ActionType; label: string }[] = [
  { value: 'move', label: 'Move File' },
  { value: 'copy', label: 'Copy File' },
  { value: 'rename', label: 'Rename File' },
  { value: 'recycle', label: 'Send to Recycle Bin' },
  { value: 'delete', label: 'Permanently Delete' },
  { value: 'zip', label: 'Compress to ZIP' },
  { value: 'run_command', label: 'Run Shell Command / Script' },
  { value: 'notify', label: 'Show Desktop Notification' },
];

export const RuleBuilderModal: React.FC<RuleBuilderModalProps> = ({
  isOpen,
  onClose,
  onSave,
  initialRule,
}) => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [monitoredFolders, setMonitoredFolders] = useState<string[]>([]);
  const [matchMode, setMatchMode] = useState<MatchMode>('all');
  const [conditions, setConditions] = useState<Condition[]>([]);
  const [actions, setActions] = useState<Action[]>([]);
  const [isBrowsingOrigin, setIsBrowsingOrigin] = useState<number | null>(null);
  const [isBrowsingDest, setIsBrowsingDest] = useState<number | null>(null);

  useEffect(() => {
    if (initialRule) {
      setName(initialRule.name);
      setDescription(initialRule.description || '');
      setMonitoredFolders(initialRule.monitored_folders || []);
      setMatchMode(initialRule.match_mode);
      setConditions(initialRule.conditions);
      setActions(initialRule.actions);
    } else {
      setName('New Automation Rule');
      setDescription('');
      setMonitoredFolders(['']);
      setMatchMode('all');
      setConditions([{ field: 'file.extension', operator: 'equals', value: 'pdf' }]);
      setActions([{ 
        type: 'move', 
        destination: 'D:/Documents/Organized/{file.created_year}/', 
        template: '{file.created_date}_{file.name}',
        collision_policy: 'rename_with_counter' 
      }]);
    }
  }, [initialRule, isOpen]);

  if (!isOpen) return null;

  const handleBrowseOrigin = async (index: number) => {
    setIsBrowsingOrigin(index);
    try {
      const selectedPath = await openFolderPicker();
      if (selectedPath) {
        const updated = [...monitoredFolders];
        if (index >= 0 && index < updated.length) {
          updated[index] = selectedPath;
        } else {
          updated.push(selectedPath);
        }
        setMonitoredFolders(updated);
      }
    } catch (err) {
      console.error('Failed to open native folder picker', err);
    } finally {
      setIsBrowsingOrigin(null);
    }
  };

  const handleAddOriginFolder = () => {
    setMonitoredFolders([...monitoredFolders, '']);
  };

  const handleRemoveOriginFolder = (index: number) => {
    setMonitoredFolders(monitoredFolders.filter((_, i) => i !== index));
  };

  const handleUpdateOriginFolder = (index: number, val: string) => {
    const updated = [...monitoredFolders];
    updated[index] = val;
    setMonitoredFolders(updated);
  };

  const handleBrowseDestination = async (index: number) => {
    setIsBrowsingDest(index);
    try {
      const selectedPath = await openFolderPicker();
      if (selectedPath) {
        const formatted = selectedPath.replace(/\\/g, '/') + '/';
        handleUpdateAction(index, 'destination', formatted);
      }
    } catch (err) {
      console.error('Failed to open native folder picker', err);
    } finally {
      setIsBrowsingDest(null);
    }
  };

  const handleAddCondition = () => {
    setConditions([...conditions, { field: 'file.extension', operator: 'equals', value: '' }]);
  };

  const handleRemoveCondition = (index: number) => {
    setConditions(conditions.filter((_, i) => i !== index));
  };

  const handleUpdateCondition = (index: number, key: keyof Condition, val: any) => {
    const updated = [...conditions];
    updated[index] = { ...updated[index], [key]: val };
    setConditions(updated);
  };

  const handleAddAction = () => {
    setActions([...actions, {
      type: 'move',
      destination: '',
      template: '',
      collision_policy: 'rename_with_counter'
    }]);
  };

  const handleRemoveAction = (index: number) => {
    setActions(actions.filter((_, i) => i !== index));
  };

  const handleUpdateAction = (index: number, key: keyof Action, val: any) => {
    const updated = [...actions];
    updated[index] = { ...updated[index], [key]: val };
    setActions(updated);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    const cleanFolders = monitoredFolders
      .map((f) => f.trim())
      .filter((f) => f.length > 0);

    const rule: Rule = {
      id: initialRule ? initialRule.id : crypto.randomUUID(),
      name,
      description,
      enabled: initialRule ? initialRule.enabled : true,
      monitored_folders: cleanFolders,
      match_mode: matchMode,
      conditions,
      actions,
      stop_processing_on_match: true,
    };
    onSave(rule);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
      <div className="bg-white dark:bg-black border border-neutral-200 dark:border-neutral-800 rounded-2xl w-full max-w-3xl max-h-[90vh] overflow-y-auto shadow-2xl flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-neutral-200 dark:border-neutral-800">
          <div>
            <h2 className="text-lg font-bold text-neutral-900 dark:text-white">
              {initialRule ? 'Edit Rule' : 'Create Automation Rule'}
            </h2>
            <p className="text-xs text-neutral-500 dark:text-neutral-400">Configure triggers, conditions, and file actions</p>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-neutral-400 hover:text-neutral-900 dark:hover:text-white rounded-lg transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6 flex-1">
          {/* Rule Meta */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="sm:col-span-2 space-y-1.5">
              <label className="text-xs font-semibold text-neutral-700 dark:text-neutral-300">Rule Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Move Invoices to Archive"
                className="w-full px-3 py-2 bg-neutral-50 dark:bg-neutral-950 border border-neutral-300 dark:border-neutral-800 rounded-lg text-neutral-900 dark:text-white text-sm focus:outline-none focus:border-blue-500"
                required
              />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-neutral-700 dark:text-neutral-300">Condition Logic</label>
              <select
                value={matchMode}
                onChange={(e) => setMatchMode(e.target.value as MatchMode)}
                className="w-full px-3 py-2 bg-neutral-50 dark:bg-neutral-950 border border-neutral-300 dark:border-neutral-800 rounded-lg text-neutral-900 dark:text-white text-sm focus:outline-none focus:border-blue-500"
              >
                <option value="all">Match ALL (AND)</option>
                <option value="any">Match ANY (OR)</option>
              </select>
            </div>
            <div className="sm:col-span-3 space-y-1.5">
              <label className="text-xs font-semibold text-neutral-700 dark:text-neutral-300">Description (Optional)</label>
              <input
                type="text"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Brief explanation of what this rule achieves"
                className="w-full px-3 py-2 bg-neutral-50 dark:bg-neutral-950 border border-neutral-300 dark:border-neutral-800 rounded-lg text-neutral-900 dark:text-white text-sm focus:outline-none focus:border-blue-500"
              />
            </div>
          </div>

          {/* Origin / Watched Folder Section */}
          <div className="space-y-3 pt-4 border-t border-neutral-200 dark:border-neutral-800">
            <div className="flex items-center justify-between">
              <div>
                <div className="flex items-center space-x-2">
                  <Folder className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                  <h3 className="text-sm font-bold text-neutral-900 dark:text-white">Origin / Watched Folder(s)</h3>
                </div>
                <p className="text-xs text-neutral-500 dark:text-neutral-400">
                  Folder(s) where FileFlow will watch and sort incoming files (e.g. Downloads, Desktop)
                </p>
              </div>
              <button
                type="button"
                onClick={handleAddOriginFolder}
                className="flex items-center space-x-1.5 text-xs text-blue-600 dark:text-blue-400 hover:underline font-semibold"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Add Watched Folder</span>
              </button>
            </div>

            {monitoredFolders.length === 0 ? (
              <div className="p-3 bg-neutral-50 dark:bg-neutral-950 rounded-lg border border-neutral-200 dark:border-neutral-800 flex items-center justify-between">
                <span className="text-xs text-neutral-500 italic">No specific folder selected. This rule will apply to all globally monitored folders.</span>
                <div className="flex items-center space-x-2">
                  <button
                    type="button"
                    disabled={isBrowsingOrigin === -1}
                    onClick={() => handleBrowseOrigin(-1)}
                    className="flex items-center space-x-1.5 px-3 py-1 bg-blue-600 hover:bg-blue-500 disabled:opacity-60 text-white rounded text-xs font-semibold shadow-sm transition"
                  >
                    <FolderSearch className="w-3.5 h-3.5" />
                    <span>{isBrowsingOrigin === -1 ? 'Opening...' : 'Browse Folder...'}</span>
                  </button>
                  <button
                    type="button"
                    onClick={handleAddOriginFolder}
                    className="text-xs text-blue-600 dark:text-blue-400 font-semibold hover:underline"
                  >
                    + Enter path
                  </button>
                </div>
              </div>
            ) : (
              <div className="space-y-2">
                {monitoredFolders.map((folderPath, idx) => (
                  <div key={idx} className="flex items-center space-x-2 bg-neutral-50 dark:bg-neutral-950 p-2.5 rounded-lg border border-neutral-200 dark:border-neutral-800">
                    <input
                      type="text"
                      value={folderPath}
                      onChange={(e) => handleUpdateOriginFolder(idx, e.target.value)}
                      placeholder="e.g. C:\Users\LENOVO\Downloads"
                      className="flex-1 px-2.5 py-1.5 bg-white dark:bg-black border border-neutral-300 dark:border-neutral-800 rounded-md text-xs text-neutral-800 dark:text-neutral-200 focus:outline-none focus:border-blue-500 font-mono"
                    />
                    <button
                      type="button"
                      disabled={isBrowsingOrigin === idx}
                      onClick={() => handleBrowseOrigin(idx)}
                      className="flex items-center space-x-1.5 px-3 py-1.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-60 text-white rounded-md text-xs font-medium transition shadow-sm"
                      title="Browse origin folder using native Windows picker"
                    >
                      <FolderSearch className="w-3.5 h-3.5" />
                      <span>{isBrowsingOrigin === idx ? 'Opening...' : 'Browse Origin...'}</span>
                    </button>
                    <button
                      type="button"
                      onClick={() => handleRemoveOriginFolder(idx)}
                      className="p-1.5 text-neutral-400 hover:text-rose-500 transition"
                      title="Remove folder"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Conditions Section */}
          <div className="space-y-3 pt-4 border-t border-neutral-200 dark:border-neutral-800">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-neutral-900 dark:text-white">Conditions</h3>
              <button
                type="button"
                onClick={handleAddCondition}
                className="flex items-center space-x-1.5 text-xs text-blue-600 dark:text-blue-400 hover:underline font-semibold"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Add Condition</span>
              </button>
            </div>

            <div className="space-y-2">
              {conditions.map((cond, idx) => (
                <div key={idx} className="flex items-center space-x-2 bg-neutral-50 dark:bg-neutral-950 p-2.5 rounded-lg border border-neutral-200 dark:border-neutral-800">
                  <select
                    value={cond.field}
                    onChange={(e) => handleUpdateCondition(idx, 'field', e.target.value)}
                    className="flex-1 px-2.5 py-1.5 bg-white dark:bg-black border border-neutral-300 dark:border-neutral-800 rounded-md text-xs text-neutral-800 dark:text-neutral-200"
                  >
                    {COMMON_FIELDS.map((f) => (
                      <option key={f.value} value={f.value}>{f.label}</option>
                    ))}
                  </select>

                  <select
                    value={cond.operator}
                    onChange={(e) => handleUpdateCondition(idx, 'operator', e.target.value)}
                    className="w-36 px-2.5 py-1.5 bg-white dark:bg-black border border-neutral-300 dark:border-neutral-800 rounded-md text-xs text-neutral-800 dark:text-neutral-200"
                  >
                    {OPERATORS.map((op) => (
                      <option key={op.value} value={op.value}>{op.label}</option>
                    ))}
                  </select>

                  <input
                    type="text"
                    value={cond.value}
                    onChange={(e) => handleUpdateCondition(idx, 'value', e.target.value)}
                    placeholder="Value (e.g. pdf, invoice)"
                    className="flex-1 px-2.5 py-1.5 bg-white dark:bg-black border border-neutral-300 dark:border-neutral-800 rounded-md text-xs text-neutral-800 dark:text-neutral-200 focus:outline-none focus:border-blue-500"
                  />

                  <button
                    type="button"
                    onClick={() => handleRemoveCondition(idx)}
                    className="p-1.5 text-neutral-400 hover:text-rose-600 rounded transition"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Actions Section */}
          <div className="space-y-3 pt-4 border-t border-neutral-200 dark:border-neutral-800">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-neutral-900 dark:text-white">Actions</h3>
              <button
                type="button"
                onClick={handleAddAction}
                className="flex items-center space-x-1.5 text-xs text-emerald-600 dark:text-emerald-400 hover:underline font-semibold"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>Add Action</span>
              </button>
            </div>

            <div className="space-y-3">
              {actions.map((act, idx) => (
                <div key={idx} className="bg-neutral-50 dark:bg-neutral-950 p-3 rounded-lg border border-neutral-200 dark:border-neutral-800 space-y-2.5">
                  <div className="flex items-center justify-between">
                    <select
                      value={act.type}
                      onChange={(e) => handleUpdateAction(idx, 'type', e.target.value)}
                      className="px-2.5 py-1.5 bg-white dark:bg-black border border-neutral-300 dark:border-neutral-800 rounded-md text-xs text-blue-600 dark:text-blue-400 font-semibold"
                    >
                      {ACTION_TYPES.map((a) => (
                        <option key={a.value} value={a.value}>{a.label}</option>
                      ))}
                    </select>

                    <button
                      type="button"
                      onClick={() => handleRemoveAction(idx)}
                      className="p-1 text-neutral-400 hover:text-rose-600 rounded transition"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>

                  {(act.type === 'move' || act.type === 'copy' || act.type === 'zip') && (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      <div className="relative">
                        <label className="text-[11px] text-neutral-500 font-medium">Destination Folder</label>
                        <div className="flex gap-1">
                          <input
                            type="text"
                            value={act.destination || ''}
                            onChange={(e) => handleUpdateAction(idx, 'destination', e.target.value)}
                            placeholder="e.g. D:/Sorted/{file.created_year}/"
                            className="flex-1 px-2.5 py-1.5 bg-white dark:bg-black border border-neutral-300 dark:border-neutral-800 rounded-md text-xs text-neutral-800 dark:text-neutral-200"
                          />
                          <button
                            type="button"
                            disabled={isBrowsingDest === idx}
                            onClick={() => handleBrowseDestination(idx)}
                            className="flex items-center space-x-1 px-3 py-1.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-60 text-white rounded text-xs font-medium transition shadow-sm"
                            title="Browse destination folder"
                          >
                            <FolderSearch className="w-3.5 h-3.5" />
                            <span>{isBrowsingDest === idx ? 'Opening...' : 'Browse...'}</span>
                          </button>
                        </div>
                      </div>
                      <div>
                        <label className="text-[11px] text-neutral-500 font-medium">Rename Template (Optional)</label>
                        <input
                          type="text"
                          value={act.template || ''}
                          onChange={(e) => handleUpdateAction(idx, 'template', e.target.value)}
                          placeholder="e.g. {file.created_date}_{file.name}"
                          className="w-full px-2.5 py-1.5 bg-white dark:bg-black border border-neutral-300 dark:border-neutral-800 rounded-md text-xs text-neutral-800 dark:text-neutral-200"
                        />
                      </div>
                    </div>
                  )}

                  {act.type === 'rename' && (
                    <div>
                      <label className="text-[11px] text-neutral-500 font-medium">New Name Template</label>
                      <input
                        type="text"
                        value={act.template || ''}
                        onChange={(e) => handleUpdateAction(idx, 'template', e.target.value)}
                        placeholder="e.g. {file.created_date}_{file.stem}"
                        className="w-full px-2.5 py-1.5 bg-white dark:bg-black border border-neutral-300 dark:border-neutral-800 rounded-md text-xs text-neutral-800 dark:text-neutral-200"
                      />
                    </div>
                  )}

                  {act.type === 'run_command' && (
                    <div>
                      <label className="text-[11px] text-neutral-500 font-medium">Command String</label>
                      <input
                        type="text"
                        value={act.command || ''}
                        onChange={(e) => handleUpdateAction(idx, 'command', e.target.value)}
                        placeholder="e.g. python process.py {file.path}"
                        className="w-full px-2.5 py-1.5 bg-white dark:bg-black border border-neutral-300 dark:border-neutral-800 rounded-md text-xs text-neutral-800 dark:text-neutral-200"
                      />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Tokens Hint */}
          <div className="p-3 bg-blue-500/10 border border-blue-500/20 rounded-xl text-xs text-blue-800 dark:text-blue-300 flex items-start space-x-2">
            <Sparkles className="w-4 h-4 text-blue-600 dark:text-blue-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-semibold">Dynamic Tokens:</span>{' '}
              <code>{"{file.name}"}</code>, <code>{"{file.stem}"}</code>, <code>{"{file.extension}"}</code>, <code>{"{file.created_date}"}</code>, <code>{"{file.created_year}"}</code>, plus any regex capture group names!
            </div>
          </div>

          {/* Footer Actions */}
          <div className="flex items-center justify-end space-x-3 pt-4 border-t border-neutral-200 dark:border-neutral-800">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 bg-neutral-200 dark:bg-neutral-800 hover:bg-neutral-300 dark:hover:bg-neutral-700 text-neutral-800 dark:text-neutral-300 text-xs font-semibold rounded-lg transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg shadow-md transition active:scale-95"
            >
              Save Rule
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
