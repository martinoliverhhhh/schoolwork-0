import subprocess
import time
import win32gui
import win32con
import win32api
import ctypes
from ctypes import wintypes
import os

user32 = ctypes.windll.user32
WM_SETTEXT = 0x000C
WM_CHAR = 0x0102
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

print(f"Stata HWND: {stata_hwnd}")

# Find '命令窗口' handle
ps_cmd = f'''
Add-Type -AssemblyName UIAutomationClient
$root = [System.Windows.Automation.AutomationElement]::FromHandle([IntPtr]{stata_hwnd})
$cond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, '命令窗口')
$elem = $root.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $cond)
if ($elem) {{ Write-Output $elem.Current.NativeWindowHandle }}
'''
res = subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, text=True)
cmd_pane_hwnd = int(res.stdout.strip())
print(f"Command Pane HWND: {cmd_pane_hwnd}")

# Find child edit of command pane
cmd_edit_hwnd = None
def child_cb(hwnd, lparam):
    global cmd_edit_hwnd
    cls_buf = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(hwnd, cls_buf, 256)
    print(f"  Command Pane Child: {hwnd}, class='{cls_buf.value}'")
    if 'rich' in cls_buf.value.lower() or 'edit' in cls_buf.value.lower():
        cmd_edit_hwnd = hwnd
    return True

WNDENUMCHILDPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
user32.EnumChildWindows(cmd_pane_hwnd, WNDENUMCHILDPROC(child_cb), 0)

print(f"Command Edit HWND: {cmd_edit_hwnd}")

if cmd_edit_hwnd:
    # Set text
    cmd_text = 'do "c:/Users/12559/test_gui.do"'
    buf = ctypes.create_unicode_buffer(cmd_text)
    user32.SendMessageW(cmd_edit_hwnd, WM_SETTEXT, 0, ctypes.byref(buf))
    time.sleep(0.5)
    
    # Send Enter key
    user32.PostMessageW(cmd_edit_hwnd, win32con.WM_KEYDOWN, VK_RETURN, 0)
    user32.PostMessageW(cmd_edit_hwnd, win32con.WM_KEYUP, VK_RETURN, 0)
    print("Posted Enter to Command Edit!")
    
    # Wait for log
    log_path = r"c:\Users\12559\Desktop\社会调查实践\test_gui.log"
    for i in range(15):
        time.sleep(1)
        if os.path.exists(log_path):
            print("SUCCESS! Log file found:")
            with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                print(f.read())
            break
    else:
        print("Timeout waiting for log file.")

subprocess.run(['taskkill', '/f', '/im', 'StataMP-64.exe'], capture_output=True)
