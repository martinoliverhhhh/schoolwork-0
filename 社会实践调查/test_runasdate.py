import subprocess
import time
import ctypes
from ctypes import wintypes

p = subprocess.Popen([
    r"D:\edge download\RunAsDate_V1.40_XiTongZhiJia\runasdate-x64\RunAsDate.exe",
    "/movetime", "01/01/2025 00:00:00",
    r"C:\Program Files\Stata18\StataMP-64.exe"
])

time.sleep(3)
user32 = ctypes.windll.user32
WM_GETTEXT = 0x000D

# List Stata processes
out = subprocess.check_output(['tasklist']).decode('gbk', errors='ignore')
for line in out.splitlines():
    if 'stata' in line.lower():
        print(line)

def enum_cb(hwnd, lparam):
    buf = ctypes.create_unicode_buffer(1024)
    user32.SendMessageW(hwnd, WM_GETTEXT, 1024, buf)
    is_vis = user32.IsWindowVisible(hwnd)
    if is_vis and 'Stata' in buf.value:
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        cls_buf = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, cls_buf, 256)
        print(f"HWND {hwnd}: pid={pid.value}, vis={is_vis}, class='{cls_buf.value}', title='{buf.value}'")
    return True

WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
user32.EnumWindows(WNDENUMPROC(enum_cb), 0)

subprocess.run(['taskkill', '/f', '/im', 'StataMP-64.exe'], capture_output=True)
