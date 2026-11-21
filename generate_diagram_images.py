import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options

# ==============================================================================
# 1. WHITE & BLUE ARCHITECTURE DIAGRAM HTML
# ==============================================================================
ARCHITECTURE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }
  body {
    background: #F1F5F9;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    color: #0F172A;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 30px;
    width: fit-content;
    height: fit-content;
  }

  /* Grid & Subtle Blue Ambient Radiance */
  .diagram-wrapper {
    position: relative;
    width: 1640px;
    height: 980px;
    background: #F8FAFC;
    background-image: 
      linear-gradient(to right, rgba(37, 99, 235, 0.04) 1px, transparent 1px),
      linear-gradient(to bottom, rgba(37, 99, 235, 0.04) 1px, transparent 1px);
    background-size: 32px 32px;
    border: 2px solid #BFDBFE;
    border-radius: 24px;
    padding: 36px 44px;
    box-shadow: 0 25px 50px -12px rgba(30, 58, 138, 0.12), 0 0 0 1px rgba(255, 255, 255, 0.8) inset;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    overflow: hidden;
  }

  /* Ambient soft blue lights */
  .glow-blue {
    position: absolute;
    top: -100px;
    right: 150px;
    width: 500px;
    height: 500px;
    background: radial-gradient(circle, rgba(59, 130, 246, 0.12) 0%, rgba(59, 130, 246, 0) 70%);
    pointer-events: none;
  }
  .glow-indigo {
    position: absolute;
    bottom: -120px;
    left: 100px;
    width: 550px;
    height: 550px;
    background: radial-gradient(circle, rgba(99, 102, 241, 0.10) 0%, rgba(99, 102, 241, 0) 70%);
    pointer-events: none;
  }

  /* Header */
  .header {
    position: relative;
    z-index: 2;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 2px solid #E2E8F0;
    padding-bottom: 22px;
  }
  .header-left {
    display: flex;
    align-items: center;
    gap: 18px;
  }
  .logo-box {
    width: 54px;
    height: 54px;
    background: linear-gradient(135deg, #1D4ED8, #3B82F6);
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 8px 18px rgba(37, 99, 235, 0.35);
  }
  .title-group h1 {
    font-size: 28px;
    font-weight: 800;
    letter-spacing: -0.5px;
    color: #0F172A;
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .title-group h1 span.blue-text {
    color: #2563EB;
  }
  .title-group p {
    font-size: 14px;
    color: #64748B;
    margin-top: 3px;
    font-weight: 500;
  }
  .header-badges {
    display: flex;
    gap: 10px;
  }
  .badge {
    padding: 7px 15px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.3px;
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .badge-blue { background: #EFF6FF; border: 1.5px solid #BFDBFE; color: #1D4ED8; }
  .badge-emerald { background: #ECFDF5; border: 1.5px solid #A7F3D0; color: #047857; }
  .badge-indigo { background: #EEF2FF; border: 1.5px solid #C7D2FE; color: #4338CA; }
  .badge-amber { background: #FFFBEB; border: 1.5px solid #FDE68A; color: #B45309; }

  /* Section Title */
  .section-label {
    font-size: 12px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: #2563EB;
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
  }

  /* Pipeline Row */
  .pipeline-row {
    position: relative;
    z-index: 2;
    display: grid;
    grid-template-columns: 248px 44px 248px 44px 274px 44px 274px 44px 254px;
    align-items: center;
    margin: 14px 0 20px 0;
  }

  /* Cards in White Theme */
  .card {
    background: #FFFFFF;
    border-radius: 16px;
    padding: 18px 20px;
    box-shadow: 0 4px 14px rgba(15, 23, 42, 0.05), 0 1px 3px rgba(0, 0, 0, 0.04);
    border: 1.5px solid #E2E8F0;
    position: relative;
  }
  .card-blue {
    border-color: #93C5FD;
    box-shadow: 0 6px 18px rgba(37, 99, 235, 0.09);
  }
  .card-amber {
    border-color: #FCD34D;
    box-shadow: 0 6px 18px rgba(245, 158, 11, 0.09);
  }
  .card-indigo {
    border-color: #C7D2FE;
    box-shadow: 0 6px 18px rgba(99, 102, 241, 0.09);
  }
  .card-emerald {
    border-color: #6EE7B7;
    box-shadow: 0 6px 18px rgba(16, 185, 129, 0.09);
  }
  .card-rose {
    border-color: #FDA4AF;
    box-shadow: 0 6px 18px rgba(244, 63, 94, 0.09);
  }

  .card-title {
    font-size: 15px;
    font-weight: 800;
    color: #0F172A;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .card-sub {
    font-size: 11px;
    font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
    font-weight: 600;
    color: #475569;
    margin-bottom: 10px;
    background: #F1F5F9;
    padding: 3px 7px;
    border-radius: 6px;
    display: inline-block;
  }
  .card-list {
    list-style: none;
    font-size: 12px;
    color: #334155;
    display: flex;
    flex-direction: column;
    gap: 6px;
    font-weight: 500;
  }
  .card-list li {
    display: flex;
    align-items: center;
    gap: 7px;
  }
  .dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
  }

  /* Connectors */
  .arrow-connector {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 4px;
  }
  .arrow-line {
    width: 36px;
    height: 2px;
    background: #2563EB;
    position: relative;
  }
  .arrow-line::after {
    content: '';
    position: absolute;
    right: 0;
    top: -4px;
    width: 0;
    height: 0;
    border-top: 5px solid transparent;
    border-bottom: 5px solid transparent;
    border-left: 7px solid #2563EB;
  }
  .arrow-tag {
    font-size: 10px;
    font-family: ui-monospace, monospace;
    font-weight: 700;
    color: #2563EB;
    background: #DBEAFE;
    padding: 2px 5px;
    border-radius: 4px;
    white-space: nowrap;
  }

  /* Bottom Row Subsystems */
  .bottom-row {
    position: relative;
    z-index: 2;
    display: grid;
    grid-template-columns: 480px 500px 520px;
    gap: 24px;
  }
  .sub-box {
    background: #FFFFFF;
    border: 1.5px solid #E2E8F0;
    border-radius: 18px;
    padding: 20px 24px;
    box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04);
  }

  /* Deduplication Steps */
  .dedup-steps {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-top: 8px;
  }
  .dedup-step {
    background: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 9px 12px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 12px;
    font-weight: 600;
    color: #1E293B;
  }
  .step-badge {
    background: #2563EB;
    color: #FFFFFF;
    font-weight: 800;
    font-size: 10px;
    padding: 2px 7px;
    border-radius: 999px;
    margin-right: 6px;
  }

  /* Footer */
  .footer {
    position: relative;
    z-index: 2;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-top: 2px solid #E2E8F0;
    padding-top: 14px;
    font-size: 12px;
    font-weight: 600;
    color: #64748B;
  }
  .footer-right {
    display: flex;
    gap: 20px;
    color: #2563EB;
  }
</style>
</head>
<body>

<div class="diagram-wrapper" id="diagram-container">
  <div class="glow-blue"></div>
  <div class="glow-indigo"></div>

  <!-- Header -->
  <div class="header">
    <div class="header-left">
      <div class="logo-box">
        <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
          <path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z"></path>
          <path d="M8 13h8"></path>
          <path d="M12 9v8"></path>
        </svg>
      </div>
      <div class="title-group">
        <h1>FileFlow <span class="blue-text">System Architecture & Reactive Workflow</span></h1>
        <p>100% Offline Local Daemon • Decoupled Desktop Monolith • Edge WebView2 Loopback IPC</p>
      </div>
    </div>
    <div class="header-badges">
      <span class="badge badge-blue">🪟 Win32 Native</span>
      <span class="badge badge-emerald">🔒 Zero Telemetry</span>
      <span class="badge badge-indigo">🔍 4-Stage Deduplication</span>
      <span class="badge badge-amber">⚡ 20–35 MB Idle RAM</span>
    </div>
  </div>

  <!-- Real-time Pipeline -->
  <div>
    <div class="section-label">
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"></path></svg>
      Primary Event-Driven Organization Pipeline
    </div>

    <div class="pipeline-row">
      <!-- 1: Watcher -->
      <div class="card card-blue">
        <div class="card-title"><span style="color:#2563EB;">1.</span> Directory Watcher</div>
        <div class="card-sub">watchdog + Win32 API</div>
        <ul class="card-list">
          <li><span class="dot" style="background:#2563EB;"></span>ReadDirectoryChangesW</li>
          <li><span class="dot" style="background:#2563EB;"></span>Non-blocking OS thread</li>
          <li><span class="dot" style="background:#2563EB;"></span>Created & Moved events</li>
        </ul>
      </div>

      <div class="arrow-connector">
        <div class="arrow-line"></div>
        <span class="arrow-tag">fs_event</span>
      </div>

      <!-- 2: Debouncer -->
      <div class="card card-amber">
        <div class="card-title"><span style="color:#D97706;">2.</span> Debounce & Locks</div>
        <div class="card-sub">Quiescence Coordinator</div>
        <ul class="card-list">
          <li><span class="dot" style="background:#D97706;"></span>1000ms sliding buffer</li>
          <li><span class="dot" style="background:#D97706;"></span>5-phase handle polling</li>
          <li><span class="dot" style="background:#D97706;"></span>Zero sharing violations</li>
        </ul>
      </div>

      <div class="arrow-connector">
        <div class="arrow-line"></div>
        <span class="arrow-tag">quiescent</span>
      </div>

      <!-- 3: Extractors -->
      <div class="card card-indigo">
        <div class="card-title"><span style="color:#4F46E5;">3.</span> Multimodal Extract</div>
        <div class="card-sub">Deep Metadata Inspection</div>
        <ul class="card-list">
          <li><span class="dot" style="background:#4F46E5;"></span>System: stem, size, dates</li>
          <li><span class="dot" style="background:#4F46E5;"></span>pypdf: text, author, title</li>
          <li><span class="dot" style="background:#4F46E5;"></span>Pillow: EXIF, camera, ISO</li>
        </ul>
      </div>

      <div class="arrow-connector">
        <div class="arrow-line"></div>
        <span class="arrow-tag">var_dict</span>
      </div>

      <!-- 4: Rule Engine -->
      <div class="card card-emerald">
        <div class="card-title"><span style="color:#059669;">4.</span> Rule Engine</div>
        <div class="card-sub">Condition Evaluator</div>
        <ul class="card-list">
          <li><span class="dot" style="background:#059669;"></span>Compound ALL / ANY logic</li>
          <li><span class="dot" style="background:#059669;"></span>Regex named group tokens</li>
          <li><span class="dot" style="background:#059669;"></span>Loop prevention guard</li>
        </ul>
      </div>

      <div class="arrow-connector">
        <div class="arrow-line"></div>
        <span class="arrow-tag">actions</span>
      </div>

      <!-- 5: Action Dispatcher -->
      <div class="card card-rose">
        <div class="card-title"><span style="color:#E11D48;">5.</span> Action Dispatcher</div>
        <div class="card-sub">Safe Filesystem Execution</div>
        <ul class="card-list">
          <li><span class="dot" style="background:#E11D48;"></span>Template: {created_year}</li>
          <li><span class="dot" style="background:#E11D48;"></span>Collision: Counter / Skip</li>
          <li><span class="dot" style="background:#E11D48;"></span>Recycle Bin: send2trash</li>
        </ul>
      </div>
    </div>
  </div>

  <!-- Bottom Row Subsystems -->
  <div class="bottom-row">
    <!-- UI & Shell -->
    <div class="sub-box">
      <div class="section-label">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line></svg>
        Presentation & Shell Layer
      </div>
      <div class="card card-blue" style="margin-top:8px;">
        <div class="card-title">Desktop Hybrid Shell</div>
        <div class="card-sub">React 18 + Edge WebView2 + Win32</div>
        <ul class="card-list">
          <li><span class="dot" style="background:#2563EB;"></span><strong>Single-Instance Guard:</strong> Named Win32 Mutex</li>
          <li><span class="dot" style="background:#2563EB;"></span><strong>Folder Picker:</strong> Win32 ctypes integration</li>
          <li><span class="dot" style="background:#2563EB;"></span><strong>IPC Security:</strong> 32-byte secret X-API-Token</li>
          <li><span class="dot" style="background:#2563EB;"></span><strong>Memory Trimmer:</strong> psapi.dll EmptyWorkingSet</li>
        </ul>
      </div>
    </div>

    <!-- Persistence -->
    <div class="sub-box">
      <div class="section-label" style="color: #4F46E5;">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path></svg>
        Persistence & Database Layer
      </div>
      <div class="card card-indigo" style="margin-top:8px;">
        <div class="card-title">Embedded SQLite 3 (WAL Mode)</div>
        <div class="card-sub">%APPDATA%/FileFlowData/fileflow.db</div>
        <ul class="card-list">
          <li><span class="dot" style="background:#4F46E5;"></span><strong>rules:</strong> JSON tree, match modes, origins</li>
          <li><span class="dot" style="background:#4F46E5;"></span><strong>monitored_folders:</strong> Active watch registrations</li>
          <li><span class="dot" style="background:#4F46E5;"></span><strong>processed_files:</strong> Mtime & hash cycle immunity</li>
          <li><span class="dot" style="background:#4F46E5;"></span><strong>audit_logs:</strong> History with 12h auto-pruning</li>
        </ul>
      </div>
    </div>

    <!-- Deduplication -->
    <div class="sub-box">
      <div class="section-label" style="color: #059669;">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path></svg>
        Progressive 4-Stage Deduplication
      </div>
      <div class="dedup-steps">
        <div class="dedup-step">
          <span><span class="step-badge">S1</span> <strong>Exact File Size Bucketing</strong></span>
          <span style="color:#64748B; font-family: monospace;">Prunes 95%+</span>
        </div>
        <div class="dedup-step">
          <span><span class="step-badge">S2</span> <strong>Head + Tail 8KB Dual Hash</strong></span>
          <span style="color:#64748B; font-family: monospace;">16-thread pool</span>
        </div>
        <div class="dedup-step">
          <span><span class="step-badge">S3</span> <strong>Full Parallel SHA-256</strong></span>
          <span style="color:#64748B; font-family: monospace;">256KB stream</span>
        </div>
        <div class="dedup-step">
          <span><span class="step-badge">S4</span> <strong>Bit-for-Bit Binary Validation</strong></span>
          <span style="color:#059669; font-weight: 700;">Zero collision</span>
        </div>
      </div>
    </div>
  </div>

  <!-- Footer -->
  <div class="footer">
    <div>FileFlow Desktop Architecture • Engineered for Windows 10 & 11 (64-bit)</div>
    <div class="footer-right">
      <span>Latency: &lt;50ms</span>
      <span>Throughput: 50,000 files / 30s</span>
      <span>Safety: Windows Recycle Bin</span>
    </div>
  </div>
</div>

</body>
</html>
"""

# ==============================================================================
# 2. WHITE & BLUE HERO BANNER HTML (EXPANDED TO PREVENT ANY CLIPPING)
# ==============================================================================
BANNER_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }
  body {
    background: #E2E8F0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 30px;
    width: fit-content;
    height: fit-content;
  }
  .banner-wrapper {
    position: relative;
    width: 1280px;
    height: 540px;
    background: #FFFFFF;
    background-image: 
      linear-gradient(to right, rgba(37, 99, 235, 0.05) 1px, transparent 1px),
      linear-gradient(to bottom, rgba(37, 99, 235, 0.05) 1px, transparent 1px);
    background-size: 30px 30px;
    border: 2px solid #BFDBFE;
    border-radius: 28px;
    box-shadow: 0 20px 45px -10px rgba(37, 99, 235, 0.16), 0 0 0 1px rgba(255, 255, 255, 0.8) inset;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 36px 48px;
    text-align: center;
    overflow: hidden;
  }

  /* Radial soft blue glow */
  .glow-center {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 700px;
    height: 700px;
    background: radial-gradient(circle, rgba(37, 99, 235, 0.09) 0%, rgba(37, 99, 235, 0) 70%);
    pointer-events: none;
  }

  .logo-box {
    position: relative;
    z-index: 2;
    width: 96px;
    height: 96px;
    background: linear-gradient(135deg, #1D4ED8, #3B82F6);
    border-radius: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 12px 28px rgba(37, 99, 235, 0.35);
    margin-bottom: 22px;
  }
  .title {
    position: relative;
    z-index: 2;
    font-size: 56px;
    font-weight: 900;
    letter-spacing: -1.2px;
    color: #0F172A;
    margin-bottom: 10px;
  }
  .title span.blue-highlight {
    color: #2563EB;
  }
  .tagline {
    position: relative;
    z-index: 2;
    font-size: 20px;
    color: #475569;
    margin-bottom: 34px;
    font-weight: 500;
    max-width: 800px;
  }
  .features-pills {
    position: relative;
    z-index: 2;
    display: flex;
    gap: 14px;
    flex-wrap: wrap;
    justify-content: center;
  }
  .pill {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 20px;
    background: #F8FAFC;
    border: 1.5px solid #CBD5E1;
    border-radius: 999px;
    font-size: 14px;
    font-weight: 700;
    color: #1E293B;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
  }
  .pill-blue {
    border-color: #BFDBFE;
    background: #EFF6FF;
    color: #1D4ED8;
  }
  .pill-emerald {
    border-color: #A7F3D0;
    background: #ECFDF5;
    color: #047857;
  }
  .pill-indigo {
    border-color: #C7D2FE;
    background: #EEF2FF;
    color: #4338CA;
  }
  .pill-sky {
    border-color: #BAE6FD;
    background: #F0F9FF;
    color: #0369A1;
  }
</style>
</head>
<body>

<div class="banner-wrapper" id="banner-container">
  <div class="glow-center"></div>

  <div class="logo-box">
    <svg width="54" height="54" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round">
      <path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13c0 1.1.9 2 2 2Z"></path>
      <path d="M8 13h8"></path>
      <path d="M12 9v8"></path>
    </svg>
  </div>
  <h1 class="title">FILE<span class="blue-highlight">FLOW</span></h1>
  <p class="tagline">Intelligent Local File Automation & Deduplication for Windows</p>

  <div class="features-pills">
    <div class="pill pill-blue"><span>⚡</span> Real-Time Watcher</div>
    <div class="pill pill-emerald"><span>🔒</span> 100% Offline & Private</div>
    <div class="pill pill-indigo"><span>🔍</span> 4-Stage Deduplication</div>
    <div class="pill pill-sky"><span>🪟</span> Native Win32 Shell</div>
    <div class="pill pill-blue"><span>🚀</span> 20–35 MB Idle RAM</div>
  </div>
</div>

</body>
</html>
"""

def render_element_to_png(html_content: str, output_path: str, container_id: str, win_width: int, win_height: int):
    temp_html = output_path.replace(".png", "_temp.html")
    with open(temp_html, "w", encoding="utf-8") as f:
        f.write(html_content)

    options = Options()
    options.add_argument('--headless=new')
    options.add_argument(f'--window-size={win_width},{win_height}')
    options.add_argument('--hide-scrollbars')
    options.add_argument('--force-device-scale-factor=2')
    options.add_argument('--disable-gpu')

    driver = webdriver.Edge(options=options)
    try:
        driver.get(f"file:///{os.path.abspath(temp_html).replace(os.sep, '/')}")
        time.sleep(1.0)
        # Find exact container element to guarantee 0 clipping!
        element = driver.find_element(By.ID, container_id)
        element.screenshot(output_path)
        print(f"Successfully rendered: {output_path} (Target: #{container_id})")
    finally:
        driver.quit()
        if os.path.exists(temp_html):
            os.remove(temp_html)

if __name__ == "__main__":
    assets_dir = r"d:\File Juggler 3\assets"
    fileflow_assets_dir = r"d:\File Juggler 3\fileflow\assets"
    os.makedirs(assets_dir, exist_ok=True)
    os.makedirs(fileflow_assets_dir, exist_ok=True)

    # 1. Architecture Workflow Image
    arch_out_1 = os.path.join(assets_dir, "architecture_workflow.png")
    arch_out_2 = os.path.join(fileflow_assets_dir, "architecture_workflow.png")
    print("Rendering White & Blue Architecture Diagram...")
    render_element_to_png(ARCHITECTURE_HTML, arch_out_1, "diagram-container", 1800, 1150)
    
    # 2. Hero Banner Image (Larger viewport so nothing is cut)
    banner_out_1 = os.path.join(assets_dir, "banner.png")
    banner_out_2 = os.path.join(fileflow_assets_dir, "banner.png")
    print("Rendering White & Blue Banner Graphic...")
    render_element_to_png(BANNER_HTML, banner_out_1, "banner-container", 1450, 750)

    # Copy to fileflow assets
    import shutil
    shutil.copyfile(arch_out_1, arch_out_2)
    shutil.copyfile(banner_out_1, banner_out_2)
    print("All White & Blue diagrams rendered with zero clipping!")
