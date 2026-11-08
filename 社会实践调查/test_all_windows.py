import subprocess
import time
import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32
p = subprocess.Popen([r"C:\Users\12559\Desktop\stata182025.lnk"], shell=True)
time.sleep(3)

# Find Stata PID
out = subprocess.check_output(['tasklist']).decode('gbk', errors='ignore')
stata_pid = None
for l in out.splitlines():
    if 'stata' in l.lower():
        parts = l.split()
        stata_pid = int(parts[1])
        print(f"Stata PID: {stata_pid}")

class RECT(ctypes.Structure):
    _fields_ = [("left", ctypes.c_long),
                ("top", ctypes.c_long),
                ("right", ctypes.c_long),
                ("bottom", ctypes.c_long)]

all_hwnds = []
def enum_cb(hwnd, lparam):
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    if pid.value == stata_pid and user32.IsWindowVisible(hwnd):
        buf = ctypes.create_unicode_buffer(256)
        user32.GetWindowTextW(hwnd, buf, 256)
        cls_buf = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, cls_buf, 256)
        rc = RECT()
        user32.GetWindowRect(hwnd, ctypes.byref(rc))
        w = rc.right - rc.left
        h = rc.bottom - rc.top
        print(f"HWND {hwnd}: class='{cls_buf.value}', title='{buf.value}', size={w}x{h}, pos=({rc.left},{rc.top})")
        all_hwnds.append(hwnd)
    return True

WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
user32.EnumWindows(WNDENUMPROC(enum_cb), 0)

subprocess.run(['taskkill', '/f', '/im', 'StataMP-64.exe'], capture_output=True)
