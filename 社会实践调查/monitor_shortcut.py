import subprocess
import time
import ctypes
from ctypes import wintypes

WM_GETTEXT = 0x000D
user32 = ctypes.windll.user32

p = subprocess.Popen([r"C:\Users\12559\Desktop\stata182025.lnk"], shell=True)
print("Started shortcut...")

for i in range(30):
    time.sleep(0.5)
    # Check processes
    out = subprocess.check_output(['tasklist']).decode('gbk', errors='ignore')
    stata_lines = [l for l in out.splitlines() if 'stata' in l.lower()]
    if not stata_lines:
        print(f"[{i*0.5}s] No stata process")
        continue
    
    # Check all windows
    def enum_cb(hwnd, lparam):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            buf = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buf, length + 1)
            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            cls_buf = ctypes.create_unicode_buffer(256)
            user32.GetClassNameW(hwnd, cls_buf, 256)
            if 'stata' in buf.value.lower() or cls_buf.value == '#32770':
                print(f"[{i*0.5}s] HWND {hwnd}: pid={pid.value}, class='{cls_buf.value}', title='{buf.value}'")
        return True
    
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    user32.EnumWindows(WNDENUMPROC(enum_cb), 0)
