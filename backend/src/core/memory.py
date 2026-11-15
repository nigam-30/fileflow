import os
import sys
import gc
import ctypes

def trim_memory():
    """
    Aggressively trims process working sets for FileFlow and all child processes (WebView2).
    Forces Python garbage collection and instructs the Windows Memory Manager to flush
    idle working set pages from physical RAM.
    """
    try:
        # Force Python garbage collection
        gc.collect()

        if sys.platform == 'win32':
            # 1. Trim current Python process
            try:
                ctypes.windll.psapi.EmptyWorkingSet(ctypes.windll.kernel32.GetCurrentProcess())
            except Exception:
                pass

            # 2. Trim all child processes (WebView2 Browser, Renderer, GPU, Utility)
            try:
                import psutil
                current_proc = psutil.Process()
                for child in current_proc.children(recursive=True):
                    try:
                        h_proc = ctypes.windll.kernel32.OpenProcess(0x1F0FFF, False, child.pid)
                        if h_proc:
                            ctypes.windll.psapi.EmptyWorkingSet(h_proc)
                            ctypes.windll.kernel32.CloseHandle(h_proc)
                    except Exception:
                        pass
            except Exception:
                pass
    except Exception as e:
        print(f"[MEMORY TRIM] Error: {e}")
