import subprocess
import time
import ctypes
from ctypes import wintypes
import win32gui
import win32con
import win32api
import win32clipboard
import os

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

def force_foreground(hwnd):
    user32.ShowWindow(hwnd, 9) # SW_RESTORE
    fore_hwnd = user32.GetForegroundWindow()
    fore_tid = user32.GetWindowThreadProcessId(fore_hwnd, None)
    cur_tid = kernel32.GetCurrentThreadId()
    user32.AttachThreadInput(cur_tid, fore_tid, True)
    user32.SetForegroundWindow(hwnd)
    user32.SetFocus(hwnd)
    user32.AttachThreadInput(cur_tid, fore_tid, False)

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
    force_foreground(stata_hwnd)
    time.sleep(1)
    
    # Put command in clipboard
    cmd = 'do "c:/Users/12559/test_gui.do"'
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(cmd, win32clipboard.CF_UNICODETEXT)
    win32clipboard.CloseClipboard()
    
    # Send Ctrl+V
    win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
    win32api.keybd_event(ord('V'), 0, 0, 0)
    win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.5)
    # Send Enter
    win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
    win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
    
    print("Sent command to Stata! Waiting for completion...")
    for _ in range(20):
        time.sleep(1)
        log_path = r"c:\Users\12559\Desktop\社会调查实践\test_gui.log"
        if os.path.exists(log_path):
            print("LOG FILE FOUND!")
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                print(f.read())
            break

subprocess.run(['taskkill', '/f', '/im', 'StataMP-64.exe'], capture_output=True)
