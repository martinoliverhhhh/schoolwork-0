import subprocess
import time
import ctypes
from ctypes import wintypes

WM_GETTEXT = 0x000D
BM_CLICK = 0x00F5

p = subprocess.Popen([r"C:\Program Files\Stata18\StataMP-64.exe"])
time.sleep(2)
user32 = ctypes.windll.user32

def find_button(dialog_hwnd):
    btns = []
    def child_cb(hwnd, lparam):
        cls_buf = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, cls_buf, 256)
        if cls_buf.value == 'Button':
            buf = ctypes.create_unicode_buffer(1024)
            user32.SendMessageW(hwnd, WM_GETTEXT, 1024, buf)
            btns.append((hwnd, buf.value))
        return True
    WNDENUMCHILDPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    user32.EnumChildWindows(dialog_hwnd, WNDENUMCHILDPROC(child_cb), 0)
    return btns

def find_dialogs():
    dialogs = []
    def enum_cb(hwnd, lparam):
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value == p.pid and user32.IsWindowVisible(hwnd):
            buf = ctypes.create_unicode_buffer(1024)
            user32.SendMessageW(hwnd, WM_GETTEXT, 1024, buf)
            if buf.value == 'Stata':
                dialogs.append(hwnd)
        return True
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    user32.EnumWindows(WNDENUMPROC(enum_cb), 0)
    return dialogs

d1 = find_dialogs()
print("Dialogs 1:", d1)
if d1:
    b1 = find_button(d1[0])
    print("Buttons 1:", b1)
    if b1:
        print("Clicking button 1...")
        user32.SendMessageW(b1[0][0], BM_CLICK, 0, 0)
        time.sleep(2)

d2 = find_dialogs()
print("Dialogs 2:", d2)
if d2:
    b2 = find_button(d2[0])
    print("Buttons 2:", b2)
    # Check text in d2
    def text_cb(hwnd, lparam):
        buf = ctypes.create_unicode_buffer(1024)
        user32.SendMessageW(hwnd, WM_GETTEXT, 1024, buf)
        cls_buf = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, cls_buf, 256)
        if buf.value:
            print(f"  Child {hwnd}: class={cls_buf.value}, text='{buf.value}'")
        return True
    WNDENUMCHILDPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    user32.EnumChildWindows(d2[0], WNDENUMCHILDPROC(text_cb), 0)
    if b2:
        print("Clicking button 2...")
        user32.SendMessageW(b2[0][0], BM_CLICK, 0, 0)
        time.sleep(2)

print("Poll after dialogs:", p.poll())
p.kill()
