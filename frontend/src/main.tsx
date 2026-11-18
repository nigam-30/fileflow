import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

// Extract session authentication token from desktop launch URL
const urlParams = new URLSearchParams(window.location.search);
const tokenFromUrl = urlParams.get('token');
if (tokenFromUrl) {
  sessionStorage.setItem('fileflow_token', tokenFromUrl);
  // Clean token parameter from address bar
  const cleanUrl = window.location.pathname + window.location.hash;
  window.history.replaceState({}, document.title, cleanUrl || '/');
}

// Global fetch interceptor: inject X-FileFlow-Token header on all API requests
const originalFetch = window.fetch;
window.fetch = async (input: RequestInfo | URL, init?: RequestInit) => {
  let token = sessionStorage.getItem('fileflow_token');
  if (!token) {
    try {
      const pywebview = (window as any).pywebview;
      if (pywebview && pywebview.api && typeof pywebview.api.get_api_token === 'function') {
        token = await pywebview.api.get_api_token();
        if (token) {
          sessionStorage.setItem('fileflow_token', token);
        }
      }
    } catch {
      // ignore
    }
  }

  const headers = new Headers(init?.headers || {});
  if (token && !headers.has('X-FileFlow-Token')) {
    headers.set('X-FileFlow-Token', token);
  }
  return originalFetch(input, { ...init, headers });
};

window.addEventListener('pywebviewready', async () => {
  try {
    const pywebview = (window as any).pywebview;
    if (pywebview?.api?.get_api_token) {
      const t = await pywebview.api.get_api_token();
      if (t) sessionStorage.setItem('fileflow_token', t);
    }
  } catch {
    // ignore
  }
});

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
