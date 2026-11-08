import subprocess
import time
import win32gui
import win32con
import win32api
import ctypes
from ctypes import wintypes
import os

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

SCI_SETTEXT = 2181
VK_RETURN = 0x0D

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

# Find Scintilla
scintilla_hwnd = None
def find_scintilla():
    global scintilla_hwnd
    def enum_all(hwnd, lparam):
        global scintilla_hwnd
        cls_buf = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, cls_buf, 256)
        if 'scintilla' in cls_buf.value.lower():
            scintilla_hwnd = hwnd
        return True
    user32.EnumChildWindows(stata_hwnd, WNDENUMCHILDPROC(enum_all), 0)

WNDENUMCHILDPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
find_scintilla()

print(f"Scintilla HWND: {scintilla_hwnd}")

if scintilla_hwnd:
    # Bring Stata to front and attach thread input
    stata_tid = user32.GetWindowThreadProcessId(stata_hwnd, None)
    cur_tid = kernel32.GetCurrentThreadId()
    user32.AttachThreadInput(cur_tid, stata_tid, True)
    user32.ShowWindow(stata_hwnd, 9)
    user32.SetForegroundWindow(stata_hwnd)
    user32.SetFocus(scintilla_hwnd)
    time.sleep(0.5)
    
    # Set text via SCI_SETTEXT
    cmd = b'do "c:/Users/12559/test_gui.do"\x00'
    user32.SendMessageA(scintilla_hwnd, SCI_SETTEXT, 0, cmd)
    time.sleep(0.5)
    
    # Send Enter key via keybd_event
    win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
    win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
    user32.AttachThreadInput(cur_tid, stata_tid, False)
    print("Sent Enter via keybd_event!")
    
    log_path = r"c:\Users\12559\Desktop\社会调查实践\test_gui.log"
    for i in range(10):
        time.sleep(1)
        if os.path.exists(log_path):
            print("SUCCESS! Log file found:")
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                print(f.read())
            break
    else:
        print("Timeout waiting for log.")

subprocess.run(['taskkill', '/f', '/im', 'StataMP-64.exe'], capture_output=True)
