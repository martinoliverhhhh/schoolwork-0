import subprocess
import time
import ctypes
from ctypes import wintypes
import win32gui
import win32con

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

def force_foreground(hwnd):
    user32.ShowWindow(hwnd, 9)
    fore_hwnd = user32.GetForegroundWindow()
    fore_tid = user32.GetWindowThreadProcessId(fore_hwnd, None)
    stata_tid = user32.GetWindowThreadProcessId(hwnd, None)
    cur_tid = kernel32.GetCurrentThreadId()
    user32.AttachThreadInput(cur_tid, stata_tid, True)
    user32.AttachThreadInput(fore_tid, stata_tid, True)
    user32.SetForegroundWindow(hwnd)
    user32.SetFocus(hwnd)
    
    # Check focused window
    focus_hwnd = user32.GetFocus()
    cls_buf = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(focus_hwnd, cls_buf, 256)
    buf = ctypes.create_unicode_buffer(256)
    user32.GetWindowTextW(focus_hwnd, buf, 256)
    print(f"Focused HWND: {focus_hwnd}, class='{cls_buf.value}', title='{buf.value}'")
    
    user32.AttachThreadInput(cur_tid, stata_tid, False)
    user32.AttachThreadInput(fore_tid, stata_tid, False)

p = subprocess.Popen([r"C:\Users\12559\Desktop\stata182025.lnk"], shell=True)
time.sleep(4)

stata_hwnd = None
def enum_cb(hwnd, lparam):
    global stata_hwnd
    if user32.IsWindowVisible(hwnd):
        buf = ctypes.create_unicode_buffer(256)
        user32.GetWindowTextW(hwnd, buf, 256)
        if 'Stata/MP 18.0' in buf.value:
            stata_hwnd = hwnd
    return True

WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
user32.EnumWindows(WNDENUMPROC(enum_cb), 0)

if stata_hwnd:
    force_foreground(stata_hwnd)

subprocess.run(['taskkill', '/f', '/im', 'StataMP-64.exe'], capture_output=True)
