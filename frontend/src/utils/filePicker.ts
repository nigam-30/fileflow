export async function openFolderPicker(): Promise<string> {
  // 1. If running inside PyWebView desktop app, use native pywebview bridge
  try {
    const pywebview = (window as any).pywebview;
    if (pywebview && pywebview.api && typeof pywebview.api.browse_folder === 'function') {
      const selected = await pywebview.api.browse_folder();
      if (selected) return selected;
      return '';
    }
  } catch (err) {
    console.warn('pywebview bridge error, falling back to HTTP API:', err);
  }

  // 2. Fallback to HTTP API
  try {
    const res = await fetch('/api/browse-folder', { method: 'POST' });
    if (res.ok) {
      const data = await res.json();
      return data.path || '';
    }
  } catch (err) {
    console.error('Failed to open folder picker:', err);
  }
  return '';
}

export async function openFilePicker(): Promise<string> {
  // 1. If running inside PyWebView desktop app, use native pywebview bridge
  try {
    const pywebview = (window as any).pywebview;
    if (pywebview && pywebview.api && typeof pywebview.api.browse_file === 'function') {
      const selected = await pywebview.api.browse_file();
      if (selected) return selected;
      return '';
    }
  } catch (err) {
    console.warn('pywebview bridge error, falling back to HTTP API:', err);
  }

  // 2. Fallback to HTTP API
  try {
    const res = await fetch('/api/browse-file', { method: 'POST' });
    if (res.ok) {
      const data = await res.json();
      return data.path || '';
    }
  } catch (err) {
    console.error('Failed to open file picker:', err);
  }
  return '';
}
