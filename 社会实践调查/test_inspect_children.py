import subprocess
import time
import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32
WM_GETTEXT = 0x000D

p = subprocess.Popen([r"C:\Users\12559\Desktop\stata182025.lnk"], shell=True)
time.sleep(3)

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

print(f"Stata HWND: {stata_hwnd}")

class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long),
                ("top", ctypes.c_long),
                ("right", ctypes.c_long),
                ("bottom", ctypes.c_long)]

if stata_hwnd:
    def child_cb(hwnd, lparam):
        cls_buf = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, cls_buf, 256)
        rc = RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rc))
        is_vis = user32.IsWindowVisible(hwnd)
        w = rc.right - rc.left
        h = rc.bottom - rc.top
        if is_vis and ('edit' in cls_buf.value.lower() or 'rich' in cls_buf.value.lower()):
            print(f"  Child {hwnd}: class='{cls_buf.value}', pos=({rc.left},{rc.top}), size={w}x{h}")
        return True
    WNDENUMCHILDPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    user32.EnumChildWindows(stata_hwnd, WNDENUMCHILDPROC(child_cb), 0)

subprocess.run(['taskkill', '/f', '/im', 'StataMP-64.exe'], capture_output=True)
