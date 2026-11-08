import subprocess
import time
import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32
WM_SETTEXT = 0x000C
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101
VK_RETURN = 0x0D

p = subprocess.Popen([r"C:\Users\12559\Desktop\stata182025.lnk"], shell=True)
time.sleep(3)

# Find Stata window
stata_hwnd = None
def enum_cb(hwnd, lparam):
    global stata_hwnd
    if user32.IsWindowVisible(hwnd):
        length = user32.GetWindowTextLengthW(hwnd)
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        if 'Stata/MP 18.0' in buf.value:
            stata_hwnd = hwnd
    return True

WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
user32.EnumWindows(WNDENUMPROC(enum_cb), 0)

print(f"Stata HWND: {stata_hwnd}")

if stata_hwnd:
    # Find child controls
    children = []
    def child_cb(hwnd, lparam):
        cls_buf = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, cls_buf, 256)
        children.append((hwnd, cls_buf.value))
        return True
    WNDENUMCHILDPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    user32.EnumChildWindows(stata_hwnd, WNDENUMCHILDPROC(child_cb), 0)
    print(f"Total children: {len(children)}")
    for h, cls in children:
        if 'edit' in cls.lower() or 'rich' in cls.lower():
            print(f"  Child {h}: class='{cls}'")

# Kill for now
subprocess.run(['taskkill', '/f', '/im', 'StataMP-64.exe'], capture_output=True)
