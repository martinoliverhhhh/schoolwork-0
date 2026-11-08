import subprocess
import time
import ctypes
from ctypes import wintypes

WM_GETTEXT = 0x000D
BM_CLICK = 0x00F5

p = subprocess.Popen([r"C:\Program Files\Stata18\StataMP-64.exe"])
time.sleep(3)
user32 = ctypes.windll.user32

btn_found = []
def enum_child(hwnd, lparam):
    cls_buf = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, cls_buf, 256)
    buf = ctypes.create_unicode_buffer(1024)
    user32.SendMessageW(hwnd, WM_GETTEXT, 1024, buf)
    if cls_buf.value == 'Button':
        print(f"Found Button {hwnd}: '{buf.value}'")
        btn_found.append(hwnd)
    return True

WNDENUMCHILDPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)

def enum_cb(hwnd, lparam):
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    if pid.value == p.pid:
        length = user32.GetWindowTextLengthW(hwnd)
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        is_vis = user32.IsWindowVisible(hwnd)
        if is_vis:
            print(f"Visible window HWND {hwnd}: title='{buf.value}'")
        if is_vis and buf.value == 'Stata':
            user32.EnumChildWindows(hwnd, WNDENUMCHILDPROC(enum_child), 0)
    return True

WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
user32.EnumWindows(WNDENUMPROC(enum_cb), 0)

if btn_found:
    print(f"Clicking button {btn_found[0]}...")
    user32.SendMessageW(btn_found[0], BM_CLICK, 0, 0)
    time.sleep(2)
    print("After click, checking windows...")
    user32.EnumWindows(WNDENUMPROC(enum_cb), 0)

time.sleep(1)
p.kill()
