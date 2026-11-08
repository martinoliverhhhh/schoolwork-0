import subprocess
import time
import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32

# Clean profile.do so Stata opens normally and stays open
with open(r'C:\Users\12559\Documents\profile.do', 'w', encoding='utf-8') as f:
    f.write('// clean\n')
with open(r'C:\Users\12559\profile.do', 'w', encoding='utf-8') as f:
    f.write('// clean\n')

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

print(f"Stata HWND: {stata_hwnd}")

if stata_hwnd:
    hmenu = user32.GetMenu(stata_hwnd)
    count = user32.GetMenuItemCount(hmenu)
    print(f"Top menu items count: {count}")
    for i in range(count):
        buf = ctypes.create_unicode_buffer(256)
        user32.GetMenuStringW(hmenu, i, buf, 256, 0x0400) # MF_BYPOSITION
        hsub = user32.GetSubMenu(hmenu, i)
        sub_count = user32.GetMenuItemCount(hsub) if hsub else 0
        print(f"Menu [{i}] '{buf.value}': subitems={sub_count}")
        if hsub:
            for j in range(sub_count):
                sbuf = ctypes.create_unicode_buffer(256)
                user32.GetMenuStringW(hsub, j, sbuf, 256, 0x0400)
                cmd_id = user32.GetMenuItemID(hsub, j)
                if sbuf.value:
                    print(f"    Submenu [{j}] '{sbuf.value}': ID={cmd_id}")

subprocess.run(['taskkill', '/f', '/im', 'StataMP-64.exe'], capture_output=True)
